"""Tests for Language value type."""

import pytest

from chronicle.errors import ChronicleValueError
from chronicle.value import Language

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_language_from_string() -> None:
    """`from_string` parses dot-prefixed ISO code into a Language instance."""
    assert Language.from_string(".en") == Language("en")


def test_language_from_string_various() -> None:
    """`from_string` works for several different language codes."""
    assert Language.from_string(".ru") == Language("ru")
    assert Language.from_string(".fr") == Language("fr")
    assert Language.from_string(".de") == Language("de")


def test_language_invalid_code_raises() -> None:
    """Constructing Language with an unknown code raises ChronicleValueError."""
    with pytest.raises(ChronicleValueError):
        Language("xx")


def test_language_equality() -> None:
    """Two Language objects with the same code compare equal."""
    assert Language("en") == Language("en")


def test_language_inequality() -> None:
    """Two Language objects with different codes are not equal."""
    assert Language("en") != Language("fr")


def test_language_to_string_english() -> None:
    """`to_string` returns the human-readable name of the language."""
    assert Language("en").to_string() == "English"


def test_language_to_string_russian() -> None:
    """`to_string` returns the human-readable name for Russian."""
    assert Language("ru").to_string() == "Russian"


def test_language_to_command() -> None:
    """`to_command` serialises back to the dot-prefixed code."""
    assert Language("ru").to_command() == ".ru"
    assert Language("en").to_command() == ".en"


def test_language_get_color() -> None:
    """`get_color` returns the configured hex color string."""
    assert Language("de").get_color() == "#F7D046"
    assert Language("en").get_color() == "#071B65"


def test_language_hash_deduplication() -> None:
    """Equal `Language` objects hash to the same value."""
    languages = {Language("en"), Language("en"), Language("fr")}
    assert len(languages) == 2  # noqa: PLR2004


def test_language_hash_equality() -> None:
    """Two equal `Language` objects produce the same hash."""
    assert hash(Language("en")) == hash(Language("en"))
