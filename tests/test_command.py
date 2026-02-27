"""Tests for command."""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from chronicle.event.art import (
    ListenAudiobookEvent,
    ListenMusicEvent,
    ListenPodcastEvent,
    WatchEvent,
)
from chronicle.event.common import LearnEvent, ProgramEvent, SleepEvent
from chronicle.event.core import Event, Objects
from chronicle.event.sport import (
    ChinUpsEvent,
    PecDeckEvent,
    RunEvent,
    WalkEvent,
)
from chronicle.objects.core import Audiobook, Book, Glasses, Object, Project
from chronicle.time import Context, Timedelta
from chronicle.timeline import CommandParser, Timeline
from chronicle.value import Interval, Language, ProgrammingLanguage

if TYPE_CHECKING:
    from chronicle.summary.core import Summary

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
    assert event.speed == 1.25  # noqa: PLR2004
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
    assert event.time.start.hour == 13  # noqa: PLR2004


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
    assert event.time.start.year == 2000  # noqa: PLR2004
    assert event.time.start.hour == 13  # noqa: PLR2004


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
    assert objects["ni_eve"].volume == 186  # noqa: PLR2004
    assert objects["ni_eve"].language == Language("fr")
    assert objects["ni_eve"].wikidata_id == 1996380  # noqa: PLR2004


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


def test_listen_audiobook_duration() -> None:
    """Test audiobook event with a plain duration token."""

    timeline: Timeline = parse(
        """
        book book_1984 = 1984 .en
        audiobook audio_1984 = @book_1984
        2000-01-01
        audiobook @audio_1984 1:52:00
        """
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.audiobook
    assert event.audiobook.book
    assert event.audiobook.book.title == "1984"
    assert event.duration == Timedelta.from_code("1:52:00")


def test_podcast_by_reference() -> None:
    """Test podcast event using a pre-defined podcast object reference."""

    timeline: Timeline = parse(
        """
        podcast podcast_es = My Podcast .es
        2000-01-01
        podcast @podcast_es e74 07:30
        """
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, ListenPodcastEvent)
    assert event.podcast
    assert event.podcast.language == Language("es")
    assert event.episode == "74"
    assert event.duration == Timedelta.from_code("07:30")


def test_watch() -> None:
    """Test watch event with language, subtitles, season, episode, duration."""

    timeline: Timeline = parse(
        """
        2000-01-01
        watch Elite .es _es s1 e1 56:31
        """
    )
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, WatchEvent)
    assert event.video
    assert event.video.title == "Elite"
    assert event.language == Language("es")
    assert event.subtitles == Language("es")
    assert event.season == 1
    assert event.episode == "1"
    assert event.duration == Timedelta.from_code("56:31")


def test_run_distance() -> None:
    """Test run event with distance only."""

    timeline: Timeline = parse("2000-01-01\nrun 5km")
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, RunEvent)
    assert event.distance == 5000.0  # noqa: PLR2004


def test_run_speed_and_distance() -> None:
    """Test run event with speed and distance."""

    timeline: Timeline = parse("2000-01-01\nrun 10km/h 3.80km")
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, RunEvent)
    assert event.speed == 10.0  # noqa: PLR2004
    assert event.distance == 3800.0  # noqa: PLR2004


def test_run_pace() -> None:
    """Test run event with distance and pace using /km suffix."""

    timeline: Timeline = parse("2000-01-01\nrun 1km 6:36/km")
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, RunEvent)
    assert event.distance == 1000.0  # noqa: PLR2004
    assert event.pace == Timedelta.from_code("6:36")
    assert event.duration is None


def test_walk() -> None:
    """Test walk event with distance."""

    timeline: Timeline = parse("2000-01-01\nwalk 3km")
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, WalkEvent)
    assert event.distance == 3000.0  # noqa: PLR2004


def test_exercise_single_set() -> None:
    """Test exercise event with a single set count."""

    timeline: Timeline = parse("2000-01-01\nchin_ups 5")
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, ChinUpsEvent)
    assert event.sets == [5]


def test_exercise_multiple_sets() -> None:
    """Test exercise event with comma-separated set counts."""

    timeline: Timeline = parse("2000-01-01\nchin_ups 5,5,4")
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, ChinUpsEvent)
    assert event.sets == [5, 5, 4]


def test_exercise_shorthand_sets() -> None:
    """Test exercise event with NxM shorthand (3x5 means [5, 5, 5])."""

    timeline: Timeline = parse("2000-01-01\nchin_ups 3x5")
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, ChinUpsEvent)
    assert event.sets == [5, 5, 5]


def test_exercise_with_weight() -> None:
    """Test exercise event with uniform weight across sets."""

    timeline: Timeline = parse("2000-01-01\npec_deck 3x10 30kg")
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, PecDeckEvent)
    assert event.sets == [10, 10, 10]
    assert event.weights == [30.0, 30.0, 30.0]


def test_exercise_with_multiple_weights() -> None:
    """Test exercise event with per-set weights."""

    timeline: Timeline = parse("2000-01-01\npec_deck 10,8,8 30kg,35kg,35kg")
    events: list[Event] = timeline.events

    assert len(events) == 1
    event: Event = events[0]
    assert isinstance(event, PecDeckEvent)
    assert event.sets == [10, 8, 8]
    assert event.weights == [30.0, 35.0, 35.0]


def test_exercise_summary() -> None:
    """Test that exercise repetitions are counted in the summary."""

    timeline: Timeline = parse("2000-01-01\nchin_ups 5,5,4")
    summary: Summary = timeline.get_summary()

    assert summary.exercises["chin_ups"] == 14  # noqa: PLR2004


def test_exercise_summary_multiple() -> None:
    """Test that multiple exercise events accumulate in the summary."""

    timeline: Timeline = parse(
        """
        2000-01-01
        chin_ups 5,5,4
        pec_deck 3x10 30kg
        chin_ups 3
        """
    )
    summary: Summary = timeline.get_summary()

    assert summary.exercises["chin_ups"] == 17  # noqa: PLR2004
    assert summary.exercises["pec_deck"] == 30  # noqa: PLR2004
