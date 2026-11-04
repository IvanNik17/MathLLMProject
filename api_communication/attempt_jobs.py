import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field

from api_communication import config
from api_communication.animation_store import AnimationStore
from api_communication.problems import Problem
from math_helper.math_problem_parser import MathProblemParser
from visualize.manim_renderer import RenderError

log = logging.getLogger(__name__)

# The stages a student sees, in order. "done" and "failed" end a job.
STAGES = ["checking_math", "writing_feedback", "animating"]


@dataclass
class AttemptJob:
    problem: Problem
    answers: list[str]
    student_roots: list[float]

    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: float = field(default_factory=time.time)
    finished_at: float | None = None

    stage: str = "checking_math"
    waiting: bool = False
    result: dict | None = None
    error: str | None = None

    @property
    def finished(self):
        return self.stage in ("done", "failed")

    def to_json(self):
        """What GET /api/attempts/<id> returns."""
        return {
            "attempt_id": self.id,
            "problem_id": self.problem.id,
            "stage": self.stage,
            "stages": STAGES,
            "waiting": self.waiting,
            "result": self.result,
            "error": self.error,
        }


class AttemptRunner:

    def __init__(self, store: AnimationStore, llm, renderer):
        self.store = store
        self.llm = llm
        self.renderer = renderer

        self.jobs: dict[str, AttemptJob] = {}

        self.render_slots = asyncio.Semaphore(config.MAX_PARALLEL_RENDERS)
        self.llm_slots = asyncio.Semaphore(config.MAX_PARALLEL_LLM_CALLS)

        self.correct_locks: dict[str, asyncio.Lock] = {}

        self._tasks: set[asyncio.Task] = set()

    # --- Public -------------------------------------------------------------

    def unfinished_count(self):
        return sum(1 for job in self.jobs.values() if not job.finished)

    def start(self, problem, answers, student_roots):
        job = AttemptJob(problem=problem, answers=answers, student_roots=student_roots)
        self.jobs[job.id] = job

        task = asyncio.create_task(self._run(job))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return job

    def get(self, attempt_id):
        return self.jobs.get(attempt_id)

    def forget_old_jobs(self):
        """Finished jobs are only kept while the frontend might still ask about them."""
        cutoff = time.time() - config.ATTEMPT_VIDEO_HOURS * 3600
        for attempt_id, job in list(self.jobs.items()):
            if job.finished and job.finished_at < cutoff:
                del self.jobs[attempt_id]

    # --- The pipeline -------------------------------------------------------

    async def _run(self, job):
        started = time.time()
        try:
            await self._pipeline(job)
            log.info(
                "Attempt %s on problem %s: %s in %.1fs",
                job.id[:8], job.problem.id, job.result["verdict"], time.time() - started,
            )
        except Exception:
            log.exception("Attempt %s failed", job.id)
            job.error = "Something went wrong while checking your answer. Please try again."
            job.stage = "failed"
        finally:
            job.waiting = False
            job.finished_at = time.time()

    async def _pipeline(self, job):
        job.stage = "checking_math"
        plan = await asyncio.to_thread(
            MathProblemParser.parse, job.problem.expression, job.student_roots
        )

        if plan.explanation_type == "correct":
            await self._correct_answer(job, plan)
            return

        text, _ = await self._write_feedback(job, plan)
        video_url = await self._animate(
            job, plan, save=lambda mp4: self.store.save_attempt_video(job.id, mp4)
        )
        self._finish(job, plan, text, video_url, reused=False)

    async def _correct_answer(self, job, plan):
        stored = self.store.find_correct(job.problem)
        if stored:
            self._finish(job, plan, stored.explanation_text, stored.video_url, reused=True)
            return

        key = self.store.correct_key(job.problem)
        lock = self.correct_locks.setdefault(key, asyncio.Lock())

        job.stage = "writing_feedback"
        job.waiting = lock.locked()
        async with lock:
            job.waiting = False

            # Someone else may have made it while we waited for the lock
            stored = self.store.find_correct(job.problem)
            if stored:
                self._finish(job, plan, stored.explanation_text, stored.video_url, reused=True)
                return

            # The video will be shown to everyone who gets this problem right, so it shows the exact roots rather than how this student wrote them
            plan.student_points = list(plan.correct_points)

            text, is_fallback = await self._write_feedback(job, plan)

            def save(mp4):
                # Only store it for reuse if the feedback came from the model.
                # Otherwise the next correct answer gets another try at it.
                if is_fallback:
                    return self.store.save_attempt_video(job.id, mp4)
                return self.store.save_correct(job.problem, mp4, text)

            video_url = await self._animate(job, plan, save)
            self._finish(job, plan, text, video_url, reused=False)

    async def _write_feedback(self, job, plan):
        """Asks the model for feedback. If it fails, uses the short text the math engine already put in the plan. Returns (text, is_fallback)."""
        job.stage = "writing_feedback"
        job.waiting = self.llm_slots.locked()

        async with self.llm_slots:
            job.waiting = False
            try:
                text = await asyncio.to_thread(self.llm.explain, plan)
            except Exception as exc:
                log.warning("Language model failed for attempt %s: %s", job.id[:8], exc)
                text = None

        if not text:
            return plan.explanation_text, True

        plan.explanation_text = text
        return text, False

    async def _animate(self, job, plan, save):
        """Renders the plan. `save` moves the finished mp4 into place and returns its URL."""
        job.stage = "animating"
        job.waiting = self.render_slots.locked()

        async with self.render_slots:
            job.waiting = False
            work_dir = self.store.new_work_dir(job.id)
            try:
                mp4 = await asyncio.to_thread(
                    self.renderer.render, plan, work_dir, config.RENDER_TIMEOUT_SECONDS
                )
                return save(mp4)
            except RenderError as exc:
                log.error("Render failed for attempt %s: %s", job.id[:8], exc)
                return None
            finally:
                self.store.discard_work_dir(work_dir)

    def _finish(self, job, plan, text, video_url, reused):
        job.result = {
            "problem_id": job.problem.id,
            "answers": job.answers,
            "student_roots": job.student_roots,
            "verdict": plan.explanation_type,
            "explanation_text": text,
            # None if the animation couldn't be made
            "video_url": video_url,
            # True when a stored correct-answer video was reused
            "reused": reused,
        }
        job.stage = "done"
