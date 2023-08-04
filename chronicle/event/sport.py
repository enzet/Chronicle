from dataclasses import dataclass

from chronicle.argument import Arguments
from chronicle.event.core import Event
from chronicle.time import Timedelta
from chronicle.objects import Objects
from chronicle.summary.core import Summary


@dataclass
class SportEvent(Event):
    """"""


@dataclass
class MoveEvent(SportEvent):
    duration: Timedelta | None = None
    """Moving time."""

    distance: float | None = None
    """Distance in meters."""

    pace: Timedelta | None = None

    kilocalories: float | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["move"], "move")
            .add_argument("duration")
            .add_argument("distance")
            .add_argument("pace")
            .add_argument("kilocalories")
        )


@dataclass
class RunEvent(MoveEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["run"], "run")



@dataclass
class WalkEvent(MoveEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["walk"], "walk")


@dataclass
class CountableSportEvent(SportEvent):
    count: int | None = None
    """The number of rounds."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["countable"], "countable").add_argument("count")


@dataclass
class SquatsEvent(CountableSportEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["squats"], "squats")


@dataclass
class ChinUpEvent(CountableSportEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["chin_up"], "chin_up")


@dataclass
class RussianTwists(CountableSportEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            super()
            .get_arguments()
            .replace(["russian_twists"], "russian_twists")
        )
