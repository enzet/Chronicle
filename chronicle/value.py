"""Argument value."""

import re
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Literal, Self

from chronicle.errors import ChronicleValueException
from chronicle.time import INTERVAL_PATTERN, Timedelta

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

LANGUAGES: dict[str, tuple[str, str]] = {
    "ar": ("Arabic", "#FF7F50"),
    "be": ("Belarusian", "#FF7F50"),
    "da": ("Danish", "#FF7F50"),
    "de": ("German", "#DFA398"),
    "el": ("Greek", "#FF7F50"),
    "en": ("English", "#FF7F50"),
    "eo": ("Esperanto", "#608F66"),
    "es": ("Spanish", "#CE6C5E"),
    "fa": ("Persian", "#FF7F50"),
    "fr": ("French", "#274766"),
    "ge": ("Georgian", "#FF7F50"),
    "he": ("Hebrew", "#FF7F50"),
    "hi": ("Hindi", "#FF7F50"),
    "hy": ("Armenian", "#FF7F50"),
    "is": ("Icelandic", "#FF7F50"),
    "it": ("Italian", "#FF7F50"),
    "ja": ("Japanese", "#CA1717"),
    "ka": ("Georgian", "#FF7F50"),
    "ko": ("Korean", "#FF7F50"),
    "la": ("Latin", "#888888"),
    "no": ("Norwegian", "#FF7F50"),
    "po": ("Polish", "#FF7F50"),
    "pt": ("Portuguese", "#FF7F50"),
    "rsl": ("Russian Sign Language", "#FF7F50"),
    "ru": ("Russian", "#FF7F50"),
    "sv": ("Swedish", "#FF7F50"),
    "uk": ("Ukrainian", "#FF7F50"),
    "zh": ("Chinese", "#FF7F50"),
}

WRITING_SYSTEM_NAMES = {
    "arab": "Arabic",
    "armn": "Armenian",
    "deva": "Devanagari",
    "geor": "Georgian",
    "hang": "Hangul",
    "kana": "Hiragana, Katakana, and Kanji",
}


@dataclass
class Value:
    """Base class for all values."""

    prefix: ClassVar[str | None] = None

    patterns: ClassVar[list[re.Pattern]] = []

    extractors: ClassVar[list[Callable[[re.Match], Self]]] = []

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Create value from string representation."""

        for i, pattern in enumerate(cls.patterns):
            if match := pattern.match(string):
                return cls.extractors[i](match.group)

        raise ChronicleValueException(f"Unknown value: `{string}`.")


@dataclass
class WikidataId(Value):
    """Wikidata entity identifier."""

    id: int
    """Wikidata entity identifier (without `Q` prefix)."""

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"Q\d+")]
    extractors: ClassVar[list[Callable]] = [lambda groups: int(groups(0)[1:])]


@dataclass
class Language:
    """Natural language of text, speach, or song."""

    code: str
    """ISO 639-1 language code."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"\.(?P<code>[a-z][a-z])")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Language(groups("code"))
    ]

    def __post_init__(self) -> None:
        """Verify that the language code is valid."""

        if self.code not in LANGUAGES:
            raise ChronicleValueException(
                f"Unknown language code: `{self.code}`."
            )

    @classmethod
    def from_json(cls, code: str) -> Self:
        """Create language from JSON."""
        return cls(code)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Language):
            raise ValueError(f"Cannot compare `{self}` with `{other}`.")
        return self.code == other.code

    def to_string(self) -> str:
        """Get English name of the language or return code."""

        if self.code in LANGUAGES:
            return LANGUAGES[self.code][0]

        return self.code

    def get_color(self) -> str:
        """Get color of the language."""
        return LANGUAGES[self.code][1]

    def to_command(self) -> str:
        """Get command representation of the language."""
        return f".{self.code}"

    def __hash__(self) -> int:
        return hash(self.code)


@dataclass
class Subject(Value):
    """Categorised subject."""

    subject: list[str]

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"\/(?P<subjects>[a-z0-9_/]+)")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Subject(groups("subjects").split("/"))
    ]

    def is_language(self) -> bool:
        """Check if the subject is a language."""
        return self.subject[0] == "language"

    def get_language(self) -> Language | None:
        """Get language from the subject."""
        if self.is_language() and len(self.subject) > 1:
            return Language(self.subject[1])
        return None

    def __hash__(self) -> int:
        return hash("/".join(self.subject))

    def to_string(self) -> str:
        """Get string representation of the subject."""
        return "/".join(self.subject)


@dataclass
class Tags:
    """Arbitrary user tag set."""

    tags: set[str]

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"!([0-9a-z_,-]+)")]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: set(groups(1).split(","))
    ]


@dataclass
class ProgrammingLanguage:
    """Programming language, e.g. `python`, `cpp`, `go`."""

    code: str

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"\.(?P<code>[a-z]+)")]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: ProgrammingLanguage(groups("code"))
    ]


@dataclass
class OSM:
    """OpenStreetMap object."""

    id: int
    version: int

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"osm:(?P<id>\d+)/(?P<version>\d+)")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: OSM(id=int(groups("id")), version=int(groups("version")))
    ]


@dataclass
class Birthday:
    """Birthday."""

    day: int
    month: int
    year: int | None = None

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<y>\d{4})?-(?P<m>\d{2})-(?P<d>\d{2})")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Birthday(
            day=int(groups("d")),
            month=int(groups("m")),
            year=int(groups("y")) if groups("y") else None,
        )
    ]


@dataclass
class Interval:
    """Time interval in seconds."""

    start: Timedelta | None = None
    end: Timedelta | None = None

    patterns: ClassVar[list[re.Pattern]] = [INTERVAL_PATTERN]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Interval().from_json(groups(0))
    ]

    @classmethod
    def from_json(cls, string: str) -> "Interval":
        start, end = string.split("/")
        return cls(
            start=Timedelta.from_json(start), end=Timedelta.from_json(end)
        )

    def to_json(self) -> str:
        return (
            (self.start.to_json() if self.start is not None else "")
            + ("/" if self.start is not None or self.end is not None else "")
            + (self.end.to_json() if self.end is not None else "")
        )

    def to_string(self) -> str:
        return self.to_json()

    def to_command(self) -> str:
        return self.to_json()

    def get_duration(self) -> float:
        if self.start is None or self.end is None:
            return 0.0
        return (self.end - self.start).total_seconds()


@dataclass
class Cost(Value):
    """Cost, price in some currency."""

    value: float
    currency: str

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<v>\d+(\.\d*)?)(?P<c>[a-z][a-z][a-z])")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Cost(value=float(groups("v")), currency=groups("c"))
    ]


class Distance:
    """Distance in meters."""

    value: float

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<v>\d+(\.\d+)?)m"),
        re.compile(r"(?P<v>\d+(\.\d+)?)km"),
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: float(groups("v")),
        lambda groups: float(groups("v")) * 1000.0,
    ]


class Kilocalories:
    """Kilocalories."""

    value: float

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<v>\d+(\.\d+)?)kcal")
    ]
    extractors: ClassVar[list[Callable]] = [lambda groups: float(groups("v"))]


class Season:
    """Season number."""

    number: int

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"[Ss](\d+)")]
    extractors: ClassVar[list[Callable]] = [lambda groups: int(groups(1))]


class Episode:
    """Episode number."""

    episode_id: int | str
    """Episode identifier.

    Sometimes it's not a number, but a string."""

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"[Ee](\d+)")]
    extractors: ClassVar[list[Callable]] = [lambda groups: groups(1)]


@dataclass
class Volume:
    """Partial volume of some object, e.g. book."""

    value: float | None = None

    from_: float | None = None

    to_: float | None = None

    of: float | None = None
    """The value of the whole object.

    If `from_` and `to_` are in percent, `of` should equal 100.
    """

    measure: str | None = None
    """Measure of the volume.

    There are two special values for `measure`: `pages` and `percent`. Pages are
    defined as approximatelly 2000 characters chunks of text. Percent is the
    percentage of the whole object. Users however can define their own measure,
    e.g. `screens` or `slides`, in that case `of` should be set.
    """

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(
            r"(?P<from>\d+(\.\d*)?)/(?P<to>\d+(\.\d*)?)/(?P<of>\d+(\.\d*)?)"
        ),
        re.compile(r"(?P<from>\d+(\.\d*)?)/(?P<to>\d+(\.\d*)?)%"),
        re.compile(r"(?P<from>\d+(\.\d*)?)/(?P<to>\d+(\.\d*)?)p"),
        re.compile(
            r"(?P<from>\d+(\.\d*)?)/(?P<to>\d+(\.\d*)?)/(?P<of>\d+(\.\d*)?)p"
        ),
        re.compile(r"(?P<value>\d+(\.\d*)?)/(?P<of>\d+(\.\d*)?)"),
        re.compile(r"(?P<value>\d+(\.\d*)?)%"),
        re.compile(r"(?P<value>\d+(\.\d*)?)p"),
        re.compile(r"(?P<value>\d+(\.\d*)?)w"),
    ]

    extractors: ClassVar[list[Callable]] = [
        lambda groups: Volume(
            from_=float(groups("from")),
            to_=float(groups("to")),
            of=float(groups("of")),
        ),
        lambda groups: Volume(
            from_=float(groups("from")),
            to_=float(groups("to")),
            of=100.0,
            measure="percent",
        ),
        lambda groups: Volume(
            from_=float(groups("from")),
            to_=float(groups("to")),
            measure="pages",
        ),
        lambda groups: Volume(
            from_=float(groups("from")),
            to_=float(groups("to")),
            of=float(groups("of")),
            measure="pages",
        ),
        lambda groups: Volume(
            value=float(groups("value")), of=float(groups("of"))
        ),
        lambda groups: Volume(value=float(groups("value")), measure="percent"),
        lambda groups: Volume(value=float(groups("value")), measure="pages"),
        lambda groups: Volume(value=float(groups("value")), measure="words"),
    ]

    def __hash__(self) -> int:
        return hash(self.to_string())

    def __post_init__(self):
        if self.measure == "percent":
            self.of = 100.0

    def verify(self) -> None:
        """Raise an error if the volume value is incorrect."""

        if self.from_ and self.to_ and self.from_ > self.to_:
            raise ChronicleValueException(
                "Start value should be less than end value, not "
                f"`{self.from_}` > `{self.to_}`."
            )
        if self.measure == "percent" and self.of != 100.0:
            raise ChronicleValueException(
                f"Maximum should be 100%, not `{self.of}`."
            )
        if (
            self.measure == "percent"
            and self.from_
            and (self.from_ < 0.0 or self.from_ > 100.0)
        ):
            raise ChronicleValueException(
                f"From should be in range 0–100%, not `{self.from_}`."
            )
        if (
            self.measure == "percent"
            and self.to_
            and (self.to_ < 0.0 or self.to_ > 100.0)
        ):
            raise ChronicleValueException(
                f"To should be in range 0–100%, not `{self.to_}`."
            )

    def get_ratio(self) -> float | None:
        if self.to_ is not None and self.from_ is not None and self.of:
            return (self.to_ - self.from_) / self.of

        return None

    def to_command(self) -> str:
        match self.measure:
            case "pages":
                return (
                    f"{self.value}p"
                    if self.value
                    else f"{self.from_}/{self.to_}p"
                )
            case "percent":
                return (
                    f"{self.value}%"
                    if self.value
                    else f"{self.from_}/{self.to_}%"
                )
        if not self.of:
            raise ChronicleValueException(
                "`of` should be set for custom measure."
            )

        return f"{self.from_}/{self.to_}/{self.of}"

    def to_string(self) -> str:
        match self.measure:
            case "pages":
                return (
                    f"{self.value} pages"
                    if self.value
                    else f"{self.from_}–{self.to_} pages"
                )
            case "percent":
                return (
                    f"{self.value}%"
                    if self.value
                    else f"{self.from_:.1f}–{self.to_:.1f}%"
                )

        return (
            f"{self.from_}–{self.to_} of {self.of}"
            if self.of
            else f"{self.from_}–{self.to_}"
        )


@dataclass
class AudiobookVolume:
    """Partial volume of some object, e.g. book."""

    from_: float | None = None
    """Interval start."""

    to_: float | None = None
    """Interval end."""

    measure: Literal["percent", "seconds"] | None = None

    of: float | None = None
    """The value of the whole object.

    If `from_` and `to_` are in percent, `of` should equal 100.
    """

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<from>\d+(\.\d*)?)/(?P<to>\d+(\.\d*)?)%")
    ]

    extractors: ClassVar[list[Callable]] = [
        lambda groups: AudiobookVolume(
            from_=float(groups("from")),
            to_=float(groups("to")),
            measure="percent",
            of=100.0,
        )
    ]

    def __hash__(self) -> int:
        return hash(self.to_string())

    def get_ratio(self) -> float:
        if self.to_ is not None and self.from_ is not None:
            return (self.to_ - self.from_) / 100.0

        raise ChronicleValueException()

    def to_command(self) -> str:
        match self.measure:
            case "percent":
                return f"{self.from_}/{self.to_}%"
            case "seconds":
                return f"{self.from_}/{self.to_}s"
        raise ChronicleValueException(f"Unknown measure `{self.measure}`.")

    def to_string(self) -> str:
        match self.measure:
            case "percent":
                return f"{self.from_}–{self.to_}%"
            case "seconds":
                return f"{self.from_}–{self.to_}s"
        raise ChronicleValueException(f"Unknown measure `{self.measure}`.")


@dataclass
class Integers:
    """List of integers."""

    values: list[int]
    """Integers."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(\d+)(,(\d+))*"),
        re.compile(r"\d+x\d+"),
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: [int(group) for group in groups(0).split(",")],
        lambda groups: (
            int(groups(0).split("x")[0]) * [int(groups(0).split("x")[1])]
        ),
    ]


@dataclass
class Weights:
    """List of weights in kilograms."""

    values: list[float]
    """Weights in kilograms."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"((\d+(\.\d+)?)kg)(,(\d+(\.\d+)?)kg)*")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: [float(group) for group in groups(0).split(",")]
    ]
