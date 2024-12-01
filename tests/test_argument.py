"""Test only creating and using arguments.

Arguments from existing events and objects should be tested in other test files.
"""

import re

from chronicle.argument import Arguments
from chronicle.value import Language

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_main_argument() -> None:
    """Test main argument."""

    parser: Arguments = Arguments(["do"], "do").add_argument("argument")
    assert parser.parse(["work"], None) == {"argument": "work"}


def test_argument_with_pattern() -> None:
    """Test argument with pattern and default extractor."""

    parser: Arguments = (
        Arguments(["do"], "do")
        .add_argument("activity")
        .add_argument("language", patterns=[re.compile("_(..)")])
    )
    assert parser.parse(["work", "_en"], None) == {
        "activity": "work",
        "language": "en",
    }


def test_argument_with_pattern_and_extractor() -> None:
    """Test argument with pattern and custom extractor."""

    parser: Arguments = (
        Arguments(["do"], "do")
        .add_argument("activity")
        .add_argument(
            "language",
            patterns=[re.compile("_(..)")],
            extractors=[lambda groups: Language(groups(1))],
        )
    )
    assert parser.parse(["work", "_en"], None) == {
        "activity": "work",
        "language": Language("en"),
    }
