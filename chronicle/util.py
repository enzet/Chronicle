"""Utility functions."""

import random
from collections.abc import Callable

from colour import Color

from chronicle.event.core import Event


def empty_filter(event: Event) -> bool:  # noqa: ARG001
    """Empty filter."""
    return True


def filter_by_year(year: int) -> Callable[[Event], bool]:
    """Filter by year."""

    def filter_(event: Event) -> bool:
        return event.time.get_moment().year == year

    return filter_


def smooth(data: list[float | None], size: int) -> list[float | None]:
    """Smooth data."""

    new_data: list[float | None] = []
    sublist: list[float] = []
    for index in range(len(data)):
        value = data[index]
        sublist.append(value if value else 0.0)
        if index > size:
            sublist = sublist[1:]
        new_data.append(
            sum(sublist) / len(sublist)
            if (sublist and sum(sublist) > 0)
            else None
        )
    return new_data


def modify_color(color: str) -> str:
    """Make color slightly darker or brighter by random."""
    red, green, blue = (
        int(color[1:3], 16),
        int(color[3:5], 16),
        int(color[5:7], 16),
    )
    red = int(red * (1 - random.random() / 10))
    green = int(green * (1 - random.random() / 10))
    blue = int(blue * (1 - random.random() / 10))
    return f"#{red:02x}{green:02x}{blue:02x}"


def pastelize(
    color: str, saturation_factor: float = 0.4, lightness_target: float = 0.8
) -> Color:
    """Convert a color to a pastel variant.

    :param color: color to pastelize
    :param saturation_factor: how much to scale down saturation
        (0-1, lower = softer)
    :param lightness_target: target lightness (0-1, higher = lighter)
    :return: pastelized color
    """

    c = Color(color)

    # Adjust saturation (c.saturation is 0–1)
    c.saturation = max(0.0, min(1.0, c.saturation * saturation_factor))

    # Adjust lightness (c.luminance is 0–1)
    c.luminance = max(0.0, min(1.0, lightness_target))

    return c
