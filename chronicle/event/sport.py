"""Events related to sports and physical activity."""

from dataclasses import dataclass
from typing import Any, ClassVar, override

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
class ExerciseEvent(SportEvent):
    """Event representing a countable sport activity."""

    sets: list[int] | None = None
    """The number of repetitions of each set."""

    weights: list[float] | None = None
    """The weights used for each set."""

    arguments: ClassVar[Arguments] = (
        SportEvent.arguments.replace(["exercise"], "exercise")
        .add_class_argument("sets", Integers)
        .add_class_argument("weights", Weights)
    )

    def __init_subclass__(
        cls, command: str | None = None, **kwargs: Any
    ) -> None:
        super().__init_subclass__(**kwargs)
        if command is not None:
            cls.arguments = ExerciseEvent.arguments.replace([command], command)

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, is_main: bool = True
    ) -> None:
        if self.sets is not None:
            summary.exercises[self.arguments.command] += sum(self.sets) * ratio


@dataclass
class AbsEvent(ExerciseEvent, command="abs"):
    """Event representing abs exercises."""


@dataclass
class SquatsEvent(ExerciseEvent, command="squats"):
    """Event representing squats."""


@dataclass
class ChinUpsEvent(ExerciseEvent, command="chin_ups"):
    """Event representing chin ups."""


@dataclass
class SitUpsEvent(ExerciseEvent, command="sit_ups"):
    """Event representing sit ups."""


@dataclass
class SquatJumpsEvent(ExerciseEvent, command="squat_jumps"):
    """Event representing squat jumps."""


@dataclass
class DipsEvent(ExerciseEvent, command="dips"):
    """Event representing dips."""


@dataclass
class PushUpsEvent(ExerciseEvent, command="push_ups"):
    """Event representing push ups."""


@dataclass
class JumpingJacksEvent(ExerciseEvent, command="jumping_jacks"):
    """Event representing jumping jacks."""


@dataclass
class HandGripsEvent(ExerciseEvent, command="hand_grips"):
    """Event representing hand grips."""


@dataclass
class BurpeeEvent(ExerciseEvent, command="burpee"):
    """Event representing burpees."""


@dataclass
class RussianTwistsEvent(ExerciseEvent, command="russian_twists"):
    """Event representing russian twists."""


@dataclass
class PecDeckEvent(ExerciseEvent, command="pec_deck"):
    """Event representing pec deck machine exercise."""


@dataclass
class LegExtensionEvent(ExerciseEvent, command="leg_extension"):
    """Event representing leg extension machine exercise."""


@dataclass
class BarbellCurlEvent(ExerciseEvent, command="barbell_curl"):
    """Event representing barbell curl."""


@dataclass
class BarbellBenchPressEvent(ExerciseEvent, command="barbell_bench_press"):
    """Event representing barbell bench press."""


@dataclass
class PulldownMachineEvent(ExerciseEvent, command="pulldown_machine"):
    """Event representing pulldown machine exercise."""


@dataclass
class DeclineSitUpsEvent(ExerciseEvent, command="decline_sit_ups"):
    """Event representing decline sit ups."""


@dataclass
class DumbbellSideUpEvent(ExerciseEvent, command="dumbbell_side_up"):
    """Event representing dumbbell lateral raises."""


@dataclass
class SupermanEvent(ExerciseEvent, command="superman"):
    """Event representing superman exercise."""


@dataclass
class BackEvent(ExerciseEvent, command="back"):
    """Event representing back exercise."""


@dataclass
class SeatedLegCurlEvent(ExerciseEvent, command="seated_leg_curl"):
    """Event representing seated leg curl machine exercise."""


@dataclass
class RowEvent(ExerciseEvent, command="row"):
    """Event representing rowing exercise."""


@dataclass
class WheelEvent(ExerciseEvent, command="wheel"):
    """Event representing ab wheel exercise."""


@dataclass
class LatMachineEvent(ExerciseEvent, command="lat_machine"):
    """Event representing lat machine exercise."""


@dataclass
class CrunchEvent(ExerciseEvent, command="crunch"):
    """Event representing crunches."""


@dataclass
class StandingCalfRaisesEvent(ExerciseEvent, command="standing_calf_raises"):
    """Event representing standing calf raises."""


@dataclass
class RomanChairEvent(ExerciseEvent, command="roman_chair"):
    """Event representing roman chair exercise."""


@dataclass
class RearDeltPecFlyEvent(ExerciseEvent, command="rear_delt_pec_fly"):
    """Event representing rear delt pec fly exercise."""


@dataclass
class DumbbellCurlEvent(ExerciseEvent, command="dumbbell_curl"):
    """Event representing dumbbell curl."""


@dataclass
class LegPressEvent(ExerciseEvent, command="leg_press"):
    """Event representing leg press machine exercise."""


@dataclass
class ProneLegCurlEvent(ExerciseEvent, command="prone_leg_curl"):
    """Event representing prone leg curl machine exercise."""


@dataclass
class PullbackMachineEvent(ExerciseEvent, command="pullback_machine"):
    """Event representing pullback machine exercise."""


@dataclass
class BeetleEvent(ExerciseEvent, command="beetle"):
    """Event representing beetle exercise."""


@dataclass
class SteeringWheelEvent(ExerciseEvent, command="steering_wheel"):
    """Event representing steering wheel exercise."""


@dataclass
class DumbbellOverheadTricepExtensionEvent(
    ExerciseEvent, command="dumbbell_overhead_tricep_extension"
):
    """Event representing dumbbell overhead tricep extension."""
