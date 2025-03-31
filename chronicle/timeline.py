import logging
from datetime import datetime, timedelta
from pathlib import Path
from re import Pattern, compile
from typing import Callable

import matplotlib.pyplot as plt
from rich.table import Table
from rich import box
from dataclasses import dataclass

from chronicle.event.common import PayEvent, SleepEvent
from chronicle.event.place import PlaceEvent
from chronicle.event.sport import MoveEvent, SportEvent
from chronicle.summary.core import Summary
from chronicle.event.transport import TransportEvent
from chronicle.objects.clothes import Clothes
from chronicle.time import Context, Time, MalformedTime, humanize_delta
from chronicle.objects.core import Medication, Thing, Objects
from chronicle.event.core import Event
from chronicle.serialize import fill
from chronicle.errors import ChronicleValueException

PYDANTIC: bool = False

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


DATE_PATTERN: Pattern = compile(
    r"(\d\d\d\d-\d\d-\d\d)( (Mo|Tu|We|Th|Fr|Sa|Su))?"
)


def type_to_class(type_: str, ending: str) -> type[Event] | None:
    """Convert string event type into event class.

    E.g. `push_ups` into `PushUpsEvent`, or `_` into `StatusEvent`.
    """
    if type_ == "_":
        class_name = "Status" + ending
    else:
        class_name: str = (
            "".join((x[0].upper() + x[1:]) for x in type_.split("_")) + ending
        )

    if class_name in globals():
        return globals()[class_name]

    logging.error(f"No such class: `{class_name}`.")
    return None


def smooth(data: list[float | None], size: int) -> list[float]:
    replaced: list[float] = [0 if x is None else x for x in data]
    new_data: list[float] = []
    for index in range(len(data)):
        new_data.append(sum(replaced[index - size + 1 : index + 1]) / size)
    return new_data


class MalformedData(Exception):
    def __init__(self, data: dict, key: str | None = None):
        self.data: dict = data
        self.key: str | None = key

    def __repr__(self):
        if self.key:
            return f"Data is malformed: {self.data[self.key]}"
        else:
            return f"Data is malformed: {self.data}"


class Timeline:
    """A collection of events and objects related to these events."""

    def __init__(self) -> None:
        self.events: list[Event] = []
        """List of events. May be unsorted."""

        self.tasks: list[Event] = []
        """List of planned events."""

        self.objects: Objects = Objects()
        """Collection of event-related objects."""

        self.prefix_to_class: dict[str, type[Event]] = {}
        """Mapping from command prefixes to event classes."""

        classes: list = Event.__subclasses__()
        for class_ in classes:
            classes += class_.__subclasses__()

        for class_ in classes:
            for prefix in class_.arguments.prefixes:
                self.prefix_to_class[prefix] = class_

    def __len__(self) -> int:
        """Number of events."""
        return len(self.events)

    def parse_data(self, data: dict) -> None:
        """Parse data.

        It is assumed that `data` has `objects` and `events` lists.
        """
        context: Context = Context()
        if "objects" in data:
            for object_type in data["objects"]:
                for object_id, object_data in data["objects"][
                    object_type
                ].items():
                    object_data["id"] = object_id
                    self.parse_object_data(object_data, object_type)
        if "events" in data:
            for event_data in data["events"]:
                self.parse_event_data(event_data, context)

    def parse_object_data(self, object_data: dict, object_type: str):
        object_class = type_to_class(object_type, "")
        if object_class:
            object_ = object_class()
            fill(object_data, object_class, object_)
            self.objects.set_object(object_data["id"], object_)

    def parse_event_data(self, event_data: dict, context: Context) -> None:
        if (
            "_" in event_data
        ):  # FIXME: remove this, it's temporary mark for comment-out.
            return
        if "type" not in event_data:
            logging.error(f"No type in event data {event_data}")
        if "time" not in event_data:
            logging.error(f"No time in event data {event_data}")
        if event_data["type"].endswith("__"):
            return

        event_class = type_to_class(event_data["type"], "Event")
        if event_class:
            time: Time = Time.from_string(event_data["time"], context)
            if time.get_lower() is None:
                logging.error(f"Bad time for {event_data}.")
                return
            event: Event = event_class(time)
            fill(event_data, event_class, event)
            self.events.append(event)
        else:
            ChronicleValueException(
                f'No class for event type `{event_data["type"]}`.'
            )

    def parse_event_command(
        self,
        command: str,
        tokens: list[str],
        context: Context | None = None,
        is_task: bool = False,
    ) -> None:
        """Parse string command describing an event.

        :param command: the initial command
        :param tokens: tokens from the command
        :param context: parsing context (current date, etc.)
        :param is_task: whether the event is a task (planned event)
        """
        if not command.strip():
            return

        time: Time | None
        prefix: str
        parameters: list[str]

        try:
            time = Time.from_string(tokens[0], context)
            prefix = tokens[1]
            parameters = tokens[2:]
        except (AttributeError, ValueError, IndexError):
            # If we cannot parse time, we suppose time was not specified at all.
            time = None
            prefix = tokens[0]
            parameters = tokens[1:]

        if time is None:
            if context and context.current_date:
                start: datetime = context.current_date
                end: datetime = context.current_date + timedelta(days=1)
                time = Time.from_string(
                    f"{start.year}-{start.month}-{start.day}T00:00/"
                    + f"{end.year}-{end.month}-{end.day}T00:00",
                    context,
                )
                time.is_assumed = True
            else:
                raise ChronicleValueException(
                    f"Not recognized as event or object: `{command}`."
                )

        if len(tokens) <= 1:
            raise ChronicleValueException(
                f"Not recognized as event or object: `{command}`: not enough "
                f"words."
            )

        if prefix in self.prefix_to_class:
            event: Event = self.prefix_to_class[prefix].parse_command(
                time, command, parameters, self.objects
            )
            self.events.append(event)
        else:
            raise ChronicleValueException(
                f"No event class for prefix `{prefix}`."
            )

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

    @staticmethod
    def get_filter(
        from_date: datetime | None, to_date: datetime | None
    ) -> Callable:
        if from_date and to_date:
            return lambda event: from_date <= event.time.get_moment() < to_date
        elif from_date:
            return lambda event: from_date <= event.time.get_moment()
        elif to_date:
            return lambda event: event.time.get_moment() < to_date

    def get_summary(self, filter_: Callable | None = None) -> Summary:
        """Get summary for events."""

        summary: Summary = Summary()

        for event in self.get_events(filter_=filter_):
            event.register_summary(summary)

        return summary

    def get_events(self, filter_: Callable | None = None) -> list[Event]:
        """Get events filtered by `filter_`."""
        if filter_ is None:
            return self.events
        return [event for event in self.events if filter_(event)]

    def get_events_by(
        self,
        get_first: Callable,
        get_next: Callable,
        filter_: Callable | None = None,
    ) -> list[tuple[datetime, list[Event], Summary]]:
        """Get events in chunks of time.

        :param get_first: function to get starting point
        :param get_next: function to get next point
        """

        filtered_events = self.get_events(filter_)

        if not filtered_events:
            return []

        min_time: datetime = min(x.time.get_lower() for x in filtered_events)
        max_time: datetime = max(x.time.get_upper() for x in filtered_events)

        sorted_events: list[Event] = sorted(
            filtered_events, key=lambda x: x.time.get_lower()
        )
        point: datetime = get_first(min_time)
        index: int = 0
        events: list[tuple[datetime, list[Event], Summary]] = []
        interval_events: list[Event]

        while point < max_time:
            interval_events: list[Event] = []
            while sorted_events[index].time.get_lower() < get_next(point):
                interval_events.append(sorted_events[index])
                index += 1
                if index >= len(sorted_events):
                    break

            summary: Summary = Summary()
            for event in interval_events:
                event.register_summary(summary)

            events.append((point, interval_events, summary))
            if index >= len(sorted_events):
                break

            point = get_next(point)

        return events

    def get_events_by_day(
        self, filter_: Callable | None = None
    ) -> list[tuple[datetime, list[Event], Summary]]:
        def get_first(point: datetime) -> datetime:
            return datetime(point.year, point.month, point.day)

        def get_next(point: datetime) -> datetime:
            return point + timedelta(days=1)

        return self.get_events_by(get_first, get_next, filter_)

    def get_events_by_month(
        self, filter_: Callable
    ) -> list[tuple[datetime, list[Event], Summary]]:
        def get_first(point: datetime) -> datetime:
            return datetime(point.year, point.month, 1)

        def get_next(point: datetime) -> datetime:
            if point.month == 12:
                return datetime(point.year + 1, 1, 1)
            return datetime(point.year, point.month + 1, 1)

        return self.get_events_by(get_first, get_next, filter_)

    def get_expired(self) -> Table:
        table: Table = Table(box=box.ROUNDED)
        table.add_column("Object")
        table.add_column("Expired in", justify="right")
        table.add_column("Temperature")

        objects: list[Medication] = [
            x
            for x in self.objects.objects.values()
            if isinstance(x, Medication) and x.expired is not None
        ]
        for object_ in sorted(objects, key=lambda x: x.expired):
            diff = object_.expired.get_lower() - datetime.now()
            style = ""
            if object_.color:
                c = object_.color.hex
                if len(c) == 4:
                    c = "#" + c[1] + c[1] + c[2] + c[2] + c[3] + c[3]
            if diff.total_seconds() > 0:
                if object_.retired:
                    style = "strike dim"
                delta = humanize_delta(diff)
            else:
                style = "red"
                if object_.retired:
                    style = "strike dim"
                delta = f"EXPIRED {humanize_delta(-diff)} ago"
            table.add_row(
                (f"[{c}]▄[/{c}] " if object_.color else "  ") + object_.title,
                delta,
                object_.temperature,
                style=style,
            )

        return table

    def get_objects_html(self, image_directory: Path) -> str:
        table: str = "<div class='object-container'>"

        for id_, object_ in self.objects.objects.items():
            if not isinstance(object_, Thing):
                continue
            if object_.expired:
                continue
            if id_.startswith("@"):
                id_ = id_[1:]
            if "__" in id_:
                id_ = id_.split("__")[0]
            # text = f"<code style='font-size: 85%; color: #AAAAAA;'>
            # {id_}</code>"
            text = ""
            if object_.name:
                text += f"<span class='object-name'>{object_.name}</span>"
            if isinstance(object_, Clothes) and object_.art:
                text += (
                    "<br /><span style='font-size: 85%; color: #AAA;'>"
                    f"{object_.art}</span>"
                )
            if object_.link:
                link: str = object_.link
                for prefix in "https://", "http://", "www.":
                    if link.startswith(prefix):
                        link = link[len(prefix) :]
                link = link[: link.find("/")]
                text += (
                    "<br /><a style='font-size: 85%;' "
                    f"href='{object_.link}'>{link}</a>"
                )
            for extension in "png", "jpg", "jpeg", "webp":
                image: str = ""
                file_path: Path = image_directory / f"{id_}.{extension}"
                if file_path.is_file():
                    image = (
                        f"<img src='{file_path}'"
                        f" style='max-width: 100px; max-height: 100px;"
                        f"' />"
                    )
                    break
            table += (
                f"<div class='object'><div class='object-image'>{image}</div>"
                f"<div class='object-text'><p>{text}</p></div></div>"
            )

        return table + "</div>"

    def get_objects(self) -> Table:
        table: Table = Table(box=box.ROUNDED)
        table.add_column("Identifier")
        table.add_column("Object")

        for id_, object_ in self.objects.objects.items():
            if isinstance(object_, Thing):
                if object_.color:
                    c = object_.color.hex
                    if len(c) == 4:
                        c = "#" + c[1] + c[1] + c[2] + c[2] + c[3] + c[3]
                table.add_row(
                    id_,
                    (f"[{c}]▄[/{c}] " if object_.color else "  ")
                    + str(object_.name),
                )

        return table

    def get_dishes(self) -> Table:
        table: Table = Table(box=box.ROUNDED)
        table.add_column("Dish")
        table.add_column("Times", justify="right")

        summary: Summary = self.get_summary()
        for dish, count in sorted(summary.dishes.items(), key=lambda x: -x[1]):
            table.add_row(dish, str(count))

        return table

    def print(self) -> None:
        for day, events, summary in self.get_events_by_day():
            print()
            print(day)
            print()
            events = sorted(events, key=lambda x: x.time.get_lower())
            for event in events:
                print(event.to_string(self.objects))

    def graph(self, filter_: Callable | None = None) -> None:
        filter_ = self.get_filter(datetime.now() - timedelta(days=30), None)

        i = 0
        for day, events, summary in self.get_events_by_day(filter_):
            i += 1
            data: list[tuple[float, float, float, str]] = []
            for event in events:
                # Skip event with not defined time.
                if event.time.is_assumed:
                    continue

                if not event.time.start or event.time.start == event.time.end:
                    marker: str = "|"
                    if isinstance(event, SportEvent):
                        marker = "+"
                    elif isinstance(event, PayEvent):
                        marker = "1"

                    moment: datetime = event.time.get_moment()
                    plt.plot(
                        [moment.hour + moment.minute / 60],
                        [i],
                        marker,
                        color=event.get_color(),
                    )
                    continue

                width: float
                if isinstance(event, PlaceEvent):
                    width = 0.5
                elif isinstance(event, TransportEvent):
                    width = 0.3
                elif isinstance(event, MoveEvent):
                    width = 0.1
                elif isinstance(event, SleepEvent):
                    width = 0.3
                else:
                    width = 0.1

                lower: datetime = event.time.get_lower()
                upper: datetime = event.time.get_upper()

                if upper > day + timedelta(days=1):
                    upper = day + timedelta(days=1)

                data.append(
                    (
                        lower.hour + lower.minute / 60,
                        ((upper - lower).total_seconds() / 60 - 1) / 60,
                        width,
                        event.get_color(),
                    )
                )
            # for value in data:
            #     a, b, width, color = value
            #     plt.barh(
            #         xranges=[(a, b)],
            #         yrange=(i - width / 2, width),
            #         facecolor=color,
            #         edgecolor=None,
            #     )
            plt.bar(
                x=[x[0] for x in data],
                height=[x[1] for x in data],
                width=[x[2] for x in data],
                color=[x[3] for x in data],
            )
        plt.show()


class CommandParser:
    """Parser of special Chronicle commands."""

    def __init__(self, timeline: Timeline | None = None):
        self.timeline: Timeline = (
            timeline if timeline is not None else Timeline()
        )
        self.context: Context = Context()

    def parse_command(self, command: str) -> None:
        """Parse special Chronicle command."""

        if not command.strip():
            # Skip empty command.
            return

        if command.strip().startswith("-- "):
            # Skip comments.
            return

        tokens: list[str] = [x for x in command.split(" ") if x]

        if "--" in tokens:
            # Remove comment.
            tokens = tokens[: tokens.index("--")]
            if not tokens:
                return

        if tokens[0] == "[x]" or tokens[0] == "[" and tokens[1] == "]":
            # Parse task (planned event).
            if len(tokens) > 1:
                if tokens[0] == "[x]":
                    parameters = tokens[1:]
                else:
                    parameters = tokens[2:]
                if parameters and parameters[0] in ["<!>", "<.>", "<*>"]:
                    parameters = parameters[1:]
                if parameters:
                    self.timeline.parse_event_command(
                        command, parameters, self.context, is_task=True
                    )
            return

        if tokens[0] == ">>>":
            # Skip planned event.
            return

        if len(tokens) >= 3 and tokens[2] == "=":
            # Parse object.
            success: bool = self.timeline.objects.parse_command(command, tokens)
            if not success:
                raise ChronicleValueException(
                    f"Failed to parse object by command `{command}`."
                )
            else:
                return

        if matcher := DATE_PATTERN.fullmatch(command):
            # Parse date setter.
            self.context.current_date = datetime.strptime(
                matcher.group(1), "%Y-%m-%d"
            )
            return

        # Parse event.
        self.timeline.parse_event_command(command, tokens, self.context)

    def parse_commands(self, commands: list[str]) -> None:
        for command in commands:
            self.parse_command(command)


@dataclass
class SportViewer:
    timeline: Timeline

    def plot_sport(self) -> None:
        _ = [
            (lambda _: summary.chin_ups, "#FF0000", "+"),
            (lambda _: summary.push_ups, "#0000FF", "x"),
            (lambda _: summary.abs_, "#008800", "|"),
            (lambda _: summary.jumping_jacks, "#888800", "o"),
            (lambda _: summary.squats, "#008888", "p"),
            (lambda _: summary.russian_twists, "#880088", "s"),
            (lambda _: summary.dips, "#888888", "*"),
        ]

        from matplotlib import pyplot as plt

        xs: list[datetime] = []

        points: str = "+x|ops*"
        types: list[str] = [
            "chin_ups",
            "push_ups",
            "abs_",
            "jumping_jacks",
            "squats",
            "russian_twists",
            "dips",
        ]
        colors: list[str] = [
            "#FF0000",
            "#0000FF",
            "#008800",
            "#888800",
            "#008888",
            "#880088",
            "#888888",
        ]

        ys: list[list[float | None]] = [[] for _ in types]
        ys_total: list[float] = []
        for day, _, summary in self.timeline.get_events_by_day():
            xs.append(day)
            total: float = 0.0
            for index, type_ in enumerate(types):
                value: float | None = getattr(summary, type_)
                ys[index].append(value if value else None)
                total += value if value else 0.0
            ys_total.append(total / len(types))

        for index, type_ in enumerate(types):
            plt.plot(
                xs,
                ys[index],
                points[index],
                color=colors[index],
                fillstyle="none",
                label=type_,
            )
            plt.plot(
                xs,
                smooth(ys[index], 7),
                color=colors[index],
                alpha=0.1,
                linewidth=1,
            )
        plt.plot(xs, smooth(ys_total, 7), color="#000000", linewidth=1)
        plt.ylim(0, None)
        plt.legend()
        plt.show()
