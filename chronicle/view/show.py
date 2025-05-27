"""View shows."""

import argparse
from dataclasses import dataclass
from typing import TYPE_CHECKING

from chronicle.timeline import Timeline

if TYPE_CHECKING:
    from datetime import datetime

    from chronicle.event.core import Event
    from chronicle.summary.core import Summary


@dataclass
class ShowViewer:
    """Viewer for shows."""

    timeline: Timeline

    def process_command(self, _: str) -> None:
        parser: argparse.ArgumentParser = argparse.ArgumentParser()
        sub_parsers: argparse._SubParsersAction = parser.add_subparsers(
            dest="command"
        )

        sub_parsers.add_parser("list")

        result: list[tuple[datetime, list[Event], Summary]] = (
            self.timeline.get_events_by_year()
        )

        for point, _events, summary in result:
            if summary.shows:
                print(point.year)
                for show in summary.shows:
                    print("   ", show.to_string())
