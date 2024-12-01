from dataclasses import dataclass

from chronicle.argument import Arguments
from chronicle.event.core import Event

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class TransportEvent(Event):
    start_place_id: str | None = None
    end_place_id: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        name = cls.__name__[:-5].lower()
        return Arguments([name], name).add_argument(
            "start_place_id", command_printer=str
        )

    def get_color(self) -> str:
        return "#000088"


@dataclass
class BusEvent(TransportEvent):
    pass


@dataclass
class FlightEvent(TransportEvent):
    pass


@dataclass
class KickScooterEvent(TransportEvent):
    def get_color(self) -> str:
        return "#008888"


@dataclass
class TaxiEvent(TransportEvent):
    def get_color(self) -> str:
        return "#888800"


@dataclass
class TrainEvent(TransportEvent):
    pass


@dataclass
class MetroEvent(TransportEvent):
    from_: str | None = None
    to_: str | None = None


@dataclass
class WaterTaxiEvent(TransportEvent):
    pass
