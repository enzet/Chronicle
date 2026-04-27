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

local_timezone = datetime.now().astimezone().tzinfo
_settings: Settings = Settings(Path.home() / ".chronicle" / "settings.json")
_TABLE_DAYS: int = int(
    (datetime.now() - datetime(2026, 3, 12, tzinfo=local_timezone)).days
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


def _post_extractor(service_id: str) -> Callable[[Summary], float]:
    return lambda s: float(s.posts.get(service_id, 0))


def _post_day_extractor(service_id: str) -> Callable[[Summary], float]:
    return lambda s: 1.0 if s.posts.get(service_id, 0) >= 1 else 0.0


def _clean_day_extractor(object_id: str) -> Callable[[Summary], float]:
    return lambda s: 1.0 if object_id in s.cleaned else 0.0


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
            + sum(v for k, v in s.read.items() if k != _RUSSIAN)
            + sum(v for k, v in s.speak.items() if k != _RUSSIAN)
            + sum(
                sum(value.values())
                for language, value in s.listen.items()
                if language != _RUSSIAN
            )
            + sum(
                sum(value.values())
                for language, value in s.write.items()
                if language != _RUSSIAN
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
    "muscle_chest": lambda s: float(s.muscle_groups.get("chest", 0)),
    "muscle_back": lambda s: float(s.muscle_groups.get("back", 0)),
    "muscle_shoulders": lambda s: float(s.muscle_groups.get("shoulders", 0)),
    "muscle_arms": lambda s: float(s.muscle_groups.get("arms", 0)),
    "muscle_core": lambda s: float(s.muscle_groups.get("core", 0)),
    "muscle_legs": lambda s: float(s.muscle_groups.get("legs", 0)),
    "muscle_calves": lambda s: float(s.muscle_groups.get("calves", 0)),
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
_BACKGROUND = "#f5f5f5"
_SURFACE = "#ffffff"
_BORDER = "#e4e4e4"
_TEXT = "#1a1a1a"
_MUTED = "#999999"
_GREEN = "#008800"  # "#2a9d5c"
_ORANGE = "#ff8800"  # "#f08b00"
_RED = "#FF0000"  # "#d63030"
_NEUTRAL = "#aaaaaa"


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
        if max_threshold > 0:
            max_val = max(max_val, max_threshold * 1.12)

    if discrete_thresholds is not None:
        color = _discrete_color(all_values, discrete_thresholds)
    else:
        color = _metric_color(smoothed[-1], thresholds)
    bar_count = len(visible_values)
    gap = 0.6
    bar_width = max(1.5, _SPARKLINE_WIDTH / bar_count - gap)

    def bar_center_x(i: int) -> float:
        return origin_x + (i + 0.5) * _SPARKLINE_WIDTH / bar_count

    def value_y(v: float) -> float:
        return origin_y + _SPARKLINE_HEIGHT - (v / max_val) * _SPARKLINE_HEIGHT

    parts: list[str] = []

    if discrete_thresholds is None:
        if thresholds_series:
            visible_thresholds = thresholds_series[-(show + 1) :]
            health_points = [
                f"{bar_center_x(i):.1f},{value_y(ts.goal):.1f}"
                for i, ts in enumerate(visible_thresholds)
                if ts.goal is not None
            ]
            if health_points:
                parts.append(
                    f'<polyline points="{" ".join(health_points)}"'
                    f' fill="none" stroke="{_TEXT}" stroke-width="0.8"'
                    f' stroke-linejoin="round"/>'
                )
        elif thresholds.goal is not None:
            health_line_y = value_y(thresholds.goal)
            parts.append(
                f'<line x1="{origin_x}" y1="{health_line_y:.1f}"'
                f' x2="{origin_x + _SPARKLINE_WIDTH}"'
                f' y2="{health_line_y:.1f}"'
                f' stroke="{_TEXT}" stroke-width="1"/>'
            )

    # bars
    for i, v in enumerate(visible_values):
        if not v:
            continue
        bar_x = origin_x + i * _SPARKLINE_WIDTH / bar_count
        bar_height = (v / max_val) * _SPARKLINE_HEIGHT
        bar_y = origin_y + _SPARKLINE_HEIGHT - bar_height
        opacity = "0.55" if i == bar_count - 1 else "0.18"
        parts.append(
            f'<rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_width:.1f}"'
            f' height="{bar_height:.1f}" fill="{color}" opacity="{opacity}"/>'
        )

    if discrete_thresholds is None:
        # threshold bands — white overlays dim bars in orange/red zones
        def _band(
            x: float, y_top: float, y_bot: float, w: float, opacity: str
        ) -> None:
            h = y_bot - y_top
            if h > 0:
                parts.append(
                    f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{w:.1f}"'
                    f' height="{h:.1f}" fill="#ffffff" opacity="{opacity}"/>'
                )

        chart_top = float(origin_y)
        chart_bot = float(origin_y + _SPARKLINE_HEIGHT)

        if thresholds_series:
            visible_thresholds = thresholds_series[-(show + 1) :]
            column_width = _SPARKLINE_WIDTH / bar_count
            for i, ts in enumerate(visible_thresholds):
                bx = origin_x + i * column_width
                if ts.soft_min and max_val > 0:
                    l2_y = value_y(ts.soft_min)
                    _band(bx, l2_y, chart_bot, column_width, "0.4")
        else:
            hard_min = thresholds.hard_min
            soft_min = thresholds.soft_min
            soft_max = thresholds.soft_max
            hard_max = thresholds.hard_max

            width = float(_SPARKLINE_WIDTH)
            ox = float(origin_x)
            if hard_min and max_val > 0:
                _band(ox, value_y(hard_min), chart_bot, width, "0.5")
            if hard_min and soft_min and max_val > 0:
                _band(ox, value_y(soft_min), value_y(hard_min), width, "0.25")
            if soft_max and hard_max and soft_max < max_val:
                _band(
                    ox,
                    value_y(min(hard_max, max_val)),
                    value_y(soft_max),
                    width,
                    "0.25",
                )
            if hard_max and hard_max < max_val:
                _band(ox, chart_top, value_y(hard_max), width, "0.5")

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


def get_dashboard_data(timeline: Timeline) -> DashboardData:
    """Extract dashboard data from the timeline."""

    now: datetime = datetime.now().astimezone()
    today_start: datetime = datetime(
        now.year, now.month, now.day, tzinfo=local_timezone
    )

    history_start: datetime = now - timedelta(days=700)
    history_filter = Timeline.get_filter(history_start, None)
    days = list(timeline.get_events_by_day(history_filter))

    sections_config: list[dict] = _settings.get("dashboard", {}).get(
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
                height_cm = float(_settings.get("height", 170))
                age = int(_settings.get("age", 30))
                sex_raw = str(_settings.get("sex", "male"))
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
                            soft_min=bmr + expenditure,
                            goal=bmr + expenditure + 200.0,
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


def generate_dashboard_svg(timeline: Timeline) -> str:
    """Generate a static SVG dashboard from timeline data."""

    data = get_dashboard_data(timeline)
    metrics: list[MetricData] = data.metrics
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")

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
    parts.append(
        f'<text x="{_PADDING}" y="20" font-size="11" fill="{_MUTED}">'
        f"{timestamp_str}</text>"
    )

    _render_cards(metrics, header_height + _PADDING, parts, "c")

    parts.append("</svg>")
    return "\n".join(parts)


def _cell_style(value: float, thresholds: Thresholds) -> str:
    color = _metric_color(value, thresholds)
    if color == _NEUTRAL:
        return ""
    return f"background:{color}88"


def _table_row(metric: MetricData) -> str:
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
            else:
                day_color = _discrete_color(all_vals[: idx + 1], dt)
                cells.append(
                    f'<td style="background:{day_color}88" class="cell"></td>'
                )
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
                style = _cell_style(v, ts)
                attr = f' style="{style}"' if style else ""
                cells.append(f'<td{attr} class="cell"></td>')

    unit_span = (
        f' <span class="unit">{metric.unit}</span>' if metric.unit else ""
    )
    return (
        f'<tr><td class="label">{metric.label}{unit_span}</td>'
        + "".join(cells)
        + "</tr>"
    )


def generate_dashboard_html(timeline: Timeline) -> str:
    """Generate a static HTML page with inline SVG and 14-day metrics table."""
    svg = generate_dashboard_svg(timeline)
    data = get_dashboard_data(timeline)

    now = datetime.now().astimezone()
    col_dates = [
        (now - timedelta(days=_TABLE_DAYS - 1 - i)).date()
        for i in range(_TABLE_DAYS)
    ]
    header_cells = "".join("<th></th>" for d in col_dates)
    rows = "".join(_table_row(m) for m in data.metrics)

    css = (
        f"*{{box-sizing:border-box}}"
        f"body{{font-family:serif;"
        f"background:{_BACKGROUND};margin:0;padding:16px}}"
        f"table{{border-collapse:collapse;font-size:11px;margin-top:16px}}"
        f"th,td{{border: 1px inset;"
        f"padding:3px 1px;text-align:right;white-space:nowrap;}}"
        f"td.cell {{border: none;}}"
        f"th{{font-weight: bold; font-size:11px}}"
        f"td.label{{text-align:left;font-weight:500;min-width:120px;"
        f"padding:3px 7px;}}"
        f".unit{{color:{_MUTED};font-weight:400;font-size:9px}}"
    )
    return (
        "<!DOCTYPE html>\n<html>\n<head>\n"
        '<meta charset="utf-8">\n<title>Dashboard</title>\n'
        f"<style>{css}</style>\n</head>\n<body>\n"
        f"{svg}\n"
        f"<table>\n"
        f"  <thead><tr><th>Metric</th>{header_cells}</tr></thead>\n"
        f"  <tbody>{rows}</tbody>\n"
        "</table>\n</body>\n</html>"
    )
