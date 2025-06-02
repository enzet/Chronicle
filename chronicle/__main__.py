"""Chronicle entry point."""

import argparse
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

from chronicle.errors import ChronicleUnknownTypeError
from chronicle.harvest.apple_health import AppleHealthImportManager
from chronicle.harvest.arc import ArcImportManager
from chronicle.harvest.duolingo import DuolingoImportManager
from chronicle.harvest.memrise import MemriseImportManager
from chronicle.harvest.old import OldImportManager
from chronicle.harvest.wikimedia import WikimediaImportManager
from chronicle.timeline import CommandParser, Timeline
from chronicle.view.objects import ObjectsHtmlViewer

if TYPE_CHECKING:
    from chronicle.harvest.core import ImportManager

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

logger: logging.Logger = logging.getLogger(__name__)


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
    argument_parser.add_argument(
        "--cache-path",
        type=str,
        default="cache",
        help="path to cache directory",
    )
    argument_parser.add_argument(
        "--cache-only", action="store_true", help="use cache only"
    )
    argument_parser.add_argument("-i", "--input", nargs="+", help="input files")

    import_parsers = argument_parser.add_argument_group("import")

    import_managers: list[type[ImportManager]] = [
        WikimediaImportManager,
        AppleHealthImportManager,
        ArcImportManager,
        DuolingoImportManager,
        MemriseImportManager,
        OldImportManager,
    ]

    for manager in import_managers:
        manager.add_argument(import_parsers)

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

    view_sub_parsers.add_parser("sport")

    arguments: argparse.Namespace = argument_parser.parse_args(sys.argv[1:])

    if arguments.logging == "info":
        logging.basicConfig(level=logging.INFO)
    elif arguments.logging == "silent":
        logging.basicConfig(level=logging.WARNING)
    elif arguments.logging == "debug":
        logging.basicConfig(level=logging.DEBUG)

    logger.info("Starting Chronicle.")

    timeline: Timeline = Timeline()

    if arguments.input:
        for file_name in arguments.input:
            if file_name.endswith(".chr"):
                logger.info("Importing data from `%s`.", file_name)
                parser: CommandParser = CommandParser(timeline)
                unknown_types: list[ChronicleUnknownTypeError] = []
                with Path(file_name).open(encoding="utf-8") as input_file:
                    for line in input_file:
                        try:
                            parser.parse_command(line[:-1].strip())
                        except ChronicleUnknownTypeError as error:
                            unknown_types.append(error)
                if unknown_types:
                    logger.warning(
                        "%d unknown types in file `%s`: %s.",
                        len(unknown_types),
                        file_name,
                        ", ".join(
                            {f"`{error.type_}`" for error in unknown_types}
                        ),
                    )
            elif file_name.endswith(".vcf"):
                from chronicle.harvest.vcf import VcfImporter

                importer = VcfImporter(Path(file_name))
                importer.import_data(timeline)
            else:
                logger.critical("Unknown format of file `%s`.", file_name)
                sys.exit(1)

    for manager in import_managers:
        manager.process_arguments(arguments, timeline)

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

            elif arguments.sub_command == "sport":
                from chronicle.view.sport import SportViewer

                SportViewer(timeline).plot_sport()

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
        elif command == "graph":
            timeline.graph()

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
