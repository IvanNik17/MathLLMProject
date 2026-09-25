# MathLLMProject
LLM-based mathematics tutor that analyzes a student's answer, generates pedagogical feedback, and produces a Manim visualization explaining the result.

## Project Structure

```text
MathLLMProject/
├── core/
│   └── explanation_plan.py
│
├── mathematics/
│   ├── answer_parser.py
│   ├── math_engine.py
│   ├── math_problem_parser.py
│   └── expression_evaluator.py
│
├── llm/
│   └── llm_explainer.py
│
├── visualization/
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

The API key should not be stored directly in the source code.
Set the API key as an environment variable:

    set MATHLLM_API_KEY=YOUR_API_KEY

and then in code:

    import os
    
    api_key = os.environ["MATHLLM_API_KEY"]

## Running the application

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


The generated_scene.py and the visuals in the media should not be committed to GitHub
