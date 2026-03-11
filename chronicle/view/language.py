"""Language learning viewer."""

import argparse
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from colour import Color
from matplotlib import pyplot as plt
from rich import box
from rich.console import Console
from rich.table import Table

from chronicle.event.core import Event
from chronicle.objects.core import Service
from chronicle.timeline import Timeline
from chronicle.value import Language

if TYPE_CHECKING:
    from chronicle.summary.core import Summary

DARK_COLOR_SCHEME: dict[str, str] = {
    "background": "#000000",
    "accent": "#EEEEEE",
}
LIGHT_COLOR_SCHEME: dict[str, str] = {
    "background": "#FFFFFF",
    "accent": "#000000",
}
COLOR_SCHEME: dict[str, str] = DARK_COLOR_SCHEME

SECONDS_IN_HOUR: float = 3600.0
MINUTES_IN_HOUR: float = 60.0
BAR_CAPTION_MIN_RATIO: float = 0.05
MAX_GOAL_ROWS: int = 5


with (Path.home() / ".config" / "machina" / "config.yml").open() as input_file:
    CONFIG: dict[str, Any] = yaml.safe_load(input_file)


@dataclass
class Method:
    """Method of language learning."""

    id_: str
    name: str
    color: Color
    hatch: str

    def __hash__(self) -> int:
        return hash(self.id_)


SPEAK_METHOD: Method = Method("speak", "Speak", Color("#4C617D"), "----")
LISTEN_METHOD: Method = Method("listen", "Listen", Color("#8CA48C"), "....")
READ_METHOD: Method = Method("read", "Read", Color("#A79186"), "||||")
WRITE_METHOD: Method = Method("write", "Write", Color("#6B8D6A"), "xxxx")
LEARN_METHOD: Method = Method("learn", "Learn", Color("#E2C0B9"), "////")
WATCH_METHOD: Method = Method("watch", "Watch", Color("#E5B1C0"), "\\\\\\\\")


methods: list[Method] = [
    SPEAK_METHOD,
    LISTEN_METHOD,
    READ_METHOD,
    WRITE_METHOD,
    LEARN_METHOD,
    WATCH_METHOD,
]


def plus(a: list[float], b: list[float]) -> list[float]:
    """Plus two lists."""
    return [a[i] + b[i] for i in range(len(a))]


def format_time(hours: float) -> str:
    """Format time."""
    h, m = int(hours), int(hours * 60 % 60)
    return f"{h}:{m:02d}"


@dataclass
class LanguageCategory:
    """Language category."""

    id_: str
    name: str

    @classmethod
    def from_id(cls, id_: str) -> "LanguageCategory":
        """Create language category from ID."""
        for category in LANGUAGE_CATEGORIES:
            if category.id_ == id_:
                return category
        message: str = f"Unknown language category ID: {id_}"
        raise ValueError(message)

    def __hash__(self) -> int:
        return hash(self.id_)


SPEAK_CATEGORY: LanguageCategory = LanguageCategory("speak", "Speak")
LISTEN_CATEGORY: LanguageCategory = LanguageCategory("listen", "Listen")
READ_CATEGORY: LanguageCategory = LanguageCategory("read", "Read")
WRITE_CATEGORY: LanguageCategory = LanguageCategory("write", "Write")
LEARN_CATEGORY: LanguageCategory = LanguageCategory("learn", "Learn")
WATCH_CATEGORY: LanguageCategory = LanguageCategory("watch", "Watch")


LANGUAGE_CATEGORIES: list[LanguageCategory] = [
    LEARN_CATEGORY,
    SPEAK_CATEGORY,
    LISTEN_CATEGORY,
    READ_CATEGORY,
    WRITE_CATEGORY,
]


@dataclass
class LanguageCategoryData:
    """Data for language category."""

    data: defaultdict[Language, defaultdict[LanguageCategory, float]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(float))
    )
    """`<language code>` to data."""

    def add(
        self,
        language: Language,
        category: LanguageCategory,
        value: float,
    ) -> None:
        """Add data to the data."""

        self.data[language][category] += value


@dataclass
class LanguageMethodServiceData:
    """Data for language learning progress."""

    data: defaultdict[
        Language,
        defaultdict[Method, defaultdict[Service, float]],
    ] = field(
        default_factory=lambda: defaultdict(
            lambda: defaultdict(lambda: defaultdict(float))
        )
    )
    """`<language code>` to `<method>` to `<service>` to data.

    E.g. `data["fr"]["learn"]["@duolingo"]` or
    `data["fr"]["watch"]["@youtube"]`.
    """

    totals: defaultdict[Language, float] = field(
        default_factory=lambda: defaultdict[Language, float](float)
    )
    """Total time spent on language learning."""

    def add(
        self,
        language: Language,
        method: Method,
        service: Service,
        value: float,
    ) -> None:
        """Add data to the data."""

        self.data[language][method][service] = value
        self.totals[language] += value

    def get_total(self, language: Language) -> float:
        """Get total time spent on language learning."""

        result: float = 0.0

        for method in self.data[language]:
            for service in self.data[language][method]:
                result += self.data[language][method][service]

        return result

    def get_language_max(self) -> float:
        return max(self.totals.values())

    def get_languages(self) -> list[Language]:
        """Get all languages."""
        return sorted(self.data, key=lambda language: self.totals[language])

    def get_language_category_data(self) -> LanguageCategoryData:
        """Get data for language category."""

        data: LanguageCategoryData = LanguageCategoryData()
        for language in self.data:
            for method in self.data[language]:
                value: float = (
                    sum(self.data[language][method].values()) / SECONDS_IN_HOUR
                )
                if method == SPEAK_METHOD:
                    data.add(language, SPEAK_CATEGORY, value)
                elif method == LISTEN_METHOD:
                    data.add(language, LISTEN_CATEGORY, value)
                elif method == READ_METHOD:
                    data.add(language, READ_CATEGORY, value)
                elif method == WRITE_METHOD:
                    data.add(language, WRITE_CATEGORY, value)
                elif method == LEARN_METHOD:
                    data.add(language, LEARN_CATEGORY, value)
                elif method == WATCH_METHOD:
                    data.add(language, LISTEN_CATEGORY, value / 2.0)
                    data.add(language, READ_CATEGORY, value / 2.0)

        return data


@dataclass
class LanguageLearningDataByTime:
    """Data for language learning progress by time."""

    xs: list[datetime] = field(default_factory=list)
    data: dict[Language, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def get_languages(self) -> list[Language]:
        """Get all languages."""
        return sorted(self.data, key=lambda language: sum(self.data[language]))

    def smooth(self, size: int, mode: str = "average") -> None:
        """Smooth data by time."""

        match mode:
            case "average":
                for language, values in self.data.items():
                    new_values: list[float] = [
                        sum(values[index - size + 1 : index + 1]) / size
                        for index in range(len(values))
                    ]
                    self.data[language] = new_values

            case "exponential":
                # Exponential moving average.
                lambda_: float = 2.0 / (size + 1)
                for language, values in self.data.items():
                    current: float = 0.0
                    new_values: list[float] = []
                    for value in values:
                        current *= 1 - lambda_
                        current += value * lambda_
                        new_values.append(current)
                    self.data[language] = new_values

        self.xs.append(self.xs[-1])
        for language in self.data:
            self.data[language].append(0.0)

    def make_cumulative(self) -> None:
        """Make cumulative data."""
        for language in self.data:
            cumulative: list[float] = []
            for value in self.data[language]:
                cumulative.append(
                    cumulative[-1] + value if cumulative else value
                )
            self.data[language] = cumulative


@dataclass
class LanguageLearningViewer:
    """Viewer of language learning progress."""

    timeline: Timeline

    def process_command(self, arguments: argparse.Namespace) -> None:
        """Process language command."""

        filter_: Callable[[Event], bool] | None = None
        if arguments.interval != 0:
            filter_ = Timeline.get_filter(
                from_date=datetime.now(UTC)
                - timedelta(days=arguments.interval),
                to_date=None,
            )
        total_summary: Summary = self.timeline.get_summary(filter_)

        keys: set[Language] = (
            set(total_summary.listen.keys())
            | set(total_summary.read.keys())
            | set(total_summary.watch.keys())
            | set(total_summary.learn_language.keys())
        )
        languages: set[Language] = {x for x in keys if x}
        excluded_languages: set[Language] = {
            Language(x) for x in arguments.exclude_languages
        }
        languages = {x for x in languages if x not in excluded_languages}

        learning_services: list[Service] = list(
            total_summary.get_learning_services()
        )

        match arguments.form:
            case "table":
                self.print_table(
                    languages,
                    learning_services,
                    self.construct_data(filter_, languages),
                    total_threshold=arguments.margin,
                    style=arguments.style,
                    colors=arguments.colors,
                )
            case "plot":
                self.plot_languages(
                    filter_=filter_,
                    languages=languages,
                    period=arguments.period,
                    smooth=arguments.smooth,
                    path=arguments.file,
                    plot_type=arguments.plot_type,
                    cumulative=arguments.cumulative,
                    interval=arguments.interval,
                )
            case "bars":
                self.plot_bar(
                    self.construct_data(filter_, languages),
                    arguments.file,
                    arguments.margin,
                )

    def construct_data_by_time(
        self,
        filter_: Callable[[Event], bool] | None,
        languages: set[Language],
        period: str,
    ) -> LanguageLearningDataByTime:
        """Construct data for plotting language learning progress by time."""

        data: LanguageLearningDataByTime = LanguageLearningDataByTime()

        events = self.timeline.get_events_by_period(period, filter_)

        for point, _, summary in events:
            data.xs.append(point)
            for language in languages:
                value: float = 0.0
                if language in summary.learn_language:
                    value += sum(summary.learn_language[language].values())
                if language in summary.watch:
                    value += sum(summary.watch[language].values())
                if language in summary.listen:
                    value += sum(summary.listen[language].values())
                if language in summary.read:
                    value += summary.read[language]
                if language in summary.write:
                    value += sum(summary.write[language].values())
                if language in summary.write_words:
                    value += sum(summary.write_words[language].values())
                if language in summary.speak:
                    value += summary.speak[language]
                data.data[language].append(value)

        return data

    def construct_data(
        self,
        filter_: Callable[[Event], bool] | None,
        languages: set[Language],
    ) -> LanguageMethodServiceData:
        """Construct data for plotting language learning progress."""

        data: LanguageMethodServiceData = LanguageMethodServiceData()

        summary: Summary = self.timeline.get_summary(filter_)

        for language in languages:
            value: float

            if language in summary.learn_language:
                for service in summary.learn_language[language]:
                    value = summary.learn_language[language][service]
                    if not service.color:
                        service.color = LEARN_METHOD.color
                    data.add(language, LEARN_METHOD, service, value)

            if language in summary.listen:
                for service in summary.listen[language]:
                    value = summary.listen[language][service]
                    if not service.color:
                        service.color = LISTEN_METHOD.color
                    data.add(language, LISTEN_METHOD, service, value)

            if language in summary.watch:
                for service in summary.watch[language]:
                    value = summary.watch[language][service]
                    if not service.color:
                        service.color = WATCH_METHOD.color
                    data.add(language, WATCH_METHOD, service, value)

            read: float = summary.read.get(language, 0.0)
            data.add(
                language,
                READ_METHOD,
                Service("unknown", color=READ_METHOD.color),
                read,
            )

            if language in summary.write:
                for service in summary.write[language]:
                    value = summary.write[language][service]
                    if not service.color:
                        service.color = WRITE_METHOD.color
                    data.add(language, WRITE_METHOD, service, value)

            if language in summary.write_words:
                for service in summary.write_words[language]:
                    value = summary.write_words[language][service]
                    if not service.color:
                        service.color = WRITE_METHOD.color
                    data.add(language, WRITE_METHOD, service, value * 2.0)

            speak: float = summary.speak.get(language, 0.0)
            data.add(
                language,
                SPEAK_METHOD,
                Service("unknown", color=SPEAK_METHOD.color),
                speak,
            )

        return data

    def plot_languages(
        self,
        path: Path | None = None,
        filter_: Callable[[Event], bool] | None = None,
        languages: set[Language] | None = None,
        *,
        period: str,
        cumulative: bool = False,
        smooth: int = 0,
        plot_type: str,
        interval: int = 0,
    ) -> None:
        """Plot language learning progress."""

        # Set fonts in matplotlib.
        if languages is None:
            languages = set[Language]()
        plt.rcParams["font.family"] = "SF Pro"
        plt.rcParams["font.size"] = 9

        # Remove box around the plot.
        for position in "right", "top", "left", "bottom":
            plt.rcParams[f"axes.spines.{position}"] = False
        for axis in "x", "y":
            plt.rcParams[f"{axis}tick.major.size"] = 0

        if plot_type == "stack":
            data_by_time: LanguageLearningDataByTime = (
                self.construct_data_by_time(filter_, languages, period)
            )
            keys = sorted(
                data_by_time.data,
                key=lambda x: -(
                    data_by_time.data[x][-1] if data_by_time.data[x] else 0
                ),
            )
            plt.stackplot(
                data_by_time.xs,
                *[data_by_time.data[key] for key in keys],
                labels=[key.to_string() for key in keys],
                colors=[key.get_color() for key in keys],
            )
            plt.legend(loc="upper left")
            plt.show()

        elif plot_type in ["bar", "fill"]:
            match period:
                case "day":
                    width = 1.0
                case "week":
                    width = 7.0
                case "month":
                    width = 31.0
                case "year":
                    width = 365.0

            data_by_time: LanguageLearningDataByTime = (
                self.construct_data_by_time(filter_, languages, period)
            )
            if smooth:
                data_by_time.smooth(smooth)
            if cumulative:
                data_by_time.make_cumulative()

            for language in data_by_time.get_languages():
                for index in range(len(data_by_time.data[language])):
                    data_by_time.data[language][index] /= width

            cummulative_values: list[float] = [0.0 for _ in data_by_time.xs]
            for language in data_by_time.get_languages():
                cummulative_values = plus(
                    cummulative_values, data_by_time.data[language]
                )
            for language in data_by_time.get_languages():
                values: list[float] = data_by_time.data[language]
                if plot_type == "bar":
                    plt.bar(
                        data_by_time.xs,
                        [
                            value / MINUTES_IN_HOUR
                            for value in cummulative_values
                        ],
                        label=language.to_string(),
                        color=language.get_color(),
                        width=width,
                    )
                elif plot_type == "fill":
                    plt.fill(
                        data_by_time.xs[0:1]
                        + data_by_time.xs
                        + data_by_time.xs[-1:],
                        [
                            value / MINUTES_IN_HOUR
                            for value in [0, *cummulative_values, 0]
                        ],
                        label=language.to_string(),
                        color=language.get_color(),
                    )
                for index in range(len(values)):
                    cummulative_values[index] -= values[index]

            if not interval:
                plt.xlim(datetime(2017, 9, 22, tzinfo=UTC), datetime.now(UTC))
            else:
                # We can also use `plt.xlim(None, data_by_time.xs[-1])` here.
                plt.xlim(None, datetime.now(UTC))
            plt.ylim(0, None)
            # We can also use `plt.legend(loc="upper left")` here.

            plt.ylabel("Minutes per day")

            if path:
                plt.gcf().set_size_inches(14, 4)
                plt.savefig(path)
            else:
                plt.show()

        elif plot_type == "percent":
            data_by_time: LanguageLearningDataByTime = (
                self.construct_data_by_time(filter_, languages, period)
            )
            data_by_time.smooth(4)

            cummulative_values: list[float] = [0.0 for _ in data_by_time.xs]
            for language in data_by_time.get_languages():
                cummulative_values = plus(
                    cummulative_values, data_by_time.data[language]
                )
            percent_values: list[float] = [100.0 for _ in data_by_time.xs]
            percent_values[0] = 0.0
            percent_values[-1] = 0.0
            for language in data_by_time.get_languages():
                values: list[float] = data_by_time.data[language]
                plt.fill(
                    data_by_time.xs,
                    list(percent_values),
                    label=language.to_string(),
                    color=language.get_color(),
                    linewidth=0,
                )
                for index in range(len(values)):
                    if cummulative_values[index] == 0.0:
                        continue
                    percent_values[index] -= (
                        values[index] / cummulative_values[index] * 100.0
                    )
            plt.xlim(datetime(2017, 9, 22, tzinfo=UTC), datetime.now(UTC))
            plt.ylim(0, None)
            # We can also use `plt.legend(loc="upper left")` here.
            if path:
                plt.gcf().set_size_inches(14, 4)
                plt.savefig(path)
            else:
                plt.show()

    def plot_bar(
        self,
        data: LanguageMethodServiceData,
        path: Path | None = None,
        total_threshold: float = 0.0,
    ) -> None:
        """Plot language learning progress as a bar chart."""

        mode: str = "color"

        match mode:
            case "paper":

                def foreground_color(_color: Color) -> Color:
                    return Color("black")

                def background_color(_color: Color) -> Color:
                    return Color("white")
            case "black":

                def foreground_color(_color: Color) -> Color:
                    return Color("white")

                def background_color(_color: Color) -> Color:
                    return Color("black")
            case "color":

                def foreground_color(_color: Color) -> Color:
                    return Color("white")

                def background_color(color: Color) -> Color:
                    return color

        for language in data.get_languages():
            if data.totals[language] / SECONDS_IN_HOUR < total_threshold:
                continue
            left: float = 0.0
            for method in methods:
                for service in data.data[language][method]:
                    value: float = (
                        data.data[language][method][service] / SECONDS_IN_HOUR
                    )
                    plt.barh(
                        language.to_string(),
                        value,
                        left=left,
                        color=background_color(service.color).hex,
                        edgecolor=foreground_color(service.color).hex,
                        linewidth=0.5,
                    )
                    ratio: float = (
                        value / data.get_language_max() * SECONDS_IN_HOUR
                    )
                    if ratio > BAR_CAPTION_MIN_RATIO:
                        caption: str = service.name or method.name
                        plt.text(
                            left + value / 2,
                            language.to_string(),
                            caption,
                            ha="center",
                            va="center",
                            color=foreground_color(service.color).hex,
                        )
                    left += value

        if path:
            plt.gcf().set_size_inches(14, 4)
            plt.savefig(path)
        else:
            plt.show()

    def print_table(
        self,
        languages: set[Language],
        _services: list[Service],
        data: LanguageMethodServiceData,
        total_threshold: float = 0.0,
        style: str = "normal",
        colors: str = "light",
    ) -> None:
        total: float = 0

        if style == "minimal":
            table_style = box.SIMPLE_HEAD
        elif style == "ascii":
            table_style = box.ASCII
        else:
            table_style = box.ROUNDED

        table: Table = Table(
            box=table_style, title="Hours spent on language learning"
        )

        table.add_column("Language")
        for method in methods:
            table.add_column(method.name, justify="right")
        table.add_column("Total", justify="right")

        max_: float = 0.0
        rows: list[list[str]] = []

        language_totals: dict[Language, float] = {}

        for language in languages:
            row: list[str] = [language.to_string()]
            row_total: float = 0.0
            for method in methods:
                time: float = (
                    sum(data.data[language][method].values()) / SECONDS_IN_HOUR
                )
                if time:
                    max_ = max(max_, time)
                    row.append(f"{time:.1f}")
                    row_total += time
                else:
                    row.append("")
            row.append(f"{row_total:.1f}")
            language_totals[language] = row_total
            if row_total > total_threshold:
                rows.append(row)
            total += row_total

        totals: dict[str, float] = {}
        for method in methods:
            totals[method] = sum(
                sum(data.data[language][method].values()) / SECONDS_IN_HOUR
                for language in languages
            )
        rows = sorted(rows, key=lambda x: -float(x[-1]))

        # TODO(enzet): refactor or remove. It's just makes output more colorful.
        if colors == "light":
            for row in rows:
                for index, value in enumerate(row[1:]):
                    if value:
                        h = hex(
                            255 - int(min(float(value), max_) / max_ * 255)
                        )[2:]
                        row[index + 1] = f"[on #FFFF{h:02}]{value}[/]"

        for row in rows:
            table.add_row(*row)

        table.add_row(
            "[bold]Total[/bold]",
            *[f"[bold]{totals[method]:.1f}[/bold]" for method in methods],
            f"[bold]{total:.1f}[/bold]",
        )

        print()
        Console().print(table, justify="center")
        print()

    def print_category_goals(self, data: LanguageMethodServiceData) -> None:
        priority: list[Language] = [
            Language(language) for language in CONFIG["language"]["priority"]
        ]

        ratio = 1.0
        total_ratio = 0.0
        language_ratios: dict[Language, float] = {}
        for language in priority:
            total_ratio += ratio
            language_ratios[language] = ratio
            ratio *= CONFIG["language"]["ratio"]

        # Hour goal for the first priority language is
        # `overall_total / total_ratio`.

        g: float = (
            (
                datetime.now(UTC) - datetime(2017, 9, 22, tzinfo=UTC)
            ).total_seconds()
            / SECONDS_IN_HOUR
            / 24.0
            * 2
        )
        category_goals: list[
            tuple[Language, LanguageCategory, float, float]
        ] = []
        language_category_data: LanguageCategoryData = (
            data.get_language_category_data()
        )
        category_ratios: dict[Language, dict[LanguageCategory, float]] = {}
        category_ratios_config: dict[str, dict[str, int]] = CONFIG["language"][
            "category_ratios"
        ]
        for (
            language_code,
            category_ratios_config_language,
        ) in category_ratios_config.items():
            language: Language = Language(language_code)
            category_ratios[language] = {}
            total_language_category_ratio: int = sum(
                category_ratios_config_language.values()
            )
            for category_id in category_ratios_config_language:
                category: LanguageCategory = LanguageCategory.from_id(
                    category_id
                )
                category_ratios[language][category] = (
                    category_ratios_config_language[category_id]
                    / total_language_category_ratio
                    * language_ratios[language]
                )
                time: float = language_category_data.data[language][category]
                value: float = time / (category_ratios[language][category] * g)
                category_goals.append((language, category, time, value))

        table: Table = Table(box=box.ROUNDED, title="Language category goals")
        table.add_column("Language")
        table.add_column("Category")
        table.add_column("Time", justify="right")
        table.add_column("Ratio", justify="right")
        rows: int = 0
        for language, category, time, value in sorted(
            category_goals, key=lambda x: x[3]
        ):
            if value < 1.0:
                table.add_row(
                    language.to_string(),
                    category.name,
                    format_time(time),
                    f"{value:.5f}",
                )
                rows += 1
            if rows > MAX_GOAL_ROWS:
                break
        Console().print(table, justify="center")
        print()

        table: Table = Table(box=box.ROUNDED, title="Language category data")
        table.add_column("Language")
        for category in LANGUAGE_CATEGORIES:
            table.add_column(category.name, justify="right")
        for language in priority:
            row: list[str] = [language.to_string()]
            for category in LANGUAGE_CATEGORIES:
                if category in category_ratios[language]:
                    time: float = language_category_data.data[language][
                        category
                    ]
                    value: float = time / (
                        category_ratios[language][category] * g
                    )
                    if value < 1.0:
                        row.append(f"{value * 100:.0f}")
                    else:
                        row.append("")
                else:
                    row.append("")
            table.add_row(*row)
        Console().print(table, justify="center")
        print()
