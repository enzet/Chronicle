"""Tests for command."""

from datetime import UTC, datetime, timedelta

from chronicle.event.art import (
    ListenAudiobookEvent,
    ListenMusicEvent,
    ListenPodcastEvent,
)
from chronicle.event.common import LearnEvent, ProgramEvent, SleepEvent
from chronicle.event.core import Event, Objects
from chronicle.objects.core import Audiobook, Book, Glasses, Object, Project
from chronicle.summary.core import Summary
from chronicle.time import Context, Timedelta
from chronicle.timeline import CommandParser, Timeline
from chronicle.value import Interval, Language, ProgrammingLanguage

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def parse(commands: str) -> Timeline:
    """Parse commands and return events and objects."""

    parser: CommandParser = CommandParser()
    for command in commands.split("\n"):
        parser.parse_command(command)
    return parser.timeline


def test_listen_podcast() -> None:
    """Test listening podcast command."""

    timeline: Timeline = parse(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 podcast Inner French e5"
        " 10:00/20:00"
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
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

    timeline: Timeline = parse("book idiot = Idiot .ru")
    objects: dict[str, Object] = timeline.objects.objects

    assert len(objects) == 1
    assert isinstance(objects["idiot"], Book)
    assert objects["idiot"].title == "Idiot"
    assert objects["idiot"].language == Language("ru")


def test_listen_music() -> None:
    """Test listening song command with title, artist, and album."""

    timeline: Timeline = parse(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 song"
        " Strawberry Fields Forever by The Beatles on Magic Mystery Tour"
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, ListenMusicEvent)
    assert event.title == "Strawberry Fields Forever"
    assert event.artist == "The Beatles"
    assert event.album == "Magic Mystery Tour"


def test_listen_audiobook() -> None:
    """Test listening song command with title, artist, and album."""

    timeline: Timeline = parse(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 audiobook Idiot x1.25"
        " 00:00/10:00"
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
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

    timeline: Timeline = parse(
        """
        2022-01-01T13:00:00/2022-01-01T14:00:00 audiobook idiot 1:10:10/2:20:20
        """
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.interval == Interval(
        start=Timedelta(timedelta(hours=1, minutes=10, seconds=10)),
        end=Timedelta(timedelta(hours=2, minutes=20, seconds=20)),
    )


def test_sleep() -> None:
    """Test sleeping event."""

    timeline: Timeline = parse("2022-01-01T00:00:00/2022-01-01T08:00:00 sleep")
    events: list[Event] = timeline.events
    summary: Summary = timeline.get_summary()

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, SleepEvent)
    assert summary.sleep == 8 * 60 * 60


def test_short_time() -> None:
    """Test listening song command with title, artist, and album."""

    book: Book = Book("idiot", title="Idiot", language=Language("ru"))
    parser: CommandParser = CommandParser()
    timeline: Timeline = parser.timeline
    timeline.objects = Objects(
        {"idiot": book, "idiot_audio": Audiobook("idiot_audio", book=book)}
    )
    parser.context = Context(current_date=datetime(2022, 1, 2, tzinfo=UTC))
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

    timeline: Timeline = parse(
        """
        book idiot = Idiot .ru
        audiobook idiot_audio = @idiot
        2000-01-01
        13:00 audiobook @idiot_audio
        """
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.to_string() == "listen to audiobook Idiot"
    assert event.time.start
    assert event.time.start == event.time.end
    assert event.time.start.year == 2000
    assert event.time.start.hour == 13


def test_file_sleep() -> None:
    """Test file command with sleeping event."""

    timeline: Timeline = parse(
        """
        2000-01-01
        00:00/08:00 sleep
        """
    )
    events: list[Event] = timeline.events
    summary: Summary = timeline.get_summary()

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, SleepEvent)
    assert event.to_string() == "sleep"
    assert summary.sleep == 8 * 60 * 60


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

    timeline: Timeline = parse(
        """
        project @linux = Linux .c
        2000-01-01
        program @linux 3:00:00 !work
        """
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, ProgramEvent)
    assert event.tags == {"work"}
    assert event.project == Project(
        "linux", title="Linux", language=ProgrammingLanguage("c")
    )


def test_object_book() -> None:
    """Test book definition."""

    timeline: Timeline = parse(
        "book @ni_eve = Ni d’Ève ni d’Adame .fr 186p Q1996380 /fiction"
    )
    objects: dict[str, Object] = timeline.objects.objects

    assert len(objects) == 1
    assert isinstance(objects["ni_eve"], Book)
    assert objects["ni_eve"].title == "Ni d’Ève ni d’Adame"
    assert objects["ni_eve"].volume == 186
    assert objects["ni_eve"].language == Language("fr")
    assert objects["ni_eve"].wikidata_id == 1996380


def test_event_clean() -> None:
    """Test cleaning event."""

    timeline: Timeline = parse(
        """
        2000-01-01
        glasses @ray_ban = Ray-Ban Glasses
        23:00 clean @ray_ban !every_day
        """
    )
    events: list[Event] = timeline.events
    objects: dict[str, Object] = timeline.objects.objects

    assert len(events) == 1
    assert isinstance(objects["ray_ban"], Glasses)
    assert objects["ray_ban"].name == "Ray-Ban Glasses"


def test_event_learn_complex_duration() -> None:
    """Test learning event with complex duration."""

    timeline: Timeline = parse(
        """
        service @duolingo = Duolingo
        2000-01-01
        learn /language/de using @duolingo 2:35,4:55
        """
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, LearnEvent)
    assert event.get_duration() == 2 * 60 + 35 + 4 * 60 + 55


def test_event_learn_unknown_duration() -> None:
    """Test learning event with complex duration and unknown points."""

    timeline: Timeline = parse(
        """
        service @duolingo = Duolingo
        2000-01-01
        learn /language/de using @duolingo 2:00,?,4:00
        """
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, LearnEvent)
    assert event.get_duration() == ((2 + 4) / 2 * 3) * 60
