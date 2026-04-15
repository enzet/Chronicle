"""Argument value."""

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar, Literal, Self

from colour import Color

from chronicle.errors import ChronicleValueError
from chronicle.time import DELTA_PATTERN_TEXT, INTERVAL_PATTERN, Timedelta

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

LANGUAGES: dict[str, tuple[str, str, str]] = {
    "ar": ("Arabic", "العربية", "#286035"),
    "be": ("Belarusian", "Беларуская", "#CB2E3F"),
    "da": ("Danish", "Dansk", "#061A57"),
    "de": ("German", "Deutsch", "#F7D046"),
    "el": ("Greek", "Ελληνικά", "#2A5DA9"),
    "en": ("English", "English", "#071B65"),
    "eo": ("Esperanto", "Esperanto", "#44982A"),
    "es": ("Spanish", "Español", "#CE6C5E"),
    "fa": ("Persian", "فارسی", "#D73E3E"),
    "fr": ("French", "Français", "#4193C3"),
    "he": ("Hebrew", "עברית", "#1334B2"),
    "hi": ("Hindi", "हिन्दी", "#E7695A"),
    "hy": ("Armenian", "Հայերեն", "#E8AD3B"),
    "is": ("Icelandic", "Íslenska", "#205098"),
    "it": ("Italian", "Italiano", "#41914D"),
    "ja": ("Japanese", "日本語", "#AE232F"),
    "ka": ("Georgian", "ქართული", "#EA3323"),
    "ko": ("Korean", "한국어", "#1B449C"),
    "la": ("Latin", "Latina", "#FDF351"),
    "nb": ("Norwegian", "Norsk bokmål", "#061A57"),
    "no": ("Norwegian", "Norsk", "#061A57"),
    "po": ("Polish", "Polski", "#CB2E3F"),
    "pt": ("Portuguese", "Português", "#2B6519"),
    "rsl": ("Russian Sign Language", "РЖЯ", "#1335A1"),
    "ru": ("Russian", "Русский", "#1335A1"),
    "sv": ("Swedish", "Svenska", "#205090"),
    "th": ("Thai", "ภาษาไทย", "#2D2A4A"),
    "tr": ("Turkish", "Türkçe", "#888888"),
    "uk": ("Ukrainian", "Українська", "#F9D849"),
    "zh": ("Chinese", "中文", "#DB352F"),
}

WRITING_SYSTEM_NAMES = {
    "arab": "Arabic",
    "armn": "Armenian",
    "deva": "Devanagari",
    "geor": "Georgian",
    "hang": "Hangul",
    "kana": "Hiragana, Katakana, and Kanji",
}

MAX_PERCENT: float = 100.0
SECONDS_IN_DAY: float = 24.0 * 3600.0


@dataclass
class Value:
    """Base class for all values."""

    prefix: ClassVar[str | None] = None
    """Prefix of the value.

    TODO: probably we should get rid of prefixes here and use it only in event
        classes.
    """

    patterns: ClassVar[list[re.Pattern]] = []
    """Patterns to match the value."""

    extractors: ClassVar[list[Callable[[re.Match], Self]]] = []
    """Extractors to extract the value from the match."""

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Create value from string representation."""

        for i, pattern in enumerate(cls.patterns):
            if match := pattern.match(string):
                return cls.extractors[i](match.group)

        message: str = f"Unknown value: `{string}`."
        raise ChronicleValueError(message)


@dataclass
class WikidataId(Value):
    """Wikidata entity identifier."""

    id: int
    """Wikidata entity identifier (without `Q` prefix)."""

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"Q\d+")]
    extractors: ClassVar[list[Callable]] = [lambda groups: int(groups(0)[1:])]


COLOR_SCHEME_DARK_BLUE: list[Color] = [
    Color("#4a28b2"),
    Color("#2b1040"),
    Color("#442375"),
    Color("#3641a9"),
    Color("#201249"),
]


@dataclass
class Language(Value):
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
            message: str = f"Unknown language code: `{self.code}`."
            raise ChronicleValueError(message, self)

    @classmethod
    def from_json(cls, code: str) -> Self:
        """Create language from JSON."""
        return cls(code)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Language):
            return NotImplemented
        return self.code == other.code

    def to_string(self) -> str:
        """Get English name of the language or return code."""

        if self.code in LANGUAGES:
            return LANGUAGES[self.code][0]

        return self.code

    def to_native(self) -> str:
        """Get native name of the language or return code."""

        if self.code in LANGUAGES:
            return LANGUAGES[self.code][1]

        return self.code

    def get_color(self) -> str:
        """Get color of the language."""
        return LANGUAGES[self.code][2]

    def to_command(self) -> str:
        """Get command representation of the language."""
        return f".{self.code}"

    def __hash__(self) -> int:
        return hash(self.code)


@dataclass
class Script(Value):
    """Script of a language."""

    code: str
    """Script code."""

    def get_language(self) -> Language | None:
        match self.code:
            case "arab":
                return Language("ar")
            case "deva":
                return Language("hi")
            case "hang":
                return Language("ko")
            case "hebr":
                return Language("he")
            case "kana":
                return Language("ja")

        msg = f"Unknown script code: `{self.code}`."
        raise ChronicleValueError(msg, self)


@dataclass
class Subject(Value):
    """Categorised subject."""

    subject: list[str]
    """Subject value: from most general to most specific.

    For example, `["language", "english"]` for English language,
    `["fiction", "mystery"]` for a mystery novels.
    """

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"\/(?P<subjects>[a-z0-9_/]+)")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Subject(groups("subjects").split("/"))
    ]

    def is_language(self) -> bool:
        """Check if the subject is a language."""
        return self.subject[0] == "language"

    def is_script(self) -> bool:
        """Check if the subject is a script."""
        return self.subject[0] == "script"

    def get_language(self) -> Language | None:
        """Get language from the subject."""
        if self.is_language() and len(self.subject) > 1:
            return Language(self.subject[1])
        if self.is_script() and len(self.subject) > 1:
            return Script(self.subject[1]).get_language()
        return None

    def __hash__(self) -> int:
        return hash("/".join(self.subject))

    def to_string(self) -> str:
        """Get string representation of the subject."""
        return "/".join(self.subject)


@dataclass
class Tags(Value):
    """Arbitrary user tag set."""

    tags: set[str]
    """Tag values."""

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"!([0-9a-z_,-]+)")]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: set(groups(1).split(","))
    ]


@dataclass
class ProgrammingLanguage(Value):
    """Programming language, e.g. `python`, `cpp`, `go`.

    For identifies it's peferrable to use GitHub Linguist scheme. See
    https://github.com/github-linguist/linguist/blob/main/lib/linguist/languages.yml.
    """

    code: str
    """Programming language identifier."""

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"\.(?P<code>[a-z]+)")]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: ProgrammingLanguage(groups("code"))
    ]


@dataclass
class OSM(Value):
    """OpenStreetMap object.

    URL of the object is
    `https://www.openstreetmap.org/<type>/<id>/history/<version>`.
    """

    type: str
    """OpenStreetMap object type."""

    id: int
    """OpenStreetMap object identifier."""

    version: int
    """OpenStreetMap object version."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"osm:(?P<type>[a-z]+)/(?P<id>\d+)/(?P<version>\d+)")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: OSM(
            type=groups("type"),
            id=int(groups("id")),
            version=int(groups("version")),
        )
    ]


@dataclass
class Date(Value):
    """Date."""

    day: int
    """Day of the month."""

    month: int
    """Month of the year."""

    year: int | None = None
    """Year."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<y>\d{4})?-(?P<m>\d{2})-(?P<d>\d{2})")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Date(
            day=int(groups("d")),
            month=int(groups("m")),
            year=int(groups("y")) if groups("y") else None,
        )
    ]


@dataclass
class Interval(Value):
    """Time interval in seconds."""

    start: Timedelta | None = None
    """Start of the interval."""

    end: Timedelta | None = None
    """End of the interval."""

    patterns: ClassVar[list[re.Pattern]] = [INTERVAL_PATTERN]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Interval().from_json(groups(0))
    ]

    @classmethod
    def from_json(cls, string: str) -> "Interval":
        start, end = string.split("/")
        return cls(
            start=Timedelta.from_code(start), end=Timedelta.from_code(end)
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
    """Cost value."""

    currency: str
    """Currency code, e.g. `usd` for United States Dollar."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<v>\d+(\.\d*)?)(?P<c>[a-z][a-z][a-z])")
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Cost(value=float(groups("v")), currency=groups("c"))
    ]


@dataclass
class Distance(Value):
    """Distance in meters."""

    value: float
    """Distance value."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<v>\d+(\.\d+)?)cm"),
        re.compile(r"(?P<v>\d+(\.\d+)?)m"),
        re.compile(r"(?P<v>\d+(\.\d+)?)km"),
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: float(groups("v")) / 100.0,
        lambda groups: float(groups("v")),
        lambda groups: float(groups("v")) * 1000.0,
    ]


@dataclass
class Speed(Value):
    """Speed in kilometers per hour."""

    value: float
    """Speed value in km/h."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<v>\d+(\.\d+)?)km/h"),
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: float(groups("v")),
    ]


@dataclass
class Pace(Value):
    """Pace in seconds per kilometer, encoded as `MM:SS/km`."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(rf"({DELTA_PATTERN_TEXT})/km"),
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Timedelta.from_code(groups(1)),
    ]


@dataclass
class Kilocalories(Value):
    """Kilocalories."""

    value: float
    """Value in kilocalories."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<v>\d+(\.\d+)?)kcal")
    ]
    extractors: ClassVar[list[Callable]] = [lambda groups: float(groups("v"))]


@dataclass
class Carbohydrates(Value):
    """Carbohydrates in grams."""

    value: float
    prefix: ClassVar[str | None] = "carbs:"

    def to_command(self) -> str:
        return f"carbs: {self.value:g}"


@dataclass
class Protein(Value):
    """Protein in grams."""

    value: float
    prefix: ClassVar[str | None] = "prot:"

    def to_command(self) -> str:
        return f"prot: {self.value:g}"


@dataclass
class Fat(Value):
    """Fat in grams."""

    value: float
    prefix: ClassVar[str | None] = "fat:"

    def to_command(self) -> str:
        return f"fat: {self.value:g}"


@dataclass
class SaturatedFat(Value):
    """Saturated fat in grams."""

    value: float
    prefix: ClassVar[str | None] = "sfat:"

    def to_command(self) -> str:
        return f"sfat: {self.value:g}"


@dataclass
class Fiber(Value):
    """Dietary fiber in grams."""

    value: float
    prefix: ClassVar[str | None] = "fib:"

    def to_command(self) -> str:
        return f"fib: {self.value:g}"


@dataclass
class Sugar(Value):
    """Total sugar in grams."""

    value: float
    prefix: ClassVar[str | None] = "sg:"

    def to_command(self) -> str:
        return f"sg: {self.value:g}"


@dataclass
class AddedSugar(Value):
    """Added sugar in grams."""

    value: float
    prefix: ClassVar[str | None] = "asg:"

    def to_command(self) -> str:
        return f"asg: {self.value:g}"


@dataclass
class Omega3(Value):
    """Omega-3 fatty acids in grams."""

    value: float
    prefix: ClassVar[str | None] = "omega3:"

    def to_command(self) -> str:
        return f"omega3: {self.value:g}"


@dataclass
class Calcium(Value):
    """Calcium in milligrams."""

    value: float
    prefix: ClassVar[str | None] = "ca:"

    def to_command(self) -> str:
        return f"ca: {self.value:g}"


@dataclass
class Iron(Value):
    """Iron in milligrams."""

    value: float
    prefix: ClassVar[str | None] = "fe:"

    def to_command(self) -> str:
        return f"fe: {self.value:g}"


@dataclass
class VitaminD(Value):
    """Vitamin D in international units (IU)."""

    value: float
    prefix: ClassVar[str | None] = "vitd:"

    def to_command(self) -> str:
        return f"vitd: {self.value:g}"


@dataclass
class Magnesium(Value):
    """Magnesium in milligrams."""

    value: float
    prefix: ClassVar[str | None] = "mg:"

    def to_command(self) -> str:
        return f"mg: {self.value:g}"


@dataclass
class Zinc(Value):
    """Zinc in milligrams."""

    value: float
    prefix: ClassVar[str | None] = "zn:"

    def to_command(self) -> str:
        return f"zn: {self.value:g}"


@dataclass
class Potassium(Value):
    """Potassium in milligrams."""

    value: float
    prefix: ClassVar[str | None] = "k:"

    def to_command(self) -> str:
        return f"k: {self.value:g}"


@dataclass
class Sodium(Value):
    """Sodium in milligrams."""

    value: float
    prefix: ClassVar[str | None] = "na:"

    def to_command(self) -> str:
        return f"na: {self.value:g}"


@dataclass
class VitaminC(Value):
    """Vitamin C in milligrams."""

    value: float
    prefix: ClassVar[str | None] = "vitc:"

    def to_command(self) -> str:
        return f"vitc: {self.value:g}"


@dataclass
class VitaminB12(Value):
    """Vitamin B12 in micrograms."""

    value: float
    prefix: ClassVar[str | None] = "vitb12:"

    def to_command(self) -> str:
        return f"vitb12: {self.value:g}"


KILO: int = 1000


@dataclass
class Liquid(Value):
    """Liquid volume in milliliters."""

    value: float
    """Volume value in milliliters."""

    prefix: ClassVar[str | None] = "lq:"

    def to_command(self) -> str:
        return f"lq: {self.value:g}"


@dataclass
class Season(Value):
    """Season number."""

    number: int
    """Season number."""

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"[Ss](\d+)")]
    extractors: ClassVar[list[Callable]] = [lambda groups: int(groups(1))]


@dataclass
class Episode(Value):
    """Episode number."""

    episode_id: int | str
    """Episode identifier.

    Sometimes it's not a number, but a string."""

    patterns: ClassVar[list[re.Pattern]] = [re.compile(r"[Ee](\d+)")]
    extractors: ClassVar[list[Callable]] = [lambda groups: groups(1)]


@dataclass
class Volume(Value):
    """Partial volume of some object, e.g. book."""

    value: float | None = None
    """Current volume value, e.g. how many pages have been read."""

    from_: float | None = None
    """Start volume value, e.g. starting page of the reading session."""

    to_: float | None = None
    """End volume value, e.g. ending page of the reading session."""

    of: float | None = None
    """The volume of the whole object.

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

    def __post_init__(self) -> None:
        if self.measure == "percent":
            self.of = 100.0

    def verify(self) -> None:
        """Raise an error if the volume value is incorrect."""

        message: str
        if self.from_ and self.to_ and self.from_ > self.to_:
            message = (
                "Start value should be less than end value, not "
                f"`{self.from_}` > `{self.to_}`."
            )
            raise ChronicleValueError(message, self)
        if self.measure == "percent" and self.of != MAX_PERCENT:
            message = f"Maximum should be 100%, not `{self.of}`."
            raise ChronicleValueError(message, self)
        if (
            self.measure == "percent"
            and self.from_
            and (self.from_ < 0.0 or self.from_ > MAX_PERCENT)
        ):
            message = f"From should be in range 0–100%, not `{self.from_}`."
            raise ChronicleValueError(message, self)
        if (
            self.measure == "percent"
            and self.to_
            and (self.to_ < 0.0 or self.to_ > MAX_PERCENT)
        ):
            message = f"To should be in range 0–100%, not `{self.to_}`."
            raise ChronicleValueError(message, self)

    def get_ratio(self) -> float | None:
        """Get ratio of the volume relative to the whole object.

        E.g. for reading session of 20 pages of a 400-page book, the ratio is
        20/400 = 0.05.
        """

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
            message: str = "`of` should be set for custom measure."
            raise ChronicleValueError(message, self)

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
class AudiobookVolume(Value):
    """Partial volume of some object, e.g. book."""

    from_: float | None = None
    """Interval start."""

    to_: float | None = None
    """Interval end."""

    measure: Literal["percent", "seconds"] | None = None
    """Measure of the volume: percents or seconds."""

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
        """Get ratio of the volume relative to the whole object.

        E.g. for reading session of 30 minutes of a 2 hour audiobook, the ratio
        is 30/120 = 0.25.
        """

        if self.to_ is not None and self.from_ is not None:
            return (self.to_ - self.from_) / 100.0

        message: str = "`from_` and `to_` should be set."
        raise ChronicleValueError(message, self)

    def to_command(self) -> str:
        match self.measure:
            case "percent":
                return f"{self.from_}/{self.to_}%"
            case "seconds":
                return f"{self.from_}/{self.to_}s"
        message: str = f"Unknown measure `{self.measure}`."
        raise ChronicleValueError(message, self)

    def to_string(self) -> str:
        match self.measure:
            case "percent":
                return f"{self.from_}–{self.to_}%"
            case "seconds":
                return f"{self.from_}–{self.to_}s"
        message: str = f"Unknown measure `{self.measure}`."
        raise ChronicleValueError(message, self)


@dataclass
class Integers(Value):
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
class Mass(Value):
    """Body mass in kilograms."""

    value: float
    """Mass in kilograms."""

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"(?P<v>\d+(\.\d+)?)kg"),
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: Mass(float(groups("v"))),
    ]


@dataclass
class Weights(Value):
    """List of weights in kilograms."""

    values: list[float]
    """Weights in kilograms."""

    LBS_TO_KG: ClassVar[float] = 0.453592

    patterns: ClassVar[list[re.Pattern]] = [
        re.compile(r"((\d+(\.\d+)?)kg)(,(\d+(\.\d+)?)kg)*"),
        re.compile(r"(\d+)x(\d+(\.\d+)?)kg"),
        re.compile(r"((\d+(\.\d+)?)lbs)(,(\d+(\.\d+)?)lbs)*"),
        re.compile(r"(\d+)x(\d+(\.\d+)?)lbs"),
        re.compile(r"((\d+(\.\d+)?)lb)(,(\d+(\.\d+)?)lb)*"),
        re.compile(r"(\d+)x(\d+(\.\d+)?)lb"),
    ]
    extractors: ClassVar[list[Callable]] = [
        lambda groups: [
            float(group.removesuffix("kg")) for group in groups(0).split(",")
        ],
        lambda groups: (
            int(groups(0).split("x")[0])
            * [float(groups(0).split("x")[1].removesuffix("kg"))]
        ),
        lambda groups: [
            float(group.removesuffix("lbs")) * Weights.LBS_TO_KG
            for group in groups(0).split(",")
        ],
        lambda groups: (
            int(groups(0).split("x")[0])
            * [
                float(groups(0).split("x")[1].removesuffix("lbs"))
                * Weights.LBS_TO_KG
            ]
        ),
        lambda groups: [
            float(group.removesuffix("lb")) * Weights.LBS_TO_KG
            for group in groups(0).split(",")
        ],
        lambda groups: (
            int(groups(0).split("x")[0])
            * [
                float(groups(0).split("x")[1].removesuffix("lb"))
                * Weights.LBS_TO_KG
            ]
        ),
    ]
