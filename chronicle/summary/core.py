from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import timedelta

from chronicle.value import Language, Subject
from chronicle.objects.core import Book, Service
from chronicle.time import format_delta

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class Summary:
    listen: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Listening something in seconds."""

    learn: defaultdict[str, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Learn something in seconds."""

    learn_language: defaultdict[Language, dict[Service, float]] = field(
        default_factory=lambda: defaultdict(dict)
    )
    """Learn language in seconds."""

    read: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Reading something in seconds."""

    read_pages: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Reading something in pages."""

    write: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Writing something in seconds."""

    speak: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Speaking something in seconds."""

    watch: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Watching something in seconds."""

    finished_books: set = field(default_factory=set)
    """Books finished."""

    sleep: float = 0
    """Sleeping time in seconds."""

    dishes: Counter = field(default_factory=lambda: Counter())
    """Counter for dishes."""

    work: float = 0
    """Working time in seconds."""

    abs_: int = 0
    """Number of abdominal crunches performed."""

    dips: int = 0
    """Number of dips performed."""

    push_ups: int = 0
    """Number of push-ups performed."""

    chin_ups: int = 0
    """Number of chin-ups performed."""

    squats: int = 0
    """Number of squats performed."""

    burpees: int = 0
    """Number of burpees performed."""

    jumping_jacks: int = 0
    """Number of jumping jacks performed."""

    russian_twists: int = 0
    """Number of Russian twists performed."""

    def register_listen(self, duration: float, language: Language) -> None:
        """Register the number of seconds listened in language."""
        self.listen[language] += duration

    def register_write(self, duration: float, language: Language) -> None:
        """Register the number of seconds writing in language."""
        self.write[language] += duration

    def register_speak(self, duration: float, language: Language) -> None:
        """Register the number of seconds speaking in language."""
        self.speak[language] += duration

    def register_watch(self, duration: float, language: Language) -> None:
        """Register the number of seconds watched in language."""
        self.watch[language] += duration

    def register_learn(
        self, duration: float, subject: Subject, service: Service | None
    ) -> None:
        """Register the number of seconds learning a subject."""
        self.learn[subject] += duration

        language: Language | None = subject.get_language()
        if language:
            if not service:
                service = Service("unknown")
            if service not in self.learn_language[language]:
                self.learn_language[language][service] = 0.0
            self.learn_language[language][service] += duration

    def register_read_pages(self, pages: float, language: Language) -> None:
        """Register the number of pages read in language."""
        self.read_pages[language] += pages

    def register_read(self, duration: float, language: Language) -> None:
        """Register the number of seconds reading in language."""
        self.read[language] += duration

    def register_finished_book(self, book: Book) -> None:
        """Register new finished book."""
        self.finished_books.add(book)

    def register_sleep(self, duration: float) -> None:
        """Register sleeping time in seconds."""
        self.sleep += duration

    def register_dish(self, dish: str) -> None:
        """Register a dish was cooked."""
        self.dishes.update({dish: 1})

    def register_work(self, duration: float) -> None:
        """Register working time in seconds."""
        self.work += duration

    def __str__(self) -> str:
        """Get human-readable text representation of the summary."""
        summary: str = ""

        summary += "Read:\n"
        for key, value in sorted(self.read.items(), key=lambda x: -x[1]):
            summary += f"    {key if key else '(Unknown)'}: {value}\n"

        summary += "Listen:\n"
        for key, value in sorted(self.listen.items(), key=lambda x: -x[1]):
            summary += (
                f"    {key if key else '(Unknown)'}: "
                f"{format_delta(timedelta(seconds=value))}\n"
            )

        summary += f"Sleep: {format_delta(timedelta(seconds=self.sleep))}\n"

        summary += f"Work: {format_delta(timedelta(seconds=self.work))}\n"

        summary += "Dishes:\n"
        for key, value in sorted(self.dishes.items(), key=lambda x: -x[1]):
            summary += f"    {key}: {value}\n"

        summary += "Finished books:\n"
        for book in self.finished_books:
            summary += f"    {book.title}\n"

        return summary
