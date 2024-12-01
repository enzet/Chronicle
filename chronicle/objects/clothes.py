from dataclasses import dataclass
import re

from chronicle.argument import Arguments
from chronicle.objects.core import Thing


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
            .add_argument("size", patterns=[re.compile(r"^(X+S|S|M|L|X+L)$")])
        )


@dataclass
class Coat(Clothes):
    """An outer garment worn over other clothes."""

    color: str
    size: str


@dataclass
class Hat(Clothes):
    """Any type of clothing worn on the head."""


@dataclass
class Jacket(Clothes):
    pass


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
