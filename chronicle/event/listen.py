"""Listen-related events."""
from typing import Any, Callable

from chronicle.event.core import Event, Language, Objects, Object

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def to_string(object_: Object) -> str:
    return object_.to_string()


class Text:
    def __init__(self, text: Any):
        self.text: str = str(text)

    def add(
        self,
        text: Any | None,
        delimiter: str = " ",
        load: Callable[[Any], str] = str,
    ) -> "Text":

        if text is not None:
            self.text += delimiter + load(text)
        return self


class ListenPodcastEvent(Event):
    """Listening podcast event."""

    podcast_id: str
    episode: str
    speed: float = 1.0

    def to_string(self, objects: Objects) -> str:
        return (
            Text(self.time)
            .add("listen podcast")
            .add(objects.get_podcast(self.podcast_id), load=to_string)
            .add(self.episode, " E ")
            .text
        )


class ListenMusicEvent(Event):
    """Listening music event."""

    title: str
    artist: str | None = None
    album: str | None = None
    language: Language | None = None

    def to_string(self, objects: Objects) -> str:
        return (
            Text(self.time)
            .add("listen music")
            .add(self.title)
            .add(self.artist, " by ")
            .add(self.album, " on ")
            .add(self.language, " in ")
            .text
        )


class ListenAudiobookEvent(Event):
    """Listening audiobook event."""

    book_id: str
    reader: str | None = None

    def to_string(self, objects: Objects) -> str:
        return (
            Text(self.time)
            .add("listen audiobook")
            .add(objects.get_book(self.book_id), load=to_string)
            .text
        )
