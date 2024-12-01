from datetime import datetime

from chronicle.time import (
    Time,
    parse_delta,
    INTERVAL_PATTERN,
    DELTA_PATTERN,
)

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def check(
    moment: datetime | None,
    year: int,
    month: int,
    day: int,
    hour: float,
    minute: float,
    second: float,
):
    assert moment
    assert moment.year == year
    assert moment.month == month
    assert moment.day == day
    assert moment.hour == hour
    assert moment.minute == minute
    assert moment.second == second


def test_delta_patterns() -> None:
    """Check whether delta patterns match right strings."""

    assert DELTA_PATTERN.match("0:00")
    assert DELTA_PATTERN.match("00:00")
    assert DELTA_PATTERN.match("0:00:00")
    assert DELTA_PATTERN.match("12:34")
    assert DELTA_PATTERN.match("1:23:45")
    assert DELTA_PATTERN.match("01:23:45")
    assert DELTA_PATTERN.match("101:23:45")


def test_interval_patterns() -> None:
    """Check whether interval patterns match right strings."""

    assert INTERVAL_PATTERN.match("2:00/3:00")
    assert INTERVAL_PATTERN.match("2:00/13:00")
    assert INTERVAL_PATTERN.match("02:00/3:00")
    assert INTERVAL_PATTERN.match("02:00/12:00")
    assert INTERVAL_PATTERN.match("02:00/2:12:00")
    assert INTERVAL_PATTERN.match("2:02:00/2:12:00")


def test_year() -> None:
    """Test particular year parsing."""

    time: Time = Time("2000")
    assert time.start
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 1, 1, 0, 0, 0)
    check(time.start.get_upper(), 2001, 1, 1, 0, 0, 0)


def test_month() -> None:
    """Test particular month parsing."""

    time: Time = Time("2000-01")
    assert time.start
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 1, 1, 0, 0, 0)
    check(time.start.get_upper(), 2000, 2, 1, 0, 0, 0)

    time = Time("2000-12")
    assert time.start
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 12, 1, 0, 0, 0)
    check(time.start.get_upper(), 2001, 1, 1, 0, 0, 0)


def test_day() -> None:
    """Test particular day parsing."""

    time: Time = Time("2000-01-01")
    assert time.start
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 1, 1, 0, 0, 0)
    check(time.start.get_upper(), 2000, 1, 2, 0, 0, 0)


def test_hour() -> None:
    """Test particular minute parsing."""

    time: Time = Time("2000-01-01T12")
    assert time.start
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 1, 1, 12, 0, 0)
    check(time.start.get_upper(), 2000, 1, 1, 13, 0, 0)


def test_minute() -> None:
    """Test particular second parsing."""

    time: Time = Time("2000-01-01T12:10")
    assert time.start
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 1, 1, 12, 10, 0)
    check(time.start.get_upper(), 2000, 1, 1, 12, 11, 0)


def test_second() -> None:
    """Test particular second parsing."""

    time: Time = Time("2000-01-01T12:10:20")

    assert time.start
    assert time.start == time.end

    check(time.start.get_lower(), 2000, 1, 1, 12, 10, 20)
    check(time.start.get_upper(), 2000, 1, 1, 12, 10, 20)


def test_parse_delta():
    """Test delta parsing with minutes and seconds."""

    assert parse_delta("00:00").seconds == 0
    assert parse_delta("0:00").seconds == 0
    assert parse_delta("10:00").seconds == 10 * 60


def test_parse_delta_with_hours():
    """Test delta parsing with hours, minutes, and seconds."""

    assert parse_delta("1:00:00").seconds == 60 * 60
    assert parse_delta("10:00:00").seconds == 10 * 60 * 60
