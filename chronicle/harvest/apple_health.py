"""Harvest data from Apple Health."""

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import override

from chronicle.event.sport import MoveEvent
from chronicle.harvest.core import Importer, ImportManager
from chronicle.time import Moment, Time
from chronicle.timeline import Timeline


class AppleHealthImportManager(ImportManager):
    """Manager for Apple Health import."""

    @staticmethod
    @override
    def add_argument(parser: argparse._ArgumentGroup) -> None:
        parser.add_argument(
            "--import-apple-health",
            help="import movement data from Apple Health",
            metavar="<path>",
        )

    @staticmethod
    @override
    def process_arguments(
        arguments: argparse.Namespace, timeline: Timeline
    ) -> None:
        if arguments.import_apple_health:
            file_path: Path = Path(arguments.import_apple_health)
            AppleHealthImporter(file_path).import_data(timeline)


@dataclass
class AppleHealthImporter(Importer):
    """Importer for Apple Health data.

    Apple Health: https://www.apple.com/ios/health
    """

    file_path: Path
    """Path to the file containing Apple Health data."""

    @override
    def import_data(self, timeline: Timeline) -> None:
        with self.file_path.open(encoding="utf-8") as input_file:
            data: dict = json.load(input_file)["data"]

        if not (metrics := data.get("metrics")):
            return

        for metric in metrics:
            if metric["name"] == "walking_running_distance":
                for element in metric["data"]:
                    moment: Moment = Moment.from_datetime(
                        datetime.strptime(
                            element["date"], "%Y-%m-%d %H:%M:%S %z"
                        )
                    )
                    event: MoveEvent = MoveEvent(
                        time=Time.from_moment(moment),
                        distance=element["qty"] * 1000,
                    )
                    timeline.events.append(event)
