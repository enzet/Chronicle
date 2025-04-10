"""Clothes objects."""

import re
from dataclasses import dataclass
from typing import ClassVar

from chronicle.argument import Argument, Arguments
from chronicle.objects.core import Thing


@dataclass
class Clothes(Thing):
    """Clothes."""

    art: str | None = None
    """Article number."""

    size: str | None = None
    """Size."""

    arguments: ClassVar[Arguments] = (
        Thing.arguments.replace(["clothes"], "clothes")
        .add(Argument("art", prefix="art:"))
        .add(Argument("size", patterns=[re.compile(r"^(X+S|S|M|L|X+L)$")]))
    )


@dataclass
class Coat(Clothes):
    """An outer garment worn over other clothes."""

    color: str | None = None
    """Color of the coat."""

    size: str | None = None
    """Size of the coat."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(["coat"], "coat")


@dataclass
class Hat(Clothes):
    """Any type of clothing worn on the head."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(["hat"], "hat")


@dataclass
class Jacket(Clothes):
    """Jacket, a light jacket worn over other clothes."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["jacket"], "jacket"
    )


@dataclass
class Pants(Clothes):
    """Pants, a type of clothing worn on the lower body."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["pants"], "pants"
    )


@dataclass
class Shoes(Clothes):
    """Shoes, a type of footwear worn on the feet."""

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
    """Sweater, a warm, knitted garment worn on the body."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["sweater"], "sweater"
    )


@dataclass
class TShirt(Clothes):
    """T-shirt, a short-sleeved shirt."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["t_shirt"], "t_shirt"
    )


@dataclass
class Underpants(Clothes):
    """Underpants, underwear worn on the body."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(
        ["underpants"], "underpants"
    )


@dataclass
class Belt(Clothes):
    """Belt, a strip of material worn around the waist."""

    arguments: ClassVar[Arguments] = Clothes.arguments.replace(["belt"], "belt")
