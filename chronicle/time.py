from datetime import datetime, timedelta


class Moment:
    """Point in time with some certainty."""

    def __init__(self, code: str) -> None:

        self.year: int | None = None
        self.month: int | None = None
        self.day: int | None = None
        self.hour: int | None = None
        self.minute: int | None = None
        self.second: float | None = None

        if not code:
            return

        date: str
        time: str

        if "T" in code:
            date, time = code.split("T")
            time_parts: list[str] = time.split(":")

            self.hour = int(time_parts[0])
            if len(time_parts) > 1:
                self.minute = int(time_parts[1])
            if len(time_parts) > 2:
                self.second = float(time_parts[2])
        else:
            date = code

        date_parts: list[str] = date.split("-")

        self.year = int(date_parts[0])
        if len(date_parts) > 1:
            self.month = int(date_parts[1])
        if len(date_parts) > 2:
            self.day = int(date_parts[2])

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

    def __str__(self) -> str:
        return (
            f"{self.year}"
            + (f".{self.month:02d}" if self.month else "")
            + (f".{self.day:02d}" if self.day else "")
            + (f" {self.hour:02d}" if self.hour is not None else "")
            + (f":{self.minute:02d}" if self.minute is not None else "")
            + (f":{self.second:02d}" if self.second is not None else "")
        )


class Time(str):
    """Point in time or time span."""

    def __init__(self, code: str):

        self.start: Moment | None
        self.end: Moment | None

        if "/" in code:
            start, end = code.split("/")
            self.start = Moment(start)
            self.end = Moment(end)
        else:
            self.start = self.end = Moment(code)

    @classmethod
    def __get_validators__(cls):
        yield cls

    def __str__(self) -> str:
        if self.start == self.end:
            return str(self.start)
        return f"{self.start or ''} - {self.end or ''}"

    def __repr__(self) -> str:
        if self.start == self.end:
            return str(self.start)
        return f"{self.start or ''}/{self.end or ''}"


class Duration:
    @classmethod
    def __get_validators__(cls):
        yield cls
