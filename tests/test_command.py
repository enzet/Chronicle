from datetime import timedelta, datetime

from chronicle.event.core import Event, Objects
from chronicle.event.common import SleepEvent
from chronicle.event.art import (
    ListenAudiobookEvent,
    ListenMusicEvent,
    ListenPodcastEvent,
)
from chronicle.event.value import Interval
from chronicle.time import Context
from chronicle.timeline import Timeline, CommandParser

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_listen_podcast() -> None:
    """Test listening podcast command."""

    (timeline := Timeline()).parse_event_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 podcast inner_french e5 "
        "10:00/20:00"
    )
    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenPodcastEvent)
    assert event.podcast_id == "inner_french"
    assert event.episode == "5"
    assert event.interval == Interval(
        start=timedelta(minutes=10), end=timedelta(minutes=20)
    )


def test_listen_music() -> None:
    """Test listening song command with title, artist, and album."""

    (timeline := Timeline()).parse_event_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 song "
        "Strawberry Fields Forever by The Beatles on Magic Mystery Tour"
    )
    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenMusicEvent)
    assert event.title == "Strawberry Fields Forever"
    assert event.artist == "The Beatles"
    assert event.album == "Magic Mystery Tour"


def test_listen_audiobook() -> None:
    """Test listening song command with title, artist, and album."""

    (timeline := Timeline()).parse_event_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 audiobook idiot x1.25 "
        "00:00/10:00"
    )
    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.audiobook_id == "idiot"
    assert event.speed == 1.25
    assert event.interval == Interval(
        start=timedelta(), end=timedelta(minutes=10)
    )


def test_listen_audiobook_hour_interval() -> None:
    """Test listening song command with title, artist, and album."""

    (timeline := Timeline()).parse_event_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 audiobook idiot "
        "1:10:10/2:20:20"
    )
    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.interval == Interval(
        start=timedelta(hours=1, minutes=10, seconds=10),
        end=timedelta(hours=2, minutes=20, seconds=20),
    )


def test_sleep() -> None:
    (timeline := Timeline()).parse_event_command(
        "2022-01-01T00:00:00/2022-01-01T08:00:00 sleep"
    )
    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, SleepEvent)
    assert timeline.get_summary().sleep == 8 * 60 * 60


def test_short_time() -> None:
    """Test listening song command with title, artist, and album."""

    context: Context = Context()
    context.current_date = datetime(2022, 1, 2)
    (timeline := Timeline()).parse_event_command(
        "13:00 audiobook idiot", context
    )
    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenAudiobookEvent)

    objects: Objects = Objects(
        books={"idiot": {"title": "Idiot", "language": "ru"}},
        audiobooks={"idiot": {"book_id": "idiot"}},
    )
    assert event.to_string(objects) == "listen audiobook Idiot"
    assert event.time.start == event.time.end
    assert event.time.start.hour == 13


def test_file() -> None:
    commands: list[str] = [
        "book idiot Idiot .ru",
        "audiobook idiot idiot",
        "2000-01-01",
        "13:00 audiobook idiot",
    ]
    parser: CommandParser = CommandParser()
    parser.parse_commands(commands)

    assert len(parser.timeline) == 1
    event: Event = parser.timeline.events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.to_string(parser.timeline.objects) == "listen audiobook Idiot"
    assert event.time.start == event.time.end
    assert event.time.start.year == 2000
    assert event.time.start.hour == 13


def test_file_sleep() -> None:
    commands: list[str] = [
        "2000-01-01",
        "00:00/08:00 sleep",
    ]
    parser: CommandParser = CommandParser()
    parser.parse_commands(commands)

    assert len(parser.timeline) == 1
    event: Event = parser.timeline.events[0]
    assert isinstance(event, SleepEvent)
    assert event.to_string(parser.timeline.objects) == "sleep"
    assert parser.timeline.get_summary().sleep == 8 * 60 * 60


def test_dump_command() -> None:
    commands: list[str] = [
        "audiobook idiot idiot",
        "book idiot Idiot .ru",
        "",
        "2000-01-01",
        "",
        "13:00 audiobook idiot",
    ]
    parser: CommandParser = CommandParser()
    parser.parse_commands(commands)

    assert commands == parser.timeline.get_commands()
