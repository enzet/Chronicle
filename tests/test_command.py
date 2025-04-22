"""Tests for command."""

from datetime import datetime, timedelta
from textwrap import dedent

from chronicle.event.art import (
    ListenAudiobookEvent,
    ListenMusicEvent,
    ListenPodcastEvent,
)
from chronicle.event.common import ProgramEvent, SleepEvent
from chronicle.event.core import Event, Objects
from chronicle.objects.core import Audiobook, Book, Project
from chronicle.time import Context, Timedelta
from chronicle.timeline import CommandParser, Timeline
from chronicle.value import Interval, Language, ProgrammingLanguage

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_listen_podcast() -> None:
    """Test listening podcast command."""

    parser: CommandParser = CommandParser()
    parser.parse_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 podcast Inner French e5 "
        "10:00/20:00"
    )
    timeline: Timeline = parser.timeline

    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenPodcastEvent)
    assert event.podcast
    assert event.podcast.title == "Inner French"
    assert event.episode == "5"
    assert event.interval == Interval(
        start=Timedelta(timedelta(minutes=10)),
        end=Timedelta(timedelta(minutes=20)),
    )


def test_book() -> None:
    """Test book command."""

    parser: CommandParser = CommandParser()
    parser.parse_command("book idiot = Idiot .ru")
    objects = parser.timeline.objects.objects

    assert len(objects) == 1
    assert isinstance(objects["idiot"], Book)
    assert objects["idiot"].title == "Idiot"
    assert objects["idiot"].language == Language("ru")


def test_listen_music() -> None:
    """Test listening song command with title, artist, and album."""

    parser: CommandParser = CommandParser()
    parser.parse_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 song "
        "Strawberry Fields Forever by The Beatles on Magic Mystery Tour"
    )
    timeline: Timeline = parser.timeline

    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenMusicEvent)
    assert event.title == "Strawberry Fields Forever"
    assert event.artist == "The Beatles"
    assert event.album == "Magic Mystery Tour"


def test_listen_audiobook() -> None:
    """Test listening song command with title, artist, and album."""

    parser: CommandParser = CommandParser()
    parser.parse_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 audiobook Idiot x1.25 "
        "00:00/10:00"
    )
    timeline: Timeline = parser.timeline

    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.audiobook
    assert event.audiobook.book
    assert event.audiobook.book.title == "Idiot"
    assert event.speed == 1.25
    assert event.interval == Interval(
        start=Timedelta(), end=Timedelta(timedelta(minutes=10))
    )


def test_listen_audiobook_hour_interval() -> None:
    """Test listening song command with title, artist, and album."""

    parser: CommandParser = CommandParser()
    parser.parse_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 audiobook idiot "
        "1:10:10/2:20:20"
    )
    timeline: Timeline = parser.timeline

    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.interval == Interval(
        start=Timedelta(timedelta(hours=1, minutes=10, seconds=10)),
        end=Timedelta(timedelta(hours=2, minutes=20, seconds=20)),
    )


def test_sleep() -> None:
    """Test sleeping event."""

    parser: CommandParser = CommandParser()
    parser.parse_command("2022-01-01T00:00:00/2022-01-01T08:00:00 sleep")
    timeline: Timeline = parser.timeline
    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, SleepEvent)
    assert timeline.get_summary().sleep == 8 * 60 * 60


def test_short_time() -> None:
    """Test listening song command with title, artist, and album."""

    book: Book = Book("idiot", title="Idiot", language=Language("ru"))
    parser: CommandParser = CommandParser()
    timeline: Timeline = parser.timeline
    timeline.objects = Objects(
        {"idiot": book, "idiot_audio": Audiobook("idiot_audio", book=book)}
    )
    parser.context = Context(current_date=datetime(2022, 1, 2))
    parser.parse_command("13:00 audiobook @idiot_audio")

    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenAudiobookEvent)

    assert event.to_string() == "listen to audiobook Idiot"
    assert event.time.start
    assert event.time.start == event.time.end
    assert event.time.start.hour == 13


def test_file() -> None:
    """Test file command."""

    commands: list[str] = [
        "book idiot = Idiot .ru",
        "audiobook idiot_audio = @idiot",
        "2000-01-01",
        "13:00 audiobook @idiot_audio",
    ]
    parser: CommandParser = CommandParser()
    parser.parse_commands(commands)

    assert len(parser.timeline) == 1
    event: Event = parser.timeline.events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.to_string() == "listen to audiobook Idiot"
    assert event.time.start
    assert event.time.start == event.time.end
    assert event.time.start.year == 2000
    assert event.time.start.hour == 13


def test_file_sleep() -> None:
    """Test file command with sleeping event."""

    commands: list[str] = ["2000-01-01", "00:00/08:00 sleep"]
    parser: CommandParser = CommandParser()
    parser.parse_commands(commands)

    assert len(parser.timeline) == 1
    event: Event = parser.timeline.events[0]
    assert isinstance(event, SleepEvent)
    assert event.to_string() == "sleep"
    assert parser.timeline.get_summary().sleep == 8 * 60 * 60


def test_dump_command() -> None:
    """Test command dumping."""

    commands: list[str] = [
        "book idiot = Idiot 600.0p .ru",
        "",
        "2000-01-01",
        "",
        "13:00 read @idiot 10.0/12.0%",
    ]
    parser: CommandParser = CommandParser()
    parser.parse_commands(commands)

    assert commands == parser.timeline.get_commands()


def test_program() -> None:
    """Test timeline with programming event."""

    commands: list[str] = dedent(
        """
        project @linux = Linux .c
        2000-01-01
        program @linux 3:00:00 !work
        """
    ).split("\n")
    (parser := CommandParser()).parse_commands(commands)
    timeline: Timeline = parser.timeline

    assert len(timeline.events) == 1

    event: Event = timeline.events[0]
    assert isinstance(event, ProgramEvent)

    assert event.tags == {"work"}
    assert event.project == Project(
        "linux", title="Linux", language=ProgrammingLanguage("c")
    )


def test_object_book() -> None:
    """Test book definition."""

    parser: CommandParser = CommandParser()
    parser.parse_command(
        "book @ni_eve = Ni d’Ève ni d’Adame .fr 186.0p Q1996380 /fiction"
    )
    timeline: Timeline = parser.timeline

    assert len(timeline.objects.objects) == 1
    assert isinstance(timeline.objects.objects["ni_eve"], Book)
    assert timeline.objects.objects["ni_eve"].volume == 186.0
    assert timeline.objects.objects["ni_eve"].language == Language("fr")
    assert timeline.objects.objects["ni_eve"].wikidata_id == 1996380


def test_event_clean() -> None:
    """Test cleaning event."""

    parser: CommandParser = CommandParser()
    parser.parse_commands(
        [
            "2000-01-01",
            "glasses @ray_ban = Ray-Ban Glasses",
            "23:00 clean @ray_ban !every_day",
        ]
    )
    timeline: Timeline = parser.timeline

    assert len(timeline.events) == 1
