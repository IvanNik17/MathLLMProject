from manim import *

import sys
from pathlib import Path
# import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)


from scenes.base_math_scene import BaseMathScene

from visualize.manim_utils import create_explanation_text

class AIControlledScene(BaseMathScene):

    PLAN = None

    

    def construct(self):

        #### Validate plan
        plan = self.get_plan()

        self.validate_plan(
            plan,
            "ai_controlled"
        )

        # ==============================
        # Stage 0: Initialize variables 
        # ==============================
        correct_roots = plan.correct_roots()
        if "period" in plan.plan.additional_info.keys():
            correct_period = plan.additional_info["period"]
        title = None
        equation = None
        axes  = None
        graph  = None
        correct_root_markers = None
        student_roots_markers = None
        wrong_roots_markers = None
        second_period_marker = None
        marker_labels = None
        period_brace = None
        brace_label = None
        explanation_text = None
        
        # ==============================
        # Stage 1: Initialize scene essentials
        # ==============================
        title, equation = self.create_header()
        axes, graph = self.create_graph()

        # ==============================
        # Stage 2: Loop through steps
        # ==============================


        for step in plan.steps:
            print(step)


        # # ==============================
        # # Stage 3: Show roots
        # # ==============================


        # roots, root_texts = self.show_correct_roots(axes)


        # print(plan)
        # print("Explanation:", plan.explanation_text)

        # explanation = create_explanation_text(
        #     plan.explanation_text
        # )

        # explanation.to_edge(DOWN)


        # self.play(
        #     Write(explanation)
        # )

        # self.wait(2)

        # # ==============================
        # # Stage 4: Show period
        # # ==============================        
        # self.play(Unwrite(root_texts))
        # self.show_correct_period(axes)
        


        # # ==============================
        # # Stage 5: Final confirmation
        # # ==============================

        # final_text = create_explanation_text(
        #     f"Correct! Solutions: {correct_roots} Period: {correct_period}"
        # )

        # final_text.to_edge(DOWN)


        # self.play(
        #     Transform(
        #         explanation,
        #         final_text
        #     )
        # )

        # self.wait(2)
