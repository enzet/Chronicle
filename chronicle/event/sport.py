from datetime import timedelta

from chronicle.argument import Arguments
from chronicle.event.core import Event


class SportEvent(Event):
    """"""


class MoveEvent(SportEvent):
    duration: timedelta | None = None
    """Moving time."""

    distance: float | None = None
    """Distance in meters."""

    pace: timedelta | None = None

    kilocalories: float | None = None

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["run"], "run")
            .add_argument("duration")
            .add_argument("distance")
            .add_argument("pace")
            .add_argument("kilocalories")
        )


class RunEvent(MoveEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["run"], "run")


class WalkEvent(MoveEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["walk"], "walk")


class CountableSportEvent(SportEvent):
    count: int
    """The number of rounds."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["countable"], "countable").add_argument("count")


class SquatsEvent(CountableSportEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["squats"], "squats")


class ChinUpEvent(CountableSportEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["chin_up"], "chin_up")


class PushUpEvent(CountableSportEvent):
    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["push_up"], "push_up")
