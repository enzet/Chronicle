import re
from datetime import timedelta

from pydantic import BaseModel

from chronicle.time import parse_delta, format_delta, INTERVAL_PATTERN

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


class Language(str):
    """Natural language of text, speach, or song."""

    def __init__(self, code: str):
        self.code: str = code

    def __eq__(self, other: "Language") -> bool:
        if not other:
            return False
        return self.code == other.code

    def __str__(self) -> str:
        """Get English name of the language or return code."""
        return self.code

    def get_name(self):
        if self.code == "fr":
            return "French"

        return self.code

    def __hash__(self) -> int:
        return hash(self.code)

    @classmethod
    def __get_validators__(cls):
        yield cls


class Interval(BaseModel):
    """Time interval in seconds."""

    start: timedelta | None
    end: timedelta | None

    @classmethod
    def from_string(cls, string: str) -> "Interval":
        start, end = string.split("/")
        return cls(start=parse_delta(start), end=parse_delta(end))

    def to_string(self, _=None) -> str:
        return (
            (format_delta(self.start) if self.start is not None else "")
            + ("/" if self.start is not None or self.end is not None else "")
            + (format_delta(self.end) if self.end is not None else "")
        )

    @staticmethod
    def get_pattern() -> re.Pattern:
        return INTERVAL_PATTERN

    def to_command(self) -> str:
        return self.to_string()

    def get_duration(self) -> float:
        if self.start is None and self.end is None:
            return 0.0
        return (self.end - self.start).total_seconds()


class Cost(BaseModel):
    value: float
    currency: str
