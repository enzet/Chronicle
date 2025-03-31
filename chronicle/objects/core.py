import json
import re
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import ClassVar, Self
from colour import Color

from chronicle.argument import Arguments
from chronicle.errors import (
    ChronicleObjectNotFoundException,
    ChronicleCodeException,
)
from chronicle.value import (
    Birthday,
    OSM,
    ChronicleValueException,
    Language,
    Cost,
    ProgrammingLanguage,
    Subject,
    Tags,
    WikidataId,
)
from chronicle.time import Moment, Timedelta
from chronicle.wikidata import (
    Property,
    WikidataItem,
    get_data,
    get_movie,
    request_sparql,
)

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


COLOR_PATTERN = re.compile(
    r"(red|darkred|lightred|"
    r"green|darkgreen|lightgreen|"
    r"blue|darkblue|lightblue|"
    r"yellow|brown|violet|"
    r"black|white|grey|gray|lightgrey|lightgray|darkgrey|darkgray)"
)


def camel_to_snake(name: str) -> str:
    """Convert CamelCase name to snake_case."""
    return re.sub(r"([A-Z])", r"_\1", name)[1:].lower()


@dataclass
class Object:
    """Any object, similar to a Wikidata item."""

    id: str
    """Unique identifier of the object."""

    tags: set[str] = field(default_factory=set)
    """Set of user defined string tags."""

    def __hash__(self) -> int:
        return hash(self.id)

    def to_string(self) -> str:
        """Get human-readable text representation of an object in English."""
        return self.__class__.__name__.lower()

    def get_type(self) -> str:
        """Get object type string identifier."""
        return camel_to_snake(self.__class__.__name__)

    @classmethod
    def from_value(cls, value: str) -> Self:
        return cls(None)

    arguments: ClassVar[Arguments] = Arguments(
        ["object"], "object"
    ).add_class_argument("tags", Tags)

    def to_command(self) -> str:
        return self.arguments.to_object_command(self)

    prefix: ClassVar[str] = None


@dataclass
class Thing(Object):
    """Physical object, not a place."""

    name: str | None = None
    """Name of the thing."""

    link: str | None = None
    """Link to the thing."""

    cost: str | None = None
    """Cost of the thing."""

    expired: Moment | None = None
    """If this field is `None`, the object is not expendable."""

    retired: bool = False
    """If the object is not in use."""

    since: Moment | None = None
    """Moment when the object was acquired."""

    temperature: str | None = None
    """Recommended temperature for storing the thing."""

    color: Color | None = None
    """Main color of the thing."""

    arguments: ClassVar[Arguments] = (
        Arguments(["thing"], "thing")
        .add_argument("name")
        .add_argument("link", patterns=[re.compile(r"(https?://[^ ]*)")])
        .add_class_argument("cost", Cost)
        .add_argument(
            "expired",
            prefix="exp:",
            loader=lambda value, _: Moment.from_string(value),
        )
        .add_argument(
            "since",
            prefix="since:",
            loader=lambda value, _: Moment.from_string(value),
        )
        .add_argument("temperature", prefix="temp:")
        .add_argument(
            "retired",
            patterns=[re.compile("retired")],
            extractors=[lambda _: True],
        )
        .add_argument(
            "color",
            patterns=[COLOR_PATTERN],
            loader=lambda value, _: Color(value),
        )
    )


@dataclass
class Place(Object):
    """Some place with geographical coordinates."""

    name: str | None = None
    """Name of the place."""

    osm: OSM | None = None
    """Link to the OpenStreetMap object."""

    arguments: ClassVar[Arguments] = (
        Arguments(["place"], "place")
        .add_argument("name")
        .add_class_argument("osm", OSM)
    )


@dataclass
class ArtObject(Object):
    name: str | None = None

    arguments: ClassVar[Arguments] = Arguments(
        ["art_object"], "art_object"
    ).add_argument("name")


@dataclass
class Country(Object):
    name: str | None = None

    arguments: ClassVar[Arguments] = Arguments(
        ["country"], "country"
    ).add_argument("name")


@dataclass
class Airport(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(
        ["airport"], "airport"
    )


@dataclass
class ArtCenter(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(
        ["art_center"], "art_center"
    )


@dataclass
class Bank(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(["bank"], "bank")


@dataclass
class Cafe(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(["cafe"], "cafe")


@dataclass
class Clinic(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(
        ["clinic"], "clinic"
    )


@dataclass
class Club(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(["club"], "club")


@dataclass
class Home(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(["home"], "home")


@dataclass
class Park(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(["park"], "park")


@dataclass
class Shop(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(["shop"], "shop")


@dataclass
class Station(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(
        ["station"], "station"
    )


@dataclass
class University(Place):
    arguments: ClassVar[Arguments] = Place.arguments.replace(
        ["university"], "university"
    )


@dataclass
class Person(Object):
    """Real human."""

    name: str | None = None
    """Person name in the form of `<first name> <second name>`."""

    telegram: str | None = None
    """Telegram messenger unique identifier."""

    birthday: Birthday | None = None
    """Person birthday."""

    prefix: ClassVar[str] = "with"
    arguments: ClassVar[Arguments] = (
        Arguments(["person"], "person")
        .add_argument("name")
        .add_argument("telegram", prefix="tg:")
        .add_class_argument("birthday", Birthday)
    )

    @classmethod
    def from_value(cls, value: str) -> Self:
        return cls(None, name=value)


SERVICE_NAMES = {
    "duolingo": "Duolingo",
    "memrise": "Memrise",
}


@dataclass
class Service(Object):
    """Service for watching, reading, listening, writing, or learning."""

    name: str | None = None
    """Name of the service."""

    arguments: ClassVar[Arguments] = Arguments(
        ["service"], "service"
    ).add_argument("name")
    prefix: ClassVar[str] = "using"

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_value(cls, value: str) -> Self:
        return cls(None, name=value)


@dataclass
class Medication(Thing):
    title: str | None = None

    arguments: ClassVar[Arguments] = (
        Arguments(["medication"], "medication").add_argument("title")
        + Thing.arguments
    )


@dataclass
class Notebook(Thing):
    """Notebook."""

    arguments: ClassVar[Arguments] = Thing.arguments.replace(
        ["notebook"], "notebook"
    )


@dataclass
class Card(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(["card"], "card")


# Physical objects.


@dataclass
class Pen(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(["pen"], "pen")


@dataclass
class Cup(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(["cup"], "cup")


@dataclass
class Device(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(
        ["device"], "device"
    )


@dataclass
class Glasses(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(
        ["glasses"], "glasses"
    )


@dataclass
class Headphones(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(
        ["headphones"], "headphones"
    )


@dataclass
class Computer(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(
        ["computer"], "computer"
    )


@dataclass
class Pack(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(["pack"], "pack")


@dataclass
class Phone(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(["phone"], "phone")


@dataclass
class Watch(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(["watch"], "watch")


@dataclass
class Ink(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(["ink"], "ink")


@dataclass
class Cable(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(["cable"], "cable")


@dataclass
class BookObject(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(
        ["book_object"], "book_object"
    )


@dataclass
class Document(Thing):
    arguments: ClassVar[Arguments] = Thing.arguments.replace(
        ["document"], "document"
    )


@dataclass
class Video(ArtObject):
    title: str | None = None
    """Title of the video."""

    language: Language | None = None
    """Language of the video."""

    wikidata_id: int = 0
    """Integer Wikidata entity identifier (0 if unspecified)."""

    subject: Subject | None = None
    """Categorised subject."""

    arguments: ClassVar[Arguments] = (
        Arguments(["video"], "video")
        .add_argument("title")
        .add_class_argument("language", Language)
        .add_class_argument("wikidata_id", WikidataId)
        .add_class_argument("subject", Subject)
    )

    @classmethod
    def from_value(cls, value: str) -> Self:
        return cls(None, title=value)


@dataclass
class Podcast(Object):
    """Episodic series of digital audio."""

    title: str | None = None
    """Title of the podcast."""

    language: Language | None = None
    """Language of the podcast."""

    wikidata_id: WikidataId | None = None
    """Wikidata entity identifier (`None` if unspecified)."""

    author: str | None = None
    """The main speaker of the podcast."""

    is_adapted: bool = False
    """Whether the podcast uses simplified language for educational purposes."""

    def __hash__(self) -> int:
        return super().__hash__()

    def to_string(self) -> str:
        return self.title

    @classmethod
    def from_value(cls, value: str) -> Self:
        return cls(None, title=value)

    arguments: ClassVar[Arguments] = (
        Arguments(["podcast"], "podcast")
        .add_argument("title")
        .add_class_argument("language", Language)
        .add_class_argument("wikidata_id", WikidataId)
    )


@dataclass
class Book(Object):
    """A book, a paper, or any other text or one of its translations."""

    title: str | None = None
    """Title in language of the text."""

    language: Language | None = None
    """Language of the text was read.

    The language of the book or its translation.
    """

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

    def __post_init__(self):
        assert self.volume is None or isinstance(self.volume, float)

    def __hash__(self) -> int:
        if self.title and self.author:
            return hash(self.title + "/" + self.author)
        elif self.title:
            return hash(self.title)

        return 0

    def to_string(self) -> str:
        if self.title:
            return self.title

        raise ChronicleValueException(f"Book `{self}` has no title.")

    @classmethod
    def from_value(cls, value: str) -> Self:
        return cls(None, title=value)

    arguments: ClassVar[Arguments] = (
        Arguments(["book"], "book")
        .add_argument("title", command_printer=str)
        .add_argument(
            "volume",
            patterns=[re.compile(r"(\d*)p")],
            extractors=[lambda groups: float(groups(1))],
        )
        .add_class_argument("language", Language)
        .add_class_argument("wikidata_id", WikidataId)
    )


@dataclass
class Audiobook(Object):
    """Audio version of the book."""

    book: Book | None = None
    """Text book that was read aloud."""

    language: Language | None = None
    """Language of the audiobook."""

    duration: timedelta | None = None
    """Duration of the audiobook."""

    reader: str | None = None
    """Name of the reader of the audiobook."""

    def to_string(self) -> str:
        return self.book.to_string()

    @classmethod
    def from_value(cls, value: str) -> Self:
        return cls(None, book=Book(None, title=value))

    def get_language(self) -> Language | None:
        if self.book and self.book.language:
            return self.book.language
        return self.language

    arguments: ClassVar[Arguments] = (
        Arguments(["audiobook"], "audiobook")
        .add_object_argument("book", Book)
        .add_class_argument("duration", Timedelta)
        .add_class_argument("language", Language)
        .add_argument("reader")
    )


class Objects:
    """Collection of event-related object collections."""

    def __init__(self, objects: dict[str, Object] | None = None) -> None:
        self.objects: dict[str, Object] = objects or {}
        """Objects indexed by their identifiers."""

        self.prefix_to_class: dict[str, type] = {}
        """Prefixes to classes."""

        classes: list = Objects.get_classes(Object)
        for class_ in classes:
            for prefix in class_.arguments.prefixes:
                if prefix in self.prefix_to_class:
                    raise ChronicleCodeException(
                        f"Prefix `{prefix}` in class `{class_.__name__}` is "
                        f"already used by `{self.prefix_to_class[prefix]}`."
                    )
                self.prefix_to_class[prefix] = class_

    @staticmethod
    def get_classes(class_: type) -> list:
        classes: list = [class_]
        if class_.__subclasses__():
            for subclass in class_.__subclasses__():
                classes += Objects.get_classes(subclass)
        return classes

    def get_object(self, object_id: str) -> Object:
        """Retrieve object by its identifier.

        :param object_id: identifier of the object with or without `@` prefix
        """
        if object_id.startswith("@"):
            object_id = object_id[1:]
        if object_id in self.objects:
            return self.objects[object_id]

        raise ChronicleObjectNotFoundException(object_id)

    def parse_command(self, command: str, tokens: list[str]) -> bool:
        prefix: str = tokens[0]
        id_: str = tokens[1]
        if id_.startswith("@"):
            id_ = id_[1:]

        if prefix in self.prefix_to_class:
            data = self.prefix_to_class[prefix].arguments.parse(
                tokens[3:], self
            )
            # Create new object.
            new_object = self.prefix_to_class[prefix](id_, **data)
            # Register new object.
            self.objects[id_] = new_object
            return True

        return False

    def get_commands(self) -> list[str]:
        commands: list[str] = []
        for id_, object_ in self.objects.items():
            commands.append(
                f"{object_.get_type()} {id_} = {object_.to_command()}"
            )
        return commands

    def fill_movie(self, object_: Video, cache_path: Path):
        object_data: dict = json.loads(
            get_data(
                cache_path / f"moving_image_{object_.title}@en.json",
                request_sparql,
                get_movie(object_.title),
            ).decode()
        )["results"]["bindings"]
        print(f"No Wikidata ID for movie {object_.title}.")
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
            items: list[WikidataItem] = list(set(items))
            for index, item in enumerate(items):
                text: str = item.labels["en"]["value"]
                for a in item.get_claim(Property.TITLE, cache_path):
                    text += " - " + a["text"]
                for a in item.get_claim(Property.START_TIME, cache_path):
                    text += " - " + a["time"][1:5]
                for a in item.get_claim(Property.DIRECTOR, cache_path):
                    text += " - " + (a.labels["en"]["value"])
                for a in item.get_claim(Property.GENRE, cache_path):
                    text += " - " + (a.labels["en"]["value"])
                for a in item.get_claim(
                    Property.ORIGINAL_BROADCASTER, cache_path
                ):
                    text += " - " + (a.labels["en"]["value"])
                for a in item.get_claim(Property.DISTRIBUTED_BY, cache_path):
                    text += " - " + (a.labels["en"]["value"])
                for a in item.get_claim(
                    Property.ORIGINAL_LANGUAGE_OF_FILM_OR_TV, cache_path
                ):
                    text += " - " + (a.labels["en"]["value"])
                print(f"    {index + 1}.", text)
            index = int(input()) - 1
            object_.wikidata_id = items[index].wikidata_id

    def fill(self, cache_path: Path):
        for object_ in self.objects.values():
            if isinstance(object_, Video):
                if object_.wikidata_id:
                    continue
                self.fill_movie(object_, cache_path)

    def has_object(self, id_: str) -> bool:
        return id_ in self.objects

    def set_object(self, id_, object_):
        self.objects[id_] = object_


@dataclass
class Project(Object):
    """Programming project."""

    title: str | None = None
    """Title of the project."""

    language: ProgrammingLanguage | None = None
    """Main programming language of the project."""

    arguments: ClassVar[Arguments] = (
        Arguments(["project"], "project")
        .add_argument("title")
        .add_class_argument("language", ProgrammingLanguage)
    )


@dataclass
class Ballet(Object):
    """Ballet performance."""

    title: str | None = None
    """Title of the ballet performance."""

    arguments: ClassVar[Arguments] = Arguments(
        ["ballet"], "ballet"
    ).add_argument("title")

    def __hash__(self) -> int:
        return hash(self.title)

    def to_string(self) -> str:
        return self.title or "Ballet"


@dataclass
class Concert(Object):
    """Concert."""

    title: str | None = None
    """Title of the concert."""

    artist: str | None = None
    """Artist that performed."""

    arguments: ClassVar[Arguments] = (
        Arguments(["concert"], "concert")
        .add_argument("title")
        .add_argument("artist", prefix="by")
    )

    def __hash__(self) -> int:
        return hash(f"{self.title}.{self.artist}")

    def to_string(self) -> str:
        title: str = self.title or "Concert"
        return f"{title} by {self.artist}"


@dataclass
class Opera(Object):
    """Opera performance."""

    title: str | None = None
    """Title of the opera performance."""

    arguments: ClassVar[Arguments] = Arguments(["opera"], "opera").add_argument(
        "title"
    )

    def __hash__(self) -> int:
        return hash(self.title)

    def to_string(self) -> str:
        return self.title or "Opera"
