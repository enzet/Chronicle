"""Language learning viewer."""

import argparse
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from matplotlib import pyplot as plt
from rich import box
from rich.console import Console
from rich.table import Table

from chronicle.event.core import Event
from chronicle.objects.core import Object, Service
from chronicle.summary.core import Summary
from chronicle.timeline import Timeline
from chronicle.value import Language

DARK_COLOR_SCHEME = {"background": "#000000", "accent": "#EEEEEE"}
LIGHT_COLOR_SCHEME = {"background": "#FFFFFF", "accent": "#000000"}
COLOR_SCHEME = DARK_COLOR_SCHEME


@dataclass
class LanguageLearningViewer:
    """Viewer of language learning progress."""

    timeline: Timeline

    def process_command(self, arguments: argparse.Namespace) -> None:
        """Process language command."""

        if arguments.interval == 0:
            filter_ = None
        else:
            filter_ = Timeline.get_filter(
                from_date=datetime.now() - timedelta(days=arguments.interval),
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

        services: list[Object] = [
            self.timeline.objects.get_object(x) for x in arguments.services
        ]
        languages = {x for x in languages if x not in excluded_languages}
        xs, data, language_data = self.construct_data(
            filter_, languages, services
        )

        is_sum: bool = True

        if is_sum:
            for index, _ in enumerate(xs):
                if index == 0:
                    continue
                for key in data:
                    data[key][index] += data[key][index - 1]
                for key in language_data:
                    language_data[key][index] += language_data[key][index - 1]

        total__ = []
        for index, _ in enumerate(xs):
            s = 0
            for key in data:
                s += data[key][index]
            total__.append(s)
        data["total__"] = total__

        match arguments.form:
            case "table":
                self.print_table(
                    languages,
                    services,
                    data,
                    total_threshold=arguments.margin,
                    style=arguments.style,
                    colors=arguments.colors,
                )
            case "plot":
                self.plot_languages(
                    xs,
                    language_data,
                    arguments.stack,
                    total_threshold=arguments.margin,
                )

    def construct_data(
        self,
        filter_: Callable[[Event], bool],
        languages: set[Language],
        services: list[Object],
    ) -> tuple[list[datetime], dict[str, list[float]], dict[str, list[float]]]:
        """Construct data for plotting language learning progress."""

        xs: list[datetime] = []
        data: dict[str, list[float]] = defaultdict(list)
        language_data: dict[str, list[float]] = defaultdict(list)

        for point, _, summary in self.timeline.get_events_by_month(
            filter_=filter_
        ):
            xs.append(point)
            for language in languages:
                language_total: float = 0.0

                # Add data for learning services.
                for service in services:
                    if (
                        language in summary.learn_language
                        and service in summary.learn_language[language]
                    ):
                        data[f"{language.code}_{service.name}"].append(
                            summary.learn_language[language][service] / 3600.0
                        )
                        language_total += (
                            summary.learn_language[language][service] / 3600.0
                        )
                    else:
                        data[f"{language.code}_{service.name}"].append(0.0)

                # Add other learning data.
                if language in summary.learn_language:
                    sum_ = 0
                    for service in summary.learn_language[language]:
                        if service not in services:
                            sum_ += summary.learn_language[language][service]
                    data[f"{language.code}_Learn"].append(sum_ / 3600.0)
                    language_total += sum_ / 3600.0
                else:
                    data[f"{language.code}_Learn"].append(0.0)

                listen: float = summary.listen.get(language, 0.0) / 3600.0
                data[f"{language.code}_Listen"].append(listen)
                language_total += listen

                watch: float = summary.watch.get(language, 0.0) / 3600.0
                data[f"{language.code}_Watch"].append(watch)
                language_total += watch

                read: float = 0.0
                read += summary.read.get(language, 0.0) / 3600.0
                data[f"{language.code}_Read"].append(read)
                language_total += read

                write: float = 0.0
                write += summary.write.get(language, 0.0) / 3600.0
                write += summary.write_words.get(language, 0.0) * 2.0 / 3600.0
                language_total += write
                data[f"{language.code}_Write"].append(write)

                data[f"{language.code}_Speak"].append(
                    summary.speak.get(language, 0.0) / 3600.0
                )
                language_total += summary.speak.get(language, 0.0) / 3600.0

                language_data[language.code].append(language_total)

        return xs, data, language_data

    def plot_languages(
        self,
        xs: list[datetime],
        language_data: dict[str, list[float]],
        stack_plot: bool,
        total_threshold: float = 0.0,
    ) -> None:
        """Plot language learning progress."""

        if stack_plot:
            keys = sorted(language_data, key=lambda x: -language_data[x][-1])
            plt.stackplot(
                xs,
                *[language_data[key] for key in keys],
                labels=[key for key in keys],
            )
            plt.legend(loc="upper left")
            plt.show()
        else:
            for key, ys in language_data.items():
                language = Language(key)
                if ys[-1] > total_threshold:
                    plt.plot(
                        xs,
                        [y if y else None for y in ys],
                        label=language.to_string(),
                        color=language.get_color(),
                    )
            plt.ylim(0, 1000)
            plt.legend(loc="upper left")
            plt.show()

    def print_table(
        self,
        languages: list[Language],
        services: list[Service],
        data: dict[str, list[float]],
        total_threshold: float = 0.0,
        style: str = "normal",
        colors: str = "light",
    ) -> None:

        methods: list[str] = [
            "Read",
            "Watch",
            "Listen",
            "Write",
            "Speak",
            "Learn",
        ] + [x.name or x.id for x in services]

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
            table.add_column(method, justify="right")
        table.add_column("Total", justify="right")

        max_: float = 0.0
        rows: list[str] = []

        for language in languages:
            row: list[str] = [language.to_string()]
            row_total: float = 0.0
            for method in methods:
                value: float = data[language.code + "_" + method][-1]
                if value:
                    max_ = max(max_, value)
                    row.append(f"{value:.1f}")
                    row_total += value
                else:
                    row.append("")
            row.append(f"{row_total:.1f}")
            if row_total > total_threshold:
                rows.append(row)
            total += row_total

        totals: dict[str, float] = {}
        for method in methods:
            totals[method] = sum(
                data[language.code + "_" + method][-1] for language in languages
            )
        rows = sorted(rows, key=lambda x: -float(x[-1]))

        # TODO: refactor or remove. It's just makes output more colorful.
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
