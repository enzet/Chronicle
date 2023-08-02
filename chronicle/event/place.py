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



@dataclass
class HomeEvent(PlaceEvent):
    pass



@dataclass
class CafeEvent(PlaceEvent):
    pass


@dataclass
class CinemaEvent(PlaceEvent):
    pass



@dataclass
class ClubEvent(PlaceEvent):
    pass



@dataclass
class PortEvent(TransportPlaceEvent):
    pass


@dataclass
class ShopEvent(PlaceEvent):
    pass


@dataclass
class UniversityEvent(PlaceEvent):
    pass
