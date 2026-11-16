import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import sympy as sp

from math_helper.expression_converter import AnswerFormatError, latex_to_sympy, normalize_latex
from math_helper.expression_evaluator import ExpressionEvaluator
from math_helper.math_engine import MathEngine

log = logging.getLogger(__name__)

# --- Limits on what an equation may be -----------------------------------------
# The answer page has room for this many solutions (api_server refuses more answers than this)
MAX_SOLUTIONS = 10
# Solutions further from 0 than this make the graph in the video unreadable
MAX_SOLUTION_SIZE = 1000
# Answers within 0.01 of a solution count as correct, so solutions closer together than this can't be told apart
MIN_SOLUTION_GAP = 0.05


@dataclass(frozen=True)
class Problem:
    # A number for the problems in problems.json. None for a problem a student typed in themselves: those are kept in the student's browser, not on the server.
    id: int | None
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

    @property
    def is_custom(self):
        """True for a problem a student typed in themselves."""
        return self.id is None

    def fingerprint(self):
        """Short code that changes whenever the maths of the problem changes. Used for caching correct-answer feedback videos."""
        text = f"{self.variable}|{self.expression}"
        return hashlib.sha256(text.encode()).hexdigest()[:10]


# --- Is this equation usable as a problem? --------------------------------------

class ProblemError(Exception):
    """The equation can't be used as a problem. str(error) is safe to show to students."""


def check_equation(latex):
    """Decides whether an equation can be used as a problem.

    Returns (latex, expression): the tidied LaTeX to show, and the same equation as SymPy text moved to the form "expression = 0".
    Raises ProblemError, saying what is wrong, for anything the rest of the system couldn't handle correctly.

    Both problems.json and the equations students type in go through here, so they follow the same rules.
    An equation with no solutions is fine. One with infinitely many (sin(x) = 0) is refused for now: see the note in _all_real_solutions.
    """
    latex = latex.strip()

    if latex == "":
        raise ProblemError("Type an equation first.")
    if "," in latex:
        raise ProblemError("Use a dot as the decimal point (1.5, not 1,5).")
    if r"\pm" in latex or r"\mp" in latex:
        raise ProblemError("± can't be used in an equation.")
    if "=" not in latex:
        latex += " = 0"

    # Each side is read on its own
    sides = latex.split("=")
    if len(sides) != 2:
        raise ProblemError("It should be an equation with exactly one = sign.")
    if sides[0].strip() == "" or sides[1].strip() == "":
        raise ProblemError("Write something on both sides of the = sign.")
    try:
        left = latex_to_sympy(sides[0])
        right = latex_to_sympy(sides[1])
    except AnswerFormatError as exc:
        raise ProblemError(str(exc)) from exc

    expression = left - right
    if expression.has(sp.zoo, sp.oo, sp.nan):
        raise ProblemError("It doesn't work out to a number. Is something divided by zero?")
    if expression.has(sp.I):
        raise ProblemError("i (the imaginary unit) can't be used in a problem. Use x as the only letter.")

    letters = sorted(str(symbol) for symbol in expression.free_symbols)
    if not letters:
        raise ProblemError("Once it is simplified there is no x left in it, so there is nothing to solve.")
    if letters != ["x"]:
        # MathEngine and the scenes are written for x only
        raise ProblemError(f"Use x as the only letter. This equation has: {', '.join(letters)}.")

    expression_text = str(expression)

    # Make sure the rest of the system can use it, now rather than mid-attempt
    try:
        solutions = MathEngine.solve_equation(expression_text)
    except Exception as exc:
        raise ProblemError("The math engine can't solve this kind of equation yet.") from exc

    # MathEngine quietly returns only some of the solutions for a few kinds of equation, and answers would then be marked wrongly. So the solutions are worked out a second way, and the two must agree.
    if not _same_numbers(solutions, _all_real_solutions(expression_text)):
        raise ProblemError("The math engine can't find every solution of this equation yet.")

    if len(solutions) > MAX_SOLUTIONS:
        raise ProblemError(f"It has {len(solutions)} solutions. A problem can have {MAX_SOLUTIONS} at most.")
    if any(abs(solution) > MAX_SOLUTION_SIZE for solution in solutions):
        raise ProblemError("Its solutions are too large to show on a graph.")
    ordered = sorted(solutions)
    if any(b - a < MIN_SOLUTION_GAP for a, b in zip(ordered, ordered[1:])):
        raise ProblemError("Two of its solutions are too close together to tell apart.")

    # The video needs to draw it
    try:
        ExpressionEvaluator.evaluate(expression_text, 1.5)
        MathEngine.get_sampling_intervals(expression_text)
    except Exception as exc:
        raise ProblemError("This equation can't be drawn as a graph.") from exc

    # The tidied LaTeX is what gets shown: MathLive writes some things (\mleft, \exponentialE) that KaTeX can't display
    return normalize_latex(latex), expression_text


def _all_real_solutions(expression_text):
    """Every real solution as a sorted list of numbers, or a ProblemError if there is no such list.

    Uses SymPy's solveset. Unlike solve (which MathEngine uses), solveset says so when an equation has infinitely many solutions, and when it can't be sure it found them all.

    Periodic equations are refused here. MathEngine.solve_periodic_equation and the period scenes exist, but the web app can't use them yet (there is no way to enter a period, and attempt_jobs always calls MathProblemParser.parse). When that is in place, this is where to let them through.
    """
    try:
        solutions = sp.solveset(sp.sympify(expression_text), sp.Symbol("x"), sp.S.Reals)
    except Exception as exc:
        raise ProblemError("The math engine can't solve this kind of equation yet.") from exc

    if solutions.is_empty:
        return []

    if isinstance(solutions, sp.FiniteSet):
        try:
            return sorted(float(solution) for solution in solutions)
        except (TypeError, ValueError) as exc:
            raise ProblemError("The math engine can't solve this kind of equation yet.") from exc

    # A ConditionSet is SymPy saying "the solutions are whichever x make this true"
    if solutions.has(sp.ConditionSet):
        raise ProblemError("The math engine can't be sure it finds every solution of this equation, so it can't be used yet.")

    # ImageSet is how SymPy writes "one solution for every whole number n", e.g. x = n*pi
    if solutions.has(sp.ImageSet):
        raise ProblemError(
            "This equation has infinitely many solutions that keep repeating (like sin(x) = 0). Those can't be used as problems yet."
        )
    if solutions.has(sp.Interval):
        raise ProblemError("This is true for a whole range of x values, so there is no list of solutions to find.")

    raise ProblemError("The math engine can't be sure it finds every solution of this equation, so it can't be used yet.")


def _same_numbers(first, second, tolerance=1e-4):
    if len(first) != len(second):
        return False
    return all(abs(a - b) <= tolerance for a, b in zip(sorted(first), sorted(second)))


def build_custom_problem(latex):
    """A Problem from an equation a student typed in, or a ProblemError saying why not."""
    latex, expression = check_equation(latex)
    return Problem(
        id=None,
        title="Your problem",
        equation_latex=latex,
        variable="x",
        expression=expression,
    )


# --- problems.json ---------------------------------------------------------------

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

    try:
        latex, expression_text = check_equation(entry["equationLatex"])
    except ProblemError as exc:
        cause = exc.__cause__
        detail = f" ({type(cause).__name__}: {cause})" if cause else ""
        raise ProblemFileError(f"{where}: '{entry['equationLatex']}': {exc}{detail}") from exc

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
