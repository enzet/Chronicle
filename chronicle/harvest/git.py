"""Harvest data from git repositories."""

import argparse
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import override

from chronicle.event.common import CommitEvent
from chronicle.harvest.core import Importer, ImportManager
from chronicle.time import Moment, Time
from chronicle.timeline import Timeline


class GitImportManager(ImportManager):
    """Manager for git repository import."""

    @staticmethod
    @override
    def add_argument(parser: argparse._ArgumentGroup) -> None:
        parser.add_argument(
            "--import-git",
            nargs="+",
            help="import git commit data from directories",
            metavar="<path>",
        )
        parser.add_argument(
            "--git-author",
            help="filter commits by author name or email",
            metavar="<author>",
        )

    @staticmethod
    @override
    def process_arguments(
        arguments: argparse.Namespace, timeline: Timeline
    ) -> None:
        if arguments.import_git:
            author: str | None = getattr(arguments, "git_author", None)
            for path_str in arguments.import_git:
                GitImporter(Path(path_str), author).import_data(timeline)


@dataclass
class GitImporter(Importer):
    """Importer for git repository commit data."""

    directory: Path
    """Path to the git repository directory."""

    author: str | None = None
    """Filter commits by this author name or email."""

    @override
    def import_data(self, timeline: Timeline) -> None:
        """Import git commits as CommitEvents, grouped one per day."""
        command: list[str] = [
            "git",
            "-C",
            str(self.directory),
            "log",
            "--format=%ad",
            "--date=short",
        ]
        if self.author:
            command += ["--author", self.author]

        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )

        counts: defaultdict[str, int] = defaultdict(int)
        for line in result.stdout.splitlines():
            date_str = line.strip()
            if date_str:
                counts[date_str] += 1

        project_name: str = self.directory.resolve().name

        for date_str, count in sorted(counts.items()):
            date: datetime = datetime.strptime(date_str, "%Y-%m-%d")
            moment: Moment = Moment(
                year=date.year, month=date.month, day=date.day
            )
            time: Time = Time.from_moment(moment)
            event: CommitEvent = CommitEvent(
                time,
                source=f"git:{self.directory}",
                project=project_name,
                count=count,
            )
            timeline.events.append(event)
