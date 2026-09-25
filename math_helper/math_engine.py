import sympy as sp
from sympy.calculus.util import continuous_domain


class MathEngine:

    @staticmethod
    def solve_equation(expression):

        x = sp.symbols("x")

        equation = sp.sympify(expression)

        solutions = sp.solve(
            equation,
            x
        )


        real_solutions = []

        for solution in solutions:

            if solution.is_real:
                real_solutions.append(
                    float(solution)
                )

        return MathEngine.normalize_roots(
            real_solutions
        )
    

    @staticmethod
    def normalize_roots(roots):

        normalized = []

        for root in roots:

            rounded = round(
                float(root),
                6
            )

            if rounded not in normalized:

                normalized.append(
                    rounded
                )

        return normalized

    @staticmethod
    def get_domain(expression):

        x = sp.symbols("x")

        expr = sp.sympify(expression)

        return continuous_domain(
            expr,
            x,
            sp.S.Reals
        )

    @staticmethod
    def get_sampling_intervals(expression):

        x = sp.symbols("x")

        expr = sp.sympify(expression)

        domain = MathEngine.get_domain(
            expression
        )

        roots = MathEngine.solve_equation(
            expression
        )

        # Default viewing window
        view_min = -5
        view_max = 5

        # Always include the roots with some padding
        if roots:

            view_min = min(
                view_min,
                min(roots) - 2
            )

            view_max = max(
                view_max,
                max(roots) + 2
            )

        intervals = []

        # ===========================
        # Entire real line
        # ===========================

        if domain == sp.S.Reals:

            return [
                (view_min, view_max)
            ]

        # ===========================
        # Single interval
        # ===========================

        if isinstance(domain, sp.Interval):

            if domain.start.is_finite:
                left = float(domain.start)
            else:
                left = view_min

            if domain.end.is_finite:
                right = float(domain.end)
            else:
                right = view_max

            if domain.left_open:
                left += 0.01

            if domain.right_open:
                right -= 0.01

            # Expand to include roots
            left = min(left, view_min)
            right = max(right, view_max)

            return [
                (left, right)
            ]

        # ===========================
        # Union of intervals
        # ===========================

        if isinstance(domain, sp.Union):

            for part in domain.args:

                if not isinstance(
                    part,
                    sp.Interval
                ):
                    continue

                if part.start.is_finite:
                    left = float(part.start)
                else:
                    left = view_min

                if part.end.is_finite:
                    right = float(part.end)
                else:
                    right = view_max

                if part.left_open:
                    left += 0.01

                if part.right_open:
                    right -= 0.01

                intervals.append(
                    (
                        left,
                        right
                    )
                )

            return intervals

        # Fallback
        return [
            (view_min, view_max)
        ]
    

if __name__ == "__main__":

    tests = [
        "x**2 - 4",
        "2*x + 4",
        "sqrt(x) - 3",
        "log(x) - 2",
        "1/x",
        "1/(x-2)",
        "exp(x)-5"
    ]

    for expr in tests:

        print(expr)
        print(MathEngine.get_domain(expr))
        print()

    print(MathEngine.get_sampling_intervals("1/(x-2)"))
    