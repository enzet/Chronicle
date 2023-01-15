import re

from chronicle.argument import ArgumentParser
from chronicle.event.value import Language


def test_main_argument() -> None:
    parser: ArgumentParser = ArgumentParser({"do"}).add_argument("argument")
    assert parser.parse("work") == {"argument": "work"}


def test_argument_with_pattern() -> None:
    parser: ArgumentParser = (
        ArgumentParser({"do"})
        .add_argument("activity")
        .add_argument("language", pattern=re.compile("_(..)"))
    )
    assert parser.parse("work _en") == {"activity": "work", "language": "en"}


def test_argument_with_pattern_and_loader() -> None:
    parser: ArgumentParser = (
        ArgumentParser({"do"})
        .add_argument("activity")
        .add_argument(
            "language",
            pattern=re.compile("_(..)"),
            extractor=lambda x: Language(x(1)),
        )
    )
    assert parser.parse("work _en") == {
        "activity": "work",
        "language": Language("en"),
    }
