from core.explanation_plan import ExplanationPlan
from math_helper.math_engine import MathEngine
from math_helper.expression_evaluator import ExpressionEvaluator
import sympy as sp


def roots_match(
        roots_a,
        roots_b,
        tolerance=0.01
    ):

        if len(roots_a) != len(roots_b):
            return False


        roots_a = sorted(
            roots_a
        )

        roots_b = sorted(
            roots_b
        )


        for a,b in zip(
            roots_a,
            roots_b
        ):

            if abs(a-b) > tolerance:
                return False


        return True

class MathProblemParser:


    @staticmethod
    def parse(
        expression,
        student_roots
    ):
        
        correct_roots = (
            MathEngine.solve_equation(
                expression
            )
        )

        wrong_roots = [
            x
            for x in student_roots
            if not any(abs(x - r) < 0.01 for r in correct_roots)
        ]

        missing_roots = [
            x
            for x in correct_roots
            if not any(abs(x - s) < 0.01 for s in student_roots)
        ]

        extra_roots = wrong_roots


        wrong_points = [
            (
                x,
                ExpressionEvaluator.evaluate(
                    expression,
                    x
                )
            )
            for x in wrong_roots
        ]

        missing_points = [
            (x, 0)
            for x in missing_roots
        ]

        extra_points = [
            (
                x,
                ExpressionEvaluator.evaluate(
                    expression,
                    x
                )
            )
            for x in extra_roots
        ]


        # No real roots

        print(ExplanationPlan)
        print(ExplanationPlan.__module__)

        if len(correct_roots) == 0:

            return ExplanationPlan(
                explanation_type="no_real_roots",
                expression=expression,
                correct_points=[],
                student_points=[
                    (x,0)
                    for x in student_roots
                ],
                steps=[
                    "show_graph",
                    "show_no_intersections",
                    "explain_no_real_roots"
                ],
                wrong_points=wrong_points,
                missing_points=missing_points,
                extra_points=extra_points,
                explanation_text="The graph never crosses the x-axis."
            )


        # Correct answer

        if roots_match(
            student_roots,
            correct_roots
        ):

            

            return ExplanationPlan(
                explanation_type="correct",
                expression=expression,
                correct_points=[
                    (x, 0)
                    for x in correct_roots
                ],
                student_points=[
                    (x, 0)
                    for x in student_roots
                ],
                steps=[
                    "show_graph",
                    "celebrate_solution"
                ],
                wrong_points=wrong_points,
                missing_points=missing_points,
                extra_points=extra_points,
                explanation_text="The graph crosses the x-axis at the correct solutions."
            )

        # Extra root

        if any(
            not any(
                abs(student-root)<0.01
                for root in correct_roots
            )
            for student in student_roots
        ) and len(student_roots) > len(correct_roots):


            return ExplanationPlan(
                explanation_type="extra_root",
                expression=expression,
                correct_points=[
                    (x,0)
                    for x in correct_roots
                ],
                student_points=[
                    (x,0)
                    for x in student_roots
                ],
                steps=[
                    "show_graph",
                    "show_student_answers",
                    "highlight_extra_root",
                    "explain_solution"
                ],
                wrong_points=wrong_points,
                missing_points=missing_points,
                extra_points=extra_points,
                explanation_text="One of the answers is not actually a root."
            )

        # Missed root

        if all(
            any(
                abs(student-root) < 0.01
                for root in correct_roots
            )
            for student in student_roots
        ):

            return ExplanationPlan(
                explanation_type="missed_root",
                expression=expression,
                correct_points=[
                    (x, 0)
                    for x in correct_roots
                ],
                student_points=[
                    (x, 0)
                    for x in student_roots
                ],
                steps=[
                    "show_graph",
                    "show_student_answers",
                    "highlight_missing_root",
                    "explain_solution"
                ],
                wrong_points=wrong_points,
                missing_points=missing_points,
                extra_points=extra_points,
                explanation_text="There is another solution."
            )


        # Wrong root

        return ExplanationPlan(
            explanation_type="wrong_root",
            expression=expression,
            correct_points=[
                (x, 0)
                for x in correct_roots
            ],
            student_points=[
                (x, 0)
                for x in student_roots
            ],
            steps=[
                "show_graph",
                "highlight_wrong_answer",
                "evaluate_y_value",
                "show_correct_root"
            ],
            wrong_points=wrong_points,
            missing_points=missing_points,
            extra_points=extra_points,
            explanation_text="A root is where y = 0."
        )

    @staticmethod
    def parse_periodic_equation(expression, student_roots, student_period=None):
        correct_roots, correct_period = MathEngine.solve_periodic_equation(expression)

        if correct_period is None or correct_period == 0:
            print("Error: equation is aperiodic!")
            return None #TODO: Find out what to do in this case

        complete_answers = [
            f"{x} + {correct_period}"
            for x in correct_roots
        ]

        complete_student_answers = [
            f"{x} + {student_period}"
            for x in student_roots
        ]

        #Wrong roots and points
        wrong_roots = [
            x
            for x in student_roots
            if not any(abs((abs(x) % round(correct_period, 2)) - r) < 0.01 for r in correct_roots)
        ]
        wrong_points = [
            (
                x,
                ExpressionEvaluator.evaluate(
                    expression,
                    x
                )
            )
            for x in wrong_roots
        ]

        missing_roots = [
            x
            for x in correct_roots
            if not any(abs(x - s) < 0.01 for s in student_roots)
        ]
        missing_points = [
            (x, 0)
            for x in missing_roots
        ]

        extra_roots = wrong_roots
        extra_points = [
            (
                x,
                ExpressionEvaluator.evaluate(
                    expression,
                    x
                )
            )
            for x in extra_roots
        ]

        # No real roots
        if len(correct_roots) == 0:
            return ExplanationPlan(
                explanation_type="no_real_roots",
                expression=expression,
                correct_points=[],
                student_points=[(x, 0) for x in student_roots],
                steps=[
                    "show_graph",
                    "show_no_intersections",
                    "explain_no_real_roots"
                ],
                wrong_points=wrong_points,
                missing_points=missing_points,
                extra_points=extra_points,
                explanation_text="The graph never crosses the x-axis.",
                additional_info={"period":round(correct_period, 3)}
            )
        # Correct answer
        if roots_match(student_roots, correct_roots) and MathEngine.expression_match(student_period, correct_period):
            return ExplanationPlan(
                explanation_type="correct_period",
                expression=expression,
                correct_points=[(x, 0) for x in correct_roots],
                student_points=[(x, 0) for x in student_roots],
                steps=[
                    "show_graph",
                    "celebrate_solution"
                ],
                wrong_points=wrong_points,
                missing_points=missing_points,
                extra_points=extra_points,
                explanation_text="The graph crosses the x-axis at the correct solutions.",
                additional_info={"period":round(correct_period, 3), 
                                 "student_period":round(sp.sympify(student_period), 3)
                        }
            )

        # Wrong period (and correct roots)
        if roots_match(student_roots, correct_roots) and not MathEngine.expression_match(student_period, correct_period):
                    return ExplanationPlan(
                        explanation_type="wrong_period",
                        expression=expression,
                        correct_points=[(x, 0) for x in correct_roots],
                        student_points=[(x, 0) for x in student_roots],
                        steps=[
                            "show_graph",
                            "celebrate_solution"
                        ],
                        wrong_points=wrong_points,
                        missing_points=missing_points,
                        extra_points=extra_points,
                        explanation_text="The graph crosses the x-axis at the correct solutions. But the given period is wrong.",
                        additional_info={"period":round(correct_period, 3), 
                                         "student_period":round(sp.sympify(student_period), 3)
                        }
                    )

        # Missing period (and correct roots)

        # Extra root
        if any(
            not any(
                abs(student-root)<0.01
                for root in correct_roots
            )
            for student in student_roots
        ) and len(student_roots) > len(correct_roots):


            return ExplanationPlan(
                explanation_type="extra_root",
                expression=expression,
                correct_points=[
                    (x,0)
                    for x in correct_roots
                ],
                student_points=[
                    (x,0)
                    for x in student_roots
                ],
                steps=[
                    "show_graph",
                    "show_student_answers",
                    "highlight_extra_root",
                    "explain_solution"
                ],
                wrong_points=wrong_points,
                missing_points=missing_points,
                extra_points=extra_points,
                explanation_text="One of the answers is not actually a root."
            )

        # Missed root
        if all(
            any(
                abs(student-root) < 0.01
                for root in correct_roots
            )
            for student in student_roots
        ):

            return ExplanationPlan(
                explanation_type="missed_root",
                expression=expression,
                correct_points=[
                    (x, 0)
                    for x in correct_roots
                ],
                student_points=[
                    (x, 0)
                    for x in student_roots
                ],
                steps=[
                    "show_graph",
                    "show_student_answers",
                    "highlight_missing_root",
                    "explain_solution"
                ],
                wrong_points=wrong_points,
                missing_points=missing_points,
                extra_points=extra_points,
                explanation_text="There is another solution."
            )

        # Wrong root
        return ExplanationPlan(
            explanation_type="wrong_root",
            expression=expression,
            correct_points=[(x, 0) for x in correct_roots],
            student_points=[(x, 0) for x in student_roots],
            steps=[
                "show_graph",
                "highlight_wrong_answer",
                "evaluate_y_value",
                "show_correct_root"
            ],
            wrong_points=wrong_points,
            missing_points=missing_points,
            extra_points=extra_points,
            explanation_text="For periodic functions we want to find everytime y = 0 for the first period and the period length",
            additional_info={"period":round(correct_period, 3)}
        )
    
    