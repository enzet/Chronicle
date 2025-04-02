"""Argument parsing utilities."""

import copy
import logging
import re
from dataclasses import dataclass
from typing import Any, Callable

from chronicle.errors import (
    ChronicleAmbiguousArgumentError,
    ChronicleArgumentError,
    ChronicleObjectNotFoundException,
)

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def default_pretty_printer(value: Any) -> str:
    """Default pretty printer for arguments."""

    if isinstance(value, str):
        return value
    if isinstance(value, float):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, set):
        return "(" + ", ".join(value) + ")"
    return value.to_string()


def default_loader(value: str, objects) -> Any:
    return value


@dataclass
class Argument:
    """Argument."""

    key: str
    """Argument key."""

    description: str | None = None
    """Argument description."""

    loader: Callable[[Any], Any] | None = default_loader
    """Value loader."""

    prefix: str | None = None
    """Prefix word that starts argument value."""

    patterns: list[re.Pattern] | None = None
    """Value patterns."""

    extractors: list[Callable[[Any], Any]] | None = None
    """Functions that extract values from a pattern matchers."""

    pretty_printer: Callable = default_pretty_printer
    """Pretty printer."""

    command_printer: Callable | None = lambda x: x.to_command()
    """Command printer."""

    html_printer: Callable = lambda x: x.to_string()
    """HTML printer."""


def one_pattern_argument(name: str, class_: type, index: int = 0) -> Argument:
    """Create an argument with one pattern."""

    return Argument(
        name,
        patterns=class_.patterns,
        extractors=[lambda x: class_.from_json(x(index))],
    )


class Arguments:
    """Arguments parser."""

    def __init__(self, prefixes: list[str], command: str) -> None:
        self.prefixes: list[str] = prefixes
        self.command: str = command
        self.arguments: list[Argument] = []

    def parse(self, tokens: list[str], objects) -> dict[str, Any]:
        """Parse arguments from command."""

        # Event may have no arguments.
        if not self.arguments:
            return {}

        # FIXME: rewrite, there should be no more than one main argument without
        # patterns. We should check it here.
        main: Argument | None = (
            self.arguments[0] if not self.arguments[0].patterns else None
        )
        result: dict[str, str] = {}

        current_key: str | None = main.key if main else None
        current_loader = main.loader if main else None
        current: str = ""

        def load_current() -> None:
            result[current_key] = current_loader(current, objects)

        for index in range(len(tokens)):
            token: str = tokens[index]
            detected: Argument | None = None

            for argument in self.arguments:
                if token == argument.prefix:
                    if detected:
                        raise ChronicleAmbiguousArgumentError(
                            "Token `{token}` is ambiguous, possible arguments: "
                            f"`{detected.key}`, `{argument.key}`."
                        )
                    if current:
                        if not current_key:
                            raise ChronicleArgumentError(
                                f"No argument name before `{current}` for "
                                f"tokens `{tokens}`."
                            )
                        load_current()
                        current = ""
                    current_key = argument.key
                    current_loader = argument.loader
                    detected = argument

                if not argument.patterns:
                    continue

                for i, pattern in enumerate(argument.patterns):
                    if matcher := pattern.fullmatch(token):
                        if current:
                            if not current_key:
                                raise ChronicleArgumentError(
                                    f"No argument name before `{current}`."
                                )
                            load_current()
                            current_key = None
                            current = ""
                        if detected:
                            raise ChronicleAmbiguousArgumentError(
                                f"Token `{token}` is ambiguous, possible "
                                f"arguments: `{detected.key}`, "
                                f"`{argument.key}`."
                            )
                        if argument.extractors is not None:
                            result[argument.key] = argument.extractors[i](
                                matcher.group
                            )
                        else:
                            result[argument.key] = argument.loader(
                                matcher.group(1), objects
                            )
                        detected = argument

            if not detected:
                current += (" " if current else "") + token

        if current and current_key:
            load_current()

        return result

    def add_argument(
        self,
        key: str,
        description: str | None = None,
        prefix: str | None = None,
        patterns: list[re.Pattern] | None = None,
        loader: Callable[[Any, Any], Any] = lambda x, _: x,
        extractors: list[Callable[[Any], Any]] | None = None,
        pretty_printer: Callable = default_pretty_printer,
        command_printer: Callable | None = None,
        html_printer: Callable = lambda o, v: v.to_string(o),
        is_insert: bool = False,
    ) -> "Arguments":
        """Add argument to a parser."""

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
        if is_insert:
            self.arguments.insert(0, argument)
        else:
            self.arguments.append(argument)
        return self

    def __add__(self, other: "Arguments") -> "Arguments":
        for argument in other.arguments:
            self.add(argument)
        return self

    def add_class_argument(self, name: str, class_: type) -> "Arguments":
        """Add argument using value class.

        Value class should specify patterns and extractors. E.g. language.
        """
        argument: Argument = Argument(name)

        assert (
            hasattr(class_, "patterns")
            and hasattr(class_, "extractors")
            or hasattr(class_, "prefix")
        ), f"{class_.__name__} should have patterns, extractors or prefix."

        if hasattr(class_, "patterns"):
            argument.patterns = class_.patterns
        if hasattr(class_, "extractors"):
            argument.extractors = class_.extractors
        if hasattr(class_, "prefix"):
            argument.prefix = class_.prefix

        self.arguments.append(argument)
        return self

    def add_object_argument(
        self, name: str, class_: type, is_insert: bool = False
    ) -> "Arguments":
        """Add argument using object class.

        Value of this argument is a link to an object or a simple description
        of an object.
        """

        def object_loader(value: str, objects):
            """Get an existing object or create a new one."""
            if value.startswith("@"):
                try:
                    return objects.get_object(value)
                except ChronicleObjectNotFoundException:
                    raise
            new_object = class_.from_value(value)
            objects.set_object(value, new_object)
            return new_object

        def to_command(value: Any) -> str:
            return f"@{value.id}"

        argument: Argument = Argument(
            name,
            loader=object_loader,
            command_printer=to_command,
            prefix=class_.prefix,
        )
        if is_insert:
            self.arguments.insert(0, argument)
        else:
            self.arguments.append(argument)
        return self

    def add(self, argument: Argument) -> "Arguments":
        self.arguments.append(argument)
        return self

    def to_string(self, value) -> str:
        text = self.command
        for argument in self.arguments:
            if hasattr(value, argument.key) and getattr(value, argument.key):
                string: str = argument.pretty_printer(
                    getattr(value, argument.key)
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
        """Convert entity with arguments to normalized command."""
        text: str = ""
        for argument in self.arguments:
            if not hasattr(value, argument.key) or not getattr(
                value, argument.key
            ):
                continue
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
                    "Cannot print command for %s of %s.", argument.key, value
                )
        return text

    def to_command(self, event):
        text = event.time.to_pseudo_edtf_time() + " " + self.prefixes[0]
        for argument in self.arguments:
            if hasattr(event, argument.key):
                if getattr(event, argument.key):
                    v = getattr(event, argument.key)
                    if argument.command_printer:
                        string: str = argument.command_printer(v)
                    elif getattr(v, "to_command", None):
                        string: str = v.to_command()
                    elif isinstance(v, float):
                        string: str = f"{v:.2f}"
                    else:
                        string: str = str(v)
                    if string:
                        text += " " + string
            else:
                logging.error("No %s of %s.", argument.key, event)
        return text

    def replace(self, prefixes: list[str], command: str) -> "Arguments":
        new_arguments = copy.deepcopy(self)
        new_arguments.prefixes = prefixes
        new_arguments.command = command
        return new_arguments
