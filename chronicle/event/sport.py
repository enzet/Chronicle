"""Events related to sports and physical activity."""

from dataclasses import dataclass
from typing import ClassVar, override

from chronicle.argument import Argument, Arguments
from chronicle.event.core import Event
from chronicle.summary.core import Summary
from chronicle.time import Timedelta
from chronicle.value import Distance, Integers, Kilocalories, Weights

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

    arguments: ClassVar[Arguments] = (
        Arguments(["move"], "move")
        .add_class_argument("duration", Timedelta)
        .add_class_argument("distance", Distance)
        .add_class_argument("pace", Timedelta)
        .add_class_argument("kilocalories", Kilocalories)
    )


@dataclass
class RunEvent(MoveEvent):
    """Event representing running."""

    arguments: ClassVar[Arguments] = MoveEvent.arguments.replace(["run"], "run")

    color: ClassVar[str] = "#FF8800"


@dataclass
class HikeEvent(MoveEvent):
    """Event representing hiking."""

    arguments: ClassVar[Arguments] = MoveEvent.arguments.replace(
        ["hike"], "hike"
    )
    color: ClassVar[str] = "#FF8800"


@dataclass
class LongboardEvent(MoveEvent):
    """Event representing longboarding."""

    arguments: ClassVar[Arguments] = MoveEvent.arguments.replace(
        ["longboard"], "longboard"
    )
    color: ClassVar[str] = "#FF8800"


@dataclass
class WalkEvent(MoveEvent):
    """Event representing walking."""

    arguments: ClassVar[Arguments] = MoveEvent.arguments.replace(
        ["walk"], "walk"
    )
    color: ClassVar[str] = "#CCCCCC"


@dataclass
class WarmUpEvent(SportEvent):
    """Event representing warming up."""

    arguments: ClassVar[Arguments] = SportEvent.arguments.replace(
        ["warm_up"], "warm_up"
    )


@dataclass
class StretchEvent(SportEvent):
    """Event representing stretching."""


@dataclass
class CyclingEvent(SportEvent):
    """Event representing cycling."""


@dataclass
class KickScooterEvent(SportEvent):
    """Event representing using a kick scooter."""

    service: str | None = None
    """Service used to rent the kick scooter."""

    arguments: ClassVar[Arguments] = Arguments(
        ["kick_scooter"], "kick_scooter"
    ).add(Argument("service", prefix="using"))


@dataclass
class PlankEvent(SportEvent):
    """Event representing planking."""

    arguments: ClassVar[Arguments] = SportEvent.arguments.replace(
        ["plank"], "plank"
    )


@dataclass
class HighPlankEvent(SportEvent):
    """Event representing high plank."""

    arguments: ClassVar[Arguments] = SportEvent.arguments.replace(
        ["high_plank"], "high_plank"
    )


@dataclass
class HighKneeEvent(SportEvent):
    """Event representing high knees."""

    arguments: ClassVar[Arguments] = SportEvent.arguments.replace(
        ["high_knee"], "high_knee"
    )


@dataclass
class CountableSportEvent(SportEvent):
    """Event representing a countable sport activity.

    Kind of activity one can count times of.
    """

    count: int | None = None
    """The number of rounds."""

    arguments: ClassVar[Arguments] = SportEvent.arguments.replace(
        ["countable"], "countable"
    ).add(Argument("count", loader=lambda value, _: int(value)), is_insert=True)

    @override
    def register_summary(self, summary: Summary) -> None:
        name: str = self.arguments.command
        if name == "abs":
            name = "abs_"
        if self.count is not None:
            setattr(summary, name, getattr(summary, name) + self.count)


@dataclass
class ExerciseEvent(CountableSportEvent):
    """Event representing an exercise."""

    repetitions: list[int] | None = None
    """The number of repetitions of each set."""

    weights: list[float] | None = None
    """The weights used for each set."""

    arguments: ClassVar[Arguments] = (
        CountableSportEvent.arguments.replace(["exercise"], "exercise")
        .add_class_argument("repetitions", Integers)
        .add_class_argument("weights", Weights)
    )


@dataclass
class AbsEvent(CountableSportEvent):
    """Event representing abs exercises."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["abs"], "abs"
    )


@dataclass
class SquatsEvent(CountableSportEvent):
    """Event representing squats."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["squats"], "squats"
    )


@dataclass
class ChinUpsEvent(CountableSportEvent):
    """Event representing chin ups."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["chin_ups"], "chin_ups"
    )


@dataclass
class SitUpsEvent(CountableSportEvent):
    """Event representing sit ups."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["sit_ups"], "sit_ups"
    )


@dataclass
class SquatJumpsEvent(CountableSportEvent):
    """Event representing squat jumps."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["squat_jumps"], "squat_jumps"
    )


@dataclass
class DipsEvent(CountableSportEvent):
    """Event representing dips."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["dips"], "dips"
    )


@dataclass
class PushUpsEvent(CountableSportEvent):
    """Event representing push ups."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["push_ups"], "push_ups"
    )


@dataclass
class JumpingJacksEvent(CountableSportEvent):
    """Event representing jumping jacks."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["jumping_jacks"], "jumping_jacks"
    )


@dataclass
class HandGripsEvent(CountableSportEvent):
    """Event representing hand grips."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["hand_grips"], "hand_grips"
    )


@dataclass
class BurpeeEvent(CountableSportEvent):
    """Event representing burpees."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["burpee"], "burpee"
    )


@dataclass
class RussianTwistsEvent(CountableSportEvent):
    """Event representing russian twists."""

    arguments: ClassVar[Arguments] = CountableSportEvent.arguments.replace(
        ["russian_twists"], "russian_twists"
    )
