from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta

from chronicle.event.value import Language
from chronicle.time import format_delta

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class Summary:
    listen: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Listening something in seconds."""

    read: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Reading something in pages."""

    sleep: float = 0
    """Sleeping time in seconds."""

    def register_listen(self, duration: float, language: Language):
        """Register the number of seconds listened in language."""
        self.listen[language] += duration

    def register_read(self, pages: float, language: Language):
        """Register the number of pages read in language."""
        self.read[language] += pages

    def register_sleep(self, duration: float):
        self.sleep += duration

    def __str__(self):
        """Get human-readable text representation of the summary."""
        summary: str = ""

        summary += "Listen:\n"
        for key, value in sorted(self.listen.items(), key=lambda x: -x[1]):
            summary += (
                f"    {key if key else '(Unknown)'}: "
                f"{format_delta(timedelta(seconds=value))}\n"
            )
        summary += f"Sleep: {format_delta(timedelta(seconds=self.sleep))}\n"

        return summary
