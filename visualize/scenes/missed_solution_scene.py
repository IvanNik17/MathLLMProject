from manim import *

import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from scenes.base_math_scene import BaseMathScene
from visualize.manim_utils import (
    create_root_marker,
    create_explanation_text
)


class MissedSolutionScene(BaseMathScene):

    PLAN = None

    def construct(self):

        plan = self.get_plan()

        self.validate_plan(
            plan,
            "missed_root"
        )

        correct_roots = plan.correct_roots()

        missing_points = plan.missing_points
        missing_root, _ = missing_points[0]

        title, equation = self.create_header()

        self.play(
            Write(title),
            Write(equation)
        )

        axes, graph = self.create_graph()

        self.play(
            Create(axes)
        )

        self.play(
            Create(graph)
        )

        self.show_student_roots(
            axes
        )

        count = len(plan.student_points)

        if count == 1:
            message = "Correct! One solution has been found."
        else:
            message = f"Correct! {count} solutions have been found."

        correct_text = create_explanation_text(
            message
        )

        self.play(
            Write(correct_text)
        )

        self.wait(1)

        question = create_explanation_text(
            "Is there another solution?"
        )

        self.play(
            Transform(
                correct_text,
                question
            )
        )

        self.wait(1)

        missing_marker = create_root_marker(
            axes,
            missing_root,
            color=YELLOW,
            label=f"Missing: x={missing_root:g}"
        )

        reveal_text = create_explanation_text(
            plan.explanation_text
        )

        self.play(
            GrowFromCenter(missing_marker),
            Transform(
                correct_text,
                reveal_text
            )
        )

        self.wait(2)

        summary = create_explanation_text(
            f"Solutions: {correct_roots}"
        )

        self.play(
            Transform(
                correct_text,
                summary
            )
        )

        self.wait(2)