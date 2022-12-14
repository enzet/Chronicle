from dataclasses import dataclass, field

from chronicle.event.listen import *
from chronicle.time import Time


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

    def parse_command(self, command: str) -> None:

        words: list[str] = command.split(" ")

        time = words[0]
        prefix = words[1]

        classes = Event.__subclasses__()

        for class_ in classes:
            parser = class_.get_parser()
            if prefix in parser.prefixes:
                event: Event = class_.parse_command(
                    Time(time), " ".join(words[2:])
                )
                self.events.append(event)
                break
