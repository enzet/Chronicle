from dataclasses import dataclass
from typing import ClassVar
import re

from chronicle.argument import Arguments
from chronicle.objects.core import Thing


@dataclass
class Clothes(Thing):
    art: str | None = None
    size: str | None = None

    arguments: ClassVar[Arguments] = (
        Thing.arguments.replace(["clothes"], "clothes")
        .add_argument("art", prefix="art:")
        .add_argument("size", patterns=[re.compile(r"^(X+S|S|M|L|X+L)$")])
    )


@dataclass
class Coat(Clothes):
    """An outer garment worn over other clothes."""

    color: str
    size: str

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(["coat"], "coat")


@dataclass
class Hat(Clothes):
    """Any type of clothing worn on the head."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(["hat"], "hat")


@dataclass
class Jacket(Clothes):
    """A jacket is a light jacket worn over other clothes."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["jacket"], "jacket"
    )


@dataclass
class Pants(Clothes):
    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["pants"], "pants"
    )


@dataclass
class Shoes(Clothes):
    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["shoes"], "shoes"
    )


@dataclass
class Socks(Clothes):
    """A pair of socks worn on the feet."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["socks"], "socks"
    )


@dataclass
class Sweater(Clothes):
    """A warm, knitted garment worn on the body."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["sweater"], "sweater"
    )


@dataclass
class TShirt(Clothes):
    """A short-sleeved shirt."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["t_shirt"], "t_shirt"
    )


@dataclass
class Underpants(Clothes):
    """Underwear worn on the body."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["underpants"], "underpants"
    )


@dataclass
class Belt(Clothes):
    """A strip of material worn around the waist."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(["belt"], "belt")
