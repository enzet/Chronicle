"""Static SVG dashboard generation."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal, cast

from chronicle.settings import Settings
from chronicle.summary.core import Summary
from chronicle.timeline import Timeline
from chronicle.value import Language
from chronicle.view.food import FoodViewer
from chronicle.view.sport import SportViewer

DASHBOARD_CSS_PATH: Path = Path(__file__).parent / "dashboard.css"

local_timezone = datetime.now().astimezone().tzinfo
_TABLE_DAYS: int = int(
    (
        datetime.now(tz=local_timezone)
        - datetime(2026, 3, 12, tzinfo=local_timezone)
    ).days
)


@dataclass
class Thresholds:
    """Five-level threshold values for a metric.

    hard_min: dangerous min (red below)
    soft_min: health min (orange below, green above)
    goal: health ideal (reference line)
    soft_max: health max (green below, orange above)
    hard_max: dangerous max (red above)
    """

    hard_min: float | None = None
    soft_min: float | None = None
    goal: float | None = None
    soft_max: float | None = None
    hard_max: float | None = None


@dataclass
class WindowCondition:
    """A condition satisfied when a window of days contains enough events."""

    count: int
    days: int


@dataclass
class DiscreteThresholds:
    """Window-based thresholds for discrete (count) metrics."""

    hard_min: WindowCondition | None = None
    soft_min: WindowCondition | None = None
    goal: WindowCondition | None = None


@dataclass
class MetricData:
    """Processed time-series data for a single dashboard metric."""

    key: str
    label: str
    unit: str
    alpha: float
    values: list[float]
    today: float
    thresholds: Thresholds
    thresholds_series: list[Thresholds] | None = None
    discrete_thresholds: DiscreteThresholds | None = None


@dataclass
class DashboardData:
    """Aggregated data returned by get_dashboard_data."""

    timestamp: str
    metrics: list[MetricData]


local_timezone = datetime.now().astimezone().tzinfo

_RUSSIAN = Language.from_json("ru")
_ENGLISH = Language.from_json("en")
_KNOWN_LANGUAGES = {_RUSSIAN, _ENGLISH}


def _post_extractor(service_id: str) -> Callable[[Summary], float]:
    return lambda s: float(s.posts.get(service_id, 0))


def _post_day_extractor(service_id: str) -> Callable[[Summary], float]:
    return lambda s: 1.0 if s.posts.get(service_id, 0) >= 1 else 0.0


def _clean_day_extractor(object_id: str) -> Callable[[Summary], float]:
    return lambda s: 1.0 if object_id in s.cleaned else 0.0


def _cut_day_extractor(object_id: str) -> Callable[[Summary], float]:
    return lambda s: 1.0 if object_id in s.cut else 0.0


def _shave_day_extractor(object_id: str) -> Callable[[Summary], float]:
    return lambda s: 1.0 if object_id in s.shaved else 0.0


def _muscle_day_extractor(group: str) -> Callable[[Summary], float]:
    return lambda s: 2.0 if s.muscle_groups.get(group, 0) >= 1 else 0.0


_EXTRACTORS: dict[str, Callable[[Summary], float]] = {
    "sport_sessions": lambda s: float(s.sport_sessions),
    "body_weight_kg": lambda s: s.body_weight_kg or 0.0,
    "energy_expenditure": lambda s: s.energy_expenditure,
    "move_energy": lambda s: s.move_energy,
    "cardio_distance_km": lambda s: s.cardio_distance / 1000.0,
    "move_distance_km": lambda s: s.move_distance / 1000.0,
    "strength_tonnage": lambda s: s.strength_tonnage,
    "read_pages_total": lambda s: sum(s.read_pages.values()),
    "learning_languages": lambda s: (
        (
            sum(sum(v.values()) for v in s.learn_language.values())
            + sum(v for k, v in s.read.items() if k not in _KNOWN_LANGUAGES)
            + sum(v for k, v in s.speak.items() if k not in _KNOWN_LANGUAGES)
            + sum(
                sum(value.values())
                for language, value in s.watch.items()
                if language not in _KNOWN_LANGUAGES
            )
            + sum(
                sum(value.values())
                for language, value in s.listen.items()
                if language not in _KNOWN_LANGUAGES
            )
            + sum(
                sum(value.values())
                for language, value in s.write.items()
                if language not in _KNOWN_LANGUAGES
            )
        )
        / 60.0
    ),
    "energy": lambda s: s.energy,
    "carbohydrates": lambda s: s.carbohydrates,
    "protein": lambda s: s.protein,
    "fat": lambda s: s.fat,
    "saturated_fat": lambda s: s.saturated_fat,
    "dairy_saturated_fat": lambda s: s.dairy_saturated_fat,
    "fiber": lambda s: s.fiber,
    "added_sugar": lambda s: s.added_sugar,
    "omega3": lambda s: s.omega3,
    "calcium": lambda s: s.calcium,
    "iron": lambda s: s.iron,
    "magnesium": lambda s: s.magnesium,
    "zinc": lambda s: s.zinc,
    "potassium": lambda s: s.potassium,
    "sodium": lambda s: s.sodium,
    "vitamin_c": lambda s: s.vitamin_c,
    "vitamin_d": lambda s: s.vitamin_d,
    "vitamin_b12": lambda s: s.vitamin_b12,
    "liquid": lambda s: s.liquid,
    "muscle_chest/upper": lambda s: float(
        s.muscle_groups.get("chest/upper", 0)
    ),
    "muscle_chest/mid": lambda s: float(s.muscle_groups.get("chest/mid", 0)),
    "muscle_back/vertical": lambda s: float(
        s.muscle_groups.get("back/vertical", 0)
    ),
    "muscle_back/horizontal": lambda s: float(
        s.muscle_groups.get("back/horizontal", 0)
    ),
    "muscle_shoulders/side": lambda s: float(
        s.muscle_groups.get("shoulders/side", 0)
    ),
    "muscle_shoulders/rear": lambda s: float(
        s.muscle_groups.get("shoulders/rear", 0)
    ),
    "muscle_arms/biceps": lambda s: float(
        s.muscle_groups.get("arms/biceps", 0)
    ),
    "muscle_arms/triceps": lambda s: float(
        s.muscle_groups.get("arms/triceps", 0)
    ),
    "muscle_core/abs": lambda s: float(s.muscle_groups.get("core/abs", 0)),
    "muscle_core/extension": lambda s: float(
        s.muscle_groups.get("core/extension", 0)
    ),
    "muscle_core/obliques": lambda s: float(
        s.muscle_groups.get("core/obliques", 0)
    ),
    "muscle_core/stabilizers": lambda s: float(
        s.muscle_groups.get("core/stabilizers", 0)
    ),
    "muscle_legs/quads": lambda s: float(s.muscle_groups.get("legs/quads", 0)),
    "muscle_legs/glutes": lambda s: float(
        s.muscle_groups.get("legs/glutes", 0)
    ),
    "muscle_legs/hamstrings": lambda s: float(
        s.muscle_groups.get("legs/hamstrings", 0)
    ),
    "muscle_calves": lambda s: float(s.muscle_groups.get("calves", 0)),
    "commits": lambda s: float(sum(s.commits.values())),
}

# Layout constants
_COLUMNS = 8
_CARD_WIDTH = 100
_CARD_HEIGHT = 140
_GAP = 8
_PADDING = 16
_HEADER_HEIGHT = 32
_SPARKLINE_WIDTH = _CARD_WIDTH - 16
_SPARKLINE_HEIGHT = 88

# Colours
_BACKGROUND = "#F5F5F5"
_SURFACE = "#FFFFFF"
_BORDER = "#E4E4E4"
_TEXT = "#1A1A1A"
_MUTED = "#999999"
_GREEN = "#00C000"  # "#2A9D5C"
_ORANGE = "#FF8800"  # "#F08B00"
_RED = "#FF0000"  # "#D63030"
_NEUTRAL = "#AAAAAA"

# ANSI terminal colours
_ANSI_GREEN = "\033[32m"
_ANSI_ORANGE = "\033[33m"
_ANSI_RED = "\033[31m"
_ANSI_NEUTRAL = "\033[37m"
_ANSI_RESET = "\033[0m"
_ANSI_BY_SVG: dict[str, str] = {
    _GREEN: _ANSI_GREEN,
    _ORANGE: _ANSI_ORANGE,
    _RED: _ANSI_RED,
    _NEUTRAL: _ANSI_NEUTRAL,
}
_CLI_COLS = 3


def _make_ema(values: list[float], alpha: float) -> list[float]:
    result: list[float] = []
    current: float | None = None
    for v in values:
        sample = v if v > 0 else 0.0
        current = (
            sample
            if current is None
            else alpha * current + (1 - alpha) * sample
        )
        result.append(current if current is not None else 0.0)
    return result


def _discrete_color(values: list[float], dt: DiscreteThresholds) -> str:
    """Color based on whether recent window conditions are satisfied."""

    def _met(cond: WindowCondition | None) -> bool:
        if cond is None:
            return True
        window = values[-cond.days :]
        return any(v >= cond.count for v in window)

    if not _met(dt.hard_min):
        return _RED
    if not _met(dt.soft_min) or not _met(dt.goal):
        return _ORANGE
    return _GREEN


def _metric_color(last_ema: float, thresholds: Thresholds) -> str:
    l1, l2, l4, l5 = (
        thresholds.hard_min,
        thresholds.soft_min,
        thresholds.soft_max,
        thresholds.hard_max,
    )
    if l1 is None and l2 is None and l4 is None and l5 is None:
        return _NEUTRAL
    if (l1 is not None and last_ema < l1) or (l5 is not None and last_ema > l5):
        return _RED
    if (l2 is not None and last_ema < l2) or (l4 is not None and last_ema > l4):
        return _ORANGE
    return _GREEN


def _sparkline_svg(
    values: list[float],
    today: float,
    thresholds: Thresholds,
    alpha: float,
    origin_x: int,
    origin_y: int,
    thresholds_series: list[Thresholds] | None = None,
    discrete_thresholds: DiscreteThresholds | None = None,
) -> str:
    """Return SVG elements for a sparkline card body at (origin_x, origin_y)."""
    all_values = [*values, today]
    smoothed = _make_ema(all_values, alpha)

    show = 40
    visible_values = all_values[-(show + 1) :]
    visible_smoothed = smoothed[-(show + 1) :]

    positives = [v for v in visible_values if v > 0]
    if not positives:
        return ""

    max_val = max(positives) * 1.12
    if max_val == 0:
        return ""

    # When a per-day series is provided, ensure max_val is tall enough to
    # accommodate the highest threshold so reference lines stay visible.
    if thresholds_series:
        visible_thresholds = thresholds_series[-(show + 1) :]
        max_threshold = max(
            (ts.goal or ts.soft_min or 0.0) for ts in visible_thresholds
        )
        max_val = max(max_val, max_threshold * 1.12)

    if thresholds:
        max_val = max(
            max_val, (thresholds.goal or thresholds.soft_min or 0.0) * 1.12
        )

    if discrete_thresholds is not None:
        color = _discrete_color(all_values, discrete_thresholds)
    else:
        color = _metric_color(smoothed[-1], thresholds)
    bar_count = len(visible_values)
    wide = 6
    gap = 0.6
    # Last two bars are `wide`× wider; solve for unit bar_width so all fits.
    total_units = bar_count - 2 + 2 * wide
    bar_width = max(
        1.0, (_SPARKLINE_WIDTH - (bar_count - 1) * gap) / total_units
    )

    # Pre-compute left edge and centre x for each bar.
    _bar_left: list[float] = []
    _bar_center: list[float] = []
    _pos = float(origin_x)
    for _i in range(bar_count):
        _w = bar_width * wide if _i >= bar_count - 2 else bar_width
        _bar_left.append(_pos)
        _bar_center.append(_pos + _w / 2)
        _pos += _w + gap

    def bar_center_x(i: int) -> float:
        return _bar_center[i]

    def value_y(v: float) -> float:
        return origin_y + _SPARKLINE_HEIGHT - (v / max_val) * _SPARKLINE_HEIGHT

    parts: list[str] = []

    if discrete_thresholds is None:
        if thresholds_series:
            visible_thresholds: list[Thresholds] = thresholds_series[
                -(show + 1) :
            ]
            for function, width in (
                (lambda x: x.hard_min, 0.5),
                (lambda x: x.soft_min, 0.5),
                (lambda x: x.goal, 1),
                (lambda x: x.soft_max, 0.5),
                (lambda x: x.hard_max, 0.5),
            ):
                goals: list[float] = [
                    function(threshold) or 0.0
                    for threshold in visible_thresholds
                ]
                goals = _make_ema(goals, alpha)
                goal_points: list[str] = [
                    f"{bar_center_x(i):.1f},{value_y(ts):.1f}"
                    for i, ts in enumerate(goals)
                ]
                if goal_points:
                    parts.append(
                        f'<polyline points="{" ".join(goal_points)}"'
                        f' fill="none" stroke="{_TEXT}" stroke-width="{width}"'
                        f' stroke-linejoin="round"/>'
                    )
        elif thresholds.goal is not None:
            for threshold, width in (
                (thresholds.hard_min, 0.5),
                (thresholds.soft_min, 0.5),
                (thresholds.goal, 1),
                (thresholds.soft_max, 0.5),
                (thresholds.hard_max, 0.5),
            ):
                if threshold:
                    line_y = value_y(threshold)
                    parts.append(
                        f'<line x1="{origin_x}" y1="{line_y:.1f}"'
                        f' x2="{origin_x + _SPARKLINE_WIDTH}"'
                        f' y2="{line_y:.1f}"'
                        f' stroke="{_TEXT}" stroke-width="{width}"/>'
                    )

    # Bars.
    for i, v in enumerate(visible_values):
        if not v:
            continue
        bar_x = _bar_left[i]
        bar_height = (v / max_val) * _SPARKLINE_HEIGHT
        bar_y = origin_y + _SPARKLINE_HEIGHT - bar_height
        is_highlighted = i >= bar_count - 2
        opacity = "0.55" if is_highlighted else "0.18"
        w = bar_width * wide if is_highlighted else bar_width
        parts.append(
            f'<rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{w:.1f}"'
            f' height="{bar_height:.1f}" fill="{color}" opacity="{opacity}"/>'
        )

    if discrete_thresholds is None:
        # EMA polyline.
        points = " ".join(
            f"{bar_center_x(i):.1f},{value_y(v):.1f}"
            for i, v in enumerate(visible_smoothed)
        )
        parts.append(
            f'<polyline points="{points}" fill="none" stroke="{color}"'
            f' stroke-width="1.5" stroke-linejoin="round"'
            f' stroke-linecap="round"/>'
        )

    return "\n".join(parts)


def _mifflin_bmr(
    weight_kg: float, height_cm: float, age: int, sex: Literal["male", "female"]
) -> float:
    """Mifflin-St Jeor basal metabolic rate in kcal/day."""
    base = 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age
    return base + 5.0 if sex == "male" else base - 161.0


def get_dashboard_data(timeline: Timeline, settings: Settings) -> DashboardData:
    """Extract dashboard data from the timeline."""

    now: datetime = datetime.now().astimezone()
    today_start: datetime = datetime(
        now.year, now.month, now.day, tzinfo=local_timezone
    )

    history_start: datetime = now - timedelta(days=700)
    history_filter = Timeline.get_filter(history_start, None)
    days = list(timeline.get_events_by_day(history_filter))

    sections_config: list[dict] = settings.get("dashboard", {}).get(
        "sections", []
    )
    all_metric_ids: set[str] = {
        m["id"] for sec in sections_config for m in sec.get("metrics", [])
    }
    # Always extract these to support dynamic energy thresholds.
    ids_to_extract: set[str] = all_metric_ids | {
        "energy_expenditure",
        "move_energy",
        "body_weight_kg",
    }

    raw_values: dict[str, list[float]] = {
        metric_id: [] for metric_id in ids_to_extract
    }
    today_index: int | None = None

    def _get_extractor(metric_id: str) -> Callable[[Summary], float] | None:
        if metric_id in _EXTRACTORS:
            return _EXTRACTORS[metric_id]
        if metric_id.startswith("post_count_"):
            return _post_extractor(metric_id[len("post_count_") :])
        if metric_id.startswith("post_day_"):
            return _post_day_extractor(metric_id[len("post_day_") :])
        if metric_id.startswith("clean_") and metric_id.endswith("_day"):
            return _clean_day_extractor(metric_id[len("clean_") : -len("_day")])
        if metric_id.startswith("cut_") and metric_id.endswith("_day"):
            return _cut_day_extractor(metric_id[len("cut_") : -len("_day")])
        if metric_id.startswith("shave_") and metric_id.endswith("_day"):
            return _shave_day_extractor(metric_id[len("shave_") : -len("_day")])
        if metric_id.startswith("muscle_") and metric_id.endswith("_day"):
            return _muscle_day_extractor(
                metric_id[len("muscle_") : -len("_day")]
            )
        return None

    for i, (day, _, summary) in enumerate(days):
        for metric_id in ids_to_extract:
            extractor = _get_extractor(metric_id)
            raw_values[metric_id].append(
                extractor(summary) if extractor else 0.0
            )
        if day >= today_start:
            today_index = i
            break

    all_metrics: list[MetricData] = []

    for section_config in sections_config:
        for metric_config in section_config.get("metrics", []):
            metric_id = metric_config["id"]
            all_vals = raw_values.get(metric_id, [])
            if today_index is not None:
                values = all_vals[:today_index]
                today_value = (
                    all_vals[today_index]
                    if today_index < len(all_vals)
                    else 0.0
                )
            else:
                values = all_vals
                today_value = 0.0

            def _lv(cfg: dict, key: str) -> float | None:
                v = cfg.get(key)
                if v is None or isinstance(v, dict):
                    return None
                return float(v)

            def _wc(cfg: dict, key: str) -> WindowCondition | None:
                v = cfg.get(key)
                if isinstance(v, dict):
                    return WindowCondition(
                        count=int(v["count"]), days=int(v["days"])
                    )
                return None

            is_discrete = metric_config.get("type") == "discrete"
            discrete_thresholds: DiscreteThresholds | None = None
            if is_discrete:
                discrete_thresholds = DiscreteThresholds(
                    hard_min=_wc(metric_config, "hard_min"),
                    soft_min=_wc(metric_config, "soft_min"),
                    goal=_wc(metric_config, "goal"),
                )

            thresholds = Thresholds(
                hard_min=_lv(metric_config, "hard_min"),
                soft_min=_lv(metric_config, "soft_min"),
                goal=_lv(metric_config, "goal"),
                soft_max=_lv(metric_config, "soft_max"),
                hard_max=_lv(metric_config, "hard_max"),
            )
            # For the energy metric, build per-day thresholds using the
            # Mifflin-St Jeor BMR adjusted by daily energy expenditure.
            series: list[Thresholds] | None = None
            if metric_id == "energy" and today_index is not None:
                height_cm = float(settings.get("height", 170))
                age = int(settings.get("age", 30))
                sex_raw = str(settings.get("sex", "male"))
                if sex_raw not in ("male", "female"):
                    raise ValueError
                sex: Literal["male", "female"] = cast(
                    "Literal['male', 'female']", sex_raw
                )
                weights = raw_values.get("body_weight_kg", [])
                expenditures = [
                    e + m
                    for e, m in zip(
                        raw_values["energy_expenditure"],
                        raw_values["move_energy"],
                        strict=False,
                    )
                ]
                fallback_l2 = float(metric_config.get("soft_min", 0.0))
                series = []
                for j, expenditure in enumerate(expenditures):
                    w = weights[j] if j < len(weights) else 0.0
                    bmr = (
                        _mifflin_bmr(w, height_cm, age, sex)
                        if w > 0
                        else fallback_l2
                    )
                    series.append(
                        Thresholds(
                            hard_min=bmr + expenditure,
                            soft_min=bmr + expenditure + 200.0,
                            goal=bmr + expenditure + 500.0,
                        )
                    )
                today_weight = (
                    weights[today_index] if today_index < len(weights) else 0.0
                )
                today_bmr = (
                    _mifflin_bmr(today_weight, height_cm, age, sex)
                    if today_weight > 0
                    else fallback_l2
                )
                today_expenditure = (
                    expenditures[today_index]
                    if today_index < len(expenditures)
                    else 0.0
                )
                thresholds.soft_min = today_bmr + today_expenditure
                if thresholds.goal is not None:
                    thresholds.goal = thresholds.soft_min + 200.0
            all_metrics.append(
                MetricData(
                    key=metric_id,
                    label=metric_config.get("label", metric_id),
                    unit=metric_config.get("unit", ""),
                    alpha=float(metric_config.get("alpha", 0.9)),
                    values=values,
                    today=round(today_value, 2),
                    thresholds=thresholds,
                    thresholds_series=series,
                    discrete_thresholds=discrete_thresholds,
                )
            )

    return DashboardData(timestamp=now.isoformat(), metrics=all_metrics)


def _render_cards(
    metrics: list[MetricData],
    content_y: int,
    parts: list[str],
    id_prefix: str,
) -> int:
    """Render a grid of sparkline cards; return updated content_y."""
    for index, metric in enumerate(metrics):
        column = index % _COLUMNS
        row = index // _COLUMNS
        card_x = _PADDING + column * (_CARD_WIDTH + _GAP)
        card_y = content_y + row * (_CARD_HEIGHT + _GAP)

        parts.append(
            f'<rect x="{card_x}" y="{card_y}"'
            f' width="{_CARD_WIDTH}" height="{_CARD_HEIGHT}"'
            f' rx="6" fill="{_SURFACE}" stroke="{_BORDER}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{card_x + 8}" y="{card_y + 16 + 6}"'
            f' font-size="16" fill="black" font-weight="normal">'
            f"{metric.label}</text>"
        )

        all_values = [*metric.values, metric.today]

        if metric.discrete_thresholds is not None:
            color = _discrete_color(all_values, metric.discrete_thresholds)
            today_int = int(metric.today)
            value_str = (
                f"{today_int}\u202f{metric.unit}" if today_int > 0 else "\u2014"
            )
        else:
            smoothed = _make_ema(all_values, metric.alpha)
            color = _metric_color(smoothed[-1], metric.thresholds)
            last_value = smoothed[-1]
            if last_value > 0:
                num = (
                    str(int(last_value))
                    if last_value == int(last_value)
                    else f"{last_value:.2f}"
                )
                value_str = f"{num}\u202f{metric.unit}"
            else:
                value_str = "\u2014"

        parts.append(
            f'<text x="{card_x + _CARD_WIDTH - 8}" y="{card_y + 16}"'
            f' font-size="9" fill="{color}" font-weight="600"'
            f' text-anchor="end">{value_str}</text>'
        )

        clip_id = f"{id_prefix}{index}"
        sparkline_x = card_x + 8
        sparkline_y = card_y + _HEADER_HEIGHT
        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="{sparkline_x}" y="{sparkline_y}"'
            f' width="{_SPARKLINE_WIDTH}" height="{_SPARKLINE_HEIGHT}"/>'
            f"</clipPath>"
        )
        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(
            _sparkline_svg(
                metric.values,
                metric.today,
                metric.thresholds,
                metric.alpha,
                sparkline_x,
                sparkline_y,
                metric.thresholds_series,
                metric.discrete_thresholds,
            )
        )
        parts.append("</g>")

    row_count = (len(metrics) + _COLUMNS - 1) // _COLUMNS
    return content_y + row_count * _CARD_HEIGHT + max(0, row_count - 1) * _GAP


def generate_dashboard_svg(timeline: Timeline, settings: Settings) -> str:
    """Generate a static SVG dashboard from timeline data."""

    data = get_dashboard_data(timeline, settings)
    metrics: list[MetricData] = data.metrics

    row_count = (len(metrics) + _COLUMNS - 1) // _COLUMNS
    total_width = _COLUMNS * _CARD_WIDTH + (_COLUMNS - 1) * _GAP + 2 * _PADDING
    header_height = 28
    cards_height = row_count * _CARD_HEIGHT + max(0, row_count - 1) * _GAP
    total_height = header_height + _PADDING + cards_height + _PADDING

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{total_width}" height="{total_height}"'
        f' viewBox="0 0 {total_width} {total_height}">'
    )
    parts.append('<style>text {font-family: "SF Pro", "Inter";}</style>')
    parts.append(
        f'<rect width="{total_width}" height="{total_height}"'
        f' fill="{_BACKGROUND}"/>'
    )

    _render_cards(metrics, header_height + _PADDING, parts, "c")

    parts.append("</svg>")
    return "\n".join(parts)


def _compute_r(value: float, thresholds: Thresholds) -> float | None:
    """Compute a normalized health score from 0 to 3.

    :return: `None` when the required thresholds are absent.
    """
    hard_min = thresholds.hard_min
    soft_min = thresholds.soft_min
    goal = thresholds.goal
    soft_max = thresholds.soft_max
    hard_max = thresholds.hard_max

    if hard_min is not None and value < hard_min:
        return value / hard_min if hard_min != 0 else 0.0
    if hard_min is not None and soft_min is not None and value < soft_min:
        denom = soft_min - hard_min
        return 1 + (value - hard_min) / denom if denom else 1
    if soft_min is not None and goal is not None and value < goal:
        denom = goal - soft_min
        return 2 + (value - soft_min) / denom if denom else 2
    if goal is not None and soft_max is not None and value < soft_max:
        denom = soft_max - goal
        return 2 + (soft_max - value) / denom if denom else 2
    if hard_max is not None and soft_max is not None and value < hard_max:
        denom = hard_max - soft_max
        return 1 + (hard_max - value) / denom if denom else 1
    return 3


_R_COLOR_STOPS: list[tuple[int, int, int]] = [
    (255, 0, 0),
    (255, 128, 0),
    (255, 255, 0),
    (0, 0xC0, 0),
]


def _r_to_hex_color(r: float) -> str:
    r = max(0.0, min(3.0, r))
    lo = int(r)
    hi = min(lo + 1, len(_R_COLOR_STOPS) - 1)
    frac = r - lo
    r1, g1, b1 = _R_COLOR_STOPS[lo]
    r2, g2, b2 = _R_COLOR_STOPS[hi]
    red = int(r1 + frac * (r2 - r1))
    grn = int(g1 + frac * (g2 - g1))
    blu = int(b1 + frac * (b2 - b1))
    return f"#{red:02x}{grn:02x}{blu:02x}"


def _cell_style(r: float | None) -> str:
    if r is None:
        return "background:#00000011"
    return f"background:{_r_to_hex_color(r)}88"


def _table_row(metric: MetricData) -> tuple[str, float | None]:
    last_r: float | None = None

    all_vals = [*metric.values, metric.today]

    cells: list[str] = []
    if metric.discrete_thresholds is not None:
        dt = metric.discrete_thresholds
        n = len(all_vals)
        for i in range(_TABLE_DAYS):
            idx = n - _TABLE_DAYS + i
            if idx < 0:
                cells.append(f'<td class="cell" style="color:{_BORDER}"></td>')
                continue
            v = all_vals[idx]
            if v > 0:
                cells.append(
                    f'<td style="background:{_GREEN}88" class="cell"></td>'
                )
                last_r = 3
            else:
                day_color = _discrete_color(all_vals[: idx + 1], dt)
                cells.append(
                    f'<td style="background:{day_color}88" class="cell"></td>'
                )
                if day_color == _GREEN:
                    last_r = 3
                if day_color == _ORANGE:
                    last_r = 1.5
                if day_color == _RED:
                    last_r = 0
    else:
        smoothed = _make_ema(all_vals, metric.alpha)
        last_14 = smoothed[-_TABLE_DAYS:]
        last_14 = [0.0] * (_TABLE_DAYS - len(last_14)) + last_14

        if metric.thresholds_series:
            ts_list = metric.thresholds_series[-_TABLE_DAYS:]
            ts_list = [Thresholds()] * (_TABLE_DAYS - len(ts_list)) + ts_list
        else:
            ts_list = [metric.thresholds] * _TABLE_DAYS

        for v, ts in zip(last_14, ts_list, strict=True):
            if v == 0.0:
                cells.append(f'<td class="cell" style="color:{_BORDER}"></td>')
            else:
                r: float | None = _compute_r(v, ts)
                last_r = r
                style = _cell_style(r)
                attr = f' style="{style}"' if style else ""
                cells.append(f'<td{attr} class="cell"></td>')

    return (
        f'<tr><td class="label">{metric.label}</td>' + "".join(cells) + "</tr>"
    ), last_r


def print_dashboard_cli(timeline: Timeline, settings: Settings) -> None:
    """Print dashboard metrics in 3 columns of 26 chars (80 total)."""
    data = get_dashboard_data(timeline, settings)
    column_width = 24
    content_w = column_width - 3

    def _fmt_value(metric: MetricData, smoothed_last: float) -> str:
        if metric.discrete_thresholds is not None:
            v = metric.today
            return f"{int(v)} {metric.unit}".strip() if v else ""
        if smoothed_last <= 0:
            return ""
        v = smoothed_last
        num = str(int(v)) if v % 1 == 0 else f"{v:.1f}"
        return f"{num} {metric.unit}".strip()

    def _cell(metric: MetricData, yc: str, tc: str, val: str) -> str:
        def get_marker(color: str) -> str:
            if color == _RED:
                return "█"
            if color == _ORANGE:
                return "▒"
            return " "

        blocks = get_marker(yc) + get_marker(tc)
        label = metric.label
        if val:
            spare = content_w - len(val) - 1
            if len(label) > spare:
                label = label[:spare]
            content = (
                label
                + " "
                + "." * (content_w - len(label) - len(val) - 2)
                + " "
                + val
            )
        else:
            content = label[:content_w].ljust(content_w)
        return f"{blocks} {content}"

    cells: list[str] = []
    for metric in data.metrics:
        all_values = [*metric.values, metric.today]

        if metric.discrete_thresholds is not None:
            dt = metric.discrete_thresholds
            has_history = bool(metric.values)
            yc = _discrete_color(metric.values, dt) if has_history else _NEUTRAL
            tc = _discrete_color(all_values, dt)
            smoothed_last = 0.0
        else:
            smoothed = _make_ema(all_values, metric.alpha)
            ts = metric.thresholds_series
            if ts:
                today_idx = len(metric.values)
                yt = ts[today_idx - 1] if today_idx > 0 else metric.thresholds
                tt = ts[today_idx] if today_idx < len(ts) else metric.thresholds
            else:
                yt = tt = metric.thresholds
            prev = smoothed[-2] if len(smoothed) > 1 else 0.0
            yc = _metric_color(prev, yt)
            tc = _metric_color(smoothed[-1], tt)
            smoothed_last = smoothed[-1]

        val = _fmt_value(metric, smoothed_last)
        cells.append(_cell(metric, yc, tc, val))

    pad = " " * column_width
    for i in range(0, len(cells), _CLI_COLS):
        row = cells[i : i + _CLI_COLS]
        row += [pad] * (_CLI_COLS - len(row))
        print(" ".join(row))


def generate_dashboard_html(timeline: Timeline, settings: Settings) -> str:
    """Generate a static HTML page with inline SVG and 14-day metrics table."""
    svg = generate_dashboard_svg(timeline, settings)
    data = get_dashboard_data(timeline, settings)

    rows: list[tuple[str, float | None]] = [_table_row(m) for m in data.metrics]
    table_body = "".join(x for x, y in sorted(rows, key=lambda z: z[1] or 0.0))

    return (
        (
            "<!DOCTYPE html>\n<html>\n<head>\n"
            '<meta charset="utf-8">\n<title>Dashboard</title>\n'
            '<link rel="stylesheet" href="dashboard.css">\n</head>\n'
            "<body>\n"
            f"{svg}\n"
            f'<table class="hystogram">\n'
            f"  <tbody>{table_body}</tbody>\n"
            "</table>\n"
        )
        + SportViewer.get_html_exercises()
        + FoodViewer(timeline).get_html_food()
        + "</body>\n</html>"
    )
