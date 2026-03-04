"""Tests for programming language value type."""

from chronicle.value import ProgrammingLanguage

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_programming_language_from_string() -> None:
    """`from_string` parses a code into a `ProgrammingLanguage`."""
    result = ProgrammingLanguage.from_string(".python")
    assert isinstance(result, ProgrammingLanguage)
    assert result.code == "python"


def test_programming_language_from_string_short() -> None:
    """`from_string` works for single-character codes."""
    result = ProgrammingLanguage.from_string(".c")
    assert isinstance(result, ProgrammingLanguage)
    assert result.code == "c"
