"""Harvest data from Duolingo."""

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, override

from chronicle.errors import ChronicleObjectTypeError
from chronicle.event.common import LearnEvent
from chronicle.harvest.core import Importer, ImportManager
from chronicle.objects.core import Object, Service
from chronicle.time import Moment, Time, Timedelta
from chronicle.timeline import Timeline
from chronicle.value import Subject

if TYPE_CHECKING:
    from collections.abc import Iterator

courses: list[tuple[str, str, Subject]] = [
    ("en", "English", Subject(["language", "en"])),
    ("en_ar", "Arabic", Subject(["writing", "arab"])),
    ("en_de", "German", Subject(["language", "de"])),
    ("en_eo", "Esperanto", Subject(["language", "eo"])),
    ("en_es", "Spanish", Subject(["language", "es"])),
    ("en_fr", "French", Subject(["language", "fr"])),
    ("en_he", "Hebrew", Subject(["writing", "hebr"])),
    ("en_hi", "Hindi", Subject(["writing", "deva"])),
    ("en_it", "Italian", Subject(["language", "it"])),
    ("en_ja", "Japanese", Subject(["language", "ja"])),
    ("en_ko", "Korean", Subject(["writing", "hang"])),
    ("en_la", "Latin", Subject(["language", "la"])),
    ("en_la2", "Latin2", Subject(["language", "la"])),
    ("en_no", "Norwegian", Subject(["language", "no"])),
    ("en_no2", "Norwegian2", Subject(["language", "no"])),
    ("ru_de", "German (ru)", Subject(["language", "de"])),
    ("ru_es", "Spanish (ru)", Subject(["language", "es"])),
    ("ru_fr", "French (ru)", Subject(["language", "fr"])),
]


def approximate_duration(xp: int, date: datetime) -> Timedelta:
    """Approximate time to complete Duolingo XP.

    There is XP inflation, so the duration is different for different years. In
    2020 in one lesson one can earn 10 XP, while in 2024 one can earn 105 XP for
    one lesson.
    """
    match date.year:
        case 2023:
            return Timedelta(delta=timedelta(seconds=xp * 8.39))
        case 2024:
            return Timedelta(delta=timedelta(seconds=xp * 5))
        case 2025:
            return Timedelta(delta=timedelta(seconds=xp * 4))
        case _:
            return Timedelta(delta=timedelta(seconds=xp * 20))


class DuolingoImportManager(ImportManager):
    """Manager for Duolingo import."""

    @staticmethod
    @override
    def add_argument(parser: argparse._ArgumentGroup) -> None:
        parser.add_argument(
            "--import-duolingo", help="import Duolingo data", metavar="<path>"
        )
        parser.add_argument(
            "--import-duome",
            help="import Duolingo data using Duome",
            metavar="<path>",
        )

    @staticmethod
    @override
    def process_arguments(
        arguments: argparse.Namespace, timeline: Timeline
    ) -> None:
        file_path: Path

        if arguments.import_duolingo:
            file_path = Path(arguments.import_duolingo)
            DuolingoImporter(file_path).import_data(timeline)

        if arguments.import_duome:
            file_path = Path(arguments.import_duome)
            DuomeImporter(file_path).import_data(timeline)


@dataclass
class DuolingoImporter(Importer):
    """Importer for Duolingo data."""

    file_path: Path
    """Path to the CSV file containing Duolingo data."""

    def import_data(self, timeline: Timeline) -> None:
        """Import Duolingo data from a CSV file.

        The file contains XP values for each course. The first column is the
        date, other columns are XP values. First row is a header, containing
        course identifiers.
        """
        duolingo_id: str = "duolingo"
        service: Object = timeline.objects.get_object(
            duolingo_id, Service(id=duolingo_id, name="Duolingo")
        )
        if not isinstance(service, Service):
            raise ChronicleObjectTypeError(duolingo_id, type(service), Service)

        with self.file_path.open(encoding="utf-8") as input_file:
            reader: Iterator[list[str]] = csv.reader(input_file)
            header: list[str] = [x.strip() for x in next(reader)]

            last_date: datetime | None = None
            last_values: dict[str, int] = {}

            for row in reader:
                if row[0].strip().startswith("#"):
                    # Skip comments.
                    continue
                date: datetime = datetime.strptime(row[0], "%Y-%m-%d")
                for index, value in enumerate(row[1:]):
                    course_id: str = header[index + 1]
                    subject: Subject | None = None
                    for course in courses:
                        if course[0] == course_id:
                            subject = course[2]
                            break

                    if not subject:
                        # Skip unknown courses or some additional data.
                        continue

                    if not value.strip() or value.strip() == "?":
                        # Skip unknown values.
                        continue

                    course_value: int = int(value)
                    actions: int = course_value - last_values.get(course_id, 0)
                    if last_date and actions > 0:
                        start: Moment = Moment.from_datetime(last_date)
                        end: Moment = Moment.from_datetime(date)
                        time: Time = Time.from_moments(start, end)
                        event: LearnEvent = LearnEvent(
                            time,
                            subject=subject,
                            service=service,
                            actions=actions,
                            duration=approximate_duration(actions, date),
                        )
                        timeline.events.append(event)

                    last_values[course_id] = course_value

                last_date = date


@dataclass
class DuomeImporter(Importer):
    """Importer for Duolingo data using Duome.

    See https://duome.eu
    """

    file_path: Path
    """Path to the file containing Duolingo data."""

    def import_data(self, timeline: Timeline) -> None:
        """Import Duolingo data from a file.

        The file contains data copied from Duome project
        (https://duome.eu/<user name>), separated by new lines and specified
        date. Example:

        ```
        2000-01-01
         Japanese W 587 L 24 XP 27550

        2000-01-02
         Japanese W 587 L 24 XP 28921
         Norwegian W 21 L 5 XP 390
        ```
        """
        duolingo_id: str = "duolingo"
        service: Object = timeline.objects.get_object(
            duolingo_id, Service(id=duolingo_id, name="Duolingo")
        )
        if not isinstance(service, Service):
            raise ChronicleObjectTypeError(duolingo_id, type(service), Service)

        data: dict[str, list[tuple[datetime, int]]] = defaultdict(list)

        date: datetime | None = None

        with self.file_path.open(encoding="utf-8") as input_file:
            for raw_line in input_file.readlines():
                line: str = raw_line[:-1]
                if not line:
                    continue
                if not line.startswith(" ") or line.startswith("\t"):
                    date = datetime.strptime(line, "%Y-%m-%d")
                else:
                    parts: list[str] = [
                        part for part in line.split(" ") if part.strip()
                    ]
                    course_name_end: int = parts.index("W")
                    course_name: str = " ".join(parts[:course_name_end])
                    for index, part in enumerate(parts):
                        if part == "XP":
                            value: int = int(parts[index + 1])
                            if date:
                                data[course_name].append((date, value))
                            break

        for course_name, values in data.items():
            previous_date: datetime | None = None
            previous_value: int | None = None

            for date, value in values:
                if (
                    previous_date
                    and previous_value
                    and (value - previous_value) > 0
                ):
                    actions: int = value - previous_value
                    start: Moment = Moment.from_datetime(previous_date)
                    end: Moment = Moment.from_datetime(date)
                    time: Time = Time.from_moments(start, end)
                    subject: Subject | None = None
                    for course in courses:
                        if course[1] == course_name:
                            subject = course[2]
                            break
                    if not subject:
                        message = f"Unknown course `{course_name}`."
                        raise ValueError(message)
                    event: LearnEvent = LearnEvent(
                        time,
                        subject=subject,
                        service=service,
                        actions=actions,
                        duration=approximate_duration(actions, date),
                    )
                    timeline.events.append(event)
                previous_date = date
                previous_value = value
