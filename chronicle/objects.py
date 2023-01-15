import re
from datetime import timedelta

from pydantic.main import BaseModel

from argument import ArgumentParser
from chronicle.event.value import Language


class Object(BaseModel):
    def to_string(self, objects: "Objects") -> str:
        """Get human-readable text representation of an object in English."""
        raise NotImplementedError()

    @staticmethod
    def get_parser() -> ArgumentParser:
        raise NotImplementedError()

    @classmethod
    def parse_command(cls, command: str) -> "Object":
        return cls(**cls.get_parser().parse(command))


class Podcast(Object):
    """Episodic series of digital audio."""

    title: str
    """Title of the podcast."""

    language: Language
    """Language of the podcast."""

    wikidata_id: int = 0
    """Integer Wikidata entity identifier (0 if unspecified)."""

    author: str | None = None
    """The main speaker of the podcast."""

    is_adapted: bool = False
    """Whether the podcast uses simplified language for educational purposes."""

    def to_string(self, objects: "Objects") -> str:
        return self.title

    @staticmethod
    def get_parser() -> ArgumentParser:
        return ArgumentParser({"podcast"}).add_argument("title")


class Book(Object):
    """A book, a paper, or any other text or one of its translations."""

    title: str
    """Title in language of the text."""

    language: Language
    """Language of the text."""

    wikidata_id: int = 0
    """Integer Wikidata entity identifier (0 if unspecified)."""

    volume: float | None = None
    """Number of pages.

    Since number of pages may vary from one printed book to another, this is an
    approximation. If there is no printed version of the book, number of pages
    may be approximated as number of symbols divided by 2000 (40 lines × 50
    symbols per line).
    """

    author: str | None = None
    """Original book author name (not translator)."""

    year: int | None = None
    """Year of the first publication of the book (not its translation)."""

    def to_string(self, objects: "Objects") -> str:
        return self.title

    @staticmethod
    def get_parser() -> ArgumentParser:
        return (
            ArgumentParser({"book"})
            .add_argument("title")
            .add_argument("language", pattern=re.compile("_(..)"))
        )


class Audiobook(Object):
    """Audio version of the book."""

    book_id: str
    """Unique string identifier."""

    wikidata_id: int = 0
    """Integer Wikidata entity identifier (0 if unspecified)."""

    duration: timedelta | None = None
    reader: str | None = None

    def to_string(self, objects: "Objects") -> str:
        return objects.get_book(self.book_id).to_string(objects)

    def get_book(self, objects: "Objects") -> Book | None:
        return objects.get_book(self.book_id)

    def get_language(self, objects: "Objects") -> Language | None:
        book: Book | None = objects.get_book(self.book_id)
        return book.language if book else None

    @staticmethod
    def get_parser() -> ArgumentParser:
        return ArgumentParser({"audiobook"}).add_argument("book_id")


class Objects(BaseModel):
    """Collection of event-related object collections."""

    podcasts: dict[str, Podcast] = {}
    books: dict[str, Book] = {}
    audiobooks: dict[str, Audiobook] = {}

    def get_podcast(self, podcast_id: str) -> Podcast | None:
        return self.podcasts.get(podcast_id)

    def get_book(self, book_id: str) -> Book | None:
        return self.books.get(book_id)

    def get_audiobook(self, audiobook_id: str) -> Audiobook | None:
        return self.audiobooks.get(audiobook_id)

    def parse_command(self, command: str) -> bool:

        parts: list[str] = command.split(" ")
        if len(parts) < 3:
            return False
        prefix: str = parts[0]
        id_: str = parts[1]

        classes: list = Object.__subclasses__()

        for class_ in classes:
            if prefix in class_.get_parser().prefixes:
                self.__getattribute__(prefix + "s")[id_] = class_.parse_command(
                    " ".join(parts[2:])
                )
                return True

        return False
