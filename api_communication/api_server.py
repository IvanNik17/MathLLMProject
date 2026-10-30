import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api_communication import config
from api_communication.animation_store import AnimationStore
from api_communication.attempt_jobs import AttemptRunner
from api_communication.problems import ProblemBook
from llm.llm_explainer import LLMExplainer
from math_helper.expression_converter import AnswerFormatError, parse_numeric_answer
from visualize.manim_renderer import ManimRenderer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("api_server")

# Limits on what one request may contain
MAX_ANSWERS = 10


# These are created when the server starts (see lifespan below)
problem_book: ProblemBook
store: AnimationStore
runner: AttemptRunner


async def cleanup_loop():
    """Deletes old videos every few minutes, for as long as the server runs."""
    while True:
        try:
            store.cleanup(problem_book.all())
            runner.forget_old_jobs()
        except Exception:
            log.exception("Cleanup failed")
        await asyncio.sleep(config.CLEANUP_EVERY_MINUTES * 60)


@asynccontextmanager
async def lifespan(app):
    """Runs once at startup (before `yield`) and once at shutdown (after `yield`)."""
    global problem_book, store, runner

    # A broken problems.json stops the server here, with the reason
    problem_book = ProblemBook(config.PROBLEMS_FILE)
    store = AnimationStore(config.DATA_DIR)

    if not config.LLM_API_KEY:
        log.warning("MATHLLM_API_KEY is not set; feedback will fall back to the engine's short text")

    llm = LLMExplainer(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.LLM_MODEL,
        timeout=config.LLM_TIMEOUT_SECONDS,
    )
    runner = AttemptRunner(store, llm, ManimRenderer())

    cleanup_task = asyncio.create_task(cleanup_loop())
    log.info("Ready: %d problems, data in %s", len(problem_book.all()), config.DATA_DIR)

    yield

    cleanup_task.cancel()


app = FastAPI(lifespan=lifespan)


# The data the frontend must send when submitting answers
class AttemptRequest(BaseModel):
    problem_id: int
    answers: list[str]


@app.get("/api/problems")
async def get_problems():
    return [problem.to_json() for problem in problem_book.all()]


@app.post("/api/attempts", status_code=202)
async def create_attempt(request: AttemptRequest):
    """Reads the answers and starts checking them. Invalid answers are reported right away; otherwise the reply is the attempt's status, which the frontend then polls (GET /api/attempts/{attempt_id})."""
    problem = problem_book.get(request.problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    if not request.answers:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_answers", "message": "Enter at least one solution."},
        )
    if len(request.answers) > MAX_ANSWERS:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_answers", "message": f"Enter at most {MAX_ANSWERS} solutions."},
        )

    student_roots = []
    answer_errors = []
    for index, latex in enumerate(request.answers, start=1):
        try:
            # Runs in a thread, so a slow answer can't hold up other students
            value = await asyncio.to_thread(parse_numeric_answer, latex, problem.variable)
            student_roots.append(value)
        except AnswerFormatError as exc:
            answer_errors.append(f"Answer {index}: {exc}")

    if answer_errors:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "invalid_answers",
                "message": "Please correct the following answers:\n" + "\n".join(answer_errors),
            },
        )

    if runner.unfinished_count() >= config.MAX_UNFINISHED_ATTEMPTS:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "busy",
                "message": "Lots of users are submitting right now. Please try again in a minute.",
            },
        )

    job = runner.start(problem, request.answers, student_roots)
    return job.to_json()


@app.get("/api/attempts/{attempt_id}")
async def get_attempt(attempt_id: str):
    job = runner.get(attempt_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail="This attempt is no longer known (the server may have restarted). Please submit again.",
        )
    return job.to_json()


@app.get("/api/videos/{kind}/{filename}")
async def get_video(kind: str, filename: str):
    path = store.video_path(kind, filename)
    if path is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path=path, media_type="video/mp4")


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "problems": len(problem_book.all()),
        "unfinished_attempts": runner.unfinished_count(),
        "llm_configured": bool(config.LLM_API_KEY),
    }
