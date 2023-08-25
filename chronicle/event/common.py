import logging
import re
from dataclasses import dataclass

from chronicle.argument import Arguments
from chronicle.event.core import Event
from chronicle.event.value import Cost
from chronicle.objects import Objects
from chronicle.summary.core import Summary


__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class DoEvent(Event):
    description: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["do"], "do").add_argument("description")


@dataclass
class MedicationEvent(Event):
    medication: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["medication"], "medication").add_argument(
            "medication"
        )


@dataclass
class AppointmentEvent(Event):
    pass


@dataclass
class CookEvent(Event):
    dish: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["cook"], "cook").add_argument("dish")

    def register_summary(self, summary: Summary, objects: Objects):
        summary.register_dish(self.dish)


@dataclass
class CleanEvent(Event):
    object_: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["clean", "wash"], "clean").add_argument("object_")


@dataclass
class CutEvent(Event):
    object_: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["cut"], "cut").add_argument("object_")


@dataclass
class CallEvent(Event):
    video: str | None = None
    """`camera` or `screen`"""


@dataclass
class EatEvent(Event):
    meal: str | None = None
    kilocalories: float | None = None


@dataclass
class LearnEvent(Event):
    subject: str | None = None
    service: str | None = None


@dataclass
class WriteEvent(Event):
    pass


@dataclass
class ReviewEvent(Event):
    pass


@dataclass
class BedEvent(Event):
    pass


@dataclass
class PlayEvent(Event):
    game: str | None = None


@dataclass
class DiscussEvent(Event):
    pass


@dataclass
class IronEvent(Event):
    pass


@dataclass
class ResearchEvent(Event):
    pass


@dataclass
class VoteEvent(Event):
    pass


@dataclass
class SiteDefectsEvent(Event):
    pass


@dataclass
class VomitEvent(Event):
    pass


@dataclass
class DrawEvent(Event):
    tool: str | None = None


@dataclass
class PainEvent(Event):
    pass


@dataclass
class ShaveEvent(Event):
    object: str | None = None


@dataclass
class DrinkEvent(Event):
    liquid: str | None = None
    amount: float | None = None
    """Amount of the liquid in litres."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["drink"], "drink")
            .add_argument("liquid")
            .add_argument(
                "amount",
                patterns=[re.compile(r"(\d*\.\d*)l"), re.compile(r"(\d*)ml")],
                extractors=[
                    lambda x: float(x(1)),
                    lambda x: float(x(1)) / 1000,
                ],
                command_printer=lambda x: f"{x}l",
            )
        )


@dataclass
class StatusEvent(Event):
    weight: float | None = None
    """Body weight in kilograms."""

    temperature: float | None = None
    """Body temperature in Celsius."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["_"], "_")
            .add_argument("weight")
            .add_argument("temperature")
        )


@dataclass
class PayEvent(Event):
    goods: str | None = None
    cost: Cost | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["pay"], "pay")
            .add_argument("goods")
            .add_argument(
                "cost", command_printer=lambda x: f"{x.value}{x.currency}"
            )
        )



@dataclass
class ProgramEvent(Event):
    project: str | None = None
    language: str | None = None
    task: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["program"], "program").add_argument(
            "project", command_printer=str
        )


class SleepEvent(Event):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["sleep"], "sleep")

    def register_summary(self, summary: Summary, objects: Objects):
        summary.register_sleep(self.time.get_duration())
