import logging
import re
from dataclasses import dataclass
from typing import ClassVar

from chronicle.argument import Arguments
from chronicle.event.core import Event
from chronicle.value import (
    ChronicleValueException,
    Cost,
    Language,
    ProgrammingLanguage,
    Subject,
    Tags,
)
from chronicle.objects.core import Object, Person, Project, Service
from chronicle.summary.core import Summary
from chronicle.time import Timedelta


__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class DoEvent(Event):
    """Event representing doing a general activity."""

    description: str | None = None
    """Description of what was done."""

    arguments: ClassVar[Arguments] = Arguments(["do"], "do").add_argument(
        "description"
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return DoEvent.arguments


@dataclass
class MedicationEvent(Event):
    """Event representing taking medication."""

    medication: str | None = None
    """Name of the medication taken."""

    arguments: ClassVar[Arguments] = Arguments(
        ["medication"], "medication"
    ).add_argument("medication")

    @staticmethod
    def get_arguments() -> Arguments:
        return MedicationEvent.arguments


@dataclass
class AppointmentEvent(Event):
    """Event representing an appointment or meeting."""

    description: str | None = None
    """Description of the appointment."""

    arguments: ClassVar[Arguments] = Arguments(
        ["appointment"], "appointment"
    ).add_argument("description")

    @staticmethod
    def get_arguments() -> Arguments:
        return AppointmentEvent.arguments


@dataclass
class CookEvent(Event):
    """Event representing cooking food."""

    dish: str | None = None
    """Name of the dish that was cooked."""

    arguments: ClassVar[Arguments] = Arguments(["cook"], "cook").add_argument(
        "dish"
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return CookEvent.arguments

    def register_summary(self, summary: Summary) -> None:
        """Register unique dish."""
        if self.dish:
            summary.register_dish(self.dish)


@dataclass
class CleanEvent(Event):
    """Event representing cleaning something."""

    object_: Object | None = None
    """Object that was cleaned."""

    tags: Tags | None = None
    """Tags of the object that was cleaned."""

    arguments: ClassVar[Arguments] = (
        Arguments(["clean", "wash"], "clean")
        .add_object_argument("object_", Object)
        .add_class_argument("tags", Tags)
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return CleanEvent.arguments


@dataclass
class CutEvent(Event):
    """Event representing cutting something."""

    object_: str | None = None
    """Object that was cut."""

    arguments: ClassVar[Arguments] = Arguments(["cut"], "cut").add_argument(
        "object_"
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return CutEvent.arguments


@dataclass
class EatEvent(Event):
    """Event representing eating food."""

    meal: str | None = None
    """Description of what was eaten."""

    kilocalories: float | None = None
    """Number of kilocalories in the meal."""

    arguments: ClassVar[Arguments] = Arguments(["eat"], "eat").add_argument(
        "meal"
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return EatEvent.arguments


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
        .add_argument("actions", prefix="actions:")
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return LearnEvent.arguments

    def register_summary(self, summary: Summary) -> None:
        if not self.subject:
            raise ChronicleValueException(f"Event {self} doesn't have subject.")

        if not isinstance(self.subject, Subject):
            raise ChronicleValueException(f"Event {self} has invalid subject.")

        if duration := self.get_duration():
            summary.register_learn(duration, self.subject, self.service)


@dataclass
class WriteEvent(Event):
    """Event representing writing something."""

    language: Language | None = None
    """Language used for writing."""

    duration: Timedelta | None = None
    """Duration of the writing event."""

    person: Person | None = None
    """Person you were writing to."""

    arguments: ClassVar[Arguments] = (
        Arguments(["write"], "write")
        .add_class_argument("language", Language)
        .add_class_argument("duration", Timedelta)
        .add_object_argument("person", Person)
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return WriteEvent.arguments

    def register_summary(self, summary: Summary) -> None:
        if self.language:
            summary.register_write(self.get_duration(), self.language)


@dataclass
class BedEvent(Event):
    """Event representing going to bed."""

    pass


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
        .add_argument("object_")
        .add_argument("for_", prefix="for")
        .add_class_argument("cost", Cost)
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return BuyEvent.arguments


@dataclass
class PlayEvent(Event):
    """Event representing playing a game."""

    game: str | None = None
    """Name of the game played."""

    arguments: ClassVar[Arguments] = Arguments(["play"], "play").add_argument(
        "game"
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return PlayEvent.arguments


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

    @staticmethod
    def get_arguments() -> Arguments:
        return SpeakEvent.arguments

    def register_summary(self, summary: Summary) -> None:
        if self.language:
            summary.register_speak(self.get_duration(), self.language)


@dataclass
class CallEvent(Event):
    """Event representing making a call."""

    with_: str | None = None
    """Person called."""

    video: str | None = None
    """Type of video call: either `camera` or `screen`."""

    arguments: ClassVar[Arguments] = Arguments(["call"], "call").add_argument(
        "with_", prefix="to"
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return CallEvent.arguments


@dataclass
class SitEvent(Event):
    """Event representing sitting."""

    arguments: ClassVar[Arguments] = Arguments(["sit"], "sit")

    @staticmethod
    def get_arguments() -> Arguments:
        return SitEvent.arguments


@dataclass
class TryEvent(Event):
    """Event representing trying clothes on."""

    item: str | None = None
    """Item that was tried on."""

    arguments: ClassVar[Arguments] = Arguments(["try"], "try").add_argument(
        "item"
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return TryEvent.arguments


@dataclass
class ReviewEvent(Event):
    """Event representing reviewing a project."""

    project: str | None = None
    """Project being reviewed."""

    arguments: ClassVar[Arguments] = Arguments(
        ["review"], "review"
    ).add_argument("project")

    @staticmethod
    def get_arguments() -> Arguments:
        return ReviewEvent.arguments


@dataclass
class IronEvent(Event):
    """Event representing ironing clothes."""

    pass


@dataclass
class ResearchEvent(Event):
    """Event representing doing research."""

    pass


@dataclass
class VoteEvent(Event):
    """Event representing voting."""

    pass


@dataclass
class SiteDefectsEvent(Event):
    """Event representing finding site defects."""

    pass


@dataclass
class VomitEvent(Event):
    """Event representing vomiting."""

    pass


@dataclass
class DrawEvent(Event):
    """Event representing drawing something."""

    tool: str | None = None
    """Tool used for drawing."""


@dataclass
class PainEvent(Event):
    """Event representing experiencing pain."""

    pass


@dataclass
class ShaveEvent(Event):
    """Event representing shaving."""

    object_: str | None = None
    """What was shaved."""

    arguments: ClassVar[Arguments] = Arguments(["shave"], "shave").add_argument(
        "object_"
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return ShaveEvent.arguments


@dataclass
class DrinkEvent(Event):
    """Event representing drinking something."""

    liquid: str | None = None
    """Type of liquid consumed."""

    amount: float | None = None
    """Amount of the liquid in litres."""

    arguments: ClassVar[Arguments] = (
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

    @staticmethod
    def get_arguments() -> Arguments:
        return DrinkEvent.arguments


@dataclass
class StatusEvent(Event):
    """Event representing a status check of body metrics."""

    weight: float | None = None
    """Body weight in kilograms."""

    temperature: float | None = None
    """Body temperature in Celsius."""

    arguments: ClassVar[Arguments] = (
        Arguments(["_"], "_").add_argument("weight").add_argument("temperature")
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return StatusEvent.arguments


@dataclass
class PayEvent(Event):
    """Event representing making a payment."""

    goods: str | None = None
    """Description of what was paid for."""

    cost: Cost | None = None
    """Amount paid."""

    arguments: ClassVar[Arguments] = (
        Arguments(["pay"], "pay")
        .add_argument("goods", prefix="for")
        .add_argument(
            "cost", command_printer=lambda x: f"{x.value}{x.currency}"
        )
    )

    @staticmethod
    def get_arguments() -> Arguments:
        return PayEvent.arguments

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

    @classmethod
    def get_arguments(cls) -> Arguments:
        return (
            super()
            .get_arguments()
            .replace(["program"], "program")
            .add_object_argument("project", Project, is_insert=True)
            .add_argument(
                "task",
                patterns=[re.compile(r"#([0-9A-Za-z!#_-]+)")],
                command_printer=lambda x: f"#{x}",
            )
            .add_class_argument("language", ProgrammingLanguage)
            .add_class_argument("duration", Timedelta)
        )

    def register_summary(self, summary: Summary) -> None:
        if self.project:
            if "work" in self.project.tags:
                summary.register_work(self.get_duration())
        else:
            logging.warning(
                f"Unknown project `{self.project}` in `{self.source}`."
            )


class SleepEvent(Event):
    """Event representing sleeping."""

    @classmethod
    def get_arguments(cls) -> Arguments:
        return Arguments(["sleep"], "sleep")

    def register_summary(self, summary: Summary) -> None:
        summary.register_sleep(self.time.get_duration())

    def get_color(self) -> str:
        return "#AACCCC"


class InBedEvent(Event):
    """Event representing being in bed."""

    arguments: ClassVar[Arguments] = Arguments(["in_bed"], "in_bed")

    @staticmethod
    def get_arguments() -> Arguments:
        return InBedEvent.arguments
