import argparse
import logging
import sys
from pathlib import Path

from chronicle.harvest.old import (
    OldMovieImporter,
    OldImporter,
    OldPodcastImporter,
)

from chronicle.timeline import (
    SportViewer,
    Timeline,
    CommandParser,
)
from chronicle.view.objects import ObjectsHtmlViewer

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def main():
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting Chronicle.")

    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser(
        "Chronicle"
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
    arguments = argument_parser.parse_args(sys.argv[1:])

    timeline: Timeline = Timeline()
    cache_path: Path = Path.home() / "program" / "chronicle" / "cache"

    if arguments.input:
        for file_name in arguments.input:
            if file_name.endswith(".chr"):
                logging.info(f"Importing data from `{file_name}`.")
                parser: CommandParser = CommandParser(timeline)
                with Path(file_name).open() as input_file:
                    for line in input_file.readlines():
                        parser.parse_command(line[:-1].strip())
            elif file_name.endswith(".vcf"):
                from chronicle.harvest.vcf import VcfImporter

                importer = VcfImporter(Path(file_name))
                importer.import_data(timeline)
            else:
                logging.critical(f"Unknown format of file `{file_name}`.")
                sys.exit(1)

    if arguments.import_arc:
        from chronicle.harvest.arc import ArcImporter

        logging.info(f"Importing Arc data from `{arguments.import_arc}`.")
        ArcImporter(Path(arguments.import_arc), cache_path).import_data(
            timeline
        )

    if arguments.import_memrise:
        from chronicle.harvest.memrise import MemriseImporter

        logging.info(
            f"Importing Memrise data from `{arguments.import_memrise}`."
        )
        MemriseImporter(Path(arguments.import_memrise)).import_data(timeline)

    if arguments.import_duome:
        from chronicle.harvest.duolingo import DuomeImporter

        logging.info(f"Importing Duome data from `{arguments.import_duome}`.")
        DuomeImporter(Path(arguments.import_duome)).import_data(timeline)

    if arguments.import_duolingo:
        from chronicle.harvest.duolingo import DuolingoImporter

        logging.info(
            f"Importing Duolingo data from `{arguments.import_duolingo}`."
        )
        DuolingoImporter(Path(arguments.import_duolingo)).import_data(timeline)

    if arguments.import_old:
        logging.info(
            f"Importing events from old format `{arguments.import_old}`."
        )
        OldImporter(Path(arguments.import_old)).import_data(timeline)

    if arguments.import_old_movie:
        logging.info(
            f"Importing movies from old format `{arguments.import_old_movie}`."
        )
        OldMovieImporter(Path(arguments.import_old_movie)).import_data(timeline)

    if arguments.import_old_podcast:
        logging.info(
            "Importing podcasts from old format "
            f"`{arguments.import_old_podcast}`."
        )
        OldPodcastImporter(Path(arguments.import_old_podcast)).import_data(
            timeline
        )

    def process_command(command: str) -> None:
        if command == "timeline":
            timeline.print()
        elif command == "summary":
            print(timeline.get_summary())
        elif command == "language":
            from chronicle.view.language import LanguageLearningViewer

            LanguageLearningViewer(timeline).process_command(
                arguments.sub_command
            )
        elif command == "objects_html":
            output_path: Path = Path("output.html")
            ObjectsHtmlViewer(timeline).write_html(output_path)
        elif command == "podcasts":
            from chronicle.view.artwork import PodcastViewer

            PodcastViewer(timeline).print_podcasts()
        elif command == "books":
            from chronicle.view.artwork import BookViewer

            BookViewer(timeline).print_books()
        elif command == "expired":
            from rich.console import Console

            Console().print(timeline.get_expired())
        elif command == "dishes":
            from rich.console import Console

            Console().print(timeline.get_dishes())
        elif command == "objects":
            from rich.console import Console

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
    sys.exit(main())
