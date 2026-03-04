"""Tests for date value type."""

from chronicle.value import Date

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_date_from_string_with_year() -> None:
    """`from_string` parses a full `yyyy-mm-dd` string."""
    result = Date.from_string("2022-03-15")
    assert isinstance(result, Date)
    assert result.year == 2022  # noqa: PLR2004
    assert result.month == 3  # noqa: PLR2004
    assert result.day == 15  # noqa: PLR2004


def test_date_from_string_without_year() -> None:
    """`from_string` parses `-mm-dd` string and leaves year as None."""
    result = Date.from_string("-01-20")
    assert isinstance(result, Date)
    assert result.year is None
    assert result.month == 1
    assert result.day == 20  # noqa: PLR2004


def test_date_from_string_december() -> None:
    """`from_string` parses December correctly."""
    result = Date.from_string("2000-12-31")
    assert result.year == 2000  # noqa: PLR2004
    assert result.month == 12  # noqa: PLR2004
    assert result.day == 31  # noqa: PLR2004
