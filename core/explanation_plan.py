class ExplanationPlan:

    def __init__(
        self,
        explanation_type,
        expression,
        correct_points,
        student_points,
        steps,
        wrong_points=None,
        missing_points=None,
        extra_points=None,
        annotations=None,
        explanation_text=None
    ):
        self.explanation_type = explanation_type
        self.expression = expression
        self.correct_points = correct_points
        self.student_points = student_points
        self.steps = steps

        self.wrong_points = wrong_points or []
        self.missing_points = missing_points or []
        self.extra_points = extra_points or []
        self.annotations = annotations or []
        self.explanation_text = explanation_text

        self.validate()


    def __repr__(self):

        return {
            "type": self.explanation_type,
            "expression": self.expression,
            "correct_points": self.correct_points,
            "student_points": self.student_points,
            "steps": self.steps,
            "wrong_points": self.wrong_points,
            "missing_points": self.missing_points,
            "extra_points": self.extra_points,
            "annotations": self.annotations,
            "explanation_text": self.explanation_text
        }.__str__()
    


    def correct_roots(self):

        return [
            p[0]
            for p in self.correct_points
        ]


    def student_roots(self):

        return [
            p[0]
            for p in self.student_points
        ]
    
    def validate(self):

        valid_types = [
            "wrong_root",
            "missed_root",
            "correct",
            "extra_root",
            "no_real_roots"
        ]

        if self.explanation_type not in valid_types:

            raise ValueError(
                f"Unknown explanation type: "
                f"{self.explanation_type}"
            )


        valid_steps = [
            "show_graph",
            "show_student_answers",
            "highlight_wrong_answer",
            "evaluate_y_value",
            "show_correct_root",
            "highlight_missing_root",
            "explain_solution",
            "celebrate_solution",
            "highlight_extra_root",
            "show_no_intersections",
            "explain_no_real_roots"
        ]

        for step in self.steps:

            if step not in valid_steps:

                raise ValueError(
                    f"Unknown step: {step}"
                )


        if not isinstance(
            self.expression,
            str
        ):

            raise ValueError(
                "Expression must be a string"
            )


        if not isinstance(
            self.correct_points,
            list
        ):

            raise ValueError(
                "correct_points must be a list"
            )


        if not isinstance(
            self.student_points,
            list
        ):

            raise ValueError(
                "student_points must be a list"
            )


        if (len(self.correct_points) == 0 and self.explanation_type != "no_real_roots"):

            raise ValueError(
                "correct_points cannot be empty"
            )

    def wrong_roots(self):

        correct = self.correct_roots()
        student = self.student_roots()

        return [
            x
            for x in student
            if x not in correct
        ]


    def missing_roots(self):

        correct = self.correct_roots()
        student = self.student_roots()

        return [
            x
            for x in correct
            if x not in student
        ]