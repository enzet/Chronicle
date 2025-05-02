"""Chronicle entry point."""

import argparse
import logging
import sys
from pathlib import Path

from rich.console import Console

from chronicle.harvest.old import (
    OldImporter,
    OldMovieImporter,
    OldPodcastImporter,
)
from chronicle.harvest.wikipedia import WikipediaImporter
from chronicle.timeline import CommandParser, SportViewer, Timeline
from chronicle.view.objects import ObjectsHtmlViewer

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def main() -> None:
    """Chronicle entry point."""

    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser(
        "Chronicle"
    )
    argument_parser.add_argument(
        "--logging",
        type=str,
        choices=["info", "silent", "debug"],
        default="silent",
        help="logging level",
    )
    argument_parser.add_argument("-c", "--command", help="command")
    argument_parser.add_argument("--sub-command", default="")
    argument_parser.add_argument("-i", "--input", nargs="+", help="input files")
    argument_parser.add_argument(
        "--import-old",
        help="import data from old Chronicle format",
        metavar="<JSON file path>",
    )
    argument_parser.add_argument(
        "--import-old-movie",
        help="import movies from old Chronicle format",
        metavar="<JSON file path>",
    )
    argument_parser.add_argument(
        "--import-old-podcast",
        help="import podcasts from old Chronicle format",
        metavar="<JSON file path>",
    )
    argument_parser.add_argument(
        "--import-arc",
        help="import data from Arc iOS application",
        metavar="<path>",
    )
    argument_parser.add_argument(
        "--import-memrise",
        help="import data from Memrise",
        metavar="<HTML file path>",
    )
    argument_parser.add_argument(
        "--import-duome",
        help="import data from Duome project",
        metavar="<text file path>",
    )
    argument_parser.add_argument(
        "--import-duolingo",
        help="import data from Duolingo",
        metavar="<CSV file path>",
    )
    argument_parser.add_argument(
        "--import-wiki",
        help="import data from Wikipedia",
        metavar="<url>",
        nargs="+",
    )

    sub_parsers = argument_parser.add_subparsers(dest="command")
    view_parser = sub_parsers.add_parser("view")
    view_parser.add_argument("--style", default="normal")
    view_parser.add_argument(
        "--colors", default="light", choices=["light", "dark", "no"]
    )

    view_sub_parsers = view_parser.add_subparsers(dest="sub_command")

    view_language_parser = view_sub_parsers.add_parser("language")
    view_language_parser.add_argument(
        "--form",
        type=str,
        choices=["table", "plot"],
        help="form of data: table or plot",
    )
    view_language_parser.add_argument(
        "--interval",
        type=int,
        default=0,
        metavar="<days>",
        help=(
            "if interval is not zero, then only events from the last interval "
            "days will be shown"
        ),
    )
    view_language_parser.add_argument(
        "--stack", action="store_true", help="stack data (only for plot)"
    )
    view_language_parser.add_argument(
        "--margin",
        type=float,
        metavar="<hours>",
        default=0.0,
        help=(
            "show only languages with more than margin hours of total learning"
        ),
    )
    view_language_parser.add_argument(
        "--exclude-languages",
        type=str,
        nargs="+",
        default=[],
        help="exclude languages from the list of languages",
    )
    view_language_parser.add_argument(
        "--services",
        type=str,
        nargs="+",
        default=[],
        help=(
            "identifiers of services of learning event to show separately, "
            "e.g. `duolingo`"
        ),
    )

    view_sub_parsers.add_parser("objects")

    view_books_parser = view_sub_parsers.add_parser("books")
    view_books_parser.add_argument("--year", default=0, type=int)
    view_books_parser.add_argument("--title", default=None, type=str)
    view_books_parser.add_argument(
        "--finished", default=False, action="store_true"
    )

    view_podcasts_parser = view_sub_parsers.add_parser("podcasts")
    view_podcasts_parser.add_argument("--title", default=None, type=str)

    arguments: argparse.Namespace = argument_parser.parse_args(sys.argv[1:])

    if arguments.logging == "info":
        logging.basicConfig(level=logging.INFO)
    elif arguments.logging == "silent":
        logging.basicConfig(level=logging.WARNING)
    elif arguments.logging == "debug":
        logging.basicConfig(level=logging.DEBUG)

    logging.info("Starting Chronicle.")

    timeline: Timeline = Timeline()
    cache_path: Path = Path.home() / "program" / "chronicle" / "cache"

    if arguments.input:
        for file_name in arguments.input:
            if file_name.endswith(".chr"):
                logging.info("Importing data from `%s`.", file_name)
                parser: CommandParser = CommandParser(timeline)
                with Path(file_name).open() as input_file:
                    for line in input_file.readlines():
                        parser.parse_command(line[:-1].strip())
            elif file_name.endswith(".vcf"):
                from chronicle.harvest.vcf import VcfImporter

                importer = VcfImporter(Path(file_name))
                importer.import_data(timeline)
            else:
                logging.critical("Unknown format of file `%s`.", file_name)
                sys.exit(1)

    if arguments.import_arc:
        from chronicle.harvest.arc import ArcImporter

        logging.info("Importing Arc data from `%s`.", arguments.import_arc)
        ArcImporter(Path(arguments.import_arc), cache_path).import_data(
            timeline
        )

    if arguments.import_memrise:
        from chronicle.harvest.memrise import MemriseImporter

        logging.info(
            "Importing Memrise data from `%s`.", arguments.import_memrise
        )
        MemriseImporter(Path(arguments.import_memrise)).import_data(timeline)

    if arguments.import_duome:
        from chronicle.harvest.duolingo import DuomeImporter

        logging.info("Importing Duome data from `%s`.", arguments.import_duome)
        DuomeImporter(Path(arguments.import_duome)).import_data(timeline)

    if arguments.import_duolingo:
        from chronicle.harvest.duolingo import DuolingoImporter

        logging.info(
            "Importing Duolingo data from `%s`.", arguments.import_duolingo
        )
        DuolingoImporter(Path(arguments.import_duolingo)).import_data(timeline)

    if arguments.import_old:
        logging.info(
            "Importing events from old format `%s`.", arguments.import_old
        )
        OldImporter(Path(arguments.import_old)).import_data(timeline)

    if arguments.import_old_movie:
        logging.info(
            "Importing movies from old format `%s`.", arguments.import_old_movie
        )
        OldMovieImporter(Path(arguments.import_old_movie)).import_data(timeline)

    if arguments.import_old_podcast:
        logging.info(
            "Importing podcasts from old format `%s`.",
            arguments.import_old_podcast,
        )
        OldPodcastImporter(Path(arguments.import_old_podcast)).import_data(
            timeline
        )

    if arguments.import_wiki:
        for value in arguments.import_wiki:
            username, url = value.split("@")
            logging.info("Importing wiki contributions for `%s`.", url)
            WikipediaImporter(
                url=url, username=username, cache_path=cache_path
            ).import_data(timeline)

    def process_command(command: str) -> None:
        console: Console = Console(highlight=False)

        if command == "view":
            if arguments.sub_command == "language":
                from chronicle.view.language import LanguageLearningViewer

                LanguageLearningViewer(timeline).process_command(arguments)

            elif arguments.sub_command == "objects":
                output_path: Path = Path("output.html")
                ObjectsHtmlViewer(timeline).write_html(output_path)

            elif arguments.sub_command == "books":
                from chronicle.view.artwork import BookViewer

                if arguments.finished:
                    BookViewer(timeline).print_finished_books(
                        console, arguments
                    )
                else:
                    BookViewer(timeline).print_books(console, arguments)

            elif arguments.sub_command == "podcasts":
                from chronicle.view.artwork import PodcastViewer

                PodcastViewer(timeline).print_podcasts()

        elif command == "timeline":
            timeline.print()

        elif command == "summary":
            print(timeline.get_summary())
        elif command == "shows":
            from chronicle.view.show import ShowViewer

            ShowViewer(timeline).process_command(arguments.sub_command)

        elif command == "movies":
            from chronicle.view.artwork import VideoViewer

            VideoViewer(timeline).print_videos(Console())

        elif command == "expired":
            Console().print(timeline.get_expired())
        elif command == "dishes":
            Console().print(timeline.get_dishes())
        elif command == "objects":
            Console().print(timeline.get_objects())
        elif command == "sport":
            SportViewer(timeline).plot_sport()
        elif command == "graph":
            timeline.graph()
        elif command == "duolingo":
            DuomeImporter(
                Path.home() / "Dropbox" / "Data" / "duome.txt"
            ).import_data(timeline)

    command = arguments.command
    if command == "interpret":
        while True:
            command = input("> ")
            process_command(command)
            if command == "":
                break
    else:
        process_command(command)


if __name__ == "__main__":
    main()
