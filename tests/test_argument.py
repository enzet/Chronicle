"""Test only creating and using arguments.

Arguments from existing events and objects should be tested in other test files.
"""

import re

from chronicle.argument import Argument, Arguments
from chronicle.objects.core import Objects
from chronicle.value import Language

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_main_argument() -> None:
    """Test main argument."""

    parser: Arguments = Arguments(["do"], "do").add(Argument("argument"))
    assert parser.parse(["work"], Objects()) == {"argument": "work"}


def test_argument_with_pattern() -> None:
    """Test argument with pattern and default extractor."""

    parser: Arguments = (
        Arguments(["do"], "do")
        .add(Argument("activity"))
        .add(
            Argument(
                "language",
                patterns=[re.compile("_(..)")],
                extractors=[lambda groups: Language(groups(1))],
            )
        )
    )
    assert parser.parse(["work", "_en"], Objects()) == {
        "activity": "work",
        "language": Language("en"),
    }


def test_argument_with_pattern_and_extractor() -> None:
    """Test argument with pattern and custom extractor."""

    parser: Arguments = (
        Arguments(["do"], "do")
        .add(Argument("activity"))
        .add(
            Argument(
                "language",
                patterns=[re.compile("_(..)")],
                extractors=[lambda groups: Language(groups(1))],
            )
        )
    )
    assert parser.parse(["work", "_en"], Objects()) == {
        "activity": "work",
        "language": Language("en"),
    }
