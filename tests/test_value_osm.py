"""Tests for OSM value type."""

import pytest

from chronicle.errors import ChronicleValueError
from chronicle.value import OSM

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_osm_from_string() -> None:
    """`from_string` parses all three OSM fields into an OSM instance."""
    result = OSM.from_string("osm:way/123456/3")
    assert isinstance(result, OSM)
    assert result.type == "way"
    assert result.id == 123456  # noqa: PLR2004
    assert result.version == 3  # noqa: PLR2004


def test_osm_from_string_node() -> None:
    """`from_string` handles 'node' type."""
    result = OSM.from_string("osm:node/42/1")
    assert result.type == "node"
    assert result.id == 42  # noqa: PLR2004
    assert result.version == 1


def test_osm_pattern_no_match_raises() -> None:
    """`from_string` raises `ChronicleValueError` for a non-matching string."""
    with pytest.raises(ChronicleValueError):
        OSM.from_string("way/123456/3")  # missing 'osm:' prefix
