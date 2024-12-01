import argparse
from collections import defaultdict
from chronicle.objects.core import Service
from chronicle.summary.core import Summary
from chronicle.timeline import Timeline

from rich import box
from rich.console import Console
from rich.table import Table

from datetime import datetime

from chronicle.value import Language

from dataclasses import dataclass


DARK_COLOR_SCHEME = {
    "background": "#000000",
    "accent": "#EEEEEE",
}
LIGHT_COLOR_SCHEME = {
    "background": "#FFFFFF",
    "accent": "#000000",
}
COLOR_SCHEME = DARK_COLOR_SCHEME


@dataclass
class LanguageLearningViewer:
    """Viewer of language learning progress."""

    timeline: Timeline

    def process_command(self, command: str) -> None:
        parser: argparse.ArgumentParser = argparse.ArgumentParser()
        sub_parsers: argparse.ArgumentParser = parser.add_subparsers(
            dest="command"
        )

        sub_parsers.add_parser("table")

        plot_parser: argparse.ArgumentParser = sub_parsers.add_parser("plot")
        plot_parser.add_argument("--stack", action="store_true")

        args = parser.parse_args(command.split())

        # filter_ = Timeline.get_filter(
        #     from_date=datetime.now() - timedelta(days=30), to_date=None
        # )
        filter_ = None
        total_summary: Summary = self.timeline.get_summary(filter_)

        keys: set[Language] = (
            set(total_summary.listen.keys())
            | set(total_summary.read.keys())
            | set(total_summary.watch.keys())
            | set(total_summary.learn_language.keys())
        )
        languages: set[Language] = {x for x in keys if x}
        excluded_languages: set[Language] = {
            Language("ru"),
            Language("uk"),
            Language("be"),
            Language("en"),
        }

        services: list[Service] = [
            self.timeline.objects.get_object(x)
            for x in ("emmio_service", "duolingo", "memrise")
        ]
        languages = {x for x in languages if x not in excluded_languages}
        xs, data, language_data = self.construct_data(
            filter_, languages, services
        )

        is_sum: bool = True

        if is_sum:
            for index, point in enumerate(xs):
                if index == 0:
                    continue
                for key in data:
                    data[key][index] += data[key][index - 1]
                for key in language_data:
                    language_data[key][index] += language_data[key][index - 1]

        total__ = []
        for index, point in enumerate(xs):
            s = 0
            for key in data:
                s += data[key][index]
            total__.append(s)
        data["total__"] = total__

        match args.command:
            case "table":
                self.print_table(languages, services, data, total_threshold=8.0)
            case "plot":
                self.plot_languages(
                    xs, language_data, args.stack, total_threshold=8.0
                )

    def construct_data(
        self, filter_, languages, services
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

                data[f"{language.code}_Listen"].append(
                    summary.listen.get(language, 0.0) / 3600.0
                )
                language_total += summary.listen.get(language, 0.0) / 3600.0
                data[f"{language.code}_Watch"].append(
                    summary.watch.get(language, 0.0) / 3600.0
                )
                language_total += summary.watch.get(language, 0.0) / 3600.0
                data[f"{language.code}_Read"].append(
                    summary.read.get(language, 0.0) / 3600.0
                )
                language_total += summary.read.get(language, 0.0) / 3600.0
                data[f"{language.code}_Write"].append(
                    summary.write.get(language, 0.0) / 3600.0
                )
                language_total += summary.write.get(language, 0.0) / 3600.0
                data[f"{language.code}_Speak"].append(
                    summary.speak.get(language, 0.0) / 3600.0
                )
                language_total += summary.speak.get(language, 0.0) / 3600.0

                language_data[language.code].append(language_total)

        return xs, data, language_data

    def plot_languages(
        self, xs, language_data, stack_plot, total_threshold: float = 0.0
    ) -> None:
        from matplotlib import pyplot as plt

        stack_plot: bool = False

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
        data,
        total_threshold: float = 0.0,
    ) -> None:
        methods = ["Read", "Watch", "Listen", "Write", "Speak", "Learn"] + [
            x.name for x in services
        ]

        total: float = 0

        table: Table = Table(
            box=box.ROUNDED, title="Hours spent on language learning"
        )
        table.add_column("")
        for method in methods:
            table.add_column(method, justify="right")
        table.add_column("Total", justify="right")

        rows = []
        max_: float = 0.0

        for language in languages:
            row: list[str] = [language.to_string()]
            row_total: float = 0.0
            for method in methods:
                value: float = data[language.code + "_" + method][-1]
                if value:
                    max_ = max(max_, value)
                    row.append(f"{value:.0f}")
                    row_total += value
                else:
                    row.append("")
            row.append(f"{row_total:.0f}")
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
        for row in rows:
            for index, value in enumerate(row[1:]):
                if value:
                    h = hex(255 - int(min(float(value), max_) / max_ * 255))[2:]
                    row[index + 1] = f"[on #FFFF{h:02}]{value}[/]"

        for row in rows:
            table.add_row(*row)

        table.add_row(
            "[bold]Total[/bold]",
            *[f"[bold]{totals[method]:.0f}[/bold]" for method in methods],
            f"[bold]{total:.0f}[/bold]",
        )

        print()
        Console().print(table)
        print()
