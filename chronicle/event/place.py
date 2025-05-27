"""Events representing being at some place."""

import re
from dataclasses import dataclass, field
from typing import ClassVar

from chronicle.argument import Argument, Arguments
from chronicle.event.core import Event
from chronicle.objects.core import Person, Place

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class PlaceEvent(Event):
    """Event representing being at some place."""

    place: Place | None = None
    """Place where the event is occurred."""

    persons: list[Person] = field(default_factory=list)
    """Persons who the person was with."""

    arguments: ClassVar[Arguments] = (
        Arguments(["place"], "place")
        .add_object_argument("place", Place)
        .add(
            Argument(
                "persons",
                prefix="with",
                patterns=[re.compile(r"@[a-zA-Z0-9_]+(;@[a-zA-Z0-9_]+)*")],
                extractors=[
                    lambda groups: [Person(x) for x in groups(0).split(";")]
                ],
            )
        )
    )
    color: ClassVar[str] = "#CCCCCC"


@dataclass
class HomeEvent(PlaceEvent):
    """Event representing being at home."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["home"], "home"
    )
    color: ClassVar[str] = "#EEEEDD"


@dataclass
class HotelEvent(PlaceEvent):
    """Event representing being at a hotel."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["hotel"], "hotel"
    )
    color: ClassVar[str] = "#EEEEDD"


@dataclass
class BarEvent(PlaceEvent):
    """Event representing being at a bar."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["bar"], "bar"
    )
    color: ClassVar[str] = "#008800"


@dataclass
class CafeEvent(PlaceEvent):
    """Event representing being at a cafe."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["cafe"], "cafe"
    )
    color: ClassVar[str] = "#008800"


@dataclass
class CinemaEvent(PlaceEvent):
    """Event representing being at a cinema."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["cinema"], "cinema"
    )
    color: ClassVar[str] = "#008800"


@dataclass
class PharmacyEvent(PlaceEvent):
    """Event representing being at a pharmacy."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["pharmacy"], "pharmacy"
    )
    color: ClassVar[str] = "#FF8888"


@dataclass
class ClinicEvent(PlaceEvent):
    """Event representing being at a clinic."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["clinic"], "clinic"
    )
    color: ClassVar[str] = "#FF8888"


@dataclass
class ClubEvent(PlaceEvent):
    """Event representing being at a club."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["club"], "club"
    )
    color: ClassVar[str] = "#008800"


@dataclass
class TransportPlaceEvent(PlaceEvent):
    """Event representing being at a transport place."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["transport"], "transport"
    )
    color: ClassVar[str] = "#000088"


@dataclass
class PortEvent(TransportPlaceEvent):
    """Event representing being at a port."""

    arguments: ClassVar[Arguments] = TransportPlaceEvent.arguments.replace(
        ["port"], "port"
    )


@dataclass
class ShopEvent(PlaceEvent):
    """Event representing being at a shop."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["shop"], "shop"
    )
    color: ClassVar[str] = "#880088"


@dataclass
class UniversityEvent(PlaceEvent):
    """Event representing being at a university."""

    arguments: ClassVar[Arguments] = PlaceEvent.arguments.replace(
        ["university"], "university"
    )
    color: ClassVar[str] = "#CC0000"
