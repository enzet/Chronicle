from typing import Any

from chronicle.argument import ArgumentParser


def test_main_argument() -> None:
    parser: ArgumentParser = ArgumentParser({"do"}).add_argument("argument")
    arguments: dict[str, Any] = parser.parse("work")

    assert arguments["argument"] == "work"
