from answer_parser import AnswerParser
from math_problem_parser import MathProblemParser
from manim_renderer import ManimRenderer
from llm_explainer import LLMExplainer

import math_problem_parser

print(math_problem_parser.__file__)


expression =  "x**2 + 4"

student_answer = "I think the answer for x = 2"


llm = LLMExplainer(
        base_url="https://app-mathllm.cloud.sdu.dk/api",
        api_key="sk-335ecbf9d39940629b7884a4ade31a8e",
        model="mistral:latest"
    )


answer_parser = AnswerParser()

student_roots = answer_parser.parse_roots(
    student_answer
)


plan = MathProblemParser.parse(
    expression,
    student_roots
)


print()
print("Plan before LLM:")
print(plan)

plan.explanation_text = llm.explain(plan)

print()
print("LLM explanation:")
print(plan.explanation_text)


renderer = ManimRenderer()

renderer.render(plan)