"""
Event and global event parameters.

This file describes events and some common attributes that events may have.
"""
from datetime import timedelta

from pydantic.main import BaseModel

from chronicle.argument import ArgumentParser
from chronicle.time import Time

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


class Language(str):
    """Natural language of text, speach, or song."""

    def __init__(self, code: str):
        self.code: str = code

    def __eq__(self, other: "Language"):
        return self.code == other.code

    def __str__(self) -> str:
        """Get English name of the language or return code."""

        if self.code == "fr":
            return "French"

        return self.code

    @classmethod
    def __get_validators__(cls):
        yield cls


class Object(BaseModel):
    def to_string(self) -> str:
        raise NotImplementedError()


class Podcast(Object):

    title: str
    """Title of the podcast."""

    language: Language
    """Language of the podcast."""

    author: str | None = None
    """The main speaker of the podcast."""

    is_adapted: bool = False
    """If the podcast used simplified language for educational purposes."""

    def to_string(self) -> str:
        return self.title


class Book(Object):
    """A book, a paper, or any other text or some of its translations."""

    title: str
    """Title in language of the text."""

    language: Language
    """Language of the text."""

    volume: float | None = None
    """
    Number of pages.

    Since number of pages may vary from one printed book to another, this is an
    approximation. If there is no printed version of the book, number of pages
    may be approximated as number of symbols divided by 2000 (40 lines × 50
    symbols per line).
    """

    author: str | None = None
    """Original book author name (not translator)."""

    year: int | None = None
    """Year of the first publication of the book (not its translation)."""

    def to_string(self) -> str:
        return self.title


class Audiobook(Object):
    """Audio version of the book."""

    book_id: str
    duration: timedelta
    reader: str

    def to_string(self) -> str:
        return self.book_id


class Objects(BaseModel):
    """Collection of event-related object collections."""

    podcasts: dict[str, Podcast] = []
    books: dict[str, Book] = []
    audiobooks: dict[str, Audiobook] = []

    def get_podcast(self, podcast_id: str) -> Podcast | None:
        return self.podcasts.get(podcast_id)

    def get_book(self, book_id: str) -> Book | None:
        return self.books.get(book_id)

    def get_audiobook(self, audiobook_id: str) -> Audiobook | None:
        return self.audiobooks.get(audiobook_id)


class Event(BaseModel):
    """
    Any event happened at some point or during some period in time.

    This includes events such as reading, running, playing, as well as
    conditions, such as current body temperature, heart rate, being at some
    place or taking some kind of transportation.
    """

    time: Time
    """Point in time or time span when event is occurred."""

    def process_command(self, arguments: list[str]) -> None:
        pass

    @staticmethod
    def get_parser() -> ArgumentParser:
        return ArgumentParser(set())

    @classmethod
    def parse_command(cls, time: Time, command: str) -> "Event":
        arguments = cls.get_parser().parse(command)
        return cls(time=time, **arguments)

    def to_string(self, objects: Objects) -> str:
        """
        Get human-readable event text representation in English.

        :param objects: object information needed to fill data, because some
            events depend on objects and know solely about object identifier
        """
        return str(self.time)


def to_camel(text: str) -> str:
    """Make the first letter capital."""
    return text[0].upper() + text[1:]
