"""Harvest data from the Arc iOS application."""

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import override

from chronicle.harvest.core import Importer, ImportManager
from chronicle.timeline import Timeline


class ArcImportManager(ImportManager):
    """Manager for Arc import."""

    @staticmethod
    @override
    def add_argument(parser: argparse._ArgumentGroup) -> None:
        parser.add_argument(
            "--import-arc",
            help="import data from the Arc iOS application",
            metavar="<path>",
        )

    @staticmethod
    @override
    def process_arguments(
        arguments: argparse.Namespace, timeline: Timeline
    ) -> None:
        if arguments.import_arc:
            file_path: Path = Path(arguments.import_arc)
            ArcImporter(
                file_path, cache_path=Path(arguments.cache_path)
            ).import_data(timeline)


@dataclass
class ArcImporter(Importer):
    """Importer for data from the Arc iOS application.

    See https://apps.apple.com/us/app/arc-app-location-activity/id1063151918
    """

    path: Path
    """Path to directory with exported Arc data (directory with the name
    `Export` that contains directories `GPX` and `JSON`)."""

    cache_path: Path
    """Path to directory to cache data."""

    @override
    def import_data(self, timeline: Timeline) -> None:
        self.cache_path.mkdir(exist_ok=True)

        for path in (self.path / "JSON" / "Daily").iterdir():
            new_path = self.cache_path / path.name
            shutil.copyfile(path, new_path)
            subprocess.run(
                ["gzip", "--decompress", "--force", new_path], check=True
            )

        for path in self.cache_path.iterdir():
            with path.open() as input_file:
                data = json.load(input_file)
                for timeline_item in data["timelineItems"]:
                    if timeline_item["isVisit"]:
                        if (
                            "place" in timeline_item
                            and "name" in timeline_item["place"]
                        ):
                            text = f"visit {timeline_item['place']['name']}"
                        else:
                            text = "visit"
                        print(
                            timeline_item["startDate"],
                            timeline_item["endDate"],
                            text,
                        )
                    elif "activityType" in timeline_item:
                        print(
                            timeline_item["startDate"],
                            timeline_item["endDate"],
                            timeline_item["activityType"],
                        )

                    # FIXME: implement.

                    # There is also "activityType" in `timeline_item`.
