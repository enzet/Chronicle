"""Viewer for books, podcasts, and videos."""

import argparse
import re
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field

from rich import box
from rich.console import Console
from rich.table import Table

from chronicle.event.art import (
    ListenAudiobookEvent,
    ListenPodcastEvent,
    ReadEvent,
    WatchEvent,
)
from chronicle.event.core import Event
from chronicle.objects.core import Book, Podcast, Video
from chronicle.timeline import Timeline
from chronicle.util import empty_filter, filter_by_year
from chronicle.value import AudiobookVolume, Language, Volume

EQUALS_TRESHOLD: float = 0.1


def format_episodes(episodes: list[int | str]) -> str:
    """Get string representation of episodes."""

    integer_episodes: list[int] = []
    other_episodes: list[str] = []

    for episode in episodes:
        if isinstance(episode, int) or episode.isdigit():
            integer_episodes.append(int(episode))
        else:
            other_episodes.append(episode)

    result: str = ""

    if integer_episodes:
        # If all episodes are numbers, mark played episodes with "×" sign.
        min_episode: int = min(integer_episodes)
        max_episode: int = max(integer_episodes)

        result += f"[grey]{min_episode} -[/grey] "

        result += "".join(
            "×" if x in integer_episodes else "-"
            for x in range(min_episode, max_episode + 1)
        )
        result += f" [grey]- {max_episode}[/grey]"

    if other_episodes:
        # If episodes are not numbers, just join them with commas.
        result += ", " + ", ".join(sorted(other_episodes))

    return result


@dataclass
class PodcastViewer:
    """Viewer of podcasts."""

    timeline: Timeline

    def print_podcasts(self) -> None:
        """Print podcasts."""

        podcasts: dict[Podcast, list[ListenPodcastEvent]] = defaultdict(list)

        for event in sorted(
            self.timeline.events, key=lambda e: e.time.get_lower()
        ):
            if isinstance(event, ListenPodcastEvent) and event.podcast:
                podcasts[event.podcast].append(event)

        for podcast, events in podcasts.items():
            seasons: dict[int, list[int | str]] = defaultdict(list)
            for event in events:
                if event.season:
                    if event.episode:
                        seasons[event.season].append(event.episode)
                    else:
                        seasons[event.season].append("")
            episodes: list[int | str]
            if len(seasons) > 1:
                Console().print(f"[bold]{podcast.title}[/bold]:")
                for season, episodes in sorted(
                    seasons.items(), key=lambda x: x[0]
                ):
                    Console().print(
                        f"  Season {season}: {format_episodes(episodes)}"
                    )
            else:
                episodes = [str(event.episode) for event in events]
                Console().print(
                    f"[bold]{podcast.title}[/bold]: "
                    f"{format_episodes(episodes)}"
                )


def normalize(
    volume: Volume | AudiobookVolume, book: Book
) -> Volume | AudiobookVolume:
    """Normalize volume."""

    if volume.measure == "percent":
        return volume

    if volume.from_ and volume.to_ and volume.of:
        return Volume(
            None,
            volume.from_ / volume.of * 100,
            volume.to_ / volume.of * 100,
            measure="percent",
            of=100,
        )

    if (
        volume.measure == "pages"
        and volume.from_
        and volume.to_
        and book.volume
    ):
        return Volume(
            None,
            volume.from_ / book.volume * 100,
            volume.to_ / book.volume * 100,
            measure="percent",
            of=100,
        )

    return volume


def equals(a: float | None, b: float | None) -> bool:
    """Check if two values are equal."""

    if a is None or b is None:
        return a is None and b is None

    return abs(a - b) < EQUALS_TRESHOLD


def union_volumes(
    volumes: set[Volume | AudiobookVolume],
) -> set[Volume | AudiobookVolume]:
    """Glue volumes if they are consecutive.

    E.g. for two reading volumes [25, 30] and [30, 40] create one volume [25,
    40].
    """
    result: set[Volume | AudiobookVolume] = set()

    while volumes:
        current: Volume | AudiobookVolume = volumes.pop()
        merged: bool = False

        for other in volumes:
            if (
                not current.measure
                or not other.measure
                or other.measure != current.measure
            ):
                continue
            if (current.of or other.of) and current.of != other.of:
                continue
            if equals(current.to_, other.from_) or equals(
                current.from_, other.to_
            ):
                if equals(current.to_, other.from_):
                    from_ = current.from_
                    to_ = other.to_
                else:
                    from_ = other.from_
                    to_ = current.to_
                volumes.remove(other)
                merged_volume: Volume = Volume(
                    None, from_, to_, measure=current.measure, of=current.of
                )
                volumes.add(merged_volume)
                merged = True
                break

        if not merged:
            result.add(current)

    return result


@dataclass
class BookViewer:
    """Viewer of books."""

    timeline: Timeline

    languages: set[Language] = field(default_factory=set)

    def print_finished_books(
        self, console: Console, arguments: argparse.Namespace
    ) -> None:
        """Print finished books."""

        if arguments.year == 0:
            filter_ = empty_filter
            title = "Finished books"
        else:
            filter_ = filter_by_year(arguments.year)
            title = f"Books finished in {arguments.year}"

        summary = self.timeline.get_summary(filter_=filter_)

        rows: list[tuple[str, str, str]] = []
        for index, book in enumerate(
            sorted(
                summary.finished_books,
                key=lambda x: int(x.volume) if x.volume else 0,
                reverse=True,
            )
        ):
            rows.append(
                (
                    str(index + 1),
                    book.title or "",
                    str(int(book.volume)) if book.volume else "",
                )
            )
        match arguments.style:
            case "minimal":
                table_style = box.SIMPLE_HEAD
            case "ascii":
                table_style = box.ASCII
            case _:
                table_style = box.ROUNDED

        table: Table = Table(box=table_style, title=title)
        table.add_column("")
        table.add_column("Title")
        table.add_column("Pages", justify="right")

        for row in rows:
            table.add_row(*row)

        console.print()
        console.print(table)
        console.print()

    def get_books(
        self, filter_: Callable
    ) -> dict[Book, list[ReadEvent | ListenAudiobookEvent]]:
        """Get books."""

        books: dict[Book, list[ReadEvent | ListenAudiobookEvent]] = defaultdict(
            list
        )
        for event in self.timeline.get_events(filter_=filter_):
            if (
                isinstance(event, ReadEvent)
                and event.book
                and (
                    not self.languages or event.get_language() in self.languages
                )
            ):
                books[event.book].append(event)
            if (
                isinstance(event, ListenAudiobookEvent)
                and event.audiobook
                and event.audiobook.book
                and (
                    not self.languages or event.get_language() in self.languages
                )
            ):
                books[event.audiobook.book].append(event)
        return books

    def print_books(
        self, console: Console, arguments: argparse.Namespace
    ) -> None:
        """Print books."""

        if arguments.title:
            pattern = re.compile(arguments.title)

            def filter_(event: Event) -> bool:
                return (
                    isinstance(event, ReadEvent)
                    and bool(event.book)
                    and bool(
                        pattern.match(event.book.title if event.book else "")
                    )
                )

        else:
            filter_ = empty_filter

        table: Table = Table(box=box.ROUNDED, title="Books")
        table.add_column("Title", width=50)
        table.add_column("Volumes")

        books: dict[Book, list[ReadEvent | ListenAudiobookEvent]] = (
            self.get_books(filter_)
        )

        for book, events in sorted(
            books.items(), key=lambda x: x[0].volume if x[0].volume else 0
        ):
            if not book:
                continue
            volumes: set[Volume | AudiobookVolume] = {
                event.volume
                for event in events
                if event.volume
                and event.volume.from_ is not None
                and event.volume.to_ is not None
            }
            volumes = {normalize(volume, book) for volume in volumes}
            volumes = union_volumes(volumes)
            table.add_row(
                book.title,
                ", ".join(
                    v.to_string()
                    for v in sorted(volumes, key=lambda v: v.from_ or 0)
                ),
            )

        console.print(table)

    def show_book_volume(self, arguments: argparse.Namespace) -> None:
        """Show book volume."""

        books: dict[Book, list[ReadEvent | ListenAudiobookEvent]] = (
            self.get_books(lambda x: arguments.request.match(x.title))
        )
        for book, events in books.items():
            if not book:
                continue
            volumes: set[Volume | AudiobookVolume] = {
                event.volume
                for event in events
                if event.volume
                and event.volume.from_ is not None
                and event.volume.to_ is not None
            }
            volumes = {normalize(volume, book) for volume in volumes}
            volumes = union_volumes(volumes)
            print(f"{book.title}: {volumes}")


def get_sort_key(title: str) -> str:
    """Remove article from title.

    E.g. "The Matrix" -> "Matrix", "A Matrix" -> "Matrix".
    """
    for prefix in ["The ", "A ", "An ", "Le ", "La ", "Les ", "L'"]:
        if title.startswith(prefix):
            return title[len(prefix) :]

    return title


@dataclass
class VideoViewer:
    """Viewer of videos."""

    timeline: Timeline

    languages: set[Language] = field(default_factory=set)

    def print_videos(self, console: Console) -> None:
        """Print videos."""

        videos: dict[Video, list[WatchEvent]] = defaultdict(list)

        table: Table = Table(box=box.ROUNDED, title="Videos")
        table.add_column("Title")
        table.add_column("Episodes")

        for event in sorted(
            self.timeline.events, key=lambda e: e.time.get_lower()
        ):
            if (
                isinstance(event, WatchEvent)
                and event.video
                and (not self.languages or event.language in self.languages)
            ):
                videos[event.video].append(event)

        for video, events in sorted(
            videos.items(), key=lambda x: get_sort_key(x[0].title or "")
        ):
            seasons: dict[int | None, list[int | str]] = defaultdict(list)
            for event in events:
                if event.episode:
                    seasons[event.season].append(event.episode)

            episodes: list[int | str]

            if not seasons:
                episodes_text = ""
            elif len(seasons) > 0:
                episodes_text = ""
                for season, episodes in sorted(
                    seasons.items(), key=lambda x: str(x[0])
                ):
                    print(video, episodes)
                    if episodes_text:
                        episodes_text += "\n"
                    episodes_text += f"S {season}: {format_episodes(episodes)}"
            else:
                episodes = [str(event.episode) for event in events]
                episodes_text = f"{format_episodes(episodes)}"

            table.add_row(video.title, episodes_text)

        console.print(table)
