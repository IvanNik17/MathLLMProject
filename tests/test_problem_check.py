"""
Which equations may be used as problems. Run from the project root with:

    python -m pytest tests
"""

import pytest

from api_communication.problems import ProblemError, build_custom_problem, check_equation


@pytest.mark.parametrize("latex, expression", [
    (r"x^{2} - 4 = 0", "x**2 - 4"),
    (r"2x + 3 = 7", "2*x - 4"),
    (r"x^2 - 4", "x**2 - 4"),              # no "=" means "= 0"
    (r"\frac{1}{x-2} = 3", "-3 + 1/(x - 2)"),
    (r"\ln(x) = 2", "log(x) - 2"),
    (r"\exponentialE^{x} = 5", "exp(x) - 5"),  # how MathLive writes e
    (r"x^2 = -1", "x**2 + 1"),             # no solutions is fine
    (r"\sin(x) = 2", "sin(x) - 2"),        # also no solutions, so not periodic
])
def test_usable_equations(latex, expression):
    assert check_equation(latex)[1] == expression


@pytest.mark.parametrize("latex, part_of_message", [
    ("", "Type an equation"),
    ("x^2 = 4 = 4", "exactly one"),
    ("x^2 =", "both sides"),
    ("y^2 = 4", "x as the only letter"),
    ("x = x", "no x left"),
    ("1,5x = 3", "decimal point"),
    (r"x^2 = \pm 4", "±"),
    (r"x^2 < 4", "Use ="),
    (r"\frac{x}{0} = 1", "divided by zero"),
    # Infinitely many solutions
    (r"\sin(x) = 0", "keep repeating"),
    (r"\tan(x) = 1", "keep repeating"),
    (r"(x-1)^2 = x^2 - 2x + 1", "whole range"),
    # The engine's answer would be wrong or incomplete
    (r"\sqrt[3]{x} = -2", "every solution"),
    (r"x^x = 2", "can't be sure"),
    # More than the rest of the app can show
    (r"x^2 = 10^{12}", "too large"),
    (r"(x-1)(x-1.01) = 0", "too close"),
    (r"(x-1)(x-2)(x-3)(x-4)(x-5)(x-6)(x-7)(x-8)(x-9)(x-10)(x-11) = 0", "at most"),
])
def test_refused_equations(latex, part_of_message):
    with pytest.raises(ProblemError) as error:
        check_equation(latex)
    assert part_of_message in str(error.value)


def test_custom_problem_has_no_id():
    problem = build_custom_problem("x^2 = 9")
    assert problem.is_custom
    assert problem.to_json() == {
        "id": None,
        "title": "Your problem",
        "equationLatex": "x^2 = 9",
        "variable": "x",
    }
