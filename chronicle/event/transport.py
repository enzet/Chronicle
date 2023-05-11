from chronicle.argument import Arguments
from chronicle.event.core import Event

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


class TransportEvent(Event):
    start_place_id: str | None = None
    end_place_id: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        name = cls.__name__[:-5].lower()
        return Arguments([name], name).add_argument(
            "start_place_id", command_printer=str
        )


class TaxiEvent(TransportEvent):
    pass


class MetroEvent(TransportEvent):
    pass


class WaterTaxiEvent(TransportEvent):
    pass
