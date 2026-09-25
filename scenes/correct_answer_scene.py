from manim import *

import sys
from pathlib import Path
# import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

# from expression_evaluator import ExpressionEvaluator
# from explanation_plan import ExplanationPlan
from scenes.base_math_scene import BaseMathScene

from manim_utils import create_explanation_text

class CorrectAnswerScene(BaseMathScene):

    PLAN = None

    # PLAN = ExplanationPlan(
    #     explanation_type="correct",
    #     expression="x**2 - 4",
    #     correct_points=[
    #         (-2,0),
    #         (2,0)
    #     ],
    #     student_points=[
    #         (-2,0),
    #         (2,0)
    #     ],
    #     steps=[]
    # )

    def construct(self):

        # plan = CorrectAnswerScene.PLAN

        # if plan.explanation_type != "correct":
        #     raise ValueError(
        #         "QuadraticCorrectAnswer requires correct plan"
        #     )

        plan = self.get_plan()

        self.validate_plan(
            plan,
            "correct"
        )

        # student_roots = plan.student_roots()

        correct_roots = plan.correct_roots()


        # ==============================
        # Stage 1: Problem setup
        # ==============================


        # title = create_scene_title(
        #     f"Student answer: roots are {student_roots}"
        # )


        # equation = Text(
        #     f"Solve: {plan.expression} = 0"
        # )

        title, equation = self.create_header()

        equation.scale(0.6)

        equation.next_to(
            title,
            DOWN
        )


        self.play(
            Write(title),
            Write(equation)
        )


        # ==============================
        # Stage 2: Graph
        # ==============================


        # axes = create_dynamic_axes(
        #     plan.expression,
        #     ExpressionEvaluator,
        #     student_roots=student_roots
        # )


        # graph = axes.plot(
        #     lambda x: ExpressionEvaluator.evaluate(
        #         plan.expression,
        #         x
        #     ),
        #     x_range=[
        #         axes.x_min,
        #         axes.x_max
        #     ],
        #     color=BLUE
        # )

        axes, graph = self.create_graph()


        self.play(
            Create(axes)
        )

        self.play(
            Create(graph)
        )


        # ==============================
        # Stage 3: Show roots
        # ==============================

        dots = []

        # for root in correct_roots:

        #     dot = Dot(
        #         axes.c2p(root,0),
        #         color=GREEN
        #     )

        #     dots.append(dot)

        # for root in correct_roots:

        #     marker = create_root_marker(
        #         axes,
        #         root,
        #         color=GREEN,
        #         label=f"x={root}"
        #     )

        #     self.play(
        #         GrowFromCenter(marker)
        #     )

        self.show_correct_roots(axes)


        # self.play(
        #     *[
        #         Create(dot)
        #         for dot in dots
        #     ]
        # )

        print(plan)
        print("Explanation:", plan.explanation_text)

        explanation = create_explanation_text(
            plan.explanation_text
        )

        explanation.to_edge(DOWN)


        self.play(
            Write(explanation)
        )

        self.wait(2)


        # ==============================
        # Stage 4: Final confirmation
        # ==============================

        final_text = create_explanation_text(
            f"Correct! Solutions: {correct_roots}"
        )

        final_text.to_edge(DOWN)


        self.play(
            Transform(
                explanation,
                final_text
            )
        )

        self.wait(2)