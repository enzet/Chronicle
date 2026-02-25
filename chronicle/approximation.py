"""Approximation for the events in the timeline."""

from collections import defaultdict
from dataclasses import dataclass, field

from rich import print as rich_print
from rich.table import Table

from chronicle.event.art import ReadEvent
from chronicle.event.core import Event
from chronicle.objects.core import Book, Language

DEBUG: bool = False


@dataclass
class PagesTime:
    """Time spent on reading pages."""

    pages: float = 0.0
    time: float = 0.0

    def __add__(self, other: "PagesTime") -> "PagesTime":
        return PagesTime(self.pages + other.pages, self.time + other.time)

    def get_speed(self) -> float:
        """Get reading speed in pages per hour."""
        return self.pages / self.time * 3600.0

    def get_pages_and_time(self) -> str:
        return f"{self.pages:.1f}/{self.time / 3600.0:.1f}"


@dataclass
class Approximation:
    """Approximation for the events in the timeline."""

    language_to_data: dict[Language, PagesTime] = field(
        default_factory=lambda: defaultdict(PagesTime)
    )
    language_year_to_data: dict[Language, dict[int, PagesTime]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(PagesTime))
    )
    book_to_data: dict[Book, PagesTime] = field(
        default_factory=lambda: defaultdict(PagesTime)
    )

    def approximate_reading_speed(self, events: list[Event]) -> None:
        """Approximate reading speed."""

        for event in events:
            if not isinstance(event, ReadEvent):
                continue

            pages: float | None = event.get_pages()
            duration: float | None = event.get_duration()

            if not pages or not duration:
                continue

            # We're assuming that a reading event cannot be longer than 5 hours.
            if duration > 5 * 3600:
                continue

            data: PagesTime = PagesTime(pages, duration)
            self.language_to_data[event.get_language()] += data
            self.language_year_to_data[event.get_language()][
                event.time.get_moment().year
            ] += data
            if event.book:
                self.book_to_data[event.book] += data

        if DEBUG:
            table = Table(title="Reading speed by language")
            table.add_column("Language")
            table.add_column("Speed (p/h)")
            table.add_column("P/h")
            for language, data in self.language_to_data.items():
                table.add_row(
                    language.to_string(),
                    f"{data.get_speed():.1f}",
                    data.get_pages_and_time(),
                )
            rich_print(table)

            table = Table(title="Reading speed by language and year")
            table.add_column("Language")
            table.add_column("Year")
            table.add_column("Speed (p/h)")
            table.add_column("P/h")
            for language, data in self.language_year_to_data.items():
                for year, d in sorted(data.items(), key=lambda x: x[0]):
                    table.add_row(
                        language.to_string(),
                        str(year),
                        f"{d.get_speed():.1f}",
                        d.get_pages_and_time(),
                    )
            rich_print(table)

            table = Table(title="Reading speed by book")
            table.add_column("Book")
            table.add_column("Speed (p/h)")
            table.add_column("P/h")
            for book, data in self.book_to_data.items():
                table.add_row(
                    book.to_string(),
                    f"{data.get_speed():.1f}",
                    data.get_pages_and_time(),
                )
            rich_print(table)

    def get_speed(self, book: Book, year: int | None = None) -> float | None:
        """Get approximated reading speed in pages per hour for a book."""

        if book in self.book_to_data:
            return self.book_to_data[book].get_speed()
        if year is not None and book.language in self.language_year_to_data:
            return self.language_year_to_data[book.language][year].get_speed()
        if book.language in self.language_to_data:
            return self.language_to_data[book.language].get_speed()
        return None
