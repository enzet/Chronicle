"""Tests for tags value type."""

import pytest

from chronicle.errors import ChronicleValueError
from chronicle.value import Tags

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_tags_from_string_single() -> None:
    """`from_string` with one tag returns a set with that tag."""
    result = Tags.from_string("!work")
    assert result == {"work"}


def test_tags_from_string_multiple() -> None:
    """`from_string` with comma-separated tags returns the full set."""
    result = Tags.from_string("!work,home")
    assert result == {"work", "home"}


def test_tags_from_string_three() -> None:
    """`from_string` handles three comma-separated tags."""
    result = Tags.from_string("!a,b,c")
    assert result == {"a", "b", "c"}


def test_tags_pattern_no_match_raises() -> None:
    """`from_string` raises `ChronicleValueError` for bad string."""
    with pytest.raises(ChronicleValueError):
        Tags.from_string("work")  # Missing leading `!`.
