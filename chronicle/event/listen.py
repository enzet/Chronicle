"""Listen-related events."""
import re
from datetime import timedelta
from typing import Any, Callable

from pydantic.main import BaseModel

from chronicle.argument import ArgumentParser
from chronicle.event.core import Event
from chronicle.event.value import Language
from chronicle.objects import Objects, Audiobook
from chronicle.time import format_delta, parse_delta, INTERVAL_PATTERN

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

from summary.core import Summary


def to_string(object_: Any) -> str:
    return object_.to_string()


class Text:
    """Chainable text builder."""

    def __init__(self, text: Any = "", loader: Callable[[Any], str] = str):
        self.text: str = loader(text)

    def add(
        self,
        text: Any | None,
        delimiter: str = " ",
        loader: Callable[[Any], str] = str,
    ) -> "Text":

        if text is not None:
            if loaded := loader(text):
                if self.text:
                    self.text += delimiter
                self.text += loaded
        return self


class Interval(BaseModel):
    """Time interval in seconds."""

    start: timedelta | None
    end: timedelta | None

    @classmethod
    def from_string(cls, string: str):
        start, end = string.split("-")
        return cls(from_=parse_delta(start), to_=parse_delta(end))

    def to_string(self) -> str:
        return (
            (format_delta(self.start) if self.start is not None else "")
            + (".." if self.start is not None or self.end is not None else "")
            + (format_delta(self.end) if self.end is not None else "")
        )

    def get_duration(self) -> float:
        if self.start is None and self.end is None:
            return 0.0
        return (self.end - self.start).total_seconds()


class ListenPodcastEvent(Event):
    """Listening podcast event."""

    podcast_id: str
    episode: str
    speed: float = 1.0
    interval: Interval | None = None

    @staticmethod
    def get_parser():
        return (
            ArgumentParser({"podcast"})
            .add_argument("podcast_id")
            .add_argument(
                "episode", prefix="episode", pattern=re.compile(r"[Ee](\d+)")
            )
            .add_argument(
                "interval",
                pattern=re.compile(r"\d\d:\d\d-\d\d:\d\d"),
                extractor=lambda x: Interval.from_string(x(0)),
            )
        )

    def to_string(self, objects: Objects) -> str:
        return (
            Text()
            .add("listen podcast")
            .add(
                objects.get_podcast(self.podcast_id),
                loader=lambda x: x.to_string(objects),
            )
            .add(self.episode, " E ")
            .add(self.interval, loader=to_string)
            .text
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

    @staticmethod
    def get_parser() -> ArgumentParser:
        return (
            ArgumentParser({"music", "song"})
            .add_argument("title")
            .add_argument("artist", prefix="by")
            .add_argument("album", prefix="on")
            .add_argument("language", pattern=re.compile("_(..)"))
        )

    def to_string(self, objects: Objects) -> str:
        return (
            Text()
            .add("listen music")
            .add(self.title)
            .add(self.artist, " by ")
            .add(self.album, " on ")
            .add(self.language, " in ")
            .add(self.interval, loader=to_string)
            .text
        )


class ListenAudiobookEvent(Event):
    """Listening audiobook event."""

    audiobook_id: str
    interval: Interval = Interval()
    speed: float | None = None

    @staticmethod
    def get_parser() -> ArgumentParser:
        return (
            ArgumentParser({"audiobook"})
            .add_argument("audiobook_id")
            .add_argument(
                "interval",
                pattern=INTERVAL_PATTERN,
                extractor=lambda x: Interval.from_string(x(0)),
            )
            .add_argument("speed", pattern=re.compile(r"x(\d*\.\d*)"))
        )

    def to_string(self, objects: Objects) -> str:
        return (
            Text()
            .add("listen audiobook")
            .add(
                objects.get_audiobook(self.audiobook_id),
                loader=lambda x: x.to_string(objects),
            )
            .add(self.interval, loader=to_string)
            .text
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
