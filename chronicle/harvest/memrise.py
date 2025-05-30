"""Harvest data from Memrise."""

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from html.parser import HTMLParser
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
    from chronicle.event.core import Event

LANGUAGE_NAMES: dict[str, tuple[str, ...]] = {
    "/writing/armn": ("армянский алфавит",),
    "/language/de": ("немецкий",),
    "/language/el": ("греческий",),
    "/language/en": ("английский (cша)",),
    "/language/es": ("испанский",),
    "/language/fr": (
        "french",
        "французский",
        "manuel de français",
        "delf b1 (часть 1)",
        "правила чтения французского языка",
    ),
    "/writing/geor": ("georgian alphabet",),
    "/language/hy": ("1000 most frequent armenian words",),
    "/language/is": ("icelandic",),
    "/language/ja": ("японский",),
    "/writing/hang": ("корейский",),
    "/language/rsl": ("русский жестовый язык", "ржя"),
    "/language/sv": ("swedish",),
}
PATTERNS = (
    re.compile(r"^(.*) \d+$"),
    re.compile(r"^(.*) \(часть \d+\)$"),
    re.compile(r"^(.*) для начинающих$"),
)
TIME_PATTERN: str = "%Y-%m-%d %H:%M:%S"
MAX_SECONDS_PER_TEST: float = 60.0


class MemriseHTMLParser(HTMLParser):
    """Parser for Memrise HTML data."""

    def __init__(self) -> None:
        super().__init__()
        self.in_learning_sessions: bool = False
        self.in_td: bool = False
        self.td: int = -1
        self.current_data: list[str | None] = []
        self.data: list[list[str | None]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag == "h2":
            for key, value in attrs:
                if key == "id" and value == "learning-sessions":
                    self.in_learning_sessions = True
                else:
                    self.in_learning_sessions = False

        if tag == "tr":
            self.current_data = [None] * 6
            self.td = 0

        if tag == "td":
            self.in_td = True
            if self.in_learning_sessions:
                self.td += 1

    def handle_data(self, data: str) -> None:
        if not self.in_learning_sessions:
            return
        if self.in_td:
            self.current_data[self.td - 1] = data.strip()
            if self.td == 0:
                self.current_data = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "td":
            self.in_td = False
        if tag == "tr" and any(self.current_data):
            self.data.append(self.current_data)


class MemriseImportManager(ImportManager):
    """Manager for Memrise import."""

    @staticmethod
    @override
    def add_argument(parser: argparse._ArgumentGroup) -> None:
        parser.add_argument(
            "--import-memrise", help="import Memrise data", metavar="<path>"
        )

    @staticmethod
    @override
    def process_arguments(
        arguments: argparse.Namespace, timeline: Timeline
    ) -> None:
        if arguments.import_memrise:
            file_path: Path = Path(arguments.import_memrise)
            MemriseImporter(file_path).import_data(timeline)


@dataclass
class MemriseImporter(Importer):
    """Importer for Memrise data."""

    path: Path
    """Path to the file containing Memrise data."""

    @override
    def import_data(self, timeline: Timeline) -> None:
        memrise_id: str = "memrise"
        service: Object = timeline.objects.get_object(
            memrise_id, Service(id=memrise_id, name="Memrise")
        )
        if not isinstance(service, Service):
            raise ChronicleObjectTypeError(memrise_id, type(service), Service)

        with self.path.open(encoding="utf-8") as input_file:
            data = input_file.read()

        parser = MemriseHTMLParser()
        parser.feed(data)

        actions: dict[str, int] = defaultdict(int)

        for (
            raw_course_name,
            _,  # Level title.
            start_time,
            completion_time,
            tests,
            _,  # Score.
        ) in parser.data:
            if not raw_course_name or not start_time or not completion_time:
                continue
            course_name = (
                raw_course_name.replace("-", " ")
                .replace("_", " ")
                .replace("  ", " ")
                .replace("  ", " ")
            )
            for pattern in PATTERNS:
                if matcher := pattern.match(course_name):
                    course_name = matcher.group(1)

            for code, names in LANGUAGE_NAMES.items():
                for name in names:
                    if course_name.lower() == name:
                        course_name = code
                        break

            start: datetime = datetime.strptime(start_time, TIME_PATTERN)
            end: datetime = datetime.strptime(completion_time, TIME_PATTERN)

            if not tests:
                continue

            actions[course_name] += int(tests)
            seconds_per_test: float = (end - start).total_seconds() / int(tests)

            # If the time per test is less than 1 minute, the time stamps look
            # valid and we want to use the actual time spent on the session.
            # Otherwise, we approximate the time spent on the session as 16
            # seconds per test.
            duration: Timedelta | None = None
            if seconds_per_test >= MAX_SECONDS_PER_TEST:
                duration = Timedelta.from_delta(
                    timedelta(seconds=float(tests) * 16.0)
                )

            subject: Subject | None = Subject.from_string(course_name)
            if not subject:
                message: str = f"Unknown course `{course_name}`."
                raise ValueError(message)

            event: Event = LearnEvent(
                Time.from_moments(
                    Moment.from_datetime(start), Moment.from_datetime(end)
                ),
                subject=subject,
                service=service,
                actions=float(tests),
                duration=duration,
            )
            timeline.events.append(event)
