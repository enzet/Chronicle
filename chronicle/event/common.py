"""Common events."""

import logging
import re
from dataclasses import dataclass
from typing import ClassVar, override

from chronicle.argument import Argument, Arguments
from chronicle.errors import ChronicleValueError
from chronicle.event.core import Event
from chronicle.objects.core import Dish, Object, Person, Project, Service
from chronicle.summary.core import Summary
from chronicle.time import Timedelta
from chronicle.value import (
    AddedSugar,
    Calcium,
    Carbohydrates,
    Cost,
    Fat,
    Fiber,
    Iron,
    Language,
    Liquid,
    Magnesium,
    Omega3,
    Potassium,
    ProgrammingLanguage,
    Protein,
    SaturatedFat,
    Sodium,
    Subject,
    Sugar,
    Tags,
    VitaminB12,
    VitaminC,
    VitaminD,
    Volume,
    Zinc,
)

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class DoEvent(Event):
    """Event representing doing a general activity."""

    description: str | None = None
    """Description of what was done."""

    arguments: ClassVar[Arguments] = Arguments(["do"], "do").add(
        Argument("description")
    )


@dataclass
class MedicationEvent(Event):
    """Event representing taking medication."""

    medication: str | None = None
    """Name of the medication taken."""

    arguments: ClassVar[Arguments] = Arguments(
        ["medication"], "medication"
    ).add(Argument("medication"))


@dataclass
class AppointmentEvent(Event):
    """Event representing an appointment or meeting."""

    description: str | None = None
    """Description of the appointment."""

    arguments: ClassVar[Arguments] = Arguments(
        ["appointment"], "appointment"
    ).add(Argument("description"))


@dataclass
class CookEvent(Event):
    """Event representing cooking food."""

    dish: Dish | None = None
    """Dish that was cooked."""

    arguments: ClassVar[Arguments] = Arguments(
        ["cook"], "cook"
    ).add_object_argument("dish", Dish, is_main=True)

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, is_main: bool = True
    ) -> None:
        """Register unique dish."""
        if is_main and self.dish:
            summary.register_dish(self.dish.title or self.dish.id)


@dataclass
class CleanEvent(Event):
    """Event representing cleaning something."""

    object_: Object | None = None
    """Object that was cleaned."""

    arguments: ClassVar[Arguments] = Event.arguments.replace(
        ["clean", "wash"], "clean"
    ).add_object_argument("object_", Object, is_main=True)


@dataclass
class CutEvent(Event):
    """Event representing cutting something."""

    object_: str | None = None
    """Object that was cut."""

    arguments: ClassVar[Arguments] = Arguments(["cut"], "cut").add(
        Argument("object_")
    )


@dataclass
class EatEvent(Event):
    """Event representing eating food."""

    meal: str | None = None
    """Description of what was eaten."""

    energy: float | None = None
    """Energy in kilocalories."""

    carbohydrates: Carbohydrates | None = None
    """Carbohydrates in grams."""

    protein: Protein | None = None
    """Protein in grams."""

    fat: Fat | None = None
    """Fat in grams."""

    saturated_fat: SaturatedFat | None = None
    """Saturated fat in grams."""

    fiber: Fiber | None = None
    """Dietary fiber in grams."""

    sugar: Sugar | None = None
    """Total sugar in grams."""

    added_sugar: AddedSugar | None = None
    """Added sugar in grams."""

    omega3: Omega3 | None = None
    """Omega-3 fatty acids in grams."""

    calcium: Calcium | None = None
    """Calcium in milligrams."""

    iron: Iron | None = None
    """Iron in milligrams."""

    vitamin_d: VitaminD | None = None
    """Vitamin D in international units."""

    magnesium: Magnesium | None = None
    """Magnesium in milligrams."""

    zinc: Zinc | None = None
    """Zinc in milligrams."""

    potassium: Potassium | None = None
    """Potassium in milligrams."""

    sodium: Sodium | None = None
    """Sodium in milligrams."""

    vitamin_c: VitaminC | None = None
    """Vitamin C in milligrams."""

    vitamin_b12: VitaminB12 | None = None
    """Vitamin B12 in micrograms."""

    liquid: Liquid | None = None
    """Liquid volume in milliliters."""

    arguments: ClassVar[Arguments] = (
        Arguments(["eat"], "eat")
        .add(Argument("meal"))
        .add(
            Argument(
                "energy",
                patterns=[re.compile(r"(\d+(?:\.\d+)?)kcal")],
                extractors=[lambda x: float(x(1))],
                command_printer=lambda x: f"{x}kcal",
            )
        )
        .add_class_argument("carbohydrates", Carbohydrates)
        .add_class_argument("protein", Protein)
        .add_class_argument("fat", Fat)
        .add_class_argument("saturated_fat", SaturatedFat)
        .add_class_argument("fiber", Fiber)
        .add_class_argument("sugar", Sugar)
        .add_class_argument("added_sugar", AddedSugar)
        .add_class_argument("omega3", Omega3)
        .add_class_argument("calcium", Calcium)
        .add_class_argument("iron", Iron)
        .add_class_argument("vitamin_d", VitaminD)
        .add_class_argument("magnesium", Magnesium)
        .add_class_argument("zinc", Zinc)
        .add_class_argument("potassium", Potassium)
        .add_class_argument("sodium", Sodium)
        .add_class_argument("vitamin_c", VitaminC)
        .add_class_argument("vitamin_b12", VitaminB12)
        .add_class_argument("liquid", Liquid)
    )

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, is_main: bool = True
    ) -> None:
        if self.energy is not None:
            summary.register_energy(self.energy * ratio)
        if self.carbohydrates is not None:
            summary.register_carbohydrates(self.carbohydrates.value * ratio)
        if self.protein is not None:
            summary.register_protein(self.protein.value * ratio)
        if self.fat is not None:
            summary.register_fat(self.fat.value * ratio)
        if self.saturated_fat is not None:
            summary.register_saturated_fat(self.saturated_fat.value * ratio)
        if self.fiber is not None:
            summary.register_fiber(self.fiber.value * ratio)
        if self.sugar is not None:
            summary.register_sugar(self.sugar.value * ratio)
        if self.added_sugar is not None:
            summary.register_added_sugar(self.added_sugar.value * ratio)
        if self.omega3 is not None:
            summary.register_omega3(self.omega3.value * ratio)
        if self.calcium is not None:
            summary.register_calcium(self.calcium.value * ratio)
        if self.iron is not None:
            summary.register_iron(self.iron.value * ratio)
        if self.vitamin_d is not None:
            summary.register_vitamin_d(self.vitamin_d.value * ratio)
        if self.magnesium is not None:
            summary.register_magnesium(self.magnesium.value * ratio)
        if self.zinc is not None:
            summary.register_zinc(self.zinc.value * ratio)
        if self.potassium is not None:
            summary.register_potassium(self.potassium.value * ratio)
        if self.sodium is not None:
            summary.register_sodium(self.sodium.value * ratio)
        if self.vitamin_c is not None:
            summary.register_vitamin_c(self.vitamin_c.value * ratio)
        if self.vitamin_b12 is not None:
            summary.register_vitamin_b12(self.vitamin_b12.value * ratio)
        if self.liquid is not None:
            summary.register_liquid(self.liquid.value * ratio)


@dataclass
class LearnEvent(Event):
    """Event representing learning or studying something."""

    subject: Subject | None = None
    """Subject being learned."""

    service: Service | None = None
    """Method of learning: Duolingo, Memrise, etc."""

    actions: float | None = None
    """Number of actions or score."""

    duration: Timedelta | None = None
    """Duration of the learning event."""

    arguments: ClassVar[Arguments] = (
        Arguments(["learn"], "learn")
        .add_class_argument("subject", Subject)
        .add_object_argument("service", Service)
        .add_class_argument("duration", Timedelta)
        .add(Argument("actions", prefix="actions:"))
        .add_class_argument("tags", Tags)
    )

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, is_main: bool = True
    ) -> None:
        message: str

        if not self.subject:
            message = f"Event {self} doesn't have subject."
            raise ChronicleValueError(message, self)

        if not isinstance(self.subject, Subject):
            message = f"Event {self} has invalid subject."
            raise ChronicleValueError(message, self)

        if duration := self.get_duration():
            summary.register_learn(duration * ratio, self.subject, self.service)


@dataclass
class WriteEvent(Event):
    """Event representing writing something."""

    title: str | None = None
    """Title of the document was written."""

    language: Language | None = None
    """Language used for writing."""

    duration: Timedelta | None = None
    """Duration of the writing event."""

    volume: Volume | None = None
    """Volume of the writing event."""

    person: Person | None = None
    """Person you were writing to."""

    service: Service | None = None
    """Service used to write the document."""

    arguments: ClassVar[Arguments] = (
        Event.arguments.replace(["write"], "write")
        .add(Argument("title"), is_main=True)
        .add_class_argument("language", Language)
        .add_class_argument("duration", Timedelta)
        .add_class_argument("volume", Volume)
        .add_object_argument("person", Person)
        .add_object_argument("service", Service)
    )

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, is_main: bool = True
    ) -> None:
        if not self.language:
            return

        if not self.get_duration() and self.volume:
            if self.volume.measure == "words" and self.volume.value:
                summary.register_write_words(
                    self.volume.value * ratio, self.language, self.service
                )
        elif duration := self.get_duration():
            summary.register_write(
                duration * ratio, self.language, self.service
            )


@dataclass
class BedEvent(Event):
    """Event representing going to bed."""


@dataclass
class BuyEvent(Event):
    """Event representing purchasing something."""

    object_: str | None = None
    """Item that was purchased."""

    for_: str | None = None
    """Who the item was purchased for."""

    cost: Cost | None = None
    """Cost of the purchase."""

    arguments: ClassVar[Arguments] = (
        Arguments(["buy"], "buy")
        .add(Argument("object_"))
        .add(Argument("for_", prefix="for"))
        .add_class_argument("cost", Cost)
    )


@dataclass
class PlayEvent(Event):
    """Event representing playing a game."""

    game: str | None = None
    """Name of the game played."""

    arguments: ClassVar[Arguments] = Arguments(["play"], "play").add(
        Argument("game")
    )


@dataclass
class SpeakEvent(Event):
    """Event representing speaking in a language."""

    language: Language | None = None
    """Language that was spoken."""

    duration: Timedelta | None = None
    """Duration of the speaking event."""

    arguments: ClassVar[Arguments] = (
        Arguments(["speak"], "speak")
        .add_class_argument("language", Language)
        .add_class_argument("duration", Timedelta)
    )

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, is_main: bool = True
    ) -> None:
        if self.language and (duration := self.get_duration()):
            summary.register_speak(duration * ratio, self.language)


@dataclass
class CallEvent(Event):
    """Event representing making a call."""

    with_: str | None = None
    """Person called."""

    video: str | None = None
    """Type of video call: either `camera` or `screen`."""

    arguments: ClassVar[Arguments] = Arguments(["call"], "call").add(
        Argument("with_", prefix="to")
    )


@dataclass
class SitEvent(Event):
    """Event representing sitting."""

    arguments: ClassVar[Arguments] = Arguments(["sit"], "sit")


@dataclass
class TryEvent(Event):
    """Event representing trying clothes on."""

    item: str | None = None
    """Item that was tried on."""

    arguments: ClassVar[Arguments] = Arguments(["try"], "try").add(
        Argument("item")
    )


@dataclass
class ReviewEvent(Event):
    """Event representing reviewing a project."""

    project: str | None = None
    """Project being reviewed."""

    arguments: ClassVar[Arguments] = Arguments(["review"], "review").add(
        Argument("project")
    )


@dataclass
class IronEvent(Event):
    """Event representing ironing clothes."""


@dataclass
class ResearchEvent(Event):
    """Event representing doing research."""


@dataclass
class VoteEvent(Event):
    """Event representing voting."""


@dataclass
class SiteDefectsEvent(Event):
    """Event representing finding site defects."""


@dataclass
class VomitEvent(Event):
    """Event representing vomiting."""


@dataclass
class DrawEvent(Event):
    """Event representing drawing something."""

    tool: str | None = None
    """Tool used for drawing."""


@dataclass
class PainEvent(Event):
    """Event representing experiencing pain."""


@dataclass
class ShaveEvent(Event):
    """Event representing shaving."""

    object_: str | None = None
    """What was shaved."""

    arguments: ClassVar[Arguments] = Arguments(["shave"], "shave").add(
        Argument("object_")
    )


@dataclass
class DrinkEvent(Event):
    """Event representing drinking something."""

    liquid: str | None = None
    """Type of liquid consumed."""

    amount: Liquid | None = None
    """Amount of the liquid."""

    energy: float | None = None
    """Energy in kilocalories."""

    carbohydrates: Carbohydrates | None = None
    """Carbohydrates in grams."""

    protein: Protein | None = None
    """Protein in grams."""

    fat: Fat | None = None
    """Fat in grams."""

    saturated_fat: SaturatedFat | None = None
    """Saturated fat in grams."""

    fiber: Fiber | None = None
    """Dietary fiber in grams."""

    sugar: Sugar | None = None
    """Total sugar in grams."""

    added_sugar: AddedSugar | None = None
    """Added sugar in grams."""

    omega3: Omega3 | None = None
    """Omega-3 fatty acids in grams."""

    calcium: Calcium | None = None
    """Calcium in milligrams."""

    iron: Iron | None = None
    """Iron in milligrams."""

    vitamin_d: VitaminD | None = None
    """Vitamin D in international units."""

    magnesium: Magnesium | None = None
    """Magnesium in milligrams."""

    zinc: Zinc | None = None
    """Zinc in milligrams."""

    potassium: Potassium | None = None
    """Potassium in milligrams."""

    sodium: Sodium | None = None
    """Sodium in milligrams."""

    vitamin_c: VitaminC | None = None
    """Vitamin C in milligrams."""

    vitamin_b12: VitaminB12 | None = None
    """Vitamin B12 in micrograms."""

    arguments: ClassVar[Arguments] = (
        Arguments(["drink"], "drink")
        .add(Argument("liquid"))
        .add_class_argument("amount", Liquid)
        .add(
            Argument(
                "energy",
                patterns=[re.compile(r"(\d+(?:\.\d+)?)kcal")],
                extractors=[lambda x: float(x(1))],
                command_printer=lambda x: f"{x}kcal",
            )
        )
        .add_class_argument("carbohydrates", Carbohydrates)
        .add_class_argument("protein", Protein)
        .add_class_argument("fat", Fat)
        .add_class_argument("saturated_fat", SaturatedFat)
        .add_class_argument("fiber", Fiber)
        .add_class_argument("sugar", Sugar)
        .add_class_argument("added_sugar", AddedSugar)
        .add_class_argument("omega3", Omega3)
        .add_class_argument("calcium", Calcium)
        .add_class_argument("iron", Iron)
        .add_class_argument("vitamin_d", VitaminD)
        .add_class_argument("magnesium", Magnesium)
        .add_class_argument("zinc", Zinc)
        .add_class_argument("potassium", Potassium)
        .add_class_argument("sodium", Sodium)
        .add_class_argument("vitamin_c", VitaminC)
        .add_class_argument("vitamin_b12", VitaminB12)
    )

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, is_main: bool = True
    ) -> None:
        if self.energy is not None:
            summary.register_energy(self.energy * ratio)
        if self.carbohydrates is not None:
            summary.register_carbohydrates(self.carbohydrates.value * ratio)
        if self.protein is not None:
            summary.register_protein(self.protein.value * ratio)
        if self.fat is not None:
            summary.register_fat(self.fat.value * ratio)
        if self.saturated_fat is not None:
            summary.register_saturated_fat(self.saturated_fat.value * ratio)
        if self.fiber is not None:
            summary.register_fiber(self.fiber.value * ratio)
        if self.sugar is not None:
            summary.register_sugar(self.sugar.value * ratio)
        if self.added_sugar is not None:
            summary.register_added_sugar(self.added_sugar.value * ratio)
        if self.omega3 is not None:
            summary.register_omega3(self.omega3.value * ratio)
        if self.calcium is not None:
            summary.register_calcium(self.calcium.value * ratio)
        if self.iron is not None:
            summary.register_iron(self.iron.value * ratio)
        if self.vitamin_d is not None:
            summary.register_vitamin_d(self.vitamin_d.value * ratio)
        if self.magnesium is not None:
            summary.register_magnesium(self.magnesium.value * ratio)
        if self.zinc is not None:
            summary.register_zinc(self.zinc.value * ratio)
        if self.potassium is not None:
            summary.register_potassium(self.potassium.value * ratio)
        if self.sodium is not None:
            summary.register_sodium(self.sodium.value * ratio)
        if self.vitamin_c is not None:
            summary.register_vitamin_c(self.vitamin_c.value * ratio)
        if self.vitamin_b12 is not None:
            summary.register_vitamin_b12(self.vitamin_b12.value * ratio)
        if self.amount is not None:
            summary.register_liquid(self.amount.value * ratio)


@dataclass
class StatusEvent(Event):
    """Event representing a status check of body metrics."""

    weight: float | None = None
    """Body weight in kilograms."""

    temperature: float | None = None
    """Body temperature in Celsius."""

    arguments: ClassVar[Arguments] = (
        Arguments(["_"], "_")
        .add(Argument("weight"))
        .add(Argument("temperature"))
    )


@dataclass
class PayEvent(Event):
    """Event representing making a payment."""

    goods: str | None = None
    """Description of what was paid for."""

    cost: Cost | None = None
    """Amount paid."""

    arguments: ClassVar[Arguments] = (
        Arguments(["pay"], "pay")
        .add(Argument("goods", prefix="for"))
        .add(
            Argument("cost", command_printer=lambda x: f"{x.value}{x.currency}")
        )
    )

    @override
    def get_color(self) -> str:
        return "#FF0000"


@dataclass
class ProgramEvent(Event):
    """Event representing programming.

    This event also includes everything that is related to programming,
    including reading code, reading documentation, searching information, etc.
    """

    project: Project | None = None
    """Project being worked on."""

    language: ProgrammingLanguage | None = None
    """Programming language used."""

    task: str | None = None
    """Task being worked on."""

    duration: Timedelta | None = None
    """Duration of programming session."""

    arguments: ClassVar[Arguments] = (
        Arguments(["program"], "program")
        .add_object_argument("project", Project, is_insert=True)
        .add(
            Argument(
                "task",
                patterns=[re.compile(r"#([0-9A-Za-z!#_-]+)")],
                command_printer=lambda x: f"#{x}",
            )
        )
        .add_class_argument("language", ProgrammingLanguage)
        .add_class_argument("duration", Timedelta)
        .add_class_argument("tags", Tags)
    )

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, is_main: bool = True
    ) -> None:
        if self.project:
            if "work" in self.project.tags and (
                duration := self.get_duration()
            ):
                summary.register_work(duration * ratio)
        else:
            logger.warning(
                "Unknown project `%s` in `%s`.", self.project, self.source
            )


class SleepEvent(Event):
    """Event representing sleeping."""

    arguments: ClassVar[Arguments] = Arguments(["sleep"], "sleep")

    @override
    def register_summary(
        self, summary: Summary, ratio: float = 1.0, is_main: bool = True
    ) -> None:
        if duration := self.get_duration():
            summary.register_sleep(duration * ratio)

    @override
    def get_color(self) -> str:
        return "#AACCCC"


class InBedEvent(Event):
    """Event representing being in bed."""

    arguments: ClassVar[Arguments] = Arguments(["in_bed"], "in_bed")
