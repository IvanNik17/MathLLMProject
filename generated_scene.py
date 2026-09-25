from scenes.no_real_solution_scene import NoRealSolutionScene
from explanation_plan import ExplanationPlan
import numpy as np

NoRealSolutionScene.PLAN = ExplanationPlan(
    explanation_type='no_real_roots',
    expression='x**2 + 4',
    correct_points=[],
    student_points=[(2.0, 0)],
    steps=['show_graph', 'show_no_intersections', 'explain_no_real_roots'],
    wrong_points=[(2.0, 8.0)],
    missing_points=[],
    extra_points=[(2.0, 8.0)],
    annotations=[],
    explanation_text='The student has correctly identified that the square of x is 4. However, the equation x^2 + 4 has no real roots, which means there is no value for x that results in a real number for y. This can be seen in the extra point (2.0, 8.0) in the data provided, as 2^2 + 4 does not equal 8.'
)

class GeneratedScene(NoRealSolutionScene):
    pass