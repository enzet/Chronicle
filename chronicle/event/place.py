from chronicle.argument import Arguments
from chronicle.event.core import Event

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


class PlaceEvent(Event):
    place_id: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        name = cls.__name__[:-5].lower()
        return Arguments([name], name).add_argument("place_id")


class HomeEvent(PlaceEvent):
    pass


class CafeEvent(PlaceEvent):
    pass


class CinemaEvent(PlaceEvent):
    pass


class ClubEvent(PlaceEvent):
    pass


class PortEvent(PlaceEvent):
    pass


class ShopEvent(PlaceEvent):
    pass


class UniversityEvent(PlaceEvent):
    pass
