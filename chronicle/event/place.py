from dataclasses import dataclass

from chronicle.argument import Arguments
from chronicle.event.core import Event

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class PlaceEvent(Event):
    place_id: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        name = cls.__name__[:-5].lower()
        return Arguments([name], name).add_argument("place_id")

    def get_color(self) -> str:
        return "#CCCCCC"


@dataclass
class HomeEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#EEEEDD"


@dataclass
class HotelEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#EEEEDD"


@dataclass
class BarEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#008800"


@dataclass
class CafeEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#008800"


@dataclass
class CinemaEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#008800"


@dataclass
class PharmacyEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#FF8888"


@dataclass
class ClinicEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#FF8888"


@dataclass
class ClubEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#008800"


@dataclass
class TransportPlaceEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#000088"


@dataclass
class PortEvent(TransportPlaceEvent):
    pass


@dataclass
class ShopEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#880088"


@dataclass
class UniversityEvent(PlaceEvent):
    def get_color(self) -> str:
        return "#CC0000"
