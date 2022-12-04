from datetime import timedelta

from pydantic.main import BaseModel

from chronicle.event.value import Language


class Object(BaseModel):
    def to_string(self, objects: "Objects") -> str:
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

    def to_string(self, objects: "Objects") -> str:
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

    def to_string(self, objects: "Objects") -> str:
        return self.title


class Audiobook(Object):
    """Audio version of the book."""

    book_id: str
    duration: timedelta | None = None
    reader: str | None = None

    def to_string(self, objects: "Objects") -> str:
        return objects.get_book(self.book_id).to_string(objects)


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
