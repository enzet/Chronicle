"""Events about reading, watching or listening things."""

import re
from dataclasses import dataclass, field
from typing import ClassVar

from chronicle.argument import Arguments
from chronicle.event.core import Event
from chronicle.value import (
    AudiobookVolume,
    ChronicleValueException,
    Episode,
    Interval,
    Language,
    Season,
    Subject,
    Volume,
)
from chronicle.objects.core import (
    Ballet,
    Book,
    Service,
    Video,
    Objects,
    Audiobook,
    Podcast,
)
from chronicle.summary.core import Summary
from chronicle.time import Timedelta

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class ListenEvent(Event):
    """Event representing listening to audio content."""

    title: str | None = None
    """Title of what was listened to."""

    duration: Timedelta | None = None
    """Duration of the listening session."""

    language: Language | None = None
    """Language of the audio content."""

    arguments: ClassVar[Arguments] = (
        Arguments(["listen"], "listen")
        .add_argument("title")
        .add_class_argument("duration", Timedelta)
        .add_class_argument("language", Language)
    )

    def register_summary(self, summary: Summary) -> None:
        if self.language:
            summary.register_listen(self.get_duration(), self.language)


@dataclass
class ListenPodcastEvent(Event):
    """Event representing listening to a podcast episode."""

    podcast: Podcast | None = None
    """Podcast that was listened to."""

    season: int | None = None
    """Season number of the podcast."""

    episode: str | None = None
    """Episode number or name."""

    speed: float | None = None
    """Speed at which the podcast was listened to."""

    interval: Interval | None = None
    """Duration of the podcast listening session."""

    duration: Timedelta | None = None
    """Duration of the podcast listening session."""

    arguments: ClassVar[Arguments] = (
        Arguments(["podcast"], "listen to podcast")
        .add_object_argument("podcast", Podcast)
        .add_class_argument("season", Season)
        .add_class_argument("episode", Episode)
        .add_class_argument("interval", Interval)
        .add_class_argument("duration", Timedelta)
        .add_argument(
            "speed",
            patterns=[re.compile(r"x(\d+(\.\d*))")],
            extractors=[lambda groups: float(groups(2))],
        )
    )

    def get_duration(self) -> float:
        """Get duration of the listening session in seconds."""
        if self.interval:
            return self.interval.get_duration()
        if self.duration:
            return self.duration.total_seconds()
        return self.time.get_duration()

    def get_language(self) -> Language | None:
        """Get language of the podcast."""
        if self.podcast:
            return self.podcast.language
        return None

    def register_summary(self, summary: Summary) -> None:
        language: Language | None = self.get_language()

        if not language:
            raise ChronicleValueException(f"Event `{self}` has no language.")

        summary.register_listen(self.get_duration(), language)


@dataclass
class ListenMusicEvent(Event):
    """Event representing listening to music."""

    title: str | None = None
    """Title of the song or music description."""

    interval: Interval = field(default_factory=Interval)
    """Duration of the music listening session."""

    artist: str | None = None
    """Artist who performed the song."""

    album: str | None = None
    """Album the song appears on."""

    language: Language | None = None
    """Language of the lyrics."""

    def get_language(self, _: Objects) -> Language:
        """Get language of the music."""
        return self.language

    arguments: ClassVar[Arguments] = (
        Arguments(["music", "song"], "listen music")
        .add_argument("title")
        .add_argument("artist", prefix="by")
        .add_argument("album", prefix="on")
        .add_class_argument("language", Language)
    )

    def get_duration(self) -> float:
        """Get duration of the listening session in seconds."""
        if self.interval:
            return self.interval.get_duration()
        return self.time.get_duration()


@dataclass
class ListenLectureEvent(Event):
    """Event representing listening to a lecture."""

    title: str | None = None
    """Title of the lecture."""

    language: Language | None = None
    """Language the lecture was given in."""

    interval: Interval = field(default_factory=Interval)
    """Duration of the lecture listening session."""

    arguments: ClassVar[Arguments] = (
        Arguments(["listen lecture"], "listen lecture")
        .add_argument("title")
        .add_class_argument("language", Language)
    )

    def get_language(self, _: Objects) -> Language | None:
        """Get language of the lecture."""
        return self.language

    def get_duration(self) -> float | None:
        """Get duration of the listening session in seconds."""
        if self.interval:
            return self.interval.get_duration()
        return self.time.get_duration()


@dataclass
class ReadEvent(Event):
    """Event representing reading a text in a natural language."""

    book: Book | None = None
    """Book that was read."""

    language: Language | None = None
    """Language of the book."""

    volume: Volume | None = None
    """Volume or portion of the book that was read."""

    subject: Subject | None = None
    """Subject category of the book (fiction, non-fiction, science, etc)."""

    arguments: ClassVar[Arguments] = (
        Arguments(["read"], "read")
        .add_object_argument("book", Book)
        .add_class_argument("language", Language)
        .add_class_argument("volume", Volume)
        .add_class_argument("subject", Subject)
    )

    def get_language(self) -> Language:
        """Get language of the book."""
        if self.language:
            return self.language
        if self.book and self.book.language:
            return self.book.language
        raise ChronicleValueException(f"Event {self} has no language.")

    def register_summary(self, summary: Summary) -> None:
        # Use language from the event or language of the book.
        language: Language
        if self.language:
            language = self.language
        else:
            if self.book and self.book.language:
                language = self.book.language
            else:
                return None

        # Compute duration.
        duration: float | None = self.get_duration()

        # Compute pages.
        pages: float | None = None
        if self.volume and self.volume.get_ratio() and self.book.volume:
            pages = self.volume.get_ratio() * self.book.volume

        if self.volume and self.volume.measure in (
            "four_inches_pages",
            "pages",
            "screens",
            "slides",
        ):
            coef = 1.0
            if self.volume.measure in (
                "screens",
                "slides",
                "four_inches_pages",
            ):
                coef = 0.5
            if self.volume and self.volume.value:
                pages = self.volume.value * coef
            if self.volume.to_ is not None and self.volume.from_ is not None:
                pages = self.volume.to_ - self.volume.from_

        # Register finished book.
        if (
            self.volume
            and self.volume.measure == "percent"
            and self.volume.to_ == 100.0
        ) or (
            self.volume and self.volume.of and self.volume.to_ == self.volume.of
        ):
            summary.register_finished_book(self.book)

        # Register reading pages.
        if pages is not None:
            summary.register_read_pages(pages, language)
        elif duration is not None:
            summary.register_read_pages(duration / 60 / 3, language)
        else:
            raise ChronicleValueException(
                f"Event {self} has neither pages, nor duration."
            )

        # Register reading duration.
        # FIXME: Check precision of the duration instead of the arbitrary limit.
        if duration is not None and duration < 16 * 3600.0:
            summary.register_read(duration, language)
        elif pages is not None:
            summary.register_read(pages * 60 * 3, language)


@dataclass
class StandupEvent(Event):
    """Event representing attending a standup comedy show."""

    title: str | None = None
    """Title or name of the standup show."""

    language: str | None = None
    """Language the show was performed in."""

    place_id: str | None = None
    """Identifier of the venue where the show took place."""

    arguments: ClassVar[Arguments] = (
        Arguments(["standup"], "standup")
        .add_argument("title")
        .add_class_argument("language", Language)
        .add_argument(
            "place_id", prefix="at", command_printer=lambda x: f"at {x}"
        )
    )


@dataclass
class WatchEvent(Event):
    """Event representing watching video content."""

    video: Video | None = None
    """Movie or TV show that was watched."""

    season: int | None = None
    """Season number for TV shows."""

    episode: int | str | None = None
    """Episode number or name."""

    interval: Interval | None = None
    """Interval of the movie or TV show that was watched."""

    duration: Timedelta | None = None
    """Duration of the watching session."""

    language: Language | None = None
    """Audio language of the content."""

    subtitles: Language | None = None
    """Language of subtitles if used."""

    service: Service | None = None
    """Streaming service used (e.g. cinema, Netflix, YouTube, TV, etc)."""

    subject: Subject | None = None
    """Categorised subject."""

    arguments: ClassVar[Arguments] = (
        Arguments(["watch"], "watch")
        .add_object_argument("video", Video)
        .add_class_argument("language", Language)
        .add_argument(
            "subtitles",
            patterns=[re.compile("_(..)")],
            extractors=[lambda groups: Language(groups(1))],
            command_printer=lambda x: f"_{x}",
        )
        .add_class_argument("season", Season)
        .add_object_argument("service", Service)
        .add_class_argument("episode", Episode)
        .add_class_argument("interval", Interval)
        .add_class_argument("duration", Timedelta)
        .add_class_argument("subject", Subject)
    )

    def register_summary(self, summary: Summary) -> None:
        language: Language | None = (
            self.subtitles if self.subtitles else self.language
        )
        if language:
            summary.register_watch(self.get_duration(), language)

        subject = self.subject if self.subject else self.video.subject
        if subject:
            summary.register_learn(self.get_duration(), subject, self.service)

    def get_duration(self) -> float:
        """Get duration of the watching session in seconds."""

        if self.interval:
            return self.interval.get_duration()
        if self.duration:
            return self.duration.total_seconds()
        if not self.time.is_assumed:
            return self.time.get_duration()

        # Estimate episode length to be 40 minutes.
        if self.episode or self.season:
            return 40.0 * 60.0

        # Estimate movie length to be 2 hours.
        return 2.0 * 60.0 * 60.0


@dataclass
class ListenAudiobookEvent(Event):
    """Event representing listening to an audiobook."""

    audiobook: Audiobook | None = None
    """Audiobook that was listened to."""

    interval: Interval | None = None
    """Interval of the audiobook that was listened to."""

    volume: AudiobookVolume | None = None
    """Volume or portion of the audiobook that was listened to."""

    speed: float | None = None
    """Playback speed multiplier."""

    arguments: ClassVar[Arguments] = (
        Arguments(["audiobook"], "listen to audiobook")
        .add_object_argument("audiobook", Audiobook)
        .add_class_argument("interval", Interval)
        .add_class_argument("volume", AudiobookVolume)
        .add_argument(
            "speed",
            loader=lambda value, _: float(value),
            patterns=[re.compile(r"x(\d*\.\d*)")],
            command_printer=lambda x: f"x{x}",
        )
    )

    def get_language(self) -> Language | None:
        """Get language of the audiobook."""
        return self.audiobook.get_language() if self.audiobook else None

    def register_summary(self, summary: Summary) -> None:
        """Register this audiobook event in the summary statistics."""
        if not self.interval and not self.volume:
            raise ChronicleValueException(
                f"Event {self} has neither interval, nor volume."
            )

        language: Language | None = self.get_language()
        if not language:
            raise ChronicleValueException(f"Event {self} has no language.")

        duration: float | None = None

        if self.interval:
            duration = self.interval.get_duration()
        elif self.volume:
            if not self.audiobook:
                raise ChronicleValueException(
                    f"Cannot get audiobook for event {self}."
                )
            if not isinstance(self.audiobook, Audiobook):
                raise ChronicleValueException(
                    f"{self.audiobook} is not an audiobook."
                )
            if not self.audiobook.duration:
                raise ChronicleValueException(
                    f"{self.audiobook} has no duration."
                )
            duration = (
                self.volume.get_ratio()
                * self.audiobook.duration.total_seconds()
            )

        if duration:
            if duration > 24.0 * 3600.0:
                raise ChronicleValueException(
                    f"Event {self} has duration {duration}."
                )
            summary.register_listen(duration, language)


@dataclass
class BalletEvent(Event):
    """Event representing attending a ballet performance."""

    ballet: Ballet | None = None
    """Show that was attended."""

    arguments: ClassVar[Arguments] = Arguments(
        ["ballet"], "ballet"
    ).add_object_argument("ballet", Ballet)

    def register_summary(self, summary: Summary) -> None:
        summary.register_show(self.ballet)


@dataclass
class ConcertEvent(Event):
    """Event representing attending a concert."""

    musician: str | None = None
    """Name of the musician or band performing."""

    arguments: ClassVar[Arguments] = Arguments(
        ["concert"], "concert"
    ).add_argument("musician")


@dataclass
class DrawEvent(Event):
    """Event representing drawing."""

    project: str | None = None
    """Project that was drawn."""

    service: Service | None = None
    """Service used to draw: graphical editor, CAD, etc."""

    arguments: ClassVar[Arguments] = (
        Arguments(["draw"], "draw")
        .add_argument("project")
        .add_object_argument("service", Service)
    )
