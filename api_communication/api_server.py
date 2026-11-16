import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api_communication import config
from api_communication.animation_store import AnimationStore
from api_communication.attempt_jobs import AttemptRunner
from api_communication.custom_problems import CustomProblemChecker, ServerBusyError
from api_communication.problems import MAX_SOLUTIONS, ProblemBook, ProblemError
from llm.llm_explainer import LLMExplainer
from math_helper.expression_converter import AnswerFormatError, parse_numeric_answer
from visualize.manim_renderer import ManimRenderer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("api_server")

# Limits on what one request may contain
MAX_ANSWERS = MAX_SOLUTIONS


# These are created when the server starts (see lifespan below)
problem_book: ProblemBook
store: AnimationStore
runner: AttemptRunner
custom_checker: CustomProblemChecker


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
    global problem_book, store, runner, custom_checker

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

    # Starts the worker process that checks students' own equations. It takes a second or two, so it runs in a thread.
    custom_checker = CustomProblemChecker()
    await asyncio.to_thread(custom_checker.start)

    cleanup_task = asyncio.create_task(cleanup_loop())
    log.info("Ready: %d problems, data in %s", len(problem_book.all()), config.DATA_DIR)

    yield

    cleanup_task.cancel()
    custom_checker.stop()


app = FastAPI(lifespan=lifespan)


# The data the frontend must send when submitting answers
class AttemptRequest(BaseModel):
    # One of these two says which problem the answers are for:
    # the id of a problem from problems.json...
    problem_id: int | None = None
    # ...or the equation of a problem the student typed in themselves
    equation_latex: str | None = None
    answers: list[str]


# The data the frontend must send to have a student's own equation checked
class ProblemCheckRequest(BaseModel):
    equation_latex: str


@app.get("/api/problems")
async def get_problems():
    return [problem.to_json() for problem in problem_book.all()]


async def read_custom_problem(equation_latex):
    """The Problem for an equation a student typed in. Replies with an error the frontend can show if it can't be used."""
    try:
        return await custom_checker.check(equation_latex)
    except ProblemError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_problem", "message": str(exc)},
        )
    except ServerBusyError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "busy",
                "message": "Lots of users are adding problems right now. Please try again in a minute.",
            },
        )


@app.post("/api/problems/check")
async def check_problem(request: ProblemCheckRequest):
    """Says whether an equation a student typed in can be used as a problem."""
    problem = await read_custom_problem(request.equation_latex)
    return problem.to_json()


@app.post("/api/attempts", status_code=202)
async def create_attempt(request: AttemptRequest):
    """Reads the answers and starts checking them. Invalid answers are reported right away; otherwise the reply is the attempt's status, which the frontend then polls (GET /api/attempts/{attempt_id})."""
    if request.equation_latex is not None:
        # Checked again here, because anyone can send anything to this address
        problem = await read_custom_problem(request.equation_latex)
    else:
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


# --- The built frontend -------------------------------------------------------
# This must come after every /api route. A mount at "/" answers any path no route above has claimed.

class FrontendFiles(StaticFiles):
    """Serves frontend/dist, telling browsers how long they may keep each file."""

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if path.startswith("assets/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        else:
            response.headers["Cache-Control"] = "no-cache"
        return response


if (config.FRONTEND_DIST / "index.html").exists():
    # html=True: a request for "/" gets index.html
    app.mount("/", FrontendFiles(directory=config.FRONTEND_DIST, html=True), name="frontend")
else:
    log.info("No built frontend at %s; serving the API only (use `npm run dev` for the frontend)", config.FRONTEND_DIST)
