import re
from typing import Any

from chronicle.argument import ArgumentParser
from chronicle.event.value import Language


def test_main_argument() -> None:
    parser: ArgumentParser = ArgumentParser({"do"}).add_argument("argument")
    arguments: dict[str, Any] = parser.parse("work")

    assert arguments["argument"] == "work"


def test_argument_with_pattern() -> None:
    parser: ArgumentParser = (
        ArgumentParser({"do"})
        .add_argument("activity")
        .add_argument("language", pattern=re.compile("_(..)"))
    )
    arguments: dict[str, Any] = parser.parse("work _en")

    assert arguments["activity"] == "work"
    assert arguments["language"] == "en"


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
    arguments: dict[str, Any] = parser.parse("work _en")

    assert arguments["activity"] == "work"
    assert arguments["language"] == Language("en")
