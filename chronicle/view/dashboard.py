"""Static SVG dashboard generation."""

from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from chronicle.settings import Settings
from chronicle.summary.core import Summary
from chronicle.timeline import Timeline
from chronicle.value import Language

_settings: Settings = Settings(Path.home() / ".chronicle" / "settings.json")
local_timezone = datetime.now().astimezone().tzinfo

_RUSSIAN = Language.from_json("ru")
_EXTRACTORS: dict[str, Callable[[Summary], float]] = {
    "sport_sessions": lambda s: float(s.sport_sessions),
    "energy_expenditure": lambda s: s.energy_expenditure,
    "cardio_distance_km": lambda s: s.cardio_distance / 1000.0,
    "move_distance_km": lambda s: s.move_distance / 1000.0,
    "strength_tonnage": lambda s: s.strength_tonnage,
    "read_pages_total": lambda s: sum(s.read_pages.values()),
    "learning_languages": lambda s: (
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
    / 60.0,
    "energy": lambda s: s.energy,
    "carbohydrates": lambda s: s.carbohydrates,
    "protein": lambda s: s.protein,
    "fat": lambda s: s.fat,
    "saturated_fat": lambda s: s.saturated_fat,
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
    "vitamin_b12": lambda s: s.vitamin_b12,
    "liquid": lambda s: s.liquid,
}

# Layout constants
_COLS = 8
_CARD_W = 100
_CARD_H = 140
_GAP = 8
_PAD = 16
_HEADER_H = 32
_SPARK_W = _CARD_W - 16
_SPARK_H = 88

# Colours
_BG = "#f5f5f5"
_SURFACE = "#ffffff"
_BORDER = "#e4e4e4"
_TEXT = "#1a1a1a"
_MUTED = "#999999"
_GREEN = "#2a9d5c"
_RED = "#d63030"
_NEUTRAL = "#aaaaaa"


def _make_ema(values: list[float], alpha: float) -> list[float]:
    out: list[float] = []
    cur: float | None = None
    for v in values:
        s = v if v > 0 else 0.0
        cur = s if cur is None else alpha * cur + (1 - alpha) * s
        out.append(cur if cur is not None else 0.0)
    return out


def _metric_color(last_ema: float, th: dict[str, float]) -> str:
    lo = th.get("min")
    hi = th.get("max")
    if lo is None and hi is None:
        return _NEUTRAL
    if lo is not None and last_ema < lo:
        return _RED
    if hi is not None and last_ema > hi:
        return _RED
    return _GREEN


def _sparkline_svg(
    values: list[float],
    today: float,
    thresholds: dict[str, float],
    alpha: float,
    x0: int,
    y0: int,
) -> str:
    """Return SVG elements for a sparkline card body at position (x0, y0)."""
    all_vals = [*values, today]
    smoothed = _make_ema(all_vals, alpha)

    show = 14
    vis_all = all_vals[-(show + 1) :]
    vis_smoothed = smoothed[-(show + 1) :]

    positives = [v for v in vis_all if v > 0]
    if not positives:
        return ""

    max_val = max(positives) * 1.12
    if max_val == 0:
        return ""

    color = _metric_color(smoothed[-1], thresholds)
    n = len(vis_all)
    gap = 0.6
    bar_w = max(1.5, _SPARK_W / n - gap)

    def sx(i: int) -> float:
        return x0 + (i + 0.5) * _SPARK_W / n

    def sy(v: float) -> float:
        return y0 + _SPARK_H - (v / max_val) * _SPARK_H

    parts: list[str] = []

    if thresholds.get("health") is not None:
        ry = sy(thresholds["health"])
        parts.append(
            f'<line x1="{x0}" y1="{ry:.1f}"'
            f' x2="{x0 + _SPARK_W}" y2="{ry:.1f}"'
            f' stroke="{_TEXT}" stroke-width="1"/>'
        )

    # bars
    for i, v in enumerate(vis_all):
        if not v:
            continue
        bx = x0 + i * _SPARK_W / n
        bh = (v / max_val) * _SPARK_H
        by = y0 + _SPARK_H - bh
        opacity = "0.55" if i == n - 1 else "0.18"
        parts.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}"'
            f' height="{bh:.1f}" fill="{color}" opacity="{opacity}"/>'
        )

    # threshold bands
    th_max = thresholds.get("max")
    th_min = thresholds.get("min")
    th_health = thresholds.get("health")
    band_color = "#ffffff"

    if th_min and th_min not in (0, th_health):
        band_h = min((th_min / max_val) * _SPARK_H, _SPARK_H)
        band_y = y0 + _SPARK_H - band_h
        parts.append(
            f'<rect x="{x0}" y="{band_y:.1f}" width="{_SPARK_W}"'
            f' height="{band_h:.1f}" fill="{band_color}" opacity="0.5"/>'
        )
    if th_max and th_max not in (0, th_health) and th_max < max_val:
        band_h = _SPARK_H - (th_max / max_val) * _SPARK_H
        parts.append(
            f'<rect x="{x0}" y="{y0}" width="{_SPARK_W}"'
            f' height="{band_h:.1f}" fill="{band_color}" opacity="0.5"/>'
        )

    # EMA polyline
    pts = " ".join(
        f"{sx(i):.1f},{sy(v):.1f}" for i, v in enumerate(vis_smoothed)
    )
    parts.append(
        f'<polyline points="{pts}" fill="none" stroke="{color}"'
        f' stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
    )

    return "\n".join(parts)


def get_dashboard_data(timeline: Timeline) -> dict[str, Any]:
    """Extract dashboard data from the timeline."""

    now: datetime = datetime.now().astimezone()
    today_start: datetime = datetime(
        now.year, now.month, now.day, tzinfo=local_timezone
    )

    hist_start: datetime = now - timedelta(days=700)
    hist_filter = Timeline.get_filter(hist_start, None)
    days = list(timeline.get_events_by_day(hist_filter))

    sections_cfg: list[dict] = _settings.get("dashboard", {}).get(
        "sections", []
    )
    all_ids: set[str] = {
        m["id"] for sec in sections_cfg for m in sec.get("metrics", [])
    }
    # Always extract energy_expenditure to support dynamic energy thresholds.
    extract_ids: set[str] = all_ids | {"energy_expenditure"}

    raw: dict[str, list[float]] = {mid: [] for mid in extract_ids}
    today_idx: int | None = None

    for i, (day, _, summary) in enumerate(days):
        for mid in extract_ids:
            extractor = _EXTRACTORS.get(mid)
            raw[mid].append(extractor(summary) if extractor else 0.0)
        if day >= today_start:
            today_idx = i
            break

    _keep = {"min", "max", "health"}
    sections: list[dict[str, Any]] = []

    for sec_cfg in sections_cfg:
        metrics: list[dict[str, Any]] = []
        for m in sec_cfg.get("metrics", []):
            mid = m["id"]
            all_vals = raw.get(mid, [])
            if today_idx is not None:
                values = all_vals[:today_idx]
                today_val = (
                    all_vals[today_idx] if today_idx < len(all_vals) else 0.0
                )
            else:
                values = all_vals
                today_val = 0.0
            if not any(v > 0 for v in values) and today_val == 0.0:
                continue
            thresholds: dict[str, float] = {
                k: float(v)
                for k, v in m.items()
                if k in _keep and v is not None
            }
            # For the energy metric, adjust min/health by today's expenditure.
            if mid == "energy" and today_idx is not None:
                expenditure = raw["energy_expenditure"][today_idx]
                if "min" in thresholds:
                    thresholds["min"] = thresholds["min"] + expenditure
                if "health" in thresholds:
                    thresholds["health"] = (
                        thresholds.get("min", 0.0) + 200.0
                    )
            metrics.append(
                {
                    "key": mid,
                    "label": m.get("label", mid),
                    "unit": m.get("unit", ""),
                    "alpha": float(m.get("alpha", 0.9)),
                    "values": values,
                    "today": round(today_val, 2),
                    "thresholds": thresholds,
                }
            )
        if metrics:
            sections.append(
                {"label": sec_cfg.get("label", ""), "metrics": metrics}
            )

    metrics: list[dict[str, Any]] = [
        m for sec in sections for m in sec["metrics"]
    ]
    return {
        "timestamp": now.isoformat(),
        "metrics": metrics,
    }


def _render_cards(
    metrics: list[dict[str, Any]],
    content_y: int,
    parts: list[str],
    id_prefix: str,
) -> int:
    """Render a grid of sparkline cards; return updated content_y."""
    for idx, metric in enumerate(metrics):
        col = idx % _COLS
        row = idx // _COLS
        cx = _PAD + col * (_CARD_W + _GAP)
        cy = content_y + row * (_CARD_H + _GAP)

        parts.append(
            f'<rect x="{cx}" y="{cy}" width="{_CARD_W}" height="{_CARD_H}"'
            f' rx="6" fill="{_SURFACE}" stroke="{_BORDER}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{cx + 8}" y="{cy + 16 + 6}"'
            f' font-size="16" fill="black" font-weight="normal">'
            f"{metric['label']}</text>"
        )

        all_vals = metric["values"] + [metric["today"]]
        smoothed = _make_ema(all_vals, metric["alpha"])
        color = _metric_color(smoothed[-1], metric["thresholds"])

        today = metric["today"]
        if today > 0:
            num = str(int(today)) if today == int(today) else f"{today:.1f}"
            value_str = f"{num}\u202f{metric['unit']}"
        else:
            value_str = "\u2014"

        parts.append(
            f'<text x="{cx + _CARD_W - 8}" y="{cy + 16}"'
            f' font-size="9" fill="{color}" font-weight="600"'
            f' text-anchor="end">{value_str}</text>'
        )

        clip_id = f"{id_prefix}{idx}"
        spark_x = cx + 8
        spark_y = cy + _HEADER_H
        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="{spark_x}" y="{spark_y}"'
            f' width="{_SPARK_W}" height="{_SPARK_H}"/>'
            f"</clipPath>"
        )
        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(
            _sparkline_svg(
                metric["values"],
                metric["today"],
                metric["thresholds"],
                metric["alpha"],
                spark_x,
                spark_y,
            )
        )
        parts.append("</g>")

    n_rows = (len(metrics) + _COLS - 1) // _COLS
    return content_y + n_rows * _CARD_H + max(0, n_rows - 1) * _GAP


def generate_dashboard_svg(timeline: Timeline) -> str:
    """Generate a static SVG dashboard from timeline data."""

    data = get_dashboard_data(timeline)
    metrics: list[dict[str, Any]] = data["metrics"]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    n_rows = (len(metrics) + _COLS - 1) // _COLS
    total_w = _COLS * _CARD_W + (_COLS - 1) * _GAP + 2 * _PAD
    header_h = 28
    cards_h = n_rows * _CARD_H + max(0, n_rows - 1) * _GAP
    total_h = header_h + _PAD + cards_h + _PAD

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{total_w}" height="{total_h}"'
        f' viewBox="0 0 {total_w} {total_h}">'
    )
    parts.append('<style>text {font-family: "SF Pro", "Inter";}</style>')
    parts.append(f'<rect width="{total_w}" height="{total_h}" fill="{_BG}"/>')
    parts.append(
        f'<text x="{_PAD}" y="20" font-size="11" fill="{_MUTED}">'
        f"{now_str}</text>"
    )

    _render_cards(metrics, header_h + _PAD, parts, "c")

    parts.append("</svg>")
    return "\n".join(parts)
