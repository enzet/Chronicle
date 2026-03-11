"""Tests for objects."""

import pytest

from chronicle.errors import (
    ChronicleObjectNotFoundError,
    ChronicleUnknownTypeError,
)
from chronicle.objects.clothes import Clothes, Coat, Shoes
from chronicle.objects.core import (
    Airport,
    ArtObject,
    Audiobook,
    Ballet,
    Book,
    City,
    Concert,
    Country,
    Mountain,
    Object,
    Objects,
    Opera,
    Person,
    Place,
    Podcast,
    Project,
    Service,
    Standup,
    Thing,
    Video,
    camel_to_snake,
)
from chronicle.timeline import CommandParser, Timeline
from chronicle.value import Language, ProgrammingLanguage

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def parse(commands: str) -> Timeline:
    """Parse commands and return timeline."""
    parser: CommandParser = CommandParser()
    for command in commands.split("\n"):
        parser.parse_command(command)
    return parser.timeline


# `camel_to_snake`.


def test_camel_to_snake_simple() -> None:
    """`camel_to_snake` converts a simple CamelCase name."""
    assert camel_to_snake("Book") == "book"


def test_camel_to_snake_two_words() -> None:
    """`camel_to_snake` converts a two-word CamelCase name."""
    assert camel_to_snake("BookObject") == "book_object"


def test_camel_to_snake_three_words() -> None:
    """`camel_to_snake` converts a three-word CamelCase name."""
    assert camel_to_snake("ArtObject") == "art_object"


# Objects collection.


def test_objects_empty() -> None:
    """`Objects` starts with no objects."""
    objects: Objects = Objects()
    assert objects.objects == {}


def test_objects_get_existing() -> None:
    """`get_object` returns an existing object by id."""
    book = Book("idiot", title="Idiot")
    objects: Objects = Objects({"idiot": book})
    assert objects.get_object("idiot") is book


def test_objects_get_with_at_prefix() -> None:
    """`get_object` strips the `@` prefix from the id."""
    book = Book("idiot", title="Idiot")
    objects: Objects = Objects({"idiot": book})
    assert objects.get_object("@idiot") is book


def test_objects_get_missing_raises() -> None:
    """`get_object` raises `ChronicleObjectNotFoundError` for unknown id."""
    objects: Objects = Objects()
    with pytest.raises(ChronicleObjectNotFoundError):
        objects.get_object("missing")


def test_objects_get_with_default() -> None:
    """`get_object` stores and returns a default when object is missing."""
    book = Book("new", title="New Book")
    objects: Objects = Objects()
    result = objects.get_object("new", default=book)
    assert result is book
    assert objects.has_object("new")


def test_objects_has_object_true() -> None:
    """`has_object` returns True for an existing object."""
    objects: Objects = Objects({"x": Book("x")})
    assert objects.has_object("x")


def test_objects_has_object_false() -> None:
    """`has_object` returns False for a missing object."""
    objects: Objects = Objects()
    assert not objects.has_object("x")


def test_objects_set_object() -> None:
    """`set_object` adds a new object to the collection."""
    objects: Objects = Objects()
    book = Book("b", title="B")
    objects.set_object("b", book)
    assert objects.get_object("b") is book


def test_objects_parse_command_book() -> None:
    """`parse_command` registers a Book from a declaration command."""
    objects: Objects = Objects()
    command = "book @idiot = Idiot .ru"
    tokens = command.split()
    objects.parse_command(command, tokens)
    assert objects.has_object("idiot")
    assert isinstance(objects.get_object("idiot"), Book)
    assert objects.get_object("idiot").title == "Idiot"


def test_objects_parse_command_unknown_prefix_raises() -> None:
    """`parse_command` raises for an unknown prefix."""
    objects: Objects = Objects()
    with pytest.raises(ChronicleUnknownTypeError):
        objects.parse_command("unknown @x = foo", ["unknown", "@x", "=", "foo"])


def test_objects_get_classes() -> None:
    """`get_classes` returns a list that includes `Object` and subclasses."""
    classes = Objects.get_classes(Object)
    assert Object in classes
    assert Book in classes
    assert Place in classes
    assert Thing in classes


# `Object.get_type`.


def test_object_get_type_book() -> None:
    """`get_type` returns the correct type string for `Book`."""
    assert Book("b").get_type() == "book"


def test_object_get_type_art_object() -> None:
    """`get_type` returns the correct type string for `ArtObject`."""
    assert ArtObject("a").get_type() == "art_object"


def test_object_get_type_video() -> None:
    """`get_type` returns the correct type string for `Video`."""
    assert Video("v").get_type() == "video"


# `Object.__hash__`.


def test_object_hash_uses_id() -> None:
    """Two objects with the same id have the same hash."""
    assert hash(Object("abc")) == hash(Object("abc"))


def test_object_hash_different_ids() -> None:
    """Two objects with different ids have different hashes."""
    assert hash(Object("a")) != hash(Object("b"))


# Book.


def test_book_to_string_with_title() -> None:
    """`to_string` returns the book title."""
    assert Book("b", title="Idiot").to_string() == "Idiot"


def test_book_to_string_without_title() -> None:
    """`to_string` returns a placeholder when title is None."""
    assert Book("b").to_string() == "(Unknown book)"


def test_book_hash_with_title_and_author() -> None:
    """`__hash__` uses title + author when both are set."""
    b1 = Book("x", title="Idiot", author="Dostoevsky")
    b2 = Book("y", title="Idiot", author="Dostoevsky")
    assert hash(b1) == hash(b2)


def test_book_hash_title_only() -> None:
    """`__hash__` uses title only when author is missing."""
    b1 = Book("x", title="Idiot")
    b2 = Book("y", title="Idiot")
    assert hash(b1) == hash(b2)


def test_book_from_value() -> None:
    """`from_value` creates a Book with the given title."""
    book = Book.from_value("Idiot")
    assert book.title == "Idiot"


def test_book_volume_is_float() -> None:
    """`__post_init__` asserts that volume is float when set."""
    book = Book("b", volume=300.0)
    assert book.volume == 300.0  # noqa: PLR2004


# Audiobook.


def test_audiobook_to_string_with_book() -> None:
    """`to_string` returns the book title from the embedded book."""
    book = Book("b", title="Idiot")
    audio = Audiobook("a", book=book)
    assert audio.to_string() == "Idiot"


def test_audiobook_to_string_without_book() -> None:
    """`to_string` returns 'Audiobook' when book is None."""
    assert Audiobook("a").to_string() == "Audiobook"


def test_audiobook_from_value() -> None:
    """`from_value` creates an Audiobook whose embedded book has the title."""
    audio = Audiobook.from_value("Idiot")
    assert audio.book is not None
    assert audio.book.title == "Idiot"


def test_audiobook_get_language_from_book() -> None:
    """`get_language` returns the language from the embedded book."""
    book = Book("b", language=Language("ru"))
    audio = Audiobook("a", book=book)
    assert audio.get_language() == Language("ru")


def test_audiobook_get_language_own() -> None:
    """`get_language` falls back to own language when book has none."""
    book = Book("b")
    audio = Audiobook("a", book=book, language=Language("en"))
    assert audio.get_language() == Language("en")


def test_audiobook_get_language_none() -> None:
    """`get_language` returns None when neither the book nor language is set."""
    assert Audiobook("a").get_language() is None


# Video


def test_video_from_value() -> None:
    """`from_value` creates a Video with id and title equal to the value."""
    v = Video.from_value("Elite")
    assert v.id == "Elite"
    assert v.title == "Elite"


def test_video_hash() -> None:
    """Two `Video` objects should have equal hashes."""
    v1 = Video("v1", title="Elite", language=Language("es"), wikidata_id=0)
    v2 = Video("v2", title="Elite", language=Language("es"), wikidata_id=0)
    assert hash(v1) == hash(v2)


# Person.


def test_person_from_value() -> None:
    """`from_value` creates a Person with the given name."""
    p = Person.from_value("Alice")
    assert p.name == "Alice"


# Service.


def test_service_from_value() -> None:
    """`from_value` creates a Service with the given name."""
    s = Service.from_value("Duolingo")
    assert s.name == "Duolingo"


# Podcast.


def test_podcast_to_string_with_title() -> None:
    """`to_string` returns the podcast title."""
    assert Podcast("p", title="Inner French").to_string() == "Inner French"


def test_podcast_to_string_without_title() -> None:
    """`to_string` returns 'Podcast' when title is None."""
    assert Podcast("p").to_string() == "Podcast"


def test_podcast_from_value() -> None:
    """`from_value` creates a Podcast with the given title."""
    p = Podcast.from_value("Inner French")
    assert p.title == "Inner French"


# Ballet / Opera / Concert / Standup.


def test_ballet_to_string() -> None:
    """`to_string` returns the ballet title."""
    assert Ballet("b", title="Swan Lake").to_string() == "Swan Lake"


def test_ballet_to_string_no_title() -> None:
    """`to_string` returns 'Ballet' when title is None."""
    assert Ballet("b").to_string() == "Ballet"


def test_opera_to_string() -> None:
    """`to_string` returns the opera title."""
    assert Opera("o", title="Carmen").to_string() == "Carmen"


def test_concert_to_string() -> None:
    """`to_string` includes title and artist."""
    c = Concert("c", title="World Tour", artist="The Beatles")
    assert c.to_string() == "World Tour by The Beatles"


def test_standup_to_string() -> None:
    """`to_string` includes title and artist."""
    s = Standup("s", title="Live", artist="Dave Chappelle")
    assert s.to_string() == "Live by Dave Chappelle"


# Project.


def test_project_parse() -> None:
    """Parsing a project declaration registers it in the timeline."""
    timeline = parse("project @linux = Linux .c")
    objects = timeline.objects.objects
    assert isinstance(objects["linux"], Project)
    assert objects["linux"].title == "Linux"
    assert objects["linux"].language == ProgrammingLanguage("c")


# Place subclasses.


def test_city_parse() -> None:
    """Parsing a city declaration registers it with a country reference."""
    timeline = parse("country @fr = France\ncity @paris = Paris in @fr")
    objects = timeline.objects.objects
    assert isinstance(objects["paris"], City)
    assert objects["paris"].name == "Paris"
    assert isinstance(objects["paris"].country, Country)
    assert objects["paris"].country.name == "France"


def test_mountain_parse() -> None:
    """Parsing a mountain declaration captures height."""
    timeline = parse("mountain @everest = Everest 8849m")
    objects = timeline.objects.objects
    assert isinstance(objects["everest"], Mountain)
    assert objects["everest"].name == "Everest"
    assert objects["everest"].height == 8849.0  # noqa: PLR2004


def test_airport_parse() -> None:
    """Parsing an airport declaration registers it."""
    timeline = parse("airport @cdg = CDG")
    objects = timeline.objects.objects
    assert isinstance(objects["cdg"], Airport)


# Clothes.


def test_clothes_parse_with_size() -> None:
    """Parsing a clothes declaration captures size."""
    timeline = parse("clothes @shirt = My Shirt M")
    objects = timeline.objects.objects
    assert isinstance(objects["shirt"], Clothes)
    assert objects["shirt"].name == "My Shirt"
    assert objects["shirt"].size == "M"


def test_clothes_parse_with_art() -> None:
    """Parsing a clothes declaration captures article number."""
    timeline = parse("coat @coat1 = Winter Coat art: ABC123")
    objects = timeline.objects.objects
    assert isinstance(objects["coat1"], Coat)
    assert objects["coat1"].art == "ABC123"


def test_shoes_parse() -> None:
    """Parsing a shoes declaration registers a Shoes object."""
    timeline = parse("shoes @nikes = Nike Air L")
    objects = timeline.objects.objects
    assert isinstance(objects["nikes"], Shoes)
    assert objects["nikes"].size == "L"


# `get_commands` round-trip.


def test_get_commands_book() -> None:
    """`get_commands` produces a reconstructable command for a Book."""
    timeline = parse("book idiot = Idiot 600.0p .ru")
    commands = timeline.objects.get_commands()
    assert len(commands) == 1
    assert "idiot" in commands[0]
    assert "Idiot" in commands[0]
