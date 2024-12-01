from collections import defaultdict
from dataclasses import dataclass, field
from chronicle.event.art import (
    ListenAudiobookEvent,
    ListenPodcastEvent,
    ReadEvent,
)
from chronicle.event.core import Event
from chronicle.objects.core import Book, Podcast
from chronicle.timeline import Timeline
from rich.console import Console
from rich.table import Table
from rich import box
from chronicle.value import Language, Volume


@dataclass
class PodcastViewer:
    """Viewer of podcasts."""

    timeline: Timeline

    @staticmethod
    def get_episodes(episodes: list[str]) -> str:
        """Get string representation of episodes."""

        if all(episode.isdigit() for episode in episodes):
            # If all episodes are numbers, mark played episodes with "×" sign.
            min_episode: int = min(int(episode) for episode in episodes)
            max_episode: int = max(int(episode) for episode in episodes)

            result: str = ""
            result += f"{min_episode} - "

            result += "".join(
                "×" if str(x) in episodes else " "
                for x in range(min_episode, max_episode + 1)
            )
            result += f" - {max_episode}"
            return result
        else:
            # If episodes are not numbers, just join them with commas.
            return ", ".join(
                sorted(episodes, key=lambda x: int(x) if x.isdigit() else 0)
            )

    def print_podcasts(self) -> None:
        """Print podcasts."""

        podcasts: dict[Podcast, list[ListenPodcastEvent]] = defaultdict(list)

        for event in sorted(
            self.timeline.events, key=lambda e: e.time.get_lower()
        ):
            if isinstance(event, ListenPodcastEvent):
                podcasts[event.podcast].append(event)

        for podcast, events in podcasts.items():
            seasons = defaultdict(list)
            for event in events:
                if event.season:
                    seasons[event.season].append(event.episode)
            if len(seasons) > 1:
                Console().print(f"[bold]{podcast.title}[/bold]:")
                for season, episodes in sorted(
                    seasons.items(), key=lambda x: x[0]
                ):
                    Console().print(
                        f"  Season {season}: {self.get_episodes(episodes)}"
                    )
            else:
                episodes = [str(event.episode) for event in events]
                Console().print(
                    f"[bold]{podcast.title}[/bold]: "
                    f"{self.get_episodes(episodes)}"
                )


def normalize(volume: Volume, book: Book) -> Volume:
    """Normalize volume."""

    if volume.measure == "percent":
        return volume

    if volume.of:
        return Volume(
            None,
            volume.from_ / volume.of * 100,
            volume.to_ / volume.of * 100,
            measure="percent",
            of=100,
        )

    if volume.measure == "pages" and book.volume:
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

    return abs(a - b) < 0.1


def union_volumes(volumes: set[Volume]) -> set[Volume]:
    """Glue volumes if they are consecutive.

    E.g. for two reading volumes [25, 30] and [30, 40] create one volume [25,
    40].
    """

    result: set[Volume] = set()

    while volumes:
        current: Volume = volumes.pop()
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
                    None,
                    from_,
                    to_,
                    measure=current.measure,
                    of=current.of,
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

    def print_books(self) -> None:
        books: dict[Book, list[Event]] = defaultdict(list)

        table: Table = Table(box=box.ROUNDED, title="Books")
        table.add_column("Title", width=50)
        table.add_column("Volumes")

        for event in sorted(
            self.timeline.events, key=lambda e: e.time.get_lower()
        ):
            if isinstance(event, ReadEvent) and event.book:
                if not self.languages or event.get_language() in self.languages:
                    books[event.book].append(event)
            if isinstance(event, ListenAudiobookEvent) and event.audiobook.book:
                if not self.languages or event.get_language() in self.languages:
                    books[event.audiobook.book].append(event)

        for book, events in sorted(
            books.items(), key=lambda x: x[0].volume if x[0].volume else 0
        ):
            if not book:
                continue
            volumes: set[Volume] = {
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
                    for v in sorted(volumes, key=lambda v: v.from_)
                ),
            )

        Console().print(table)
