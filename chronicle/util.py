"""Utility functions."""

from collections.abc import Callable

from chronicle.event.core import Event


def empty_filter(event: Event) -> bool:
    """Empty filter."""
    return True


def filter_by_year(year: int) -> Callable[[Event], bool]:
    """Filter by year."""
    return lambda event: event.time.year == year


def smooth(data: list[float | None], size: int) -> list[float]:
    """Smooth data."""

    replaced: list[float] = [0 if x is None else x for x in data]
    new_data: list[float] = [
        sum(replaced[index - size + 1 : index + 1]) / size
        for index in range(len(data))
    ]
    return new_data
