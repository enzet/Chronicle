"""Summary of the timeline events."""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import timedelta

from colour import Color

from chronicle.objects.core import Book, Object, Service
from chronicle.time import format_delta
from chronicle.value import Language, Subject

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class Summary:
    """Summary of the timeline events."""

    listen: defaultdict[Language, defaultdict[Service, float]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(float))
    )
    """Listening something in seconds."""

    learn: defaultdict[Subject, float] = field(
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

    write: defaultdict[Language, defaultdict[Service, float]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(float))
    )
    """Writing something in seconds."""

    write_words: defaultdict[Language, defaultdict[Service, float]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(float))
    )
    """Writing something in words."""

    speak: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Speaking something in seconds."""

    watch: defaultdict[Language, dict[Service, float]] = field(
        default_factory=lambda: defaultdict(dict)
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

    exercises: defaultdict[str, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    """Exercise repetition counts by exercise name."""

    energy_expenditure: float = 0.0
    """Energy spent during sport activities in kilocalories."""

    sport_sessions: int = 0
    """Number of sport sessions."""

    cardio_distance: float = 0.0
    """Distance covered in cardio activities in meters."""

    move_distance: float = 0.0
    """Distance covered in move activities (walk, run, hike, etc.) in meters."""

    move_energy: float = 0.0
    """Move energy expenditure in kilocalories."""

    strength_tonnage: float = 0.0
    """Total weight lifted in strength training in kg·reps."""

    body_weight_kg: float | None = None
    """Current body weight in kilograms, used for bodyweight exercise tonnage."""

    energy: float = 0.0
    """Energy consumed in kilocalories."""

    carbohydrates: float = 0.0
    """Carbohydrates consumed in grams."""

    protein: float = 0.0
    """Protein consumed in grams."""

    fat: float = 0.0
    """Fat consumed in grams."""

    saturated_fat: float = 0.0
    """Saturated fat consumed in grams."""

    fiber: float = 0.0
    """Dietary fiber consumed in grams."""

    sugar: float = 0.0
    """Total sugar consumed in grams."""

    added_sugar: float = 0.0
    """Added sugar consumed in grams."""

    omega3: float = 0.0
    """Omega-3 fatty acids consumed in grams."""

    calcium: float = 0.0
    """Calcium consumed in milligrams."""

    iron: float = 0.0
    """Iron consumed in milligrams."""

    vitamin_d: float = 0.0
    """Vitamin D consumed in international units."""

    magnesium: float = 0.0
    """Magnesium consumed in milligrams."""

    zinc: float = 0.0
    """Zinc consumed in milligrams."""

    potassium: float = 0.0
    """Potassium consumed in milligrams."""

    sodium: float = 0.0
    """Sodium consumed in milligrams."""

    vitamin_c: float = 0.0
    """Vitamin C consumed in milligrams."""

    vitamin_b12: float = 0.0
    """Vitamin B12 consumed in micrograms."""

    liquid: float = 0.0
    """Liquid consumed in milliliters."""

    shows: set[Object] = field(default_factory=set)
    """Shows watched."""

    def register_listen(
        self, duration: float, language: Language, service: Service | None
    ) -> None:
        """Register the number of seconds listened in language."""
        if not service:
            service = Service("unknown")
        self.listen[language][service] += duration

    def register_write(
        self, duration: float, language: Language, service: Service | None
    ) -> None:
        """Register the number of seconds writing in language."""
        if not service:
            service = Service("unknown")
        self.write[language][service] += duration

    def register_write_words(
        self, words: float, language: Language, service: Service | None
    ) -> None:
        """Register the number of words written in language."""
        if not service:
            service = Service("unknown")
        self.write_words[language][service] += words

    def register_speak(self, duration: float, language: Language) -> None:
        """Register the number of seconds speaking in language."""
        self.speak[language] += duration

    def register_watch(
        self, duration: float, language: Language, service: Service | None
    ) -> None:
        """Register the number of seconds watched in language."""
        if not service:
            service = Service("watch", name="Watch", color=Color("gray"))
        if service not in self.watch[language]:
            self.watch[language][service] = 0.0
        self.watch[language][service] += duration

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

    def register_liquid(self, milliliters: float) -> None:
        """Register liquid consumed in milliliters."""
        self.liquid += milliliters

    def register_energy_expenditure(self, kcal: float) -> None:
        """Register energy spent during sport activities in kilocalories."""
        self.energy_expenditure += kcal

    def register_sport_session(self) -> None:
        """Register a sport session."""
        self.sport_sessions += 1

    def register_cardio_distance(self, meters: float) -> None:
        """Register cardio distance in meters."""
        self.cardio_distance += meters

    def register_move_distance(self, meters: float) -> None:
        """Register move distance in meters."""
        self.move_distance += meters

    def register_move_energy(self, energy: float) -> None:
        """Register move energy in kilocalories."""
        self.move_energy += energy

    def register_strength_tonnage(self, kg_reps: float) -> None:
        """Register strength training tonnage in kg·reps."""
        self.strength_tonnage += kg_reps

    def register_energy(self, kcal: float) -> None:
        """Register energy consumed in kilocalories."""
        self.energy += kcal

    def register_carbohydrates(self, grams: float) -> None:
        """Register carbohydrates consumed in grams."""
        self.carbohydrates += grams

    def register_protein(self, grams: float) -> None:
        """Register protein consumed in grams."""
        self.protein += grams

    def register_fat(self, grams: float) -> None:
        """Register fat consumed in grams."""
        self.fat += grams

    def register_saturated_fat(self, grams: float) -> None:
        """Register saturated fat consumed in grams."""
        self.saturated_fat += grams

    def register_fiber(self, grams: float) -> None:
        """Register dietary fiber consumed in grams."""
        self.fiber += grams

    def register_sugar(self, grams: float) -> None:
        """Register total sugar consumed in grams."""
        self.sugar += grams

    def register_added_sugar(self, grams: float) -> None:
        """Register added sugar consumed in grams."""
        self.added_sugar += grams

    def register_omega3(self, grams: float) -> None:
        """Register omega-3 fatty acids consumed in grams."""
        self.omega3 += grams

    def register_calcium(self, mg: float) -> None:
        """Register calcium consumed in milligrams."""
        self.calcium += mg

    def register_iron(self, mg: float) -> None:
        """Register iron consumed in milligrams."""
        self.iron += mg

    def register_vitamin_d(self, iu: float) -> None:
        """Register vitamin D consumed in international units."""
        self.vitamin_d += iu

    def register_magnesium(self, mg: float) -> None:
        """Register magnesium consumed in milligrams."""
        self.magnesium += mg

    def register_zinc(self, mg: float) -> None:
        """Register zinc consumed in milligrams."""
        self.zinc += mg

    def register_potassium(self, mg: float) -> None:
        """Register potassium consumed in milligrams."""
        self.potassium += mg

    def register_sodium(self, mg: float) -> None:
        """Register sodium consumed in milligrams."""
        self.sodium += mg

    def register_vitamin_c(self, mg: float) -> None:
        """Register vitamin C consumed in milligrams."""
        self.vitamin_c += mg

    def register_vitamin_b12(self, mcg: float) -> None:
        """Register vitamin B12 consumed in micrograms."""
        self.vitamin_b12 += mcg

    def register_show(self, show: Object) -> None:
        """Register a show was watched."""
        self.shows.add(show)

    def get_learning_services(self) -> set[Service]:
        """Get all learning services."""
        return {x for y in self.learn_language.values() for x in y}

    def get_watching_services(self) -> set[Service]:
        """Get all watching services."""
        return {x for y in self.watch.values() for x in y}

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
