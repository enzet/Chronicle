import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from chronicle.event.art import (
    ListenAudiobookEvent,
    ListenMusicEvent,
    ListenPodcastEvent,
    ReadEvent,
    WatchEvent,
)
from chronicle.event.core import Event
from chronicle.harvest.core import Importer
from chronicle.objects.core import Audiobook, Book, Podcast, Video
from chronicle.time import Context, Moment, Time, Timedelta
from chronicle.timeline import Timeline
from chronicle.value import ChronicleValueException, Interval, Language, Volume

OLD_TIME_FORMAT: str = "%d.%m.%Y %H:%M"


class OldImporter(Importer):
    """Importer from old Chronicle format."""

    def __init__(self, file_path: Path):
        self.file_path: Path = file_path

    def import_data(self, timeline: Timeline) -> None:
        objects = timeline.objects

        with self.file_path.open() as input_file:
            structure: dict[str, Any] = json.load(input_file)

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
                # FIXME: Add warning.

            event: Event | None = None

            if data["type"] == "listen":
                if data.get("kind") in ("music111", "song111", None):
                    data["kind"] = "music"
                    event: ListenMusicEvent = ListenMusicEvent(time=time)

                elif data["kind"] == "podcast":
                    title: str = data["title"]
                    language = Language(data["language"])
                    assert "from" in data and "to" in data
                    interval = Interval.from_json(
                        data["from"] + "/" + data["to"]
                    )
                    podcast_id: str = title
                    podcast = Podcast(
                        id=podcast_id, title=title, language=language
                    )
                    for object in timeline.objects.objects.values():
                        if (
                            isinstance(object, Podcast)
                            and object.title == podcast.title
                        ):
                            podcast = object
                            break
                    objects.set_object(podcast_id, podcast)
                    event: ListenPodcastEvent = ListenPodcastEvent(
                        time=time,
                        podcast=podcast,
                        interval=interval,
                        episode=data["episode"] if "episode" in data else None,
                        season=data["season"] if "season" in data else None,
                    )

                elif data["kind"] == "audiobook111":
                    title: str = data["title"]
                    language = Language(data["language"])
                    book_id: str = title
                    data["audiobook_id"] = book_id
                    book = Book(id=book_id, title=title, language=language)
                    audiobook = Audiobook(id="audio_" + book_id, book=book)
                    objects.set_object(book_id, book)
                    objects.set_object("audio_" + book_id, audiobook)
                    event: ListenAudiobookEvent = ListenAudiobookEvent(
                        time=time, audiobook=audiobook
                    )

            elif data["type"] == "watch":
                if "movie_id" not in data and "title" in data:
                    title = data["title"]
                    movie_id = title
                    movie = Video(id=movie_id, title=title)
                    objects.set_object(movie_id, movie)
                duration = None
                interval = None
                if "duration" in data:
                    duration = Timedelta.from_json(data["duration"])
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
                    for object in timeline.objects.objects.values():
                        if (
                            isinstance(object, Book)
                            and object.title == data["title"]
                        ):
                            book = object
                            book_id = object.id
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
                            book = objects.get_object(book_id)
                    data["book_id"] = book_id

                def get_volume(structure: dict[str, Any]) -> Volume:
                    if "size" in structure:
                        volume = Volume(value=structure["size"])
                    elif "from" in structure and "to" in structure:
                        volume = Volume(
                            from_=structure["from"], to_=structure["to"]
                        )
                    else:
                        return None
                    if "of" not in structure and "measure" not in structure:
                        raise ChronicleValueException(
                            "Cannot determine volume measure for "
                            f"`{structure}`."
                        )
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

            pass


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
            structure: dict[str, Any] = json.load(input_file)

        for data in structure:
            if "_" in data and data["_"] == "_":
                continue

            if "date" not in data or not data["date"]:
                time: Time = Time.from_string("1990-01-01", Context())
            else:
                time: Time = Time.from_string(data["date"], Context())
            time.is_assumed = True

            if "title" not in data:
                title = "---"
            else:
                title = data["title"]

            movie: Video = Video(id=title, title=title)

            duration: Timedelta | None = None
            if "duration" in data:
                duration = Timedelta.from_json(data["duration"])

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
            structure: dict[str, Any] = json.load(input_file)["sessions"]

        for data in structure:
            time: Time = Time.from_string(data["date"], Context())
            duration: Timedelta | None = None
            if "duration" in data:
                duration = Timedelta.from_json(data["duration"])
            podcast: Podcast = Podcast(
                id=data["title"],
                title=data["title"],
                language=Language(data["language"]),
            )
            for object in timeline.objects.objects.values():
                if (
                    isinstance(object, Podcast)
                    and object.title == podcast.title
                ):
                    podcast = object
                    break
            event: ListenPodcastEvent = ListenPodcastEvent(
                time=time,
                podcast=podcast,
                duration=duration,
                episode=data["episode"] if "episode" in data else None,
                season=data["season"] if "season" in data else None,
            )
            timeline.events.append(event)
