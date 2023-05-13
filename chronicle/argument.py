import logging
import re
from dataclasses import dataclass
from typing import Any, Callable

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class Argument:
    key: str
    description: str | None = None

    loader: Callable[[Any], Any] = lambda x: x
    """Value loader."""

    prefix: str | None = None
    """Prefix word that starts argument value."""

    patterns: list[re.Pattern] | None = None
    """Value patterns."""

    extractors: list[Callable[[Any], Any]] | None = None
    """Functions that extract values from a pattern matchers."""

    pretty_printer: Callable = lambda x: x.to_string()

    command_printer: Callable = lambda x: x.to_command()

    html_printer: Callable = lambda x: x.to_string()


class Arguments:
    def __init__(self, prefixes: list[str], command: str) -> None:
        self.prefixes: list[str] = prefixes
        self.command: str = command
        self.arguments: list[Argument] = []

    def parse(self, text: str) -> dict[str, Any]:
        # Event may have no arguments.
        if not self.arguments:
            return {}

        main: Argument = self.arguments[0]
        result: dict[str, str] = {}
        words: list[str] = text.split(" ")

        current_key: str | None = main.key
        current: str = ""

        for index in range(len(words)):
            word: str = words[index]
            detected: bool = False

            for argument in self.arguments:
                if word == argument.prefix:
                    if current:
                        result[current_key] = current
                        current = ""
                    current_key = argument.key
                    detected = True
                    break

                if not argument.patterns:
                    continue

                for i, pattern in enumerate(argument.patterns):
                    if matcher := pattern.match(word):
                        if current:
                            result[current_key] = current
                            current_key = None
                            current = ""
                        if argument.extractors is not None:
                            result[argument.key] = argument.extractors[i](
                                matcher.group
                            )
                        else:
                            result[argument.key] = argument.loader(
                                matcher.group(1)
                            )
                        detected = True
                        break

            if not detected:
                current += (" " if current else "") + word

        if current and current_key:
            result[current_key] = current

        return result

    def add_argument(
        self,
        key: str,
        description: str | None = None,
        prefix: str | None = None,
        patterns: list[re.Pattern] | None = None,
        loader: Callable[[Any], Any] = lambda x: x,
        extractors: list[Callable[[Any], Any]] | None = None,
        pretty_printer: Callable = lambda o, v: v.to_string(o),
        command_printer: Callable = None,
        html_printer: Callable = lambda o, v: v.to_string(o),
    ) -> "Arguments":
        argument: Argument = Argument(
            key,
            description,
            prefix=prefix,
            patterns=patterns,
            loader=loader,
            extractors=extractors,
            pretty_printer=pretty_printer,
            command_printer=command_printer,
            html_printer=html_printer,
        )
        self.arguments.append(argument)
        return self

    def add(self, argument: Argument) -> "Arguments":
        self.arguments.append(argument)
        return self

    def to_string(self, objects, value):
        text = self.command
        for argument in self.arguments:
            if hasattr(value, argument.key) and getattr(value, argument.key):
                string: str = argument.pretty_printer(
                    objects, getattr(value, argument.key)
                )
                if string:
                    text += " " + string
        return text

    def to_html(self, objects, value):
        text = self.command
        for argument in self.arguments:
            if hasattr(value, argument.key) and getattr(value, argument.key):
                string: str = argument.html_printer(
                    objects, getattr(value, argument.key)
                )
                if string:
                    text += " " + string
        return text

    def to_object_command(self, value):
        text = ""
        for argument in self.arguments:
            if hasattr(value, argument.key) and getattr(value, argument.key):
                try:
                    v = getattr(value, argument.key)
                    if argument.command_printer:
                        string: str = argument.command_printer(v)
                    elif getattr(v, "to_command", None):
                        string: str = v.to_command()
                    else:
                        string: str = str(v)

                    if string:
                        if text:
                            text += " " + string
                        else:
                            text += string
                except AttributeError:
                    logging.error(
                        f"Cannot print command for {argument.key} of {value}."
                    )
        return text

    def get_command(self, value):
        text = value.time.to_pseudo_edtf_time() + " " + self.prefixes[0]
        for argument in self.arguments:
            if hasattr(value, argument.key):
                if getattr(value, argument.key):
                    v = getattr(value, argument.key)
                    if argument.command_printer:
                        string: str = argument.command_printer(v)
                    elif getattr(v, "to_command", None):
                        string: str = v.to_command()
                    else:
                        string: str = str(v)
                    if string:
                        text += " " + string
            else:
                logging.error(f"No {argument.key} of {value}.")
        return text

    def replace(self, prefixes: list[str], command: str) -> "Arguments":
        self.prefixes = prefixes
        self.command = command
        return self
