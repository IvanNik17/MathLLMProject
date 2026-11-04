from functools import lru_cache

import numpy as np
import sympy as sp


@lru_cache(maxsize=128)
def _compile(expression):
    """Turns a SymPy expression string, e.g. "log(x) - 2", into a fast NumPy function of x. lambdify knows every SymPy function , which the old eval() table had to list one by one."""
    x = sp.Symbol("x")
    return sp.lambdify(x, sp.sympify(expression), modules="numpy")


class ExpressionEvaluator:

    @staticmethod
    def evaluate(expression, x):
        """y for a given x (a number or a NumPy array). Outside the domain, e.g. log of a negative number, the answer is nan rather than an error."""
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            return _compile(expression)(x)
