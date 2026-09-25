# import numpy as np


# class ExpressionEvaluator:

#     @staticmethod
#     def evaluate(expression, x):

#         return eval(
#             expression,
#             {
#                 "__builtins__": {},
#                 "x": x,
#                 "np": np
#             }
#         )

import numpy as np


class ExpressionEvaluator:

    @staticmethod
    def evaluate(expression, x):

        with np.errstate(
            divide="ignore",
            invalid="ignore",
            over="ignore"
        ):

            return eval(
                expression,
                {
                    "__builtins__": {},
                    "x": x,

                    "np": np,

                    "sin": np.sin,
                    "cos": np.cos,
                    "tan": np.tan,

                    "asin": np.arcsin,
                    "acos": np.arccos,
                    "atan": np.arctan,

                    "exp": np.exp,
                    "log": np.log,
                    "log10": np.log10,

                    "sqrt": np.sqrt,
                    "abs": np.abs,

                    "pi": np.pi,
                    "e": np.e
                }
            )