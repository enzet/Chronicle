import re
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Argument:
    key: str
    description: str | None = None

    loader: Callable[[Any], Any] = lambda x: x
    """Value loader."""

    prefix: str | None = None
    """Prefix word that starts argument value."""

    pattern: re.Pattern | None = None
    """Value pattern."""

    extractor: Callable[[Any], Any] | None = None
    """Function that extracts values from a pattern matcher."""


class ArgumentParser:
    def __init__(self, prefixes: set[str]) -> None:
        self.prefixes: set[str] = prefixes
        self.arguments: list[Argument] = []

    def parse(self, text: str) -> dict[str, str] | None:

        main: Argument = self.arguments[0]
        result: dict[str, str] = {}
        words = text.split(" ")

        current_key: str | None = main.key
        current: str = ""

        for index in range(len(words)):

            word = words[index]
            detected: bool = False

            for argument in self.arguments:

                if word == argument.prefix:
                    if current:
                        result[current_key] = current
                        current = ""
                    current_key = argument.key
                    detected = True
                    break

                if argument.pattern and (
                    matcher := argument.pattern.match(word)
                ):
                    if current:
                        result[current_key] = current
                        current_key = None
                        current = ""
                    if argument.extractor is not None:
                        result[argument.key] = argument.extractor(matcher.group)
                    else:
                        result[argument.key] = argument.loader(matcher.group(1))
                    detected = True
                    break

            if not detected:
                current += (" " if current else "") + word

        if current:
            result[current_key] = current

        return result

    def add_argument(
        self,
        key: str,
        description: str | None = None,
        prefix: str | None = None,
        pattern: re.Pattern | None = None,
        loader: Callable[[Any], Any] = lambda x: x,
        extractor: Callable[[Any], Any] | None = None,
    ) -> "ArgumentParser":

        argument: Argument = Argument(
            key,
            description,
            prefix=prefix,
            pattern=pattern,
            loader=loader,
            extractor=extractor,
        )
        self.arguments.append(argument)
        return self
