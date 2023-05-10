import json
from dataclasses import dataclass, field

from chronicle.event.listen import *
from chronicle.time import Context, Time


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

    def parse_command(
        self, command: str, context: Context | None = None
    ) -> None:
        """Parse string command describing an event."""

        words: list[str] = command.split(" ")

        time: str = Time.from_string(words[0], context).to_pseudo_edtf()
        prefix: str = words[1]

        classes: list = Event.__subclasses__()

        for class_ in classes:
            parser: ArgumentParser = class_.get_parser()
            if prefix in parser.prefixes:
                event: Event = class_.parse_command(time, " ".join(words[2:]))
                self.events.append(event)
                break

    def get_summary(self):
        summary = Summary()
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

        if self.timeline.objects.parse_command(command):
            return

        if DATE_PATTERN.match(command):
            self.context.current_date = datetime.strptime(command, "%Y-%m-%d")
            return

        self.timeline.parse_command(command, self.context)

    def parse_commands(self, commands: list[str]) -> None:
        for command in commands:
            self.parse_command(command)
