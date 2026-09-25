from manim import *

import sys
from pathlib import Path
# import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)


from scenes.base_math_scene import BaseMathScene

from visualize.manim_utils import create_explanation_text

class CorrectAnswerScene(BaseMathScene):

    PLAN = None

    

    def construct(self):


        plan = self.get_plan()

        self.validate_plan(
            plan,
            "correct"
        )

       

        correct_roots = plan.correct_roots()


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


        self.show_correct_roots(axes)


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