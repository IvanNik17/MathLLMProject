import re
from sympy.parsing.latex import parse_latex
from sympy import pi as sympy_pi
from sympy import Symbol
def latex_to_sympy(latex: str):
    latex = latex.strip()
    latex = re.sub(
        r"\\sqrt(?!\{)\s*(-?\d+(?:\.\d+)?|\\pi)",
        r"\\sqrt{\1}",
        latex
    )

    print("Normalized LaTeX:", repr(latex))

    try:
        expression = parse_latex(latex, backend="antlr")

        # Replace a symbol named "pi" with SymPy's actual pi constant.
        expression = expression.subs(Symbol("pi"), sympy_pi)

        return expression

    except Exception as e:
        raise ValueError(
            f"Could not parse LaTeX: {latex}"
        ) from e