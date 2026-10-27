import re
from sympy.parsing.latex import parse_latex


def latex_to_sympy(latex: str):
    latex = latex.strip()

    # Normalize unbraced square roots, e.g. \sqrt2 -> \sqrt{2}
    latex = re.sub(
        r"\\sqrt(?!\{)\s*(-?\d+(?:\.\d+)?)",
        r"\\sqrt{\1}",
        latex
    )

    print("Normalized LaTeX:", repr(latex))

    try:
        return parse_latex(latex, backend="antlr")
    except Exception as e:
        raise ValueError(f"Could not parse LaTeX: {latex}") from e