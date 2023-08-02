import json
import logging
import re
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from colour import Color

import pydantic.error_wrappers

from chronicle.argument import Arguments, Argument
from chronicle.event.value import Language
from chronicle.time import Moment
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


@dataclass
class Object:
    tags: set[str] = field(default_factory=set)

    def to_string(self, objects: "Objects") -> str:
        """Get human-readable text representation of an object in English."""
        return self.__class__.__name__.lower()

    @classmethod
    def get_arguments(cls) -> Arguments:
        name: str = cls.__name__.lower()
        return Arguments([name], name)

    @classmethod
    def parse_command(cls, command: str) -> "Object":
        try:
            data = cls.get_arguments().parse(command)
            return cls(**data)
        except pydantic.error_wrappers.ValidationError as error:
            logging.critical(
                f"Command `{command}` could not be parsed: {error}"
            )

    def get_command(self) -> str:
        return self.get_arguments().to_object_command(self)


@dataclass
class Place(Object):
    name: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        name: str = cls.__name__.lower()
        return Arguments([name], name).add_argument("name")


@dataclass
class Airport(Place):
    pass


@dataclass
class Cafe(Place):
    pass


@dataclass
class Club(Place):
    pass


@dataclass
class Home(Place):
    pass


@dataclass
class Park(Place):
    pass


@dataclass
class Shop(Place):
    pass


@dataclass
class Station(Place):
    pass


@dataclass
class University(Place):
    pass


@dataclass
class Person(Object):
    """Real human."""

    name: str | None = None
    """Person name in the form of "<first name> <second name>"."""

    telegram: str | None = None
    """Telegram messenger unique identifier."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["person"], "person")
            .add_argument("name")
            .add_argument("telegram", prefix="tg")
        )


@dataclass
class Project(ArtObject):
    """Programming project."""

    title: str | None = None
    """Title of the project."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["project"], "project").add_argument("title")


@dataclass
class Medication(Thing):
    title: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["medication"], "medication").add_argument("title")
            + super().get_arguments()
        )


@dataclass
class Notebook(Thing):
    """"""


# Clothes.


@dataclass
class Clothes(Thing):
    art: str | None = None
    size: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            super()
            .get_arguments()
            .add_argument("art", prefix="art:")
            .add_argument(
                "size", patterns=[re.compile("^(XXS|XS|S|M|L|XL|XXL)$")]
            )
        )


@dataclass
class Pants(Clothes):
    pass


@dataclass
class Shoes(Clothes):
    pass


@dataclass
class Socks(Clothes):
    pass


@dataclass
class Sweater(Clothes):
    pass


@dataclass
class TShirt(Clothes):
    pass


@dataclass
class Underpants(Clothes):
    pass


# Physical objects.


@dataclass
class Pen(Thing):
    pass


@dataclass
class Cup(Thing):
    pass


@dataclass
class Device(Thing):
    pass


@dataclass
class Glasses(Thing):
    pass


@dataclass
class Headphones(Thing):
    pass


@dataclass
class Computer(Thing):
    pass


@dataclass
class Pack(Thing):
    pass


@dataclass
class Phone(Thing):
    pass


@dataclass
class Watch(Thing):
    pass


@dataclass
class Ink(Thing):
    pass


@dataclass
class Cable(Thing):
    pass


@dataclass
class BookObject(Thing):
    pass


@dataclass
class Movie(ArtObject):
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


@dataclass
class Podcast(Object):
    """Episodic series of digital audio."""

    title: str | None = None
    """Title of the podcast."""

    language: Language | None = None
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


@dataclass
class Book(Object):
    """A book, a paper, or any other text or one of its translations."""

    title: str | None = None
    """Title in language of the text."""

    language: Language | None = None
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

    wikidata_id: int | None = None
    """Wikidata item identifier."""

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


@dataclass
class Audiobook(Object):
    """Audio version of the book."""

    book_id: str | None = None
    """Unique string identifier."""

    wikidata_id: int = 0
    """Integer Wikidata entity identifier (0 if unspecified)."""

    duration: timedelta | None = None
    reader: str | None = None

    def to_string(self, objects: "Objects") -> str:
        return objects.get_object(self.book_id).to_string(objects)

    def get_book(self, objects: "Objects") -> Book | None:
        return objects.get_object(self.book_id)

    def get_language(self, objects: "Objects") -> Language | None:
        book: Book | None = objects.get_object(self.book_id)
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


@dataclass
class Objects:
    """Collection of event-related object collections."""

    objects: dict[str, Object] = field(default_factory=dict)

    def get_object(self, object_id: str) -> Object | None:
        if object_id in self.objects:
            return self.objects[object_id]
        else:
            logging.error(f"No such object: `{object_id}`.")

    def parse_command(self, command: str) -> bool:
        parts: list[str] = command.split(" ")
        prefix: str = parts[0]
        id_: str = parts[1]

        classes: list = Object.__subclasses__()
        for class_ in classes:
            classes += class_.__subclasses__()
            # FIXME: what if we have more levels?

        for class_ in classes:
            if prefix in class_.get_arguments().prefixes:
                self.objects[id_] = class_.parse_command(" ".join(parts[3:]))
                return True

        return False

    def get_commands(self) -> list[str]:
        commands: list[str] = []
        for key in sorted(self.__dict__.keys()):
            d = getattr(self, key)
            for id_ in sorted(d.keys()):
                object_ = d[id_]
                commands.append(f"{key[:-1]} {id_} {object_.to_command()}")
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
