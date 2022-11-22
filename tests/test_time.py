from chronicle.time import Time, Moment


def check(
    moment: Moment,
    year: int,
    month: int,
    day: int,
    hour: float,
    minute: float,
    second: float,
):
    assert moment.year == year
    assert moment.month == month
    assert moment.day == day
    assert moment.hour == hour
    assert moment.minute == minute
    assert moment.second == second


def test_year() -> None:
    time: Time = Time("2000")
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 1, 1, 0, 0, 0)
    check(time.start.get_upper(), 2001, 1, 1, 0, 0, 0)


def test_month() -> None:
    time: Time = Time("2000-01")
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 1, 1, 0, 0, 0)
    check(time.start.get_upper(), 2000, 2, 1, 0, 0, 0)

    time = Time("2000-12")
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 12, 1, 0, 0, 0)
    check(time.start.get_upper(), 2001, 1, 1, 0, 0, 0)


def test_day() -> None:
    time: Time = Time("2000-01-01")
    assert time.start == time.end
    check(time.start.get_lower(), 2000, 1, 1, 0, 0, 0)
    check(time.start.get_upper(), 2000, 1, 2, 0, 0, 0)
