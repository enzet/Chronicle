import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

from typing import Callable, ClassVar, Optional

DELTA_PATTERN_TEXT: str = r"(\d+:)?\d?\d:\d\d"
DELTA_PATTERN_TEXT_GROUPS: str = r"((?P<h>\d+):)?(?P<m>\d?\d):(?P<s>\d\d)"
DELTA_PATTERN: re.Pattern = re.compile(DELTA_PATTERN_TEXT)
DELTA_PATTERN_GROUPS: re.Pattern = re.compile(DELTA_PATTERN_TEXT_GROUPS)
INTERVAL_PATTERN: re.Pattern = re.compile(
    rf"{DELTA_PATTERN_TEXT}/{DELTA_PATTERN_TEXT}"
)


@dataclass
class Context:
    current_date: datetime | None = None


@dataclass
class Moment:
    """
    Point in time with some certainty.

    For example,
        - `1912` means time period from 1 January 1912 to 1 January 1913,
        - `1912-01` means time period from 1 January 1912 to 1 February 1912.
        - `1912-01-01` means time period from 1 January 1912 00:00 to 2 January
          1912 00:00.
    """

    year: int | None = None
    month: int | None = None
    day: int | None = None
    hour: int | None = None
    minute: int | None = None
    second: float | None = None

    @classmethod
    def from_pseudo_edtf(cls, code: str) -> "Moment":
        moment: "Moment" = cls()

        date: str
        time: str

        if "T" in code:
            date, time = code.split("T")
            time_parts: list[str] = time.split(":")

            moment.hour = int(time_parts[0])
            if len(time_parts) > 1:
                moment.minute = int(time_parts[1])
            if len(time_parts) > 2:
                moment.second = float(time_parts[2])
        else:
            date = code

        date_parts: list[str] = date.split("-")

        moment.year = int(date_parts[0])
        if len(date_parts) > 1:
            moment.month = int(date_parts[1])
        if len(date_parts) > 2:
            moment.day = int(date_parts[2])

        return moment

    @classmethod
    def from_string(cls, code: str, context: Context | None = None) -> "Moment":
        moment: "Moment" = cls()

        if "T" in code:
            date, time = code.split("T")
            date_parts: list[str] = date.split("-")

            moment.year = int(date_parts[0])
            if len(date_parts) > 1:
                moment.month = int(date_parts[1])
            if len(date_parts) > 2:
                moment.day = int(date_parts[2])
        elif ":" in code and context and context.current_date:
            time = code
            moment.year = context.current_date.year
            moment.month = context.current_date.month
            moment.day = context.current_date.day
        else:
            time = None
            date_parts: list[str] = code.split("-")
            moment.year = int(date_parts[0])
            if len(date_parts) > 1:
                moment.month = int(date_parts[1])
            if len(date_parts) > 2:
                moment.day = int(date_parts[2])

        if time:
            time_parts: list[str] = time.split(":")

            moment.hour = int(time_parts[0])
            if len(time_parts) > 1:
                moment.minute = int(time_parts[1])
            if len(time_parts) > 2:
                moment.second = float(time_parts[2])

        return moment

    def get_lower(self) -> datetime | None:
        """Compute lower bound of the moment."""

        if self.year is None:
            return None

        return datetime(
            year=self.year,
            month=self.month or 1,
            day=self.day or 1,
            hour=self.hour or 0,
            minute=self.minute or 0,
            second=int(self.second) if self.second is not None else 0,
        )

    def __lt__(self, other: "Moment"):
        return self.get_lower() < other.get_lower()  # FIXME

    def get_upper(self) -> datetime | None:
        """Compute upper bound of the moment."""

        if self.year is None:
            return None

        if self.month is None:
            return datetime(year=self.year + 1, month=1, day=1)

        if self.day is None:
            if self.month < 12:
                return datetime(year=self.year, month=self.month + 1, day=1)
            return datetime(year=self.year + 1, month=1, day=1)

        lower: datetime = self.get_lower()

        if self.hour is None:
            return lower + timedelta(days=1)

        if self.minute is None:
            return lower + timedelta(hours=1)

        if self.second is None:
            return lower + timedelta(minutes=1)

        return lower

    def to_pseudo_edtf(self) -> str:
        return (
            f"{self.year}"
            + (f"-{self.month:02d}" if self.month else "")
            + (f"-{self.day:02d}" if self.day else "")
            + (f"T{self.hour:02d}" if self.hour is not None else "")
            + (f":{self.minute:02d}" if self.minute is not None else "")
            + (f":{self.second}" if self.second is not None else "")
        )

    def to_pseudo_edtf_time(self) -> str:
        if self.hour is None:
            return (
                f"{self.year}"
                + (f"-{self.month:02d}" if self.month else "")
                + (f"-{self.day:02d}" if self.day else "")
            )
        return (
            (f"{self.hour:02d}" if self.hour is not None else "")
            + (f":{self.minute:02d}" if self.minute is not None else "")
            + (f":{self.second}" if self.second is not None else "")
        )

    def to_string(self) -> str:
        return (
            f"{self.year}"
            + (f".{self.month:02d}" if self.month else "")
            + (f".{self.day:02d}" if self.day else "")
            + (f" {self.hour:02d}" if self.hour is not None else "")
            + (f":{self.minute:02d}" if self.minute is not None else "")
            + (f":{self.second}" if self.second is not None else "")
        )

    def __repr__(self) -> str:
        return self.to_string()

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_datetime(cls, date: datetime) -> "Moment":
        moment = Moment(
            date.year, date.month, date.day, date.hour, date.minute, date.second
        )
        return moment


class MalformedTime(Exception):
    pass


@dataclass
class Timedelta:
    delta: timedelta = timedelta()

    def __sub__(self, other: "Timedelta") -> "Timedelta":
        return Timedelta(self.delta - other.delta)

    def total_seconds(self) -> float:
        return self.delta.total_seconds()

    @classmethod
    def from_json(cls, code: str) -> Optional["Timedelta"]:
        if not code:
            return None
        return cls(parse_delta(code))

    @classmethod
    def from_delta(cls, delta: timedelta) -> "Timedelta":
        return cls(delta)

    def to_json(self) -> str:
        return format_delta(self.delta)

    def to_string(self) -> str:
        return format_delta(self.delta)

    patterns: ClassVar[list[re.Pattern]] = [DELTA_PATTERN_GROUPS]

    extractors: ClassVar[list[Callable]] = [
        lambda groups: Timedelta(
            delta=timedelta(
                seconds=(float(groups("h")) if groups("h") else 0.0) * 3600.0
                + float(groups("m")) * 60.0
                + float(groups("s"))
            )
        )
    ]


class Time:
    """Point in time or time span."""

    def __init__(self, code: str) -> None:
        self.start: Moment | None
        self.end: Moment | None

        self.start = self.end = None

        self.is_assumed: bool = False

        if "/" in code:
            start, end = code.split("/")
            if start:
                self.start = Moment.from_pseudo_edtf(start)
            if end:
                self.end = Moment.from_pseudo_edtf(end)
        elif code:
            self.start = self.end = Moment.from_pseudo_edtf(code)

    def __lt__(self, other: "Time") -> bool:
        return self.get_lower() < other.get_lower()

    @classmethod
    def from_moments(cls, start_moment: Moment, end_moment: Moment) -> "Time":
        time: "Time" = cls("")
        time.start = start_moment
        time.end = end_moment
        return time

    @classmethod
    def from_moment(cls, moment: Moment) -> "Time":
        time: "Time" = cls("")
        time.start = moment
        time.end = moment
        return time

    @classmethod
    def from_string(cls, code: str, context: Context | None = None) -> "Time":
        time: "Time" = cls("")

        if "/" in code:
            start_, end_ = code.split("/")
            if start_:
                time.start = Moment.from_string(start_, context)
            if end_:
                time.end = Moment.from_string(end_, context)
            return time

        time.start = time.end = Moment.from_string(code, context)

        return time

    def __str__(self) -> str:
        return self.to_pseudo_edtf()

    def to_pseudo_edtf(self) -> str:
        if self.start == self.end:
            return self.start.to_pseudo_edtf()
        return (
            (self.start.to_pseudo_edtf() if self.start else "")
            + "/"
            + (self.end.to_pseudo_edtf() if self.end else "")
        )

    def to_string(self) -> str:
        if self.start == self.end:
            return self.start.to_string()

        return (
            (self.start.to_string() if self.start else "")
            + " - "
            + (self.end.to_string() if self.end else "")
        )

    def __repr__(self) -> str:
        return self.to_string()

    def to_pseudo_edtf_time(self):
        if self.start == self.end:
            return self.start.to_pseudo_edtf_time()

        return (
            (self.start.to_pseudo_edtf_time() if self.start else "")
            + "/"
            + (self.end.to_pseudo_edtf_time() if self.end else "")
        )

    def get_duration(self) -> float | None:
        if not self.start or not self.end:
            return 0  # FIXME

        if self.start == self.end:
            return 0

        return (self.end.get_lower() - self.start.get_lower()).total_seconds()

    def get_lower(self) -> datetime:
        if self.start:
            return self.start.get_lower()
        elif self.end:
            return self.end.get_lower()

        raise MalformedTime()

    def get_upper(self) -> datetime:
        if self.end:
            return self.end.get_upper()
        elif self.start:
            # return self.start.get_upper()
            return datetime.now()

        raise MalformedTime()

    def get_moment(self) -> datetime:
        if self.start and self.end:
            return (
                self.start.get_lower()
                + (self.end.get_lower() - self.start.get_lower()) / 2
            )
        elif self.start:
            return self.start.get_lower()
        elif self.end:
            return self.end.get_lower()

        raise MalformedTime()

    def get_random(self) -> datetime:
        if self.start and self.end:
            return (
                self.start.get_lower()
                + (self.end.get_lower() - self.start.get_lower())
                * random.random()
            )
        elif self.start:
            return self.start.get_lower()
        elif self.end:
            return self.end.get_lower()

        raise MalformedTime()


def parse_delta(string_delta: str) -> timedelta:
    """Parse time delta from a string representation."""
    if string_delta.count(":") == 2:
        hour, minute, second = (int(x) for x in string_delta.split(":"))
    elif string_delta.count(":") == 1:
        hour = 0
        minute, second = (int(x) for x in string_delta.split(":"))
    return timedelta(seconds=hour * 3600 + minute * 60 + second)


def format_delta(delta: timedelta) -> str:
    """Get string representation of a time delta.

    Format is `MM:SS` if number of hours is zero, otherwise `HH:MM:SS`. Hours
    are not zero-prefixed.
    """

    seconds: float = delta.total_seconds()
    minutes, seconds = int(seconds // 60), int(seconds % 60)
    hours, minutes = int(minutes // 60), int(minutes % 60)

    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes:02}:{seconds:02}"


def humanize_delta(delta: timedelta) -> str:
    if delta.days > 365 * 2:
        return f"{delta.days // 365} years"
    elif delta.days > 365:
        return "1 year"
    else:
        return f"{delta.days} days"


def start_of_day(time: datetime) -> datetime:
    return datetime(year=time.year, month=time.month, day=time.day)


def start_of_month(time: datetime) -> datetime:
    return datetime(year=time.year, month=time.month, day=1)


def start_of_year(time: datetime) -> datetime:
    return datetime(year=time.year, month=1, day=1)
