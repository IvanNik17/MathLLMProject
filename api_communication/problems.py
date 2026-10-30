import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import sympy as sp

from math_helper.expression_converter import AnswerFormatError, latex_to_sympy
from math_helper.expression_evaluator import ExpressionEvaluator
from math_helper.math_engine import MathEngine

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Problem:
    id: int
    title: str
    # Shown to students
    equation_latex: str
    variable: str
    # The same equation as SymPy text, moved to the form "expression = 0"
    expression: str

    def to_json(self):
        """What the frontend receives."""
        return {
            "id": self.id,
            "title": self.title,
            "equationLatex": self.equation_latex,
            "variable": self.variable,
        }

    def fingerprint(self):
        """Short code that changes whenever the maths of the problem changes. Used for caching correct-answer feedback videos."""
        text = f"{self.variable}|{self.expression}"
        return hashlib.sha256(text.encode()).hexdigest()[:10]


class ProblemFileError(Exception):
    pass


def _build_problem(entry, position):
    """One entry of the JSON list -> Problem, or a ProblemFileError saying what's wrong."""
    where = f"Problem #{position} (id {entry.get('id', '?')})"

    for field in ("id", "title", "equationLatex"):
        if field not in entry:
            raise ProblemFileError(f"{where}: missing '{field}'")
    if not isinstance(entry["id"], int):
        raise ProblemFileError(f"{where}: 'id' must be a whole number")

    variable = entry.get("variable", "x")
    if variable != "x":
        # MathEngine and the scenes are written for x only
        raise ProblemFileError(f"{where}: the variable must be x (the engine only solves for x)")

    latex = entry["equationLatex"].strip()
    if "=" not in latex:
        latex += " = 0"

    try:
        equation = latex_to_sympy(latex)
    except AnswerFormatError as exc:
        raise ProblemFileError(f"{where}: couldn't read '{latex}': {exc}") from exc
    if not isinstance(equation, sp.Equality):
        raise ProblemFileError(f"{where}: '{latex}' should be an equation with one '='")

    expression = equation.lhs - equation.rhs
    letters = {str(s) for s in expression.free_symbols}
    if letters != {"x"}:
        raise ProblemFileError(
            f"{where}: the equation should contain x and no other letters, but has {sorted(letters) or 'none'}"
        )

    expression_text = str(expression)

    # Make sure the rest of the system can use it, now rather than mid-attempt
    try:
        MathEngine.solve_equation(expression_text)
    except Exception as exc:
        raise ProblemFileError(
            f"{where}: the math engine can't solve '{expression_text}' ({type(exc).__name__}: {exc})"
        ) from exc
    try:
        ExpressionEvaluator.evaluate(expression_text, 1.5)
    except Exception as exc:
        raise ProblemFileError(
            f"{where}: '{expression_text}' can't be drawn ({type(exc).__name__}: {exc})"
        ) from exc

    return Problem(
        id=entry["id"],
        title=entry["title"],
        equation_latex=latex,
        variable=variable,
        expression=expression_text,
    )


def load_problems(path: Path):
    """Reads and checks the whole file. All mistakes are reported together."""
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProblemFileError(f"{path.name} isn't valid JSON: {exc}") from exc

    if not isinstance(entries, list):
        raise ProblemFileError(f"{path.name} should contain a list: [ {{...}}, {{...}} ]")

    problems, errors = [], []
    for position, entry in enumerate(entries, start=1):
        try:
            problems.append(_build_problem(entry, position))
        except ProblemFileError as exc:
            errors.append(str(exc))

    ids = [p.id for p in problems]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        errors.append(f"These ids are used more than once: {duplicates}")

    if errors:
        raise ProblemFileError("\n".join(errors))

    return problems


class ProblemBook:
    """Holds the current problem list and reloads it when the file changes."""

    def __init__(self, path: Path):
        self.path = path
        self._problems = load_problems(path)
        self._loaded_mtime = path.stat().st_mtime

    def all(self):
        self._reload_if_changed()
        return list(self._problems)

    def get(self, problem_id):
        return next((p for p in self.all() if p.id == problem_id), None)

    def _reload_if_changed(self):
        try:
            mtime = self.path.stat().st_mtime
        except FileNotFoundError:
            log.error("%s has disappeared; keeping the last good problem list", self.path)
            return
        if mtime == self._loaded_mtime:
            return

        self._loaded_mtime = mtime
        try:
            self._problems = load_problems(self.path)
            log.info("Reloaded %d problems from %s", len(self._problems), self.path.name)
        except ProblemFileError as exc:
            log.error("%s has mistakes; keeping the last good list:\n%s", self.path.name, exc)


if __name__ == "__main__":
    import sys
    from api_communication.config import PROBLEMS_FILE

    try:
        for problem in load_problems(PROBLEMS_FILE):
            roots = MathEngine.solve_equation(problem.expression)
            print(f"{problem.id:>3}  {problem.equation_latex:<30} -> {problem.expression:<25} roots {roots}")
        print("All problems OK.")
    except ProblemFileError as exc:
        print(exc)
        sys.exit(1)
