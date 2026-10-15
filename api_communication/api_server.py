from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from math_helper.answer_parser import AnswerParser
from math_helper.math_problem_parser import MathProblemParser
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()
answer_parser = AnswerParser()

class AttemptRequest(BaseModel):
    problem_id: int
    answer: str

@app.get("/api/problems")
async def get_problems():
    return [
    {
        "id": 1,
        "title": "Problem 1",
        "equationLatex": "x**2 - 4",
        "variable": "x"
    },
    {
        "id": 2,
        "title": "Problem 2",
        "equationLatex": "x ** 4 - 2",
        "variable": "x"
    },
    {
        "id": 3,
        "title": "Problem 3",
        "equationLatex": "x ** 5 - 2",
        "variable": "x"
    }]
# 3. Define the POST endpoint
@app.post("/api/attempts")
async def create_attempt(request: AttemptRequest):
    problems = await get_problems()

    # Find the selected problem
    problem = next(
        (p for p in problems if p["id"] == request.problem_id),
        None
    )

    if problem is None:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    # Extract the student's proposed solutions
    student_roots = answer_parser.parse_roots(request.answer)

    # Compare the student's solutions with the correct solutions
    plan = MathProblemParser.parse(
        problem["equationLatex"],
        student_roots
    )

    # Send the result back to the frontend
    return {
        "problem_id": request.problem_id,
        "answer": request.answer,
        "student_roots": student_roots,
        "verdict": plan.explanation_type,
        "explanation_text": plan.explanation_text
    }
@app.get("/api/video")
async def get_video():
    video_path = Path("media/videos/generated_scene/480p15/GeneratedScene.mp4")

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )

    return FileResponse(path=video_path, media_type="video/mp4")