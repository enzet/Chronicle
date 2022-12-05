"""
Event and global event parameters.

This file describes events and some common attributes that events may have.
"""
from datetime import timedelta

from pydantic.json import timedelta_isoformat
from pydantic.main import BaseModel

from chronicle.argument import ArgumentParser
from chronicle.objects import Objects
from chronicle.time import Time

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

from summary.core import Summary


class Event(BaseModel):
    """
    Any event happened at some point or during some period in time.

    This includes events such as reading, running, playing, as well as
    conditions, such as current body temperature, heart rate, being at some
    place or taking some kind of transportation.
    """

    time: Time
    """Point in time or time span when event is occurred."""

    class Config:
        json_encoders = {timedelta: timedelta_isoformat}

    @staticmethod
    def get_parser() -> ArgumentParser:
        return ArgumentParser(set())

    @classmethod
    def parse_command(cls, time: str, command: str) -> "Event":
        return cls(time=time, **cls.get_parser().parse(command))

    def register_summary(self, summary: Summary, objects: Objects):
        """"""

    def to_string(self, objects: Objects) -> str:
        """
        Get human-readable event text representation in English.

        :param objects: object information needed to fill data, because some
            events depend on objects and know solely about object identifier
        """
        return str(self.time)


def to_camel(text: str) -> str:
    """Make the first letter capital."""
    return text[0].upper() + text[1:]
