from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from math_helper.answer_parser import AnswerParser
from math_helper.math_problem_parser import MathProblemParser
from fastapi.responses import FileResponse
from pathlib import Path
from visualize.manim_renderer import ManimRenderer
from llm.llm_explainer import LLMExplainer

# create a fastAPI application
app = FastAPI()

# create instances of component used by the api
answer_parser = AnswerParser()
renderer = ManimRenderer()
llm = LLMExplainer(
    base_url="https://app-mathllm.cloud.sdu.dk/api",
    api_key="",
    model="mistral:latest"
)

# Define the data that frontend must send when submitting answers
class AttemptRequest(BaseModel):
    problem_id: int
    answer: str

# The current exercises that can be completed, can easily be expanded.
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
# This is here we handle user answers
@app.post("/api/attempts")
async def create_attempt(request: AttemptRequest):
    problems = await get_problems()

    # we retrieve all available exercises and run a for loop to find which one is selected
    problem = next(
        (p for p in problems if p["id"] == request.problem_id),
        None
    )
# just making sure it works, if no problem is found we put up an error
    if problem is None:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    # we find the students roots from their submitted answer
    student_roots = answer_parser.parse_roots(request.answer)

    # Compare the student's solutions with the correct solutions
    plan = MathProblemParser.parse(
        problem["equationLatex"],
        student_roots
    )
    # Ask Mistral to generate written feedback
    plan.explanation_text = llm.explain(plan)
    # just making sure the backend catches the students answer.
    print("Student answer:", request.answer)
    print("Selected explanation type:", plan.explanation_type)

    #generate the manim video using the explanation plan
    video_path = renderer.render(plan)

    # Send the result back to the frontend as JSON
    return {
        "problem_id": request.problem_id,
        "answer": request.answer,
        "student_roots": student_roots,
        "verdict": plan.explanation_type,
        "explanation_text": plan.explanation_text,
        "video_url":"/api/video"
    }
# Serve the generated video when requested by the frontend
@app.get("/api/video")
async def get_video():
    #Path to the mp4 file.
    video_path = Path("media/videos/generated_scene/480p15/GeneratedScene.mp4")

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )
    #Sending the file to the frontend so students can see
    return FileResponse(path=video_path, media_type="video/mp4")