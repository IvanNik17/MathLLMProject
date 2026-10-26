from manim import *

from math_helper.expression_evaluator import ExpressionEvaluator

from visualize.manim_utils import create_root_marker
from visualize.manim_utils import create_period_brace

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

        #Calculculate next period if relevant
        next_period = []
        if plan.additional_info is not None and "period" in plan.additional_info.keys():
            next_period.append(plan.correct_roots()[0] + plan.additional_info["period"])
        
        if plan.additional_info is not None and "student_period" in plan.additional_info.keys():
                    next_period.append(plan.correct_roots()[0] + plan.additional_info["student_period"])

        #Create axes
        axes = create_dynamic_axes(
            plan.expression,
            ExpressionEvaluator,
            student_roots=plan.student_roots(),
            correct_roots=plan.correct_roots(),
            x_values=next_period
        )

        graphs = GraphBuilder.build(
            axes,
            plan.expression,
            [(axes.x_min, axes.x_max)]
        )

        return axes, graphs


    def show_student_roots(self, axes):

        plan = self.get_plan()

        dots = []
        texts = []
        elevated = True

        for root in plan.student_roots():

            elevated = not elevated

            marker = create_root_marker(
                axes,
                root,
                color=RED,
                label=f"Student: x={root:g}",
                elevated=elevated
            )

            self.play(
                GrowFromCenter(marker)
            )
            dots.append(marker[0])
            texts.append(marker[1])

        return VGroup(*dots), VGroup(*texts)


    def show_correct_roots(self, axes):

        plan = self.get_plan()

        dots = []
        texts = []
        elevated = True

        for root in plan.correct_roots():

            elevated = not elevated

            marker = create_root_marker(
                axes,
                root,
                color=GREEN,
                label=f"Correct: x={root:g}",
                elevated=elevated
            )

            self.play(
                GrowFromCenter(marker)
            )
            dots.append(marker[0])
            texts.append(marker[1])

        return VGroup(*dots), VGroup(*texts)


    def show_correct_period(self, 
        axes, 
        _brace=None, 
        _brace_text=None, 
        tex_overide=None
    ):

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

        #Show first root of second period
        self.play(
            GrowFromCenter(second_period_marker)
        )

        #Create brace
        brace, brace_text = create_period_brace(
            axes,
            plan.correct_roots()[0],
            period
        )

        #Change text of brace if override is provided
        if tex_overide is not None:
            brace_text = brace.get_tex(tex_overide)

        #Transform old brace into new, if provided
        if _brace is not None and _brace_text is not None:
            anims = [Transform(_brace, brace),
                Transform(_brace_text, brace_text)]
            self.play(anims)
        else:
            self.play(
                GrowFromCenter(brace),
                GrowFromCenter(brace_text)
            )

        #return brace
        return brace, brace_text

    def show_student_period(self, 
        axes, 
        _brace=None, 
        _brace_text=None, 
        tex_overide=None
    ):

        plan = self.get_plan()

        # Get student period
        student_period = plan.additional_info["student_period"]

        # Create point for student period
        second_period_marker = create_root_marker(
            axes,
            plan.correct_roots()[0] + student_period,
            color=RED,
            label="Student answer next period"
        )

        self.play(
            GrowFromCenter(second_period_marker)
        )

        #Create brace
        brace, brace_text = create_period_brace(
            axes,
            plan.correct_roots()[0],
            student_period
        )

        #Change text of brace if override is provided
        if tex_overide is not None:
            brace_text = brace.get_tex(tex_overide)

        #Transform old brace into new, if provided
        if _brace is not None and _brace_text is not None:
            anims = [Transform(_brace, brace),
                Transform(_brace_text, brace_text)]
            self.play(anims)
        else:
            self.play(
                GrowFromCenter(brace),
                GrowFromCenter(brace_text)
            )

        #return brace
        return brace, brace_text, second_period_marker[0], second_period_marker[1]
        


    def validate_plan(
        self,
        plan,
        expected_type
    ):
        if plan.explanation_type != expected_type:
            raise ValueError(
                f"Expected {expected_type}"
            )