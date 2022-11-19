import sys
from dataclasses import dataclass, field

from chronicle.event.core import to_camel
from chronicle.event.listen import *


@dataclass
class Timeline:
    """A collection of events and objects related to these events."""

    events: list[Event] = field(default_factory=list)
    objects: Objects = Objects()

    def dict(self) -> dict[str, Any]:
        return {
            "events": [x.dict() for x in self.events],
            "objects": self.objects.dict(),
        }

    def __len__(self) -> int:
        return len(self.events)

    def process_command(self, command: str) -> None:

        words: list[str] = command.split(" ")

        types: list[tuple[str, int]] = [(to_camel(words[0]), 1)]
        if len(words) >= 2:
            types += [(to_camel(words[0]) + to_camel(words[1]), 2)]

        class_ = None
        arguments: list[str] = []

        for type_, size in types:
            try:
                class_ = getattr(sys.modules[__name__], type_ + "Event")
                arguments = words[size:]
            except AttributeError:
                pass

        if class_:
            event: Event = class_.process_command(arguments)
            self.events.append(event)
