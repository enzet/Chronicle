import json
import shutil
import subprocess
from pathlib import Path

from chronicle.harvest.core import Importer
from chronicle.timeline import Timeline


class ArcImporter(Importer):
    """
    Importer for data from the Arc iOS application.

    See https://apps.apple.com/us/app/arc-app-location-activity/id1063151918
    """

    def __init__(self, path: Path, cache_path: Path) -> None:
        """
        :param path: path to directory with exported Arc data (directory with
            the name `Export` that contains directories `GPX` and `JSON`)
        """
        self.path: Path = path
        self.cache_path: Path = cache_path / "arc"

    def import_data(self, timeline: Timeline) -> None:
        self.cache_path.mkdir(exist_ok=True)

        for path in (self.path / "JSON" / "Daily").iterdir():
            new_path = self.cache_path / path.name
            shutil.copyfile(path, new_path)
            subprocess.run(["gzip", "--decompress", "--force", new_path])

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
