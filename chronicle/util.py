"""Utility functions."""

from typing import Callable

from chronicle.event.core import Event


def empty_filter(event: Event) -> bool:
    """Empty filter."""
    return True


def filter_by_year(year: int) -> Callable[[Event], bool]:
    """Filter by year."""
    return lambda event: event.time.year == year
