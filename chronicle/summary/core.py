from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta

from chronicle.event.value import Language
from chronicle.time import format_delta


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

    def register_listen(self, duration: float, language: Language):
        """Register the number of seconds listened in language."""
        self.listen[language] += duration

    def register_read(self, pages: float, language: Language):
        """Register the number of pages read in language."""
        self.listen[language] += pages

    def __str__(self):
        """Get human-readable text representation of the summary."""
        summary: str = ""

        summary += "Listen:\n"
        for key, value in sorted(self.listen.items(), key=lambda x: -x[1]):
            summary += (
                f"    {key if key else '(Unknown)'}: "
                f"{format_delta(timedelta(seconds=value))}\n"
            )

        return summary
