from manim import *
import sys
from pathlib import Path
import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from expression_evaluator import ExpressionEvaluator

from manim_utils import (
    create_explanation_text,
    create_label_text
)


from scenes.base_math_scene import BaseMathScene

class NoRealSolutionScene(BaseMathScene):

    PLAN = None


    def construct(self):

        # plan = NoRealSolutionScene.PLAN


        # if plan.explanation_type != "no_real_roots":
        #     raise ValueError(
        #         "QuadraticNoRealRoots requires no_real_roots plan"
        #     )


        plan = self.get_plan()

        self.validate_plan(
            plan,
            "no_real_roots"
        )


        # title = create_scene_title(
        #     f"Solve: {plan.expression}=0"
        # )


        # self.play(
        #     Write(title)
        # )

        title, equation = self.create_header()

        self.play(
            Write(title),
            Write(equation)
        )


        # axes = create_dynamic_axes(
        #     plan.expression,
        #     ExpressionEvaluator
        # )


        # axes.shift(
        #     DOWN*0.5
        # )


        # graph = axes.plot(
        #     lambda x:
        #         ExpressionEvaluator.evaluate(
        #             plan.expression,
        #             x
        #         ),
        #     x_range=[
        #         axes.x_min,
        #         axes.x_max
        #     ],
        #     color=BLUE
        # )

        axes, graph = self.create_graph()


        self.play(
            Create(axes),
            Create(graph)
        )

        # =================================
        # Find minimum point
        # =================================

        sample_x = np.linspace(
            axes.x_min,
            axes.x_max,
            500
        )

        sample_y = [
            ExpressionEvaluator.evaluate(
                plan.expression,
                x
            )
            for x in sample_x
        ]


        min_index = np.argmin(sample_y)

        min_x = sample_x[min_index]
        min_y = sample_y[min_index]


        minimum_dot = Dot(
            axes.c2p(
                min_x,
                min_y
            ),
            color=YELLOW
        )


        minimum_label = create_label_text(
            f"Minimum: y={min_y:.2f}"
        )


        minimum_label.next_to(
            minimum_dot,
            UP
        )


        self.play(
            GrowFromCenter(minimum_dot),
            Write(minimum_label)
        )


        # =================================
        # Show distance above x-axis
        # =================================

        vertical_line = Line(
            axes.c2p(
                min_x,
                0
            ),
            axes.c2p(
                min_x,
                min_y
            )
        )


        self.play(
            Create(vertical_line)
        )


        gap_text = create_explanation_text(
            plan.explanation_text
        )


        gap_text.to_edge(
            DOWN,
            buff=0.3
        )


        self.play(
            Write(gap_text)
        )



        # explanation = create_explanation_text(
        #     "The parabola stays above the x-axis.\n"
        #     "Therefore there are no real roots."
        # )


        # explanation.to_edge(
        #     DOWN,
        #     buff=0.3
        # )


        # self.play(
        #     Write(explanation)
        # )


        self.wait(3)