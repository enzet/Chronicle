"""
Event and global event parameters.

This file describes events and some common attributes that events may have.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional, Any

import pydantic

from chronicle.argument import Arguments
from chronicle.objects import Objects
from chronicle.summary.core import Summary
from chronicle.time import Time

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class Event:
    """
    Any event happened at some point or during some period in time.

    This includes events such as reading, running, playing, as well as
    conditions, such as current body temperature, heart rate, being at some
    place or taking some kind of transportation.
    """

    time: Time
    """Point in time or time span when event is occurred."""

    source: Any
    """Source representation was used to create this event."""

    tags: set[str] = field(default_factory=set)

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments([], "")

    @classmethod
    def parse_command(cls, time: str, command: str) -> Optional["Event"]:
        parsed = cls.get_arguments().parse(command)
        try:
            return cls(time=time, **parsed)
        except pydantic.error_wrappers.ValidationError as e:
            print(
                f"Cannot construct class {cls} from {parsed} and time {time}."
            )
            logging.error(parsed)
            raise e
        except TypeError as e:
            print(f"Cannot construct class {cls} from {parsed}.")
            logging.error(parsed)
            raise e

    def register_summary(self, summary: Summary, objects: Objects):
        """"""

    def to_string(self, objects: Objects) -> str:
        """
        Get human-readable event text representation in English.

        :param objects: object information needed to fill data, because some
            events depend on objects and know solely about object identifier
        """
        return self.get_arguments().to_string(objects, self)

    def to_html(self, objects: Objects) -> str:
        return self.get_arguments().to_html(objects, self)

    def to_command(self) -> str:
        return self.get_arguments().to_command(self)

    def get_color(self) -> str:
        return "#000000"


def to_camel(text: str) -> str:
    """Make the first letter capital."""
    return text[0].upper() + text[1:]
