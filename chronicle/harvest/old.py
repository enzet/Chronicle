"""Importer for old Chronicle format."""

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, override

from chronicle.errors import ChronicleValueError
from chronicle.event.art import (
    ListenAudiobookEvent,
    ListenMusicEvent,
    ListenPodcastEvent,
    ReadEvent,
    WatchEvent,
)
from chronicle.event.core import Event
from chronicle.harvest.core import Importer, ImportManager
from chronicle.objects.core import Audiobook, Book, Object, Podcast, Video
from chronicle.time import Context, Moment, Time, Timedelta
from chronicle.timeline import Timeline
from chronicle.value import Interval, Language, Volume

OLD_TIME_FORMAT: str = "%d.%m.%Y %H:%M"


class OldImportManager(ImportManager):
    """Manager for old Chronicle format import."""

    @staticmethod
    @override
    def add_argument(parser: argparse._ArgumentGroup) -> None:
        parser.add_argument(
            "--import-old", help="import old Chronicle format", metavar="<path>"
        )
        parser.add_argument(
            "--import-old-movie",
            help="import old Chronicle format",
            metavar="<path>",
        )
        parser.add_argument(
            "--import-old-podcast",
            help="import old Chronicle format",
            metavar="<path>",
        )

    @staticmethod
    @override
    def process_arguments(
        arguments: argparse.Namespace, timeline: Timeline
    ) -> None:
        file_path: Path

        if arguments.import_old:
            file_path = Path(arguments.import_old)
            OldImporter(file_path).import_data(timeline)

        if arguments.import_old_movie:
            file_path = Path(arguments.import_old_movie)
            OldMovieImporter(file_path).import_data(timeline)

        if arguments.import_old_podcast:
            file_path = Path(arguments.import_old_podcast)
            OldPodcastImporter(file_path).import_data(timeline)


class OldImporter(Importer):
    """Importer from old Chronicle format."""

    def __init__(self, file_path: Path):
        self.file_path: Path = file_path

    def import_data(self, timeline: Timeline) -> None:
        objects = timeline.objects

        with self.file_path.open() as input_file:
            structure: list[dict[str, Any]] = json.load(input_file)

        for data in structure:
            if "_" in data and data["_"] == "_":
                continue
            time: Time | None = None
            if "begin" in data and "end" in data:
                begin: datetime = datetime.strptime(
                    data["begin"], OLD_TIME_FORMAT
                )
                end: datetime = datetime.strptime(data["end"], OLD_TIME_FORMAT)
                time = Time.from_moments(
                    Moment.from_datetime(begin), Moment.from_datetime(end)
                )
            if "middle" in data:
                middle: datetime = datetime.strptime(
                    data["middle"], OLD_TIME_FORMAT
                )
                time = Time.from_moment(Moment.from_datetime(middle))

            if not time:
                continue
                # TODO(enzet): Add warning.

            event: Event | None = None

            title: str
            language: Language
            book: Book | None

            if data["type"] == "listen":
                if data.get("kind") in ("music111", "song111", None):
                    data["kind"] = "music"
                    event = ListenMusicEvent(time=time)

                elif data["kind"] == "podcast":
                    title = data["title"]
                    language = Language(data["language"])
                    assert "from" in data and "to" in data
                    interval = Interval.from_json(
                        data["from"] + "/" + data["to"]
                    )
                    podcast_id: str = title
                    podcast = Podcast(
                        id=podcast_id, title=title, language=language
                    )
                    for object_ in timeline.objects.objects.values():
                        if (
                            isinstance(object_, Podcast)
                            and object_.title == podcast.title
                        ):
                            podcast = object_
                            break
                    objects.set_object(podcast_id, podcast)
                    event = ListenPodcastEvent(
                        time=time,
                        podcast=podcast,
                        interval=interval,
                        episode=data.get("episode", None),
                        season=data.get("season", None),
                    )

                elif data["kind"] == "audiobook111":
                    title = data["title"]
                    language = Language(data["language"])
                    book_id: str = title
                    data["audiobook_id"] = book_id
                    book = Book(id=book_id, title=title, language=language)
                    audiobook = Audiobook(id="audio_" + book_id, book=book)
                    objects.set_object(book_id, book)
                    objects.set_object("audio_" + book_id, audiobook)
                    event = ListenAudiobookEvent(time=time, audiobook=audiobook)

            elif data["type"] == "watch":
                if "movie_id" not in data and "title" in data:
                    title = data["title"]
                    movie_id = title
                    movie = Video(id=movie_id, title=title)
                    objects.set_object(movie_id, movie)
                duration = None
                interval = None
                if "duration" in data:
                    duration = Timedelta.from_code(data["duration"])
                if "from" in data and "to" in data:
                    interval = Interval.from_json(
                        data["from"] + "/" + data["to"]
                    )
                event = WatchEvent(
                    time=time,
                    video=movie,
                    duration=duration,
                    interval=interval,
                    language=(
                        Language(data["language"])
                        if "language" in data and data["language"]
                        else None
                    ),
                    subtitles=(
                        Language(data["subtitles"])
                        if "subtitles" in data and data["subtitles"]
                        else None
                    ),
                    season=data.get("season", None),
                    episode=data.get("episode", None),
                )

            elif data["type"] == "read":
                book = None
                if "book_id" not in data and "title" in data:
                    for object_ in timeline.objects.objects.values():
                        if (
                            isinstance(object_, Book)
                            and object_.title == data["title"]
                        ):
                            book = object_
                            book_id = object_.id
                            break
                    else:
                        book_id = data["title"]
                        if (
                            not objects.has_object(book_id)
                            and "language" in data
                        ):
                            book = Book(
                                book_id,
                                title=data["title"],
                                language=Language(str(data["language"])),
                            )
                            objects.set_object(book_id, book)
                        else:
                            book_object: Object = objects.get_object(book_id)
                            if not isinstance(book_object, Book):
                                message: str = (
                                    f"Expected book, got `{book_object}`."
                                )
                                raise ValueError(message)
                            book = book_object

                    data["book_id"] = book_id

                def get_volume(structure: dict[str, Any]) -> Volume | None:
                    if "size" in structure:
                        volume = Volume(value=structure["size"])
                    elif "from" in structure and "to" in structure:
                        volume = Volume(
                            from_=structure["from"], to_=structure["to"]
                        )
                    else:
                        return None
                    if "of" not in structure and "measure" not in structure:
                        message: str = (
                            "Cannot determine volume measure for "
                            f"`{structure}`."
                        )
                        raise ChronicleValueError(message)
                    if "of" in structure:
                        volume.of = structure["of"]
                    if "measure" in structure:
                        volume.measure = structure["measure"]
                    return volume

                volume = None
                if "volume" in data:
                    if not data["volume"]:
                        volume = None
                    else:
                        volume = get_volume(data["volume"])
                else:
                    volume = get_volume(data)

                event = ReadEvent(
                    time=time,
                    book=book,
                    volume=volume,
                    language=(
                        Language(data["language"])
                        if "language" in data and data["language"]
                        else None
                    ),
                )

            if event:
                timeline.events.append(event)


class OldMovieImporter(Importer):
    """Importer for movies from old Chronicle format."""

    def __init__(self, file_path: Path):
        self.file_path: Path = file_path

    def import_data(self, timeline: Timeline) -> None:
        language_with_subtitles_pattern: re.Pattern = re.compile(
            r"(?P<language>..)\[(?P<subtitles>..)\]"
        )
        language_pattern: re.Pattern = re.compile(r"(?P<language>..)\[\]")

        with self.file_path.open() as input_file:
            structure: list[dict[str, Any]] = json.load(input_file)

        for data in structure:
            if "_" in data and data["_"] == "_":
                continue

            time: Time
            if "date" not in data or not data["date"]:
                time = Time.from_string("1990-01-01", Context())
            else:
                time = Time.from_string(data["date"], Context())
            time.is_assumed = True

            title = data.get("title", "---")

            movie: Video = Video(id=title, title=title)

            duration: Timedelta | None = None
            if "duration" in data:
                duration = Timedelta.from_code(data["duration"])

            if not duration:
                duration = Timedelta(timedelta(minutes=120))

            language: Language | None = None
            subtitles: Language | None = None

            if "language" not in data:  # Silent movie.
                pass
            elif match := language_with_subtitles_pattern.match(
                data["language"]
            ):
                language = Language(match.group("language"))
                subtitles = Language(match.group("subtitles"))
            elif match := language_pattern.match(data["language"]):
                language = Language(match.group("language"))
            elif len(data["language"]) == 2:
                language = Language(data["language"])

            event: WatchEvent = WatchEvent(
                time=time,
                video=movie,
                duration=duration,
                language=language,
                subtitles=subtitles,
                episode=data.get("episode", None),
                season=data.get("season", None),
            )
            timeline.events.append(event)


class OldPodcastImporter(Importer):
    """Importer for podcasts from old Chronicle format."""

    def __init__(self, file_path: Path):
        self.file_path: Path = file_path

    def import_data(self, timeline: Timeline) -> None:
        with self.file_path.open() as input_file:
            structure: list[dict[str, Any]] = json.load(input_file)["sessions"]

        for data in structure:
            time: Time = Time.from_string(data["date"], Context())
            duration: Timedelta | None = None
            if "duration" in data:
                duration = Timedelta.from_code(data["duration"])
            podcast: Podcast = Podcast(
                id=data["title"],
                title=data["title"],
                language=Language(data["language"]),
            )
            for object_ in timeline.objects.objects.values():
                if (
                    isinstance(object_, Podcast)
                    and object_.title == podcast.title
                ):
                    podcast = object_
                    break
            event: ListenPodcastEvent = ListenPodcastEvent(
                time=time,
                podcast=podcast,
                duration=duration,
                episode=data.get("episode", None),
                season=data.get("season", None),
            )
            timeline.events.append(event)
