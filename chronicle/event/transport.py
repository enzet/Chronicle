import re
from dataclasses import dataclass, field
from typing import ClassVar

from chronicle.argument import Arguments
from chronicle.event.core import Event
from chronicle.objects.core import Person, Place, Service
from chronicle.value import Cost

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class TransportEvent(Event):
    """Moving by any means of transport."""

    places: list[Place] = field(default_factory=list)
    persons: list[Person] = field(default_factory=list)

    arguments: ClassVar[Arguments] = (
        Arguments(["transport"], "transport")
        .add_argument(
            "places",
            patterns=[re.compile(r"@[a-zA-Z0-9_]+(/@[a-zA-Z0-9_]+)+")],
            extractors=[
                lambda groups: [Place(x) for x in groups(0).split("/")]
            ],
        )
        .add_argument(
            "persons",
            prefix="with",
            patterns=[re.compile(r"@[a-zA-Z0-9_]+(;@[a-zA-Z0-9_]+)*")],
            extractors=[
                lambda groups: [Person(x) for x in groups(0).split(";")]
            ],
        )
    )
    color: ClassVar[str] = "#000088"


@dataclass
class BusEvent(TransportEvent):
    """Moving by bus."""

    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["bus"], "bus"
    )


@dataclass
class FlightEvent(TransportEvent):
    """Flying by airplane."""

    number: str | None = None

    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["flight"], "flight"
    ).add_argument("number", is_insert=True)


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

    arguments: ClassVar[Arguments] = TransportEvent.arguments.replace(
        ["train"], "train"
    )


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
