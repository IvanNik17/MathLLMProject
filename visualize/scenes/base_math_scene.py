from manim import *

from math_helper.expression_evaluator import ExpressionEvaluator

from visualize.manim_utils import create_root_marker

from visualize.manim_utils import (
    create_dynamic_axes,
    create_scene_title
)

from visualize.graph_builder import GraphBuilder

class BaseMathScene(Scene):

    PLAN = None


    def get_plan(self):

        if self.PLAN is None:
            raise ValueError(
                "Scene has no ExplanationPlan"
            )

        return self.PLAN



    def create_header(self):

        plan = self.get_plan()

        title = create_scene_title(
            f"Student answer: {plan.student_roots()}"
        )


        equation = Text(
            f"Solve: {plan.expression}=0"
        )

        equation.scale(0.6)

        equation.next_to(
            title,
            DOWN
        )


        return title, equation



    def create_graph(self):

        plan = self.get_plan()

        axes = create_dynamic_axes(
            plan.expression,
            ExpressionEvaluator,
            student_roots=plan.student_roots(),
            correct_roots=plan.correct_roots()
        )

        graphs = GraphBuilder.build(
            axes,
            plan.expression,
            axes.intervals
        )

        return axes, graphs


    def show_student_roots(self, axes):

        plan = self.get_plan()

        for root in plan.student_roots():

            marker = create_root_marker(
                axes,
                root,
                color=RED,
                label=f"Student: x={root:g}"
            )

            self.play(
                GrowFromCenter(marker)
            )


    def show_correct_roots(self, axes):

        plan = self.get_plan()

        for root in plan.correct_roots():

            marker = create_root_marker(
                axes,
                root,
                color=GREEN,
                label=f"Correct: x={root:g}"
            )

            self.play(
                GrowFromCenter(marker)
            )

    def show_correct_period(self, axes):

        plan = self.get_plan()

        # Get period
        period =  plan.additional_info["period"] 

        # Create next period point
        second_period_marker = create_root_marker(
            axes,
            plan.correct_roots()[0] + period,
            color=BLUE,
            label="Next period"
        )

        self.play(
            GrowFromCenter(second_period_marker)
        )

        # Create brace
        dot1 = Dot([plan.correct_roots()[0], 0 , 0])
        line = Line(dot1.get_center(), second_period_marker.get_center())
        brace = Brace(line)
        brace_text = brace.get_text(f"Correct Period: n * {period}")
        self.play(
            GrowFromCenter(brace),
            GrowFromCenter(brace_text)
        )

    def show_student_period(self, axes):

        plan = self.get_plan()

        # Get student period
        student_period = plan.additional_info["student_root"]

        # Create point for student period
        second_period_marker = create_root_marker(
            axes,
            plan.correct_roots()[0] + student_period,
            color=RED,
            label="Student answer"
        )

        self.play(
            GrowFromCenter(second_period_marker)
        )

        # Create brace
        dot1 = Dot([plan.correct_roots()[0], 0 , 0])
        line = Line(dot1.get_center(), second_period_marker.get_center())
        brace = Brace(line)
        brace_text = brace.get_text(f"Student Period: n * {period}")
        self.play(
            GrowFromCenter(brace),
            GrowFromCenter(brace_text)
        )
        


    def validate_plan(
        self,
        plan,
        expected_type
    ):
        if plan.explanation_type != expected_type:
            raise ValueError(
                f"Expected {expected_type}"
            )