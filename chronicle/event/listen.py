"""Listen-related events."""
import re
from datetime import timedelta
from typing import Any, Callable

from pydantic.main import BaseModel

from chronicle.argument import ArgumentParser
from chronicle.event.core import Event
from chronicle.event.value import Language
from chronicle.objects import Object, Objects
from chronicle.time import format_delta, parse_delta, INTERVAL_PATTERN

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def to_string(object_: Object) -> str:
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
            self.text += delimiter + loader(text)
        return self


class Interval(BaseModel):
    """Time interval in seconds."""

    from_: timedelta | None
    to_: timedelta | None

    @classmethod
    def from_string(cls, string: str):
        from_, to_ = string.split("-")
        return cls(from_=parse_delta(from_), to_=parse_delta(to_))

    def __str__(self) -> str:
        return (
            Text()
            .add(self.from_, loader=format_delta)
            .add("..")
            .add(self.to_, loader=format_delta)
            .text
        )


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
            Text(self.time, loader=to_string)
            .add("listen podcast")
            .add(objects.get_podcast(self.podcast_id), loader=to_string)
            .add(self.episode, " E ")
            .add(self.interval)
            .text
        )


class ListenMusicEvent(Event):
    """Listening music event."""

    title: str
    """Title of the song or music description."""

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
            Text(self.time, loader=to_string)
            .add("listen music")
            .add(self.title)
            .add(self.artist, " by ")
            .add(self.album, " on ")
            .add(self.language, " in ")
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
            Text(self.time, loader=to_string)
            .add("listen audiobook")
            .add(objects.get_audiobook(self.audiobook_id), loader=to_string)
            .text
        )
