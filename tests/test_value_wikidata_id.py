"""Tests for `WikidataId` value type."""

import pytest

from chronicle.errors import ChronicleValueError
from chronicle.value import WikidataId

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_wikidata_id_from_string() -> None:
    """`from_string` strips the "Q" prefix and returns an integer."""
    result = WikidataId.from_string("Q12345")
    assert result == 12345  # noqa: PLR2004


def test_wikidata_id_from_string_small() -> None:
    """`from_string` works for small identifiers."""
    result = WikidataId.from_string("Q1")
    assert result == 1


def test_wikidata_id_pattern_no_match_raises() -> None:
    """`from_string` raises exception when the string doesn't match."""
    with pytest.raises(ChronicleValueError):
        WikidataId.from_string("12345")  # missing 'Q' prefix
