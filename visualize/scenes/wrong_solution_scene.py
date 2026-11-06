from manim import *
import sys
from pathlib import Path


sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)


from scenes.base_math_scene import BaseMathScene
from visualize.manim_utils import create_root_marker, create_explanation_text, format_number

class WrongSolutionScene(BaseMathScene):

    PLAN = None

    

    def construct(self):

        

        plan = self.get_plan()


        self.validate_plan(
            plan,
            "wrong_root"
        )

        

        correct_roots = plan.correct_roots()

        wrong_points = plan.wrong_points
        missing_points = plan.missing_points

        wrong_point = (
            wrong_points[0]
            if wrong_points
            else None
        )

        has_extra_root = (
            len(wrong_points) > 0 and
            len(missing_points) == 0
        )

        

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



        self.show_student_roots(axes)

        self.wait(2)


        # =================================
        # Stage 4: Investigate x = 3
        # =================================
        investigate_text = create_explanation_text(" ")
        if wrong_point is not None and not has_extra_root:

            wrong_x, y_value = wrong_point
            investigate_text = create_explanation_text(
                f"Let's check x = {format_number(wrong_x)}"
            )

            investigate_text.to_corner(
                DL
            )


            self.play(
                Write(investigate_text)
            )


            

            curve_point = Dot(
                axes.c2p(
                    wrong_x,
                    y_value
                ),
                color=YELLOW
            )


            vertical_line = Line(
                axes.c2p(
                    wrong_x,
                    0
                ),
                axes.c2p(
                    wrong_x,
                    y_value
                )
            )


            self.play(
                Create(vertical_line),
                GrowFromCenter(curve_point)
            )

            value_text = create_explanation_text(
                f"At x = {format_number(wrong_x)},\ny = {format_number(y_value)}"
            )

            value_text.next_to(
                curve_point,
                RIGHT
            )


            self.play(
                Write(value_text)
            )


            self.wait(2)


        # =================================
        # Stage 5: Reveal correct root
        # =================================

        self.play(
            FadeOut(investigate_text)
        )


        if missing_points:

            for root, _ in missing_points:

                correct_marker = create_root_marker(
                    axes,
                    root,
                    color=GREEN,
                    label=f"Correct: x={root:.3f}"
                )

                self.play(
                    GrowFromCenter(correct_marker)
                )

            formatted_roots = ", ".join(
                f"{root:.3f}"
                for root in correct_roots
            )

            summary = create_explanation_text(
                f"Correct roots: {formatted_roots}"
            )

            summary.to_edge(
                DOWN,
                buff=0.3
            )

            self.play(
                Write(summary)
            )

        self.wait(3)