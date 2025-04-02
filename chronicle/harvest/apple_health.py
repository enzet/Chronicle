"""Harvest data from Apple Health."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import override

from chronicle.event.sport import MoveEvent
from chronicle.harvest.core import Importer
from chronicle.time import Moment, Time
from chronicle.timeline import Timeline


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

        if metrics := data.get("metrics"):
            for metric in metrics:
                if metric["name"] == "walking_running_distance":
                    for element in metric["data"]:
                        moment = Moment.from_datetime(
                            datetime.strptime(
                                element["date"], "%Y-%m-%d %H:%M:%S %z"
                            )
                        )
                        timeline.events.append(
                            MoveEvent(
                                time=Time.from_moment(moment),
                                distance=element["qty"] * 1000,
                            )
                        )
