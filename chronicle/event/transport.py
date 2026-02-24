"""Comute events."""

import re
from dataclasses import dataclass, field
from typing import ClassVar

from chronicle.argument import Argument, Arguments
from chronicle.event.core import Event
from chronicle.objects.core import Person, Service
from chronicle.value import Cost

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class TransportEvent(Event):
    """Moving by any means of transport."""

    place_ids: list[str] = field(default_factory=list)
    """TODO: change to places."""

    persons: list[Person] = field(default_factory=list)

    is_transit: bool = False
    """Whether the middle and destination points were transit.

    This means that we want to count only the first point of `place_ids` as
    fully visited place.
    """

    arguments: ClassVar[Arguments] = (
        Arguments(["transport"], "transport")
        .add(
            Argument(
                "place_ids",
                patterns=[re.compile(r"@[a-zA-Z0-9_]+(/@[a-zA-Z0-9_]+)+")],
                extractors=[lambda groups: groups(0).split("/")],
            )
        )
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
        .add(
            Argument(
                "is_transit",
                patterns=[re.compile(r"(transit)")],
                extractors=[lambda groups: groups(0) == "transit"],
            )
        )
    )
    color: ClassVar[str] = "#000088"


@dataclass
class BusEvent(TransportEvent):
    """Moving by bus."""

    number: str | None = None

    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["bus"], "bus"
    ).add(Argument("number"), is_insert=True)


@dataclass
class CarEvent(TransportEvent):
    """Moving by car."""

    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["car"], "car"
    )


@dataclass
class CableCarEvent(TransportEvent):
    """Moving by cable car."""

    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["cable_car"], "cable_car"
    )


@dataclass
class FlightEvent(TransportEvent):
    """Flying by airplane."""

    number: str | None = None

    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["flight"], "flight"
    ).add(Argument("number"), is_insert=True)


@dataclass
class KickScooterEvent(TransportEvent):
    """Riding a kick scooter."""

    service: Service | None = None
    cost: Cost | None = None

    color: ClassVar[str] = "#008888"
    arguments: ClassVar[Arguments] = (
        TransportEvent.arguments.replace(["kick_scooter"], "kick_scooter")
        .add_class_argument("service", Service)
        .add_class_argument("cost", Cost)
    )


@dataclass
class TaxiEvent(TransportEvent):
    """Moving by taxi."""

    color: ClassVar[str] = "#888800"
    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["taxi"], "taxi"
    )


@dataclass
class TrainEvent(TransportEvent):
    """Traveling by train."""

    number: str | None = None
    """Train number or name."""

    carriage: str | None = None
    """Carriage number or name."""

    seat: str | None = None
    """Seat number."""

    arguments: ClassVar[Arguments] = (
        TransportEvent.arguments.replace(["train"], "train")
        .add(Argument("number"), is_insert=True)
        .add(
            Argument(
                "carriage",
                patterns=[re.compile(r"c([^ ]*)")],
                extractors=[lambda groups: groups(0)],
            )
        )
        .add(
            Argument(
                "seat",
                patterns=[re.compile(r"s([^ ]*)")],
                extractors=[lambda groups: groups(0)],
            )
        )
    )


@dataclass
class FerryEvent(TransportEvent):
    """Traveling by ferry."""

    number: str | None = None

    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["ferry"], "ferry"
    ).add(Argument("number"), is_insert=True)


@dataclass
class MetroEvent(TransportEvent):
    """Moving by metro."""

    from_: str | None = None
    to_: str | None = None
    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["metro"], "metro"
    )


@dataclass
class WaterTaxiEvent(TransportEvent):
    """Moving by water taxi."""

    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["water_taxi"], "water_taxi"
    )
