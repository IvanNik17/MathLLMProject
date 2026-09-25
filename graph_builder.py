from manim import *
import numpy as np

from expression_evaluator import ExpressionEvaluator


class GraphBuilder:

    @staticmethod
    def build(
        axes,
        expression,
        intervals
    ):

        graphs = VGroup()

        for left, right in intervals:

            xs = np.linspace(
                left,
                right,
                800
            )

            points = []

            for x in xs:

                try:

                    y = ExpressionEvaluator.evaluate(
                        expression,
                        x
                    )

                    if not np.isfinite(y):
                        continue

                    # Avoid gigantic spikes
                    if abs(y) > 100:
                        continue

                    points.append(
                        axes.c2p(
                            float(x),
                            float(y)
                        )
                    )

                except Exception:
                    continue

            if len(points) < 2:
                continue

            curve = VMobject()

            curve.set_points_smoothly(
                points
            )

            curve.set_color(BLUE)

            graphs.add(curve)

        return graphs