# MathLLMProject
LLM-based mathematics tutor that analyzes a student's answer, generates pedagogical feedback, and produces a Manim visualization explaining the result.

## Project Structure

```text
MathLLMProject/
├── core/
│   └── explanation_plan.py
│
├── math_helper/
│   ├── answer_parser.py
│   ├── math_engine.py
│   ├── math_problem_parser.py
│   └── expression_evaluator.py
│
├── llm/
│   └── llm_explainer.py
│
├── visualize/
│   ├── manim_renderer.py
│   ├── manim_utils.py
│   ├── graph_builder.py
│   └── scenes/
│       ├── base_math_scene.py
│       ├── correct_answer_scene.py
│       ├── missed_solution_scene.py
│       ├── wrong_solution_scene.py
│       ├── extra_solution_scene.py
│       └── no_real_solution_scene.py
│
├── tests/
├── _APP_TEST_SCRIPT.py
├── requirements.txt
└── README.md
```

## Installation

Create the Conda environment:

    conda create -n MathLLM python=3.12

Activate it:

    conda activate MathLLM

Install the required packages:

    pip install -r requirements.txt

## Configuration

The API key should not be stored directly in the source code. Copy `.env.example` to `.env` in the project root and put the key there; `.env` is ignored by git.

    MATHLLM_API_KEY=YOUR_API_KEY


## Running the web app

From the project root, start the API as one process:

    uvicorn api_communication.api_server:app --port 8000

and in another terminal the frontend:

    cd frontend
    npm run dev

Without Vite: run `npm run build` in `frontend/` once, then the API server serves the built page from `frontend/dist`.

`POST /api/attempts` checks the answers can be read and replies at once with an attempt id; the work then happens in the background, and the frontend polls `GET /api/attempts/<id>` to show which stage it is on.

Rendered videos go in `data/` (ignored by git). Videos for wrong answers are deleted after a few hours; the video and feedback for a correct answer are stored once per problem and reused. 
Change `ANIMATION_VERSION` in `config.py` after editing a scene or the prompt, so stored videos are remade.

## Problems

The problem list is `content/problems.json`, written in LaTeX (with every backslash doubled, as JSON requires). The server re-reads it when it changes.
To check it after editing:

    python -m api_communication.problems

### Problems students add themselves

In the web app, "Add your own problem" at the top of the problem list opens a page for typing in an equation.

- The backend decides whether the equation can be used (`check_equation` in `api_communication/problems.py`, reached through `POST /api/problems/check`). The same check is applied to `content/problems.json`.
- An accepted problem is saved in the student's browser only (localStorage, see `frontend/src/storage/customProblems.ts`). The server keeps no list of them, so no login is needed and students can't see each other's problems. They are lost if the student clears their browser data.
- When the student answers one, the browser sends the equation itself with the attempt (`equation_latex` instead of `problem_id`), and the backend checks it again.

An equation is refused if the engine can't solve it, if SymPy's `solveset` disagrees with the engine about the solutions, or if it has infinitely many solutions. This keeps periodic equations such as `sin(x) = 0` out until the web app can ask for a period; the place to change it is `_all_real_solutions` in `problems.py`.

The check runs in a separate worker process with a time limit (`api_communication/custom_problems.py`), because some equations keep the solver busy for minutes.

To run the tests for the check:

    python -m pytest tests


## Running the engine without the web app

    python _APP_TEST_SCRIPT.py

## Testing different scenarios

In the _APP_TEST_SCRIPT.py, you can change:

    expression = "4*x - 4"
    student_answer = "x = 1, 5"

More examples:

| Scene             | Expression | Student Answer | Expected Result                                        |
| ----------------- | ---------- | -------------- | ------------------------------------------------------ |
| Correct answer    | `x**2 - 4` | `x = -2, 2`    | Both solutions are correct → `CorrectAnswerScene`      |
| Missed solution   | `x**2 - 4` | `x = -2`       | `x = 2` is missing → `MissedSolutionScene`             |
| Wrong solution    | `x**2 - 4` | `x = 3`        | `x = 3` is not a solution → `WrongSolutionScene`       |
| Extra solution    | `4*x - 4`  | `x = 1, 5`     | `x = 5` is an extra solution → `ExtraSolutionScene`    |
| No real solutions | `x**2 + 4` | `x = 2`        | Equation has no real solutions → `NoRealSolutionScene` |


## Generated Files

Some files are generated automatically during execution and should not be
edited or committed to the repository.

### `generated_scene.py`

`generated_scene.py` is created automatically by `ManimRenderer` whenever a
scene is rendered. It contains the selected Manim scene and the current
`ExplanationPlan`. Each render gets its own copy in its own folder
(`data/work/<attempt id>/` for the server, `media/test_render/` for
`_APP_TEST_SCRIPT.py`), which is what lets several renders run at once.

Do not edit this file manually. Changes should be made in the corresponding
source files under `visualization/`.

### `media/`

The `media/` directory contains Manim's generated video files, images, and
other rendering output.

This directory is generated automatically and is excluded from Git using
`.gitignore`.

If you need to change the appearance or behaviour of a scene, modify the
source scene in:

```text
visualization/scenes/
