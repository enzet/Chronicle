import re
from dataclasses import dataclass, field
from typing import ClassVar

from chronicle.argument import Arguments
from chronicle.event.core import Event
from chronicle.objects.core import Person, Place

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class PlaceEvent(Event):
    place: Place | None = None
    persons: list[Person] = field(default_factory=list)

    arguments: ClassVar[Arguments] = (
        Arguments(["place"], "place")
        .add_object_argument("place", Place)
        .add_argument(
            "persons",
            prefix="with",
            patterns=[re.compile(r"@[a-zA-Z0-9_]+(;@[a-zA-Z0-9_]+)*")],
            extractors=[
                lambda groups: [Person(x) for x in groups(0).split(";")]
            ],
        )
    )

    color: ClassVar[str] = "#CCCCCC"


@dataclass
class HomeEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["home"], "home"
    )
    color: ClassVar[str] = "#EEEEDD"


@dataclass
class HotelEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["hotel"], "hotel"
    )
    color: ClassVar[str] = "#EEEEDD"


@dataclass
class BarEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["bar"], "bar"
    )
    color: ClassVar[str] = "#008800"


@dataclass
class CafeEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["cafe"], "cafe"
    )
    color: ClassVar[str] = "#008800"


@dataclass
class CinemaEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["cinema"], "cinema"
    )
    color: ClassVar[str] = "#008800"


@dataclass
class PharmacyEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["pharmacy"], "pharmacy"
    )
    color: ClassVar[str] = "#FF8888"


@dataclass
class ClinicEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["clinic"], "clinic"
    )
    color: ClassVar[str] = "#FF8888"


@dataclass
class ClubEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["club"], "club"
    )
    color: ClassVar[str] = "#008800"


@dataclass
class TransportPlaceEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["transport"], "transport"
    )
    color: ClassVar[str] = "#000088"


@dataclass
class PortEvent(TransportPlaceEvent):
    arguments: ClassVar[Arguments] = TransportPlaceEvent.arguments.replace(
        ["port"], "port"
    )


@dataclass
class ShopEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["shop"], "shop"
    )
    color: ClassVar[str] = "#880088"


@dataclass
class UniversityEvent(PlaceEvent):
    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["university"], "university"
    )
    color: ClassVar[str] = "#CC0000"
