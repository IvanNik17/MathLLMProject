from manim import *
import sys
from pathlib import Path


sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
#Put all outer calls to libraries after this

# from explanation_plan import ExplanationPlan
# from expression_evaluator import ExpressionEvaluator

# from manim_utils import (
#     create_dynamic_axes,
#     create_root_marker,
#     create_scene_title,
#     create_bottom_text,
#     create_explanation_text,
#     create_label_text
# )

from scenes.base_math_scene import BaseMathScene
from manim_utils import create_root_marker, create_explanation_text

class WrongSolutionScene(BaseMathScene):

    PLAN = None

    # PLAN = ExplanationPlan(
    #     explanation_type="wrong_root",
    #     expression="x**2 - 4",
    #     correct_points=[
    #         (-2, 0),
    #         (2, 0)
    #     ],
    #     student_points=[
    #         (-2, 0),
    #         (3, 0)
    #     ],
    #     steps=[]
    # )

    def construct(self):

        # plan = WrongSolutionScene.PLAN

        plan = self.get_plan()


        self.validate_plan(
            plan,
            "wrong_root"
        )

        # student_roots = plan.student_roots()

        correct_roots = plan.correct_roots()



        # wrong_roots = plan.wrong_roots()

        # missing_roots = plan.missing_roots()

        # has_extra_root = len(wrong_roots) > 0 and len(missing_roots) == 0

        # wrong_root = None

        # if wrong_roots:
        #     wrong_root = wrong_roots[0]

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

        # correct_root = None

        # if missing_roots:
        #     correct_root = missing_roots[0]

        # =================================
        # Stage 1: Problem setup
        # =================================



        # title = create_scene_title(
        #     f"Student answer: roots are {student_roots}"
        # )


        # equation = Text(
        #     f"Solve: {plan.expression} = 0"
        # )

        # equation.scale(0.7)

        # equation.next_to(
        #     title,
        #     DOWN
        # )

        title, equation = self.create_header()

        


        self.play(
            Write(title),
            Write(equation)
        )


        # =================================
        # Stage 2: Graph
        # =================================

        # axes = create_dynamic_axes(
        #     plan.expression,
        #     ExpressionEvaluator,
        #     student_roots=student_roots,
        #     correct_roots=correct_roots
        # )

        # axes.shift(
        #     DOWN * 0.5
        # )

        # # graph = axes.plot(
        # #     lambda x: x**2 - 4,
        # #     x_range=[-3, 3],
        # #     color=BLUE
        # # )

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

        # axes, graph = self.create_graph(
        #     plan.expression,
        #     student_roots,
        #     correct_roots
        # )

        # axes.shift(
        #     DOWN * 0.5
        # )

        axes, graph = self.create_graph()


        self.play(
            Create(axes)
        )

        self.play(
            Create(graph)
        )


        # =================================
        # Stage 3: Student answers
        # =================================

        # student_points = [-2, 3]


        # for x_value in student_roots:

        #     dot = Dot(
        #         axes.c2p(x_value, 0),
        #         color=RED
        #     )

        #     label = Text(
        #         f"Student: x={x_value}"
        #     )

        #     if x_value == -2:

        #         label.next_to(
        #             dot,
        #             DOWN
        #         )

        #     else:

        #         label.next_to(
        #             dot,
        #             RIGHT
        #         )

        #     self.play(
        #         GrowFromCenter(dot),
        #         Write(label)
        #     )

        # =================================
# Stage 3: Student answers
# =================================

        # for x_value in student_roots:

        #     marker = create_root_marker(
        #         axes,
        #         x_value,
        #         color=RED,
        #         label=f"Student: x={x_value}"
        #     )

        #     self.play(
        #         GrowFromCenter(marker)
        #     )

        self.show_student_roots(axes)

        self.wait(2)


        # =================================
        # Stage 4: Investigate x = 3
        # =================================
        investigate_text = create_explanation_text(" ")
        if wrong_point is not None and not has_extra_root:

            wrong_x, y_value = wrong_point
            investigate_text = create_explanation_text(
                f"Let's check x = {wrong_x:g}"
            )

            investigate_text.to_corner(
                DL
            )


            self.play(
                Write(investigate_text)
            )


            # point on x-axis

            # student_x = Dot(
            #     axes.c2p(wrong_x, 0),
            #     color=RED
            # )


            # point on curve

            # y_value = wrong_root**2 - 4

            

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
                f"At x = {wrong_x:g},\ny = {y_value:g}"
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

        correction = create_explanation_text(
            plan.explanation_text
        )

        correction.to_corner(
            DL
        )


        self.play(
            FadeOut(investigate_text),
            Write(correction)
        )


        # correct_dot = Dot(
        #     axes.c2p(
        #         correct_root,
        #         0
        #     ),
        #     color=GREEN
        # )


        # correct_label = Text(
        #     f"Correct: x = {correct_root}"
        # )

        # correct_label.next_to(
        #     correct_root,
        #     UP
        # )

        # correct_label.shift(
        #     LEFT
        # )


        # self.play(
        #     GrowFromCenter(correct_dot),
        #     Write(correct_label)
        # )


        # if correct_root is not None:

        #     correct_marker = create_root_marker(
        #         axes,
        #         correct_root,
        #         color=GREEN,
        #         label=f"Correct: x = {correct_root}"
        #     )


        #     self.play(
        #         GrowFromCenter(correct_marker)
        #     )

        # else:

        #     extra_text = create_explanation_text(
        #         "Your answer contains an extra root"
        #     )

        #     extra_text.to_edge(
        #         DOWN,
        #         buff=0.3
        #     )

        #     self.play(
        #         Transform(
        #             correction,
        #             extra_text
        #         )
        #     )

        # if missing_roots:

        #     for root in missing_roots:

        #         correct_marker = create_root_marker(
        #             axes,
        #             root,
        #             color=GREEN,
        #             label=f"Correct: x={root:g}"
        #         )

        #         self.play(
        #             GrowFromCenter(correct_marker)
        #         )

        #     summary = create_explanation_text(
        #         f"Correct roots: {missing_roots}"
        #     )

        #     summary.to_edge(
        #         DOWN,
        #         buff=0.3
        #     )

        #     self.play(
        #         Transform(
        #             correction,
        #             summary
        #         )
        #     )

        if missing_points:

            for root, _ in missing_points:

                correct_marker = create_root_marker(
                    axes,
                    root,
                    color=GREEN,
                    label=f"Correct: x={root:g}"
                )

                self.play(
                    GrowFromCenter(correct_marker)
                )


            summary = create_explanation_text(
                f"Correct roots: {correct_roots}"
            )

            summary.to_edge(
                DOWN,
                buff=0.3
            )

            self.play(
                Transform(
                    correction,
                    summary
                )
            )

        self.wait(3)