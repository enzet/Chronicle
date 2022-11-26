from datetime import timedelta

from chronicle.event.core import Event
from chronicle.event.listen import (
    Interval,
    ListenAudiobookEvent,
    ListenMusicEvent,
    ListenPodcastEvent,
)
from chronicle.event.timeline import Timeline


def test_listen_podcast() -> None:
    """Test listening podcast command."""

    timeline: Timeline = Timeline()
    timeline.parse_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 podcast inner_french e5 "
        "10:00-20:00"
    )
    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenPodcastEvent)
    assert event.podcast_id == "inner_french"
    assert event.episode == "5"
    assert event.interval == Interval(
        from_=timedelta(minutes=10), to_=timedelta(minutes=20)
    )


def test_listen_music() -> None:
    """Test listening song command with title, artist, and album."""

    timeline: Timeline = Timeline()
    timeline.parse_command(
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

    timeline: Timeline = Timeline()
    timeline.parse_command(
        "2022-01-01T13:00:00/2022-01-01T14:00:00 audiobook idiot x1.25 "
        "00:00-10:00"
    )
    assert len(timeline) == 1
    event: Event = timeline.events[0]
    assert isinstance(event, ListenAudiobookEvent)
    assert event.audiobook_id == "idiot"
    assert event.speed == 1.25
    assert event.interval == Interval(
        from_=timedelta(), to_=timedelta(minutes=10)
    )
