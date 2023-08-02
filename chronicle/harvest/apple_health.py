import json
from datetime import datetime
from pathlib import Path

from chronicle.event.sport import MoveEvent
from chronicle.timeline import Timeline
from chronicle.time import Time, Moment
from chronicle.harvest.core import Importer


class AppleHealthImporter(Importer):
    """
    Importer for Apple Health data.

    Apple Health: https://www.apple.com/ios/health
    """

    def __init__(self, file_path: Path):
        self.file_path: Path = file_path

    def import_data(self, timeline: Timeline) -> None:
        with self.file_path.open() as input_file:
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
                                time=str(Time.from_moment(moment)),
                                distance=element["qty"] * 1000,
                            )
                        )
