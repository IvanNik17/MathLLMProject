import asyncio
import logging
import multiprocessing
from collections import OrderedDict

from api_communication import config
from api_communication.problems import Problem, ProblemError, build_custom_problem
from math_helper.expression_converter import MAX_LATEX_LENGTH

log = logging.getLogger(__name__)

# How many checked equations to remember
MAX_REMEMBERED = 500


class ServerBusyError(Exception):
    """Too many equations are already waiting to be checked."""


def _new_worker():
    # "spawn" starts a clean Python process, the same way on Windows and Linux.
    worker = multiprocessing.get_context("spawn").Pool(processes=1)
    # A new process has to import SymPy first, which takes a second or two. Doing a check now means that isn't counted against the first student's time limit.
    worker.apply(build_custom_problem, ("x = 1",))
    return worker


class CustomProblemChecker:

    def __init__(self):
        self._worker = None
        # Only one equation is checked at a time; the others wait for this lock
        self._turn = asyncio.Lock()
        self._waiting = 0
        # Equation -> the Problem it became, or the message saying why it can't be used
        self._remembered: OrderedDict[str, Problem | str] = OrderedDict()

    def start(self):
        self._worker = _new_worker()

    def stop(self):
        if self._worker:
            self._worker.terminate()

    async def check(self, latex) -> Problem:
        """The Problem for an equation a student typed. Raises ProblemError (safe to show the student) if it can't be used, or ServerBusyError."""
        latex = latex.strip()
        if len(latex) > MAX_LATEX_LENGTH:
            raise ProblemError("It is too long. Simplify it a little.")

        if latex not in self._remembered:
            if self._waiting >= config.MAX_WAITING_PROBLEM_CHECKS:
                raise ServerBusyError()

            self._waiting += 1
            try:
                async with self._turn:
                    # Someone else may have sent the same equation while we waited
                    if latex not in self._remembered:
                        outcome = await asyncio.to_thread(self._check_in_worker, latex)
                        self._remember(latex, outcome)
            finally:
                self._waiting -= 1

        outcome = self._remembered[latex]
        self._remembered.move_to_end(latex)

        if isinstance(outcome, str):
            raise ProblemError(outcome)
        return outcome

    def _check_in_worker(self, latex):
        """Returns a Problem, or the message saying why the equation can't be used."""
        result = self._worker.apply_async(build_custom_problem, (latex,))
        try:
            return result.get(timeout=config.PROBLEM_CHECK_SECONDS)
        except ProblemError as exc:
            return str(exc)
        except multiprocessing.TimeoutError:
            log.warning("Stopped checking %r after %s seconds", latex, config.PROBLEM_CHECK_SECONDS)
            self._worker.terminate()
            self._worker = _new_worker()
            return "This equation takes too long to solve, so it can't be used."
        except Exception:
            # Something in the parser or solver broke in a way check_equation didn't expect
            log.exception("Checking %r failed", latex)
            return "This equation couldn't be checked. Try writing it differently."

    def _remember(self, latex, outcome):
        self._remembered[latex] = outcome
        while len(self._remembered) > MAX_REMEMBERED:
            # Forget the one that was used longest ago
            self._remembered.popitem(last=False)
