import re
from dataclasses import dataclass

from pydantic import BaseModel

from chronicle.time import INTERVAL_PATTERN, Timedelta

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class Language:
    """Natural language of text, speach, or song."""

    code: str

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


@dataclass
class Interval:
    """Time interval in seconds."""

    start: Timedelta | None = None
    end: Timedelta | None = None

    @classmethod
    def from_json(cls, string: str) -> "Interval":
        start, end = string.split("/")
        return cls(
            start=Timedelta.from_json(start), end=Timedelta.from_json(end)
        )

    def to_json(self) -> str:
        return (
            (self.start.to_json() if self.start is not None else "")
            + ("/" if self.start is not None or self.end is not None else "")
            + (self.end.to_json() if self.end is not None else "")
        )

    def to_string(self) -> str:
        return self.to_json()

    @staticmethod
    def get_pattern() -> re.Pattern:
        return INTERVAL_PATTERN

    def to_command(self) -> str:
        return self.to_json()

    def get_duration(self) -> float:
        if self.start is None and self.end is None:
            return 0.0
        return (self.end - self.start).total_seconds()


class Cost(BaseModel):
    value: float
    currency: str
