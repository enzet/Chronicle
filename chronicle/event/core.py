"""Event and global event parameters.

This file describes events and some common attributes that events may have.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

from chronicle.argument import Arguments
from chronicle.errors import (
    ChronicleArgumentError,
    ChronicleObjectNotFoundError,
)
from chronicle.objects.core import Objects
from chronicle.summary.core import Summary
from chronicle.time import Time, Timedelta
from chronicle.value import Interval, Tags, TimedeltaList

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class Event:
    """Any event happened at some point or during some period in time.

    This includes events such as reading, running, playing, as well as
    conditions, such as current body temperature, heart rate, being at some
    place or taking some kind of transportation.
    """

    time: Time
    """Point in time or time span when event is occurred."""

    source: Any = None
    """Source was used to create this event."""

    tags: set[str] = field(default_factory=set)
    """Arbitrary user tag set for an event."""

    def __post_init__(self) -> None:
        assert self.time

    arguments: ClassVar[Arguments] = Arguments(
        ["event"], "event"
    ).add_class_argument("tags", Tags)

    @classmethod
    def parse_command(
        cls, time: Time, command: str, tokens: list[str], objects: Objects
    ) -> Self:
        """Create an event from a command."""

        arguments: Arguments = cls.arguments
        try:
            parsed = arguments.parse(tokens, objects)
        except ChronicleArgumentError as error:
            raise ChronicleArgumentError(
                f"Cannot parse command `{command}`."
            ) from error
        except ChronicleObjectNotFoundError as error:
            raise ChronicleObjectNotFoundError(
                f"Object with id `{error.object_id}` not found, needed to "
                f"parse `{cls.__name__}` from command `{command}`."
            ) from error
        try:
            return cls(time=time, source=(command, parsed), **parsed)
        except TypeError as e:
            logging.error("Cannot construct class %s from %s.", cls, parsed)
            raise e

    def register_summary(self, summary: Summary) -> None:
        """Register event effect on summary."""

    def to_string(self) -> str:
        """
        Get human-readable event text representation in English.

        :param objects: object information needed to fill data, because some
            events depend on objects and know solely about object identifier
        """
        return self.arguments.to_string(self)

    def to_html(self, objects: Objects) -> str:
        """Get HTML representation of an event."""
        return self.arguments.to_html(objects, self)

    def to_command(self) -> str:
        """Get command representation of an event."""
        return self.arguments.to_command(self)

    def get_color(self) -> str:
        """Get color of an event."""

        if hasattr(self, "color"):
            color: str = getattr(self, "color")
            return color

        # Default event color is gray, to be seen on the white and on the
        # black background.
        return "#888888"

    def get_duration(self) -> float | None:
        """Get event duration in seconds.

        Duration may be implemented as `self.time.get_duration()` or
        `self.interval.get_duration()`, but it should be done explicitly.
        """
        if hasattr(self, "duration"):
            duration: Timedelta = getattr(self, "duration")
            if duration:
                return duration.total_seconds()

        if hasattr(self, "durations"):
            durations: TimedeltaList = getattr(self, "durations")
            if durations:
                return sum(
                    duration.total_seconds() for duration in durations.values
                )

        if hasattr(self, "interval"):
            interval: Interval = getattr(self, "interval")
            if interval:
                return interval.get_duration()

        if not self.time.is_assumed:
            result: float | None = self.time.get_duration()
            if result:
                return result

        return None
