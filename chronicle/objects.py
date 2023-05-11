import json
import re
from datetime import timedelta
from pathlib import Path

from pydantic.main import BaseModel

from chronicle.argument import Arguments, Argument
from chronicle.event.value import Language
from chronicle.wikidata import (
    Property,
    WikidataItem,
    get_data,
    get_movie,
    request_sparql,
)

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


wikidata_argument: Argument = Argument(
    "wikidata_id",
    patterns=[re.compile(r"Q(\d*)")],
    command_printer=lambda x: f"Q{x}",
)


class Object(BaseModel):
    def to_string(self, objects: "Objects") -> str:
        """Get human-readable text representation of an object in English."""
        return self.__class__.__name__.lower()

    @classmethod
    def get_arguments(cls) -> Arguments:
        name: str = cls.__name__.lower()
        return Arguments([name], name)

    @classmethod
    def parse_command(cls, command: str) -> "Object":
        return cls(**cls.get_arguments().parse(command))

    def get_command(self) -> str:
        return self.get_arguments().to_object_command(self)


class Place(Object):
    name: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        name: str = cls.__name__.lower()
        return Arguments([name], name).add_argument("name")


class Airport(Place):
    pass


class Cafe(Place):
    pass


class Club(Place):
    pass


class Home(Place):
    pass


class Park(Place):
    pass


class Shop(Place):
    pass


class Station(Place):
    pass


class University(Place):
    pass


class Project(Object):
    """Programming project."""

    title: str
    """Title of the project."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["project"], "project").add_argument("title")


class Movie(Object):
    title: str | None = None
    """Title of the movie."""

    wikidata_id: int = 0
    """Integer Wikidata entity identifier (0 if unspecified)."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["movie"], "movie")
            .add_argument("title")
            .add_argument("language", patterns=[re.compile(r"\.(..)")])
            .add(wikidata_argument)
        )


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

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["podcast"], "podcast")
            .add_argument("title")
            .add_argument(
                "language",
                patterns=[re.compile(r"\.(..)")],
                command_printer=lambda x: f".{x}",
            )
            .add(wikidata_argument)
        )


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

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["book"], "book")
            .add_argument("title", command_printer=str)
            .add_argument(
                "language",
                patterns=[re.compile(r"\.(..)")],
                command_printer=lambda x: f".{x}",
            )
            .add(wikidata_argument)
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

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["audiobook"], "audiobook")
            .add_argument("book_id")
            .add(wikidata_argument)
        )

    def get_command(self) -> str:
        return self.book_id


class Objects(BaseModel):
    """Collection of event-related object collections."""

    podcasts: dict[str, Podcast] = {}
    books: dict[str, Book] = {}
    audiobooks: dict[str, Audiobook] = {}
    airports: dict[str, Airport] = {}
    cafes: dict[str, Cafe] = {}
    clubs: dict[str, Club] = {}
    parks: dict[str, Park] = {}
    projects: dict[str, Project] = {}
    stations: dict[str, Station] = {}
    homes: dict[str, Home] = {}
    shops: dict[str, Shop] = {}
    universitys: dict[str, University] = {}
    movies: dict[str, Movie] = {}

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
            classes += class_.__subclasses__()
            # FIXME: what if we have more levels?

        for class_ in classes:
            if prefix in class_.get_arguments().prefixes:
                # FIXME: dirty hack.
                self.__getattribute__(prefix + "s")[id_] = class_.parse_command(
                    " ".join(parts[2:])
                )
                return True

        return False

    def get_commands(self) -> list[str]:
        commands: list[str] = []
        for key in sorted(self.__dict__.keys()):
            d = getattr(self, key)
            for id_ in sorted(d.keys()):
                object_ = d[id_]
                commands.append(f"{key[:-1]} {id_} {object_.get_command()}")
        return commands

    def fill(self, cache_path: Path):
        for movie in self.movies.values():
            if movie.wikidata_id:
                continue
            object_data: dict = json.loads(
                get_data(
                    cache_path / f"moving_image_{movie.title}@en.json",
                    request_sparql,
                    get_movie(movie.title),
                ).decode()
            )["results"]["bindings"]
            print(f"No Wikidata ID for movie {movie.title}.")
            if object_data:
                print("  Possible candidates:")
                items = [
                    WikidataItem.from_id(
                        int(
                            x["item"]["value"][
                                len("http://www.wikidata.org/entity/Q") :
                            ]
                        ),
                        cache_path,
                    )
                    for x in object_data
                ]
                items = list(set(items))
                for index, i in enumerate(items):
                    s = i.labels["en"]["value"]
                    for a in i.get_claim(Property.TITLE, cache_path):
                        s += " - " + a["text"]
                    for a in i.get_claim(Property.START_TIME, cache_path):
                        s += " - " + a["time"][1:5]
                    for a in i.get_claim(Property.DIRECTOR, cache_path):
                        s += " - " + (a.labels["en"]["value"])
                    for a in i.get_claim(Property.GENRE, cache_path):
                        s += " - " + (a.labels["en"]["value"])
                    for a in i.get_claim(
                        Property.ORIGINAL_BROADCASTER, cache_path
                    ):
                        s += " - " + (a.labels["en"]["value"])
                    for a in i.get_claim(Property.DISTRIBUTED_BY, cache_path):
                        s += " - " + (a.labels["en"]["value"])
                    for a in i.get_claim(
                        Property.ORIGINAL_LANGUAGE_OF_FILM_OR_TV, cache_path
                    ):
                        s += " - " + (a.labels["en"]["value"])
                    print(f"    {index + 1}.", s)
                index = int(input()) - 1
                movie.wikidata_id = items[index].wikidata_id
