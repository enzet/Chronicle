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

    muscle_groups: ClassVar[frozenset[str]] = frozenset()
    """WHO muscle groups targeted by this exercise."""

    equipment: ClassVar[frozenset[str]] = frozenset()
    """Equipment required to perform this exercise."""

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
        cls,
        command: str | None = None,
        muscle_groups: set[str] | frozenset[str] | None = None,
        equipment: set[str] | frozenset[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if command is not None:
            cls.arguments = ExerciseEvent.arguments.replace([command], command)
        if muscle_groups is not None:
            cls.muscle_groups = frozenset(muscle_groups)
        if equipment is not None:
            cls.equipment = frozenset(equipment)

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
            for group in self.muscle_groups:
                summary.muscle_groups[group] += 1

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
class HeavyLabourEvent(SportEvent):
    """Event representing heavy manual labour (counts as exercise)."""

    duration: Timedelta | None = None
    """Duration of the labour activity."""

    muscle_groups: ClassVar[frozenset[str]] = frozenset()
    """WHO muscle groups targeted by this activity."""

    equipment: ClassVar[frozenset[str]] = frozenset()
    """Equipment required to perform this activity."""

    arguments: ClassVar[Arguments] = SportEvent.arguments.replace(
        ["heavy_labour"], "heavy_labour"
    ).add_class_argument("duration", Timedelta)

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, *, is_main: bool = True
    ) -> None:
        super().register_summary(summary, ratio, is_main=is_main)
        if is_main:
            summary.register_sport_session()
            for group in self.muscle_groups:
                summary.muscle_groups[group] += 1


@dataclass
class StumpRemovalEvent(HeavyLabourEvent):
    """Event representing tree stump removal or heavy digging."""

    muscle_groups: ClassVar[frozenset[str]] = frozenset(
        {"back", "legs", "arms", "core", "shoulders"}
    )

    arguments: ClassVar[Arguments] = HeavyLabourEvent.arguments.replace(
        ["stump_removal"], "stump_removal"
    )


@dataclass
class SquatsEvent(ExerciseEvent, command="squats", muscle_groups={"legs"}):
    """Event representing squats."""

    bodyweight_fraction: ClassVar[float | None] = 0.75


@dataclass
class ChinUpsEvent(
    ExerciseEvent,
    command="chin_ups",
    muscle_groups={"arms"},
    equipment={"pull_up_bar"},
):
    """Event representing chin ups."""

    bodyweight_fraction: ClassVar[float | None] = 0.75


@dataclass
class SitUpsEvent(ExerciseEvent, command="sit_ups", muscle_groups={"core"}):
    """Event representing sit ups."""


@dataclass
class SquatJumpsEvent(
    ExerciseEvent, command="squat_jumps", muscle_groups={"legs"}
):
    """Event representing squat jumps."""


@dataclass
class DipsEvent(
    ExerciseEvent,
    command="dips",
    muscle_groups={"arms", "chest"},
    equipment={"dip_bars"},
):
    """Event representing dips."""

    bodyweight_fraction: ClassVar[float | None] = 0.75


@dataclass
class PushUpsEvent(ExerciseEvent, command="push_ups", muscle_groups={"chest"}):
    """Event representing push ups."""

    bodyweight_fraction: ClassVar[float | None] = 0.69


@dataclass
class JumpingJacksEvent(
    ExerciseEvent, command="jumping_jacks", muscle_groups={"legs"}
):
    """Event representing jumping jacks."""


@dataclass
class HandGripsEvent(
    ExerciseEvent,
    command="hand_grips",
    muscle_groups={"arms"},
    equipment={"hand_gripper"},
):
    """Event representing hand grips."""


@dataclass
class BurpeeEvent(
    ExerciseEvent, command="burpee", muscle_groups={"legs", "core"}
):
    """Event representing burpees."""


@dataclass
class RussianTwistsEvent(
    ExerciseEvent, command="russian_twists", muscle_groups={"core"}
):
    """Event representing russian twists."""


@dataclass
class PecDeckEvent(
    ExerciseEvent,
    command="pec_deck",
    muscle_groups={"chest"},
    equipment={"pec_deck_machine"},
):
    """Event representing pec deck machine exercise."""


@dataclass
class LegExtensionEvent(
    ExerciseEvent,
    command="leg_extension",
    muscle_groups={"legs"},
    equipment={"leg_extension_machine"},
):
    """Event representing leg extension machine exercise."""


@dataclass
class BarbellCurlEvent(
    ExerciseEvent,
    command="barbell_curl",
    muscle_groups={"arms"},
    equipment={"barbell"},
):
    """Event representing barbell curl."""


@dataclass
class BarbellBenchPressEvent(
    ExerciseEvent,
    command="barbell_bench_press",
    muscle_groups={"chest"},
    equipment={"barbell", "bench"},
):
    """Event representing barbell bench press."""


@dataclass
class DeclineSitUpsEvent(
    ExerciseEvent,
    command="decline_sit_ups",
    muscle_groups={"core"},
    equipment={"decline_bench"},
):
    """Event representing decline sit ups."""


@dataclass
class DumbbellLateralRaiseEvent(
    ExerciseEvent,
    command="dumbbell_lateral_raise",
    muscle_groups={"shoulders"},
    equipment={"dumbbell"},
):
    """Event representing dumbbell lateral raises."""


@dataclass
class SupermanEvent(ExerciseEvent, command="superman", muscle_groups={"core"}):
    """Event representing superman exercise."""


@dataclass
class SeatedLegCurlEvent(
    ExerciseEvent,
    command="seated_leg_curl",
    muscle_groups={"legs"},
    equipment={"seated_leg_curl_machine"},
):
    """Event representing seated leg curl machine exercise."""


@dataclass
class LatPulldownsEvent(
    ExerciseEvent,
    command="lat_pulldowns",
    muscle_groups={"back"},
    equipment={"lat_machine"},
):
    """Event representing lat pulldown exercise."""


@dataclass
class CrunchesEvent(ExerciseEvent, command="crunches", muscle_groups={"core"}):
    """Event representing crunches."""


@dataclass
class StandingCalfRaisesEvent(
    ExerciseEvent, command="standing_calf_raises", muscle_groups={"calves"}
):
    """Event representing standing calf raises."""


@dataclass
class RomanChairEvent(
    ExerciseEvent,
    command="roman_chair",
    muscle_groups={"core"},
    equipment={"roman_chair"},
):
    """Event representing roman chair exercise."""


@dataclass
class RearDeltPecFlyEvent(
    ExerciseEvent,
    command="rear_delt_pec_fly",
    muscle_groups={"shoulders"},
    equipment={"rear_delt_pec_fly_machine"},
):
    """Event representing rear delt pec fly exercise."""


@dataclass
class DumbbellCurlEvent(
    ExerciseEvent,
    command="dumbbell_curl",
    muscle_groups={"arms"},
    equipment={"dumbbell"},
):
    """Event representing dumbbell curl."""


@dataclass
class LegPressEvent(
    ExerciseEvent,
    command="leg_press",
    muscle_groups={"legs"},
    equipment={"leg_press_machine"},
):
    """Event representing leg press machine exercise."""


@dataclass
class ProneLegCurlEvent(
    ExerciseEvent,
    command="prone_leg_curl",
    muscle_groups={"legs"},
    equipment={"prone_leg_curl_machine"},
):
    """Event representing prone leg curl machine exercise."""


@dataclass
class SteeringWheelEvent(
    ExerciseEvent,
    command="steering_wheel",
    muscle_groups={"shoulders"},
    equipment={"plate"},
):
    """Event representing steering wheel exercise."""


@dataclass
class DumbbellOverheadTricepExtensionEvent(
    ExerciseEvent,
    command="dumbbell_overhead_tricep_extension",
    muscle_groups={"arms"},
    equipment={"dumbbell"},
):
    """Event representing dumbbell overhead tricep extension."""


@dataclass
class DeadBugEvent(ExerciseEvent, command="dead_bug", muscle_groups={"core"}):
    """Event representing dead bug exercise."""


@dataclass
class DumbbellOverheadPressEvent(
    ExerciseEvent,
    command="dumbbell_overhead_press",
    muscle_groups={"shoulders"},
    equipment={"dumbbell"},
):
    """Event representing dumbbell overhead press exercise."""


@dataclass
class LowRowEvent(
    ExerciseEvent,
    command="low_row",
    muscle_groups={"back"},
    equipment={"low_row_machine"},
):
    """Event representing low row machine exercise."""


@dataclass
class PecFlyEvent(
    ExerciseEvent,
    command="pec_fly",
    muscle_groups={"chest"},
    equipment={"pec_fly_machine"},
):
    """Event representing pec fly machine exercise."""
