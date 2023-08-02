import json
from dataclasses import field
from datetime import datetime, timedelta
from pathlib import Path
from re import Pattern
from types import UnionType

import matplotlib.pyplot as plt
from rich.table import Table
from rich import box

from chronicle.event.common import *
from chronicle.event.art import *
from chronicle.event.place import *
from chronicle.event.sport import *
from chronicle.event.transport import *
from chronicle.time import Context, Time, MalformedTime, humanize_delta
from chronicle.objects import Medication, Thing, Clothes
from chronicle.event.core import Event

PYDANTIC: bool = False

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


DATE_PATTERN: Pattern = re.compile(
    r"(\d\d\d\d-\d\d-\d\d)( (Mo|Tu|We|Th|Fr|Sa|Su))?"
)


def event_type_to_class(event_type: str):
    """
    Convert string event type into event class.

    E.g. `push_up` into `PushUpEvent`.
    """
    if event_type == "_":
        class_name = "StatusEvent"
    else:
        class_name: str = (
            "".join((x[0].upper() + x[1:]) for x in event_type.split("_"))
            + "Event"
        )

    if class_name in globals():
        return globals()[class_name]

    logging.error(f"No such event class: `{class_name}`.")
    return None


def construct_types(event_class, field: str):
    if field in ["from", "to"]:
        field += "_"

    value_class = event_class.__dict__["__dataclass_fields__"][field].type

    if isinstance(value_class, UnionType):
        types = []
        for type_ in str(value_class).split(" | "):
            if "." in type_:
                type_ = type_.split(".")[-1]
            if type_ in globals():
                types.append(globals()[type_])
            elif type_ in __builtins__:
                types.append(__builtins__[type_])
            else:
                raise TypeError(type_, type(type_))

        return types

    return [value_class]


def smooth(data, size):
    replaced = [0 if x is None else x for x in data]
    new_data = []
    for index in range(len(data)):
        new_data.append(sum(replaced[index - size + 1 : index + 1]) / size)
    return new_data


@dataclass
class Timeline:
    """A collection of events and objects related to these events."""

    events: list[Event] = field(default_factory=list)
    objects: Objects = Objects()

    def dict(self) -> dict[str, Any]:
        return {
            "events": [
                json.loads(x.json(exclude_unset=True)) for x in self.events
            ],
            "objects": self.objects.dict(exclude_unset=True),
        }

    def __len__(self) -> int:
        return len(self.events)

    def parse_data(self, data: dict, context: Context) -> None:
        if data["type"].endswith("__"):
            return

        event_class = event_type_to_class(data["type"])
        print(event_class)
        if event_class:
            event = event_class(Time.from_string(data["time"], context))
            for key, value in data.items():
                if key in ["type", "time"] or key.startswith("__"):
                    continue
                for value_class in construct_types(event_class, key):
                    print(value_class)
                    if value_class in [str, bool, float, int]:
                        event.__setattr__(key, value_class(value))
                        break
                    else:
                        event.__setattr__(key, value_class.from_json(value))
                        break
            self.events.append(event)

    def parse_event_command(
        self, command: str, context: Context | None = None
    ) -> None:
        """Parse string command describing an event."""

        words: list[str] = command.split(" ")

        try:
            time: str = Time.from_string(words[0], context).to_pseudo_edtf()
        except AttributeError as e:
            logging.error(
                f"Not recognized as event or object: `{command}`: {e}."
            )
            return None
        except ValueError as e:
            logging.error(
                f"Not recognized as event or object: `{command}`: {e}."
            )
            return None

        prefix: str = words[1]

        classes: list = Event.__subclasses__()
        for class_ in classes:
            classes += class_.__subclasses__()

        for class_ in classes:
            parser: Arguments = class_.get_arguments()
            if prefix in parser.prefixes:
                try:
                    event: Event = class_.parse_command(
                        time, " ".join(words[2:])
                    )
                    self.events.append(event)
                except TypeError as e:
                    logging.error(f"Cannot parse `{command}`: {e}.")
                except ValueError as e:
                    logging.error(f"Cannot parse `{command}`: {e}.")
                break

    def get_commands(self) -> list[str]:
        commands: list[str] = []

        commands += self.objects.get_commands()
        last_date: str | None = None
        for event in sorted(self.events, key=lambda x: x.time.get_moment()):
            try:
                date: str = event.time.get_moment().strftime("%Y-%m-%d")
                if last_date != date:
                    commands += ["", date, ""]
                commands.append(event.to_command())
                last_date = date
            except MalformedTime:
                logging.error(f"Bad time for {event}.")

        return commands

    def get_summary(self) -> Summary:
        summary: Summary = Summary()
        for event in self.events:
            event.register_summary(summary, self.objects)
        return summary


class CommandParser:
    def __init__(self, timeline: Timeline = None):
        if timeline is None:
            timeline = Timeline()
        self.timeline: Timeline = timeline
        self.context: Context = Context()

    def parse_command(self, command: str) -> None:
        if not command:
            return

        words = command.split(" ")
        if len(words) >= 3 and words[2] == "=":
            self.timeline.objects.parse_command(command)
            return

        if matcher := DATE_PATTERN.match(command):
            self.context.current_date = datetime.strptime(
                matcher.group(1), "%Y-%m-%d"
            )
            return

        self.timeline.parse_event_command(command, self.context)

    def parse_commands(self, commands: list[str]) -> None:
        for command in commands:
            self.parse_command(command)
