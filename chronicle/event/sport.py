"""Events related to sports and physical activity."""

import logging
from dataclasses import dataclass
from typing import Any, ClassVar, override

from chronicle.argument import Argument, Arguments
from chronicle.event.core import Event
from chronicle.summary.core import Summary
from chronicle.time import Timedelta
from chronicle.value import (
    Distance,
    Integers,
    Kilocalories,
    Pace,
    Speed,
    Weights,
)

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class SportEvent(Event):
    """Excercise, warmup or any other sport activity."""

    energy: float | None = None
    """Spent energy in kilocalories."""

    arguments: ClassVar[Arguments] = Arguments(
        ["sport"], "sport"
    ).add_class_argument("energy", Kilocalories)

    def get_color(self) -> str:
        return "#008800"

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, *, is_main: bool = True
    ) -> None:
        if self.energy is not None:
            summary.register_energy_expenditure(self.energy * ratio)


@dataclass
class MoveEvent(SportEvent):
    """Event representing a moving activity."""

    duration: Timedelta | None = None
    """Moving time."""

    distance: float | None = None
    """Distance in meters."""

    pace: Timedelta | None = None
    """Pace in seconds per kilometer."""

    speed: float | None = None
    """Speed in km/h."""

    kilocalories: float | None = None
    """Kilocalories burned."""

    arguments: ClassVar[Arguments] = (
        Arguments(["move"], "move")
        .add_class_argument("duration", Timedelta)
        .add_class_argument("distance", Distance)
        .add_class_argument("speed", Speed)
        .add_class_argument("pace", Pace)
        .add_class_argument("kilocalories", Kilocalories)
    )

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, *, is_main: bool = True
    ) -> None:
        super().register_summary(summary, ratio, is_main=is_main)
        if self.distance is not None:
            summary.register_move_distance(self.distance * ratio)
        if self.kilocalories is not None:
            summary.register_move_energy(self.kilocalories * ratio)


@dataclass
class RunEvent(MoveEvent):
    """Event representing running."""

    arguments: ClassVar[Arguments] = MoveEvent.arguments.replace(["run"], "run")

    color: ClassVar[str] = "#FF8800"

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, *, is_main: bool = True
    ) -> None:
        super().register_summary(summary, ratio, is_main=is_main)
        if self.distance is not None:
            summary.register_cardio_distance(self.distance * ratio)


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

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, *, is_main: bool = True
    ) -> None:
        super().register_summary(summary, ratio, is_main=is_main)
        if is_main:
            summary.register_sport_session()


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

    min_sets_to_count: ClassVar[int] = 3
    """Minimum total repetitions for the event to count as an exercise."""

    bodyweight_fraction: ClassVar[float | None] = None
    """Fraction of body weight used as load (e.g. 0.69 for push-ups).

    When set, body weight from the summary is used as the base load per rep,
    with any recorded `weights` added on top (e.g. weighted chin-ups).
    If body weight is unknown, tonnage is skipped for this exercise.
    """

    arguments: ClassVar[Arguments] = (
        SportEvent.arguments.replace(["exercise"], "exercise")
        .add_class_argument("sets", Integers)
        .add_class_argument("weights", Weights)
    )

    def __post_init__(self) -> None:
        if self.sets is not None and self.weights is not None:
            if len(self.weights) == 1 and len(self.sets) > 1:
                self.weights = self.weights * len(self.sets)
            elif len(self.weights) != len(self.sets):
                logger.warning(
                    "Sets length %d doesn't match weights length %d for %s.",
                    len(self.sets),
                    len(self.weights),
                    self,
                )

    def __init_subclass__(
        cls, command: str | None = None, **kwargs: Any
    ) -> None:
        super().__init_subclass__(**kwargs)
        if command is not None:
            cls.arguments = ExerciseEvent.arguments.replace([command], command)

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, *, is_main: bool = True
    ) -> None:
        super().register_summary(summary, ratio, is_main=is_main)
        if self.sets is not None:
            summary.exercises[self.arguments.command] += sum(self.sets) * ratio

        if (
            self.sets is not None
            and is_main
            and len(self.sets) >= self.min_sets_to_count
        ):
            summary.register_sport_session()

        if self.sets is None:
            return

        if self.weights is not None:
            # Explicit weight recorded (possibly added on top of bodyweight).
            base = self.weights
            if self.bodyweight_fraction is not None and summary.body_weight_kg:
                bw_load = self.bodyweight_fraction * summary.body_weight_kg
                base = [w + bw_load for w in base]
            tonnage = sum(r * w for r, w in zip(self.sets, base, strict=True))
            summary.register_strength_tonnage(tonnage * ratio)
        elif self.bodyweight_fraction is not None:
            # No explicit weight — use bodyweight fraction alone.
            if summary.body_weight_kg is not None:
                bw_load = self.bodyweight_fraction * summary.body_weight_kg
                tonnage = sum(self.sets) * bw_load
                summary.register_strength_tonnage(tonnage * ratio)


@dataclass
class AbsEvent(ExerciseEvent, command="abs"):
    """Event representing abs exercises."""


@dataclass
class SquatsEvent(ExerciseEvent, command="squats"):
    """Event representing squats."""

    bodyweight_fraction: ClassVar[float | None] = 0.75


@dataclass
class ChinUpsEvent(ExerciseEvent, command="chin_ups"):
    """Event representing chin ups."""

    bodyweight_fraction: ClassVar[float | None] = 0.75


@dataclass
class SitUpsEvent(ExerciseEvent, command="sit_ups"):
    """Event representing sit ups."""


@dataclass
class SquatJumpsEvent(ExerciseEvent, command="squat_jumps"):
    """Event representing squat jumps."""


@dataclass
class DipsEvent(ExerciseEvent, command="dips"):
    """Event representing dips."""

    bodyweight_fraction: ClassVar[float | None] = 0.75


@dataclass
class PushUpsEvent(ExerciseEvent, command="push_ups"):
    """Event representing push ups."""

    bodyweight_fraction: ClassVar[float | None] = 0.69


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
class DumbbellSideUpsEvent(ExerciseEvent, command="dumbbell_side_ups"):
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
class CrunchesEvent(ExerciseEvent, command="crunches"):
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


@dataclass
class DeadBugEvent(ExerciseEvent, command="dead_bug"):
    """Event representing dead bug exercise."""
