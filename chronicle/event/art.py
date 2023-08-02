"""Events about reading, watching or listening things."""
import re

from chronicle.argument import Arguments, Argument
from chronicle.event.core import Event
from chronicle.event.value import Language
from chronicle.objects import Objects, Audiobook
from chronicle.summary.core import Summary

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

from chronicle.event.value import Interval


language_argument: Argument = Argument(
    "language",
    patterns=[re.compile(r"\.(..)")],
    command_printer=lambda x: f".{x}",
)
episode_argument: Argument = Argument(
    "episode",
    prefix="episode",
    patterns=[re.compile(r"[Ee](\d+)")],
    pretty_printer=lambda o, v: f"E {v}",
    command_printer=lambda x: f"e{x}",
)


def text_argument(name: str):
    return Argument(
        name,
        pretty_printer=lambda o, v: o.get_podcast(v).title,
    )


def one_pattern_argument(name, class_, index: int = 0):
    return Argument(
        name,
        patterns=[class_.get_pattern()],
        extractors=[lambda x: class_.from_string(x(index))],
        pretty_printer=lambda o, v: v.to_string(),
    )


interval_argument: Argument = one_pattern_argument("interval", Interval)


class ListenPodcastEvent(Event):
    """Listening podcast event."""

    podcast_id: str | None = None
    """Unique string identifier of the podcast."""

    episode: str | None = None
    """Episode number or name."""

    speed: float | None = None
    """"""

    interval: Interval | None = None

    @classmethod
    def get_arguments(cls):
        return (
            Arguments(["podcast"], "listen podcast")
            .add_argument(
                "podcast_id",
                pretty_printer=lambda o, v: o.get_podcast(v).title,
            )
            .add(episode_argument)
            .add(one_pattern_argument("interval", Interval))
        )

    def register_summary(self, summary: Summary, objects: Objects):
        summary.register_listen(
            self.interval.get_duration(),
            objects.get_podcast(self.podcast_id).language,
        )


class ListenMusicEvent(Event):
    """Listening music event."""

    title: str
    """Title of the song or music description."""

    interval: Interval = Interval()
    artist: str | None = None
    album: str | None = None
    language: Language | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["music", "song"], "listen music")
            .add_argument("title")
            .add_argument("artist", prefix="by")
            .add_argument("album", prefix="on")
            .add(language_argument)
        )


class ReadEvent(Event):
    book_id: str
    language: str | None = None
    pages: tuple[float, float] | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["read"], "read")
            .add_argument("book_id")
            .add(language_argument)
            .add_argument(
                "pages",
                patterns=[re.compile(r"(\d+(\.\d*)?)/(\d+(\.\d*)?)")],
                extractors=[lambda x: (float(x(1)), float(x(3)))],
                command_printer=lambda x: f"{x[0]}/{x[1]}",
            )
        )


class StandupEvent(Event):
    title: str
    language: str | None = None
    place_id: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["standup"], "standup")
            .add_argument("title")
            .add(language_argument)
            .add_argument(
                "place_id", prefix="at", command_printer=lambda x: f"at {x}"
            )
        )


class WatchEvent(Event):
    movie_id: str
    season: int | None = None
    episode: int | None = None
    interval: Interval | None = None
    language: str | None = None
    subtitles: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["watch"], "watch")
            .add_argument("movie_id")
            .add(language_argument)
            .add_argument(
                "subtitles",
                patterns=[re.compile("_(..)")],
                command_printer=lambda x: f"_{x}",
            )
            .add_argument(
                "season",
                patterns=[re.compile(r"s(\d+)")],
                extractors=[lambda x: int(x(1))],
                command_printer=lambda x: f"s{x}",
            )
            .add(episode_argument)
            .add(interval_argument)
        )

    def get_language(self) -> Language | None:
        return self.language

    def register_summary(self, summary: Summary, objects: Objects):
        if self.interval:
            summary.register_listen(
                self.interval.get_duration(), self.get_language()
            )


class ListenAudiobookEvent(Event):
    """Listening audiobook event."""

    audiobook_id: str
    interval: Interval = Interval()
    speed: float | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["audiobook"], "listen audiobook")
            .add_argument(
                "audiobook_id",
                pretty_printer=lambda o, v: o.get_book(
                    o.get_audiobook(v).book_id
                ).title,
            )
            .add(interval_argument)
            .add_argument(
                "speed",
                patterns=[re.compile(r"x(\d*\.\d*)")],
                command_printer=lambda x: f"x{x}",
            )
        )

    def get_audiobook(self, objects: Objects) -> Audiobook | None:
        return objects.get_audiobook(self.audiobook_id)

    def get_language(self, objects: Objects) -> Language | None:
        audiobook: Audiobook | None = self.get_audiobook(objects)
        return audiobook.get_language(objects) if audiobook else None

    def register_summary(self, summary: Summary, objects: Objects):
        summary.register_listen(
            self.interval.get_duration(), self.get_language(objects)
        )
