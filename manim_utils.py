from manim import *
import numpy as np
import textwrap

from math_engine import MathEngine


def create_dynamic_axes(
    expression,
    evaluator,
    x_values=None,
    student_roots=None,
    correct_roots=None
):

    intervals = MathEngine.get_sampling_intervals(
        expression
    )

    x_min = min(
        left
        for left, _
        in intervals
    )

    x_max = max(
        right
        for _, right
        in intervals
    )

    important_points = []

    if student_roots:
        important_points.extend(student_roots)

    if correct_roots:
        important_points.extend(correct_roots)

    if important_points:

        x_min = min(
            x_min,
            min(important_points) - 2
        )

        x_max = max(
            x_max,
            max(important_points) + 2
        )

    sample_x = np.concatenate([
        np.linspace(left, right, 300)
        for left, right in intervals
    ])

    sample_y = evaluator.evaluate(
        expression,
        sample_x
    )

    sample_y = np.asarray(sample_y)

    valid = (
        np.isfinite(sample_y)
        &
        ~np.isnan(sample_y)
    )

    sample_x = sample_x[valid]
    sample_y = sample_y[valid]

    if len(sample_y) == 0:

        y_min = -5
        y_max = 5

    else:

        sample_y = np.clip(
            sample_y,
            -20,
            20
        )

        y_min = sample_y.min()
        y_max = sample_y.max()

        if abs(y_max - y_min) < 1:

            y_min -= 1
            y_max += 1

        padding = max(
            1,
            (y_max - y_min) * 0.2
        )

        y_min -= padding
        y_max += padding

    x_step = calculate_step(
        x_max - x_min
    )

    y_step = calculate_step(
        y_max - y_min
    )

    axes = Axes(
        x_range=[
            x_min,
            x_max,
            x_step
        ],
        y_range=[
            y_min,
            y_max,
            y_step
        ],
        axis_config={
            "include_numbers": False
        }
    )

    axes.scale_to_fit_height(4)
    axes.move_to(ORIGIN)

    axes.x_min = x_min
    axes.x_max = x_max
    axes.intervals = intervals

    return axes



def create_root_marker(
    axes,
    x,
    color=GREEN,
    label=None
):

    dot = Dot(
        axes.c2p(x,0),
        color=color
    )

    objects = [dot]


    if label:

        text = Text(
            label
        ).scale(0.4)


        # put labels above by default
        text.next_to(
            dot,
            UP
        )


        objects.append(text)


    return VGroup(
        *objects
    )


def create_scene_title(text):

    title = Text(
        text
    )

    # Prevent long titles from dominating the screen
    if title.width > 5:
        title.scale(
            5 / title.width
        )

    title.to_corner(
        UL
    )

    return title



def create_bottom_text(text):

    t = Text(
        text
    )

    t.scale(0.7)

    t.to_edge(
        DOWN
    )

    return t





def create_explanation_text(text):

    wrapped_text = textwrap.fill(
        text,
        width=65
    )

    t = Text(
        wrapped_text,
        font_size=22,
        line_spacing=0.8
    )

    max_height = 1.5

    if t.height > max_height:
        t.scale(max_height / t.height)

    t.to_edge(
        DOWN,
        buff=0.2
    )

    return t


def create_label_text(text):

    t = Text(
        text
    )

    t.scale(
        0.4
    )

    return t


def calculate_step(value_range):

    size = abs(value_range)

    if size < 10:
        return 1

    if size < 50:
        return 5

    if size < 200:
        return 20

    return 50