"""Events related to sports and physical activity."""

from dataclasses import dataclass

from chronicle.argument import Arguments
from chronicle.event.core import Event
from chronicle.value import Distance, Kilocalories
from chronicle.time import Timedelta
from chronicle.summary.core import Summary

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class SportEvent(Event):
    """Event representing a sport."""

    def get_color(self) -> str:
        return "#008800"


@dataclass
class MoveEvent(SportEvent):
    """Event representing a moving activity."""

    duration: Timedelta | None = None
    """Moving time."""

    distance: float | None = None
    """Distance in meters."""

    pace: Timedelta | None = None
    """Pace in seconds per kilometer."""

    kilocalories: float | None = None
    """Kilocalories burned."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            Arguments(["move"], "move")
            .add_argument("duration", Timedelta)
            .add_class_argument("distance", Distance)
            .add_argument("pace", Timedelta)
            .add_argument("kilocalories", Kilocalories)
        )


@dataclass
class RunEvent(MoveEvent):
    """Event representing running."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["run"], "run")

    def get_color(self) -> str:
        return "#FF8800"


@dataclass
class HikeEvent(MoveEvent):
    """Event representing hiking."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["hike"], "hike")

    def get_color(self) -> str:
        return "#FF8800"


@dataclass
class LongboardEvent(MoveEvent):
    """Event representing longboarding."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["longboard"], "longboard")

    def get_color(self) -> str:
        return "#FF8800"


@dataclass
class WalkEvent(MoveEvent):
    """Event representing walking."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["walk"], "walk")

    def get_color(self) -> str:
        return "#CCCCCC"


@dataclass
class WarmUpEvent(SportEvent):
    """Event representing warming up."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["warm_up"], "warm_up")


@dataclass
class StretchEvent(SportEvent):
    """Event representing stretching."""

    pass


@dataclass
class CyclingEvent(SportEvent):
    """Event representing cycling."""

    pass


@dataclass
class KickScooterEvent(SportEvent):
    """Event representing using a kick scooter."""

    service: str | None = None
    """Service used to rent the kick scooter."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["kick_scooter"], "kick_scooter").add_argument(
            "service", prefix="using"
        )


@dataclass
class PlankEvent(SportEvent):
    """Event representing planking."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["plank"], "plank")


@dataclass
class HighPlankEvent(SportEvent):
    """Event representing high plank."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["high_plank"], "high_plank")


@dataclass
class HighKneeEvent(SportEvent):
    """Event representing high knees."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["high_knee"], "high_knee")


@dataclass
class CountableSportEvent(SportEvent):
    count: int | None = None
    """The number of rounds."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            super()
            .get_arguments()
            .replace(["countable"], "countable")
            .add_argument(
                "count", loader=lambda value, _: int(value), is_insert=True
            )
        )

    def register_summary(self, summary: Summary) -> None:
        name: str = self.get_arguments().command
        if name == "abs":
            name = "abs_"
        if self.count is not None:
            setattr(summary, name, getattr(summary, name) + self.count)


@dataclass
class AbsEvent(CountableSportEvent):
    """Event representing abs exercises."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["abs"], "abs")


@dataclass
class SquatsEvent(CountableSportEvent):
    """Event representing squats."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["squats"], "squats")


@dataclass
class ChinUpsEvent(CountableSportEvent):
    """Event representing chin ups."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["chin_ups"], "chin_ups")


@dataclass
class SquatJumpsEvent(CountableSportEvent):
    """Event representing squat jumps."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["squat_jumps"], "squat_jumps")


@dataclass
class DipsEvent(CountableSportEvent):
    """Event representing dips."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["dips"], "dips")


@dataclass
class PushUpsEvent(CountableSportEvent):
    """Event representing push ups."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["push_ups"], "push_ups")


@dataclass
class JumpingJacksEvent(CountableSportEvent):
    """Event representing jumping jacks."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            super().get_arguments().replace(["jumping_jacks"], "jumping_jacks")
        )


@dataclass
class HandGripsEvent(CountableSportEvent):
    """Event representing hand grips."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["hand_grips"], "hand_grips")


@dataclass
class BurpeeEvent(CountableSportEvent):
    """Event representing burpees."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return super().get_arguments().replace(["burpee"], "burpee")


@dataclass
class RussianTwistsEvent(CountableSportEvent):
    """Event representing russian twists."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            super()
            .get_arguments()
            .replace(["russian_twists"], "russian_twists")
        )
