from manim import *

import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from scenes.base_math_scene import BaseMathScene
from manim_utils import create_explanation_text


class ExtraSolutionScene(BaseMathScene):

    PLAN = None

    def construct(self):

        plan = self.get_plan()

        self.validate_plan(
            plan,
            "extra_root"
        )

        extra_points = plan.extra_points

        title, equation = self.create_header()

        self.play(
            Write(title),
            Write(equation)
        )

        axes, graph = self.create_graph()

        self.play(
            Create(axes),
            Create(graph)
        )

        self.show_student_roots(
            axes
        )

        self.wait(1)

        if extra_points:

            extra_x, y_value = extra_points[0]

            explanation = create_explanation_text(
                f"x = {extra_x:g} gives y = {y_value:g}\n"
                f"{plan.explanation_text}"
            )

            explanation.to_edge(
                DOWN,
                buff=0.3
            )

            self.play(
                Write(explanation)
            )

            curve_point = Dot(
                axes.c2p(
                    extra_x,
                    y_value
                ),
                color=YELLOW
            )

            self.play(
                GrowFromCenter(curve_point)
            )

        self.wait(2)