import re

from chronicle.argument import Arguments
from chronicle.event.value import Language

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_main_argument() -> None:
    parser: Arguments = Arguments(["do"], "do").add_argument("argument")
    assert parser.parse("work") == {"argument": "work"}


def test_argument_with_pattern() -> None:
    parser: Arguments = (
        Arguments(["do"], "do")
        .add_argument("activity")
        .add_argument("language", patterns=[re.compile("_(..)")])
    )
    assert parser.parse("work _en") == {"activity": "work", "language": "en"}


def test_argument_with_pattern_and_loader() -> None:
    parser: Arguments = (
        Arguments(["do"], "do")
        .add_argument("activity")
        .add_argument(
            "language",
            patterns=[re.compile("_(..)")],
            extractors=[lambda x: Language(x(1))],
        )
    )
    assert parser.parse("work _en") == {
        "activity": "work",
        "language": Language("en"),
    }
