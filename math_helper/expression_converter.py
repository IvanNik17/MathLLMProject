"""
Turns LaTeX (from the MathLive answer fields, or from content/problems.json) into SymPy expressions. 
This needed to be a lot bigger because SymPy's LaTeX parser reads every letter as a variable. 
On its own it turns "\\pi" into a variable called pi rather than 3.14159..., reads "1,5" as just 1, and gives a complex number for "\\sqrt[3]{-2}".
"""

import math
import re

import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy.parsing.latex.errors import LaTeXParsingError


class AnswerFormatError(ValueError):
    """The LaTeX couldn't be used. str(error) is safe to show to students."""


# ---------------------------------------------------------------------------
# Step 1: tidy the LaTeX text
# ---------------------------------------------------------------------------

# Much longer than any real answer. Limits how much work one request can cause.
MAX_LATEX_LENGTH = 300

# SymPy works exact numbers out in full, so 9^{9^{9}} would keep the server busy for hours. Exponents bigger than this are refused before anything is worked out.
MAX_EXPONENT = 1000

# Commands that only change spacing or size. They are removed.
_IGNORED_COMMANDS = [r"\displaystyle", r"\,", r"\;", r"\:", r"\!", "~"]

# Plain text replacements, applied in this order.
_REPLACEMENTS = [
    # MathLive sometimes writes \mleft( ... \mright) instead of \left( ... \right)
    (r"\mleft", r"\left"),
    (r"\mright", r"\right"),
    # MathLive's own names for e and i
    (r"\exponentialE", "e"),
    (r"\imaginaryI", "i"),
    # Absolute value bars. The parser only understands plain |x|.
    (r"\left\vert", "|"), (r"\right\vert", "|"),
    (r"\left|", "|"), (r"\right|", "|"),
    (r"\lvert", "|"), (r"\rvert", "|"), (r"\vert", "|"),
    # \dfrac and \tfrac are just differently sized fractions
    (r"\dfrac", r"\frac"),
    (r"\tfrac", r"\frac"),
]


def normalize_latex(latex: str) -> str:
    """Cleans up LaTeX so SymPy's parser accepts it. Raises AnswerFormatError for input that can't mean a single value (empty boxes, ±, commas)."""
    latex = latex.strip()

    if len(latex) > MAX_LATEX_LENGTH:
        raise AnswerFormatError("It is too long. Simplify it a little.")

    for command in _IGNORED_COMMANDS:
        latex = latex.replace(command, "")
    for old, new in _REPLACEMENTS:
        latex = latex.replace(old, new)

    # \operatorname{ln} -> \ln, and \mathrm{e} / \text{e} -> e
    latex = re.sub(r"\\operatorname\{(\w+)\}", r"\\\1", latex)
    latex = re.sub(r"\\(?:mathrm|text|mathit)\{([^{}]*)\}", r"\1", latex)

    # Unbraced square roots of numbers, e.g. \sqrt2 -> \sqrt{2}
    latex = re.sub(r"\\sqrt(?![{\[])\s*(\d+(?:\.\d+)?)", r"\\sqrt{\1}", latex)

    latex = latex.strip()

    if latex == "":
        raise AnswerFormatError("It is empty.")
    if r"\placeholder" in latex:
        raise AnswerFormatError("It still has an empty box. Fill it in or delete it.")
    if r"\pm" in latex or r"\mp" in latex:
        raise AnswerFormatError(
            "Write ± answers as two separate solutions, one with + and one with -."
        )
    if re.search(r"<|>|\\(?:le|leq|ge|geq|lt|gt|ne|neq)(?![a-zA-Z])", latex):
        raise AnswerFormatError("Use = rather than <, > or ≠.")
    if "," in latex:
        # SymPy would silently read "1,5" as 1, so refuse instead of guessing
        raise AnswerFormatError(
            "Use a dot decimal point (1.5, not 1,5), and put each solution in its own row."
        )

    return latex


# ---------------------------------------------------------------------------
# Step 2: parse, then fix what the parser gets wrong
# ---------------------------------------------------------------------------

def _refuse_huge_numbers(parsed):
    """Runs on the parser's output, before SymPy works anything out (the parser leaves 9^{9^{9}} as an unevaluated tree, so looking at it is cheap)."""
    if parsed.has(sp.factorial, sp.factorial2):
        raise AnswerFormatError("! (factorial) isn't supported here.")

    for node in sp.preorder_traversal(parsed):
        if getattr(node, "is_Pow", False) and not node.exp.free_symbols:
            try:
                size = abs(complex(sp.N(node.exp, 5)))
            except (TypeError, ValueError):
                continue
            if size > MAX_EXPONENT:
                raise AnswerFormatError("It contains a number far too large to work with.")


def _fix_constants(expression):
    """The parser treats every letter as a variable. Swap the letters that are really constants for SymPy's constants: pi -> π, e -> Euler's number, i -> √-1."""
    constants = {
        sp.Symbol("pi"): sp.pi,
        sp.Symbol("e"): sp.E,
        sp.Symbol("i"): sp.I,
    }
    return sp.sympify(expression).subs(constants).doit()


def _use_real_odd_roots(expression):
    """SymPy's (-2)**(1/3) is a complex number. In this course the cube root of -2 is the real number -1.26, so roots with an odd index of a negative number are replaced by their real value."""

    def is_odd_root_of_negative(node):
        return (
            node.is_Pow
            and node.exp.is_Rational
            and not node.exp.is_Integer
            and node.exp.q % 2 == 1
            and node.base.is_negative is True
        )

    def real_value(node):
        p, q = node.exp.p, node.exp.q
        return (-1) ** p * sp.Abs(node.base) ** sp.Rational(p, q)

    return expression.replace(is_odd_root_of_negative, real_value)


def latex_to_sympy(latex: str):
    """LaTeX -> SymPy. Equations ("a = b") come back as sp.Eq."""
    latex = normalize_latex(latex)

    try:
        parsed = parse_latex(latex, backend="antlr")
    except LaTeXParsingError as exc:
        raise AnswerFormatError("It couldn't be read as math. Check for typos.") from exc

    _refuse_huge_numbers(parsed)

    if isinstance(parsed, sp.Equality):
        lhs = _use_real_odd_roots(_fix_constants(parsed.lhs))
        rhs = _use_real_odd_roots(_fix_constants(parsed.rhs))
        return sp.Eq(lhs, rhs, evaluate=False)

    expression = _use_real_odd_roots(_fix_constants(parsed))

    if not isinstance(expression, sp.Expr):
        # e.g. something the parser turned into True/False
        raise AnswerFormatError("It couldn't be read as a number or an equation.")

    return expression


# ---------------------------------------------------------------------------
# Student answers
# ---------------------------------------------------------------------------

def parse_numeric_answer(latex: str, variable: str = "x") -> float:
    """Accepts anything that works out to a single real number: 2, -1.5, \\frac{1}{2}, 2\\sqrt{3}, \\sqrt[3]{-2}, \\pi/2, \\ln(2)"""
    expression = latex_to_sympy(latex)

    if isinstance(expression, sp.Equality):
        if expression.lhs != sp.Symbol(variable):
            raise AnswerFormatError(f"Write just the value of {variable}, not an equation.")
        expression = expression.rhs

    leftover_letters = sorted(str(s) for s in expression.free_symbols)
    if leftover_letters:
        raise AnswerFormatError(
            f"It contains {', '.join(leftover_letters)}. The answer should be a number."
        )

    if expression.has(sp.zoo, sp.oo, -sp.oo, sp.nan):
        raise AnswerFormatError("It doesn't work out to a number. Is something divided by zero?")

    try:
        value = complex(expression.evalf())
    except (TypeError, ValueError) as exc:
        raise AnswerFormatError("It couldn't be worked out as a number.") from exc

    if abs(value.imag) > 1e-9 * max(1.0, abs(value.real)):
        raise AnswerFormatError("It isn't a real number.")
    if not math.isfinite(value.real):
        raise AnswerFormatError("It is too large to work with.")

    return value.real
