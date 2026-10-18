from math_helper.answer_parser import AnswerParser
from math_helper.math_problem_parser import MathProblemParser
from visualize.manim_renderer import ManimRenderer
from llm.llm_explainer import LLMExplainer
import os

import math_helper.math_problem_parser

print(math_helper.math_problem_parser.__file__)

expression =  "sin(x)"

student_answer = "x = 0, x = 3.1415"
student_period = "2*pi"

llm = LLMExplainer(
        base_url="https://app-mathllm.cloud.sdu.dk/api",
        api_key=os.environ["MATHLLM_API_KEY"],
        model="mistral:latest"
    )


answer_parser = AnswerParser()

student_roots = answer_parser.parse_roots(
    student_answer
)

plan = MathProblemParser.parse_periodic_equation(expression, student_roots, student_period)
print(plan.additional_info)


renderer = ManimRenderer()

renderer.render(plan)

# plan = MathProblemParser.parse_periodic_equation(
#     expression,
#     student_roots
# )


# print()
# print("Plan before LLM:")
# print(plan)