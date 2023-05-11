import re

from chronicle.argument import Arguments
from chronicle.event.core import Event
from chronicle.event.value import Cost
from chronicle.objects import Objects
from chronicle.summary.core import Summary

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


class DoEvent(Event):
    description: str

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["do"], "do").add_argument("description")


class CookEvent(Event):
    dish: str

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["cook"], "cook").add_argument("dish")


class CleanEvent(Event):
    object_: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["clean", "wash"], "clean").add_argument("object_")


class CutEvent(Event):
    object_: str | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["cut"], "cut").add_argument("object_")


class DrinkEvent(Event):
    liquid: str
    amount: float
    """Amount of the liquid in litres."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["drink"], "drink")
            .add_argument("liquid")
            .add_argument(
                "amount",
                patterns=[re.compile("(\d*\.\d*)l"), re.compile("(\d*)ml")],
                extractors=[
                    lambda x: float(x(1)),
                    lambda x: float(x(1)) / 1000,
                ],
                command_printer=lambda x: f"{x}l",
            )
        )


class PayEvent(Event):
    cost: Cost
    goods: str

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["pay"], "pay")
            .add_argument("goods")
            .add_argument(
                "cost", command_printer=lambda x: f"{x.value}{x.currency}"
            )
        )


class ProgramEvent(Event):
    project: str | None = None

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
