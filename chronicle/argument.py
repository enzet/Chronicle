"""Argument parsing utilities."""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from chronicle.errors import (
    ChronicleAmbiguousArgumentError,
    ChronicleArgumentError,
)

if TYPE_CHECKING:
    import re
    from collections.abc import Callable

    from chronicle.event.core import Event
    from chronicle.objects.core import Objects

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

logger: logging.Logger = logging.getLogger(__name__)


def default_pretty_printer(value: Any) -> str:
    """Return the value based on its type."""

    if isinstance(value, str):
        return value
    if isinstance(value, float):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, set):
        return "(" + ", ".join(value) + ")"
    return value.to_string()


def default_loader(value: Any, _: Objects) -> Any:
    """Return the value as is."""
    return value


@dataclass
class Argument:
    """Argument."""

    key: str
    """Argument key."""

    description: str | None = None
    """Argument description."""

    loader: Callable[[Any, Objects], Any] | None = default_loader
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


class Arguments:
    """Arguments parser."""

    def __init__(self, prefixes: list[str], command: str) -> None:
        self.prefixes: list[str] = prefixes
        self.command: str = command
        self.arguments: list[Argument] = []
        self.main_argument: Argument | None = None

    def parse(self, tokens: list[str], objects: Objects) -> dict[str, Any]:
        """Parse arguments from command."""

        # Event may have no arguments.
        if not self.arguments:
            return {}

        # TODO(enzet): rewrite, there should be no more than one main argument
        # without patterns. We should check it here.
        main: Argument | None
        if self.main_argument:
            main = self.main_argument
        else:
            main = self.arguments[0] if not self.arguments[0].patterns else None

        result: dict[str, str] = {}

        current_key: str | None = main.key if main else None
        current_loader: Callable[[Any, Objects], Any] | None = (
            main.loader if main else None
        )
        current_value: str = ""

        def load_current() -> None:
            """Load current argument."""
            if not current_loader:
                message = f"No loader for argument `{current_key}`."
                raise ChronicleArgumentError(message)
            if not current_key:
                message = "No key for argument."
                raise ChronicleArgumentError(message)
            result[current_key] = current_loader(current_value, objects)

        for token in tokens:
            detected: Argument | None = None
            message: str

            for argument in self.arguments:
                if token == argument.prefix:
                    if detected:
                        message = (
                            "Token `{token}` is ambiguous, possible arguments: "
                            f"`{detected.key}`, `{argument.key}`."
                        )
                        raise ChronicleAmbiguousArgumentError(message)
                    if current_value:
                        if not current_key:
                            message = (
                                f"No argument key for value `{current_value}` "
                                f"for tokens `{tokens}`."
                            )
                            raise ChronicleArgumentError(message)
                        load_current()
                        current_value = ""
                    current_key = argument.key
                    current_loader = argument.loader
                    detected = argument

                if not argument.patterns:
                    continue

                for i, pattern in enumerate(argument.patterns):
                    if not (matcher := pattern.fullmatch(token)):
                        continue
                    if current_value:
                        if not current_key:
                            message = (
                                f"No argument key for value `{current_value}` "
                                f"for tokens `{tokens}`."
                            )
                            raise ChronicleArgumentError(message)
                        load_current()
                        current_key = None
                        current_value = ""
                    if detected:
                        message = (
                            f"Token `{token}` is ambiguous, possible "
                            f"argument patterns: `{detected.key}`, "
                            f"`{argument.key}`."
                        )
                        raise ChronicleAmbiguousArgumentError(message)
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
                current_value += (" " if current_value else "") + token

        if current_value and current_key:
            load_current()

        return result

    def add(
        self,
        argument: Argument,
        *,
        is_insert: bool = False,
        is_main: bool = False,
    ) -> Self:
        """Add argument to a parser."""

        if is_insert:
            self.arguments.insert(0, argument)
        else:
            self.arguments.append(argument)

        if is_main:
            self.main_argument = argument

        return self

    def __add__(self, other: Self) -> Self:
        for argument in other.arguments:
            self.add(argument)
        return self

    def add_class_argument(self, name: str, class_: type) -> Self:
        """Add argument using value class.

        Value class should specify patterns and extractors. E.g. language.
        """
        argument: Argument = Argument(name)

        assert (
            hasattr(class_, "patterns") and hasattr(class_, "extractors")
        ) or hasattr(class_, "prefix"), (
            f"{class_.__name__} should have patterns, extractors or prefix."
        )

        if hasattr(class_, "patterns"):
            argument.patterns = class_.patterns
        if hasattr(class_, "extractors"):
            argument.extractors = class_.extractors
        if hasattr(class_, "prefix"):
            argument.prefix = class_.prefix

        self.arguments.append(argument)
        return self

    def add_object_argument(
        self,
        name: str,
        class_: type,
        *,
        is_insert: bool = False,
        is_main: bool = False,
    ) -> Self:
        """Add argument using object class.

        Value of this argument is a link to an object or a simple description
        of an object.
        """

        def object_loader(value: str, objects: Objects) -> Any:
            """Get an existing object or create a new one."""
            if value.startswith("@"):
                return objects.get_object(value)
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

        if is_main:
            self.main_argument = argument

        return self

    def to_string(self, value: Any) -> str:
        """Get text representation of arguments."""

        text: str = self.command
        for argument in self.arguments:
            if hasattr(value, argument.key) and getattr(value, argument.key):
                string: str = argument.pretty_printer(
                    getattr(value, argument.key)
                )
                if string:
                    text += " " + string
        return text

    def to_html(self, objects: Objects, value: Any) -> str:
        """Get HTML representation of arguments."""

        text: str = self.command
        for argument in self.arguments:
            if hasattr(value, argument.key) and getattr(value, argument.key):
                string: str = argument.html_printer(
                    objects, getattr(value, argument.key)
                )
                if string:
                    text += " " + string
        return text

    def to_object_command(self, value: Any) -> str:
        """Convert entity with arguments to normalized command."""

        text: str = ""
        for argument in self.arguments:
            if not hasattr(value, argument.key) or not getattr(
                value, argument.key
            ):
                continue
            try:
                v = getattr(value, argument.key)
                string: str
                if argument.command_printer:
                    string = argument.command_printer(v)
                elif getattr(v, "to_command", None):
                    string = v.to_command()
                else:
                    string = str(v)

                if string:
                    if text:
                        text += " " + string
                    else:
                        text += string
            except AttributeError:
                logger.exception(
                    "Cannot print command for %s of %s.", argument.key, value
                )
        return text

    def to_command(self, event: Event) -> str:
        """Get command representation of event."""

        text: str = event.time.to_pseudo_edtf_time() + " " + self.prefixes[0]
        for argument in self.arguments:
            if hasattr(event, argument.key):
                if getattr(event, argument.key):
                    v = getattr(event, argument.key)
                    string: str
                    if argument.command_printer:
                        string = argument.command_printer(v)
                    elif getattr(v, "to_command", None):
                        string = v.to_command()
                    elif isinstance(v, float):
                        string = f"{v:.2f}"
                    else:
                        string = str(v)
                    if string:
                        text += " " + string
            else:
                logger.error("No {argument.key} of {event}.")
        return text

    def replace(self, prefixes: list[str], command: str) -> Arguments:
        new_arguments = copy.deepcopy(self)
        new_arguments.prefixes = prefixes
        new_arguments.command = command
        return new_arguments
