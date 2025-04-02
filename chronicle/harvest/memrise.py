import re
from collections import defaultdict
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path

from chronicle.event.common import LearnEvent
from chronicle.event.core import Event
from chronicle.harvest.core import Importer
from chronicle.time import Moment, Time, Timedelta
from chronicle.timeline import Timeline
from chronicle.value import Subject

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


class MemriseHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_learning_sessions: bool = False
        self.in_td: bool = False
        self.td: int = -1
        self.current_data = []
        self.data = []

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
        if tag == "tr":
            if any(self.current_data):
                self.data.append(self.current_data)


class MemriseImporter(Importer):
    """Importer for Memrise data."""

    def __init__(self, path: Path):
        self.path: Path = path

    def import_data(self, timeline: Timeline) -> None:
        with self.path.open() as input_file:
            data = input_file.read()

        parser = MemriseHTMLParser()
        parser.feed(data)

        actions = defaultdict(int)

        for (
            course_name,
            level_title,
            start_time,
            completion_time,
            tests,
            score,
        ) in parser.data:
            if not course_name or not start_time or not completion_time:
                continue
            course_name: str = (
                course_name.replace("-", " ")
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
            if seconds_per_test >= 60:
                duration = Timedelta.from_delta(
                    timedelta(seconds=float(tests) * 16.0)
                )

            event: Event = LearnEvent(
                Time.from_moments(
                    Moment.from_datetime(start), Moment.from_datetime(end)
                ),
                subject=Subject.from_string(course_name),
                service=timeline.objects.get_object("memrise"),
                actions=tests,
                duration=duration,
            )
            timeline.events.append(event)
