"""View nutrition statistics."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from chronicle.settings import Settings
from chronicle.timeline import Timeline
from chronicle.util import ema

settings: Settings = Settings(Path().home() / ".chronicle" / "settings.json")


def _nutrition(key: str) -> float:
    """Return the ``health`` target for a nutrition key from settings."""
    entry = settings.get("nutrition", {}).get(key, {})
    return float(entry.get("health", 0.0))


@dataclass
class Recommended:
    """Recommended daily intake."""

    energy: float
    """Energy in kilocalories."""

    carbohydrates: float
    """Carbohydrates in grams."""

    protein: float
    """Protein in grams."""

    fat: float
    """Fat in grams."""

    liquid: float
    """Liquid in millilitres."""


def get_recommended() -> Recommended:
    """Load recommended daily intake from settings."""
    return Recommended(
        energy=_nutrition("calories"),
        carbohydrates=_nutrition("carbs_g"),
        protein=_nutrition("protein_g"),
        fat=_nutrition("fat_g"),
        liquid=_nutrition("water_ml"),
    )


# (summary attribute, settings key, unit, label, ema alpha)
_NUTRIENTS: list[tuple[str, str, str, str, float]] = [
    ("energy", "calories", "kcal", "Energy", 0.85),
    ("carbohydrates", "carbs_g", "g", "Carbohydrates", 0.85),
    ("protein", "protein_g", "g", "Protein", 0.85),
    ("fat", "fat_g", "g", "Fat", 0.85),
    ("saturated_fat", "saturated_fat_g", "g", "Saturated fat", 0.85),
    ("fiber", "fiber_g", "g", "Fiber", 0.85),
    ("added_sugar", "added_sugar_g", "g", "Added sugar", 0.85),
    ("omega3", "omega3_g", "g", "Omega-3", 0.97),
    ("calcium", "calcium_mg", "mg", "Calcium", 0.9),
    ("iron", "iron_mg", "mg", "Iron", 0.9),
    ("vitamin_d", "vitamin_d_iu", "IU", "Vitamin D", 0.97),
    ("magnesium", "magnesium_mg", "mg", "Magnesium", 0.9),
    ("zinc", "zinc_mg", "mg", "Zinc", 0.9),
    ("potassium", "potassium_mg", "mg", "Potassium", 0.85),
    ("sodium", "sodium_mg", "mg", "Sodium", 0.85),
    ("vitamin_c", "vitamin_c_mg", "mg", "Vitamin C", 0.85),
    ("vitamin_b12", "vitamin_b12_mcg", "mcg", "Vitamin B12", 0.97),
    ("liquid", "water_ml", "ml", "Liquid", 0.85),
]

_COLOR_OK: str = "#2ca02c"
_COLOR_BAD: str = "#d62728"
_COLOR_NEUTRAL: str = "#7f7f7f"

# Reference-line style: (settings subkey, colour, linestyle, label)
_REF_LINES: list[tuple[str, str, str, str]] = [
    ("health", "#2ca02c", "-", "health"),
    ("gain", "#000000", "-", "gain"),
]


def _plot_nutrient(
    ax: Axes,
    xs_num: np.ndarray,
    ys: list[float | None],
    settings_key: str,
    unit: str,
    label: str,
    alpha: float,
) -> None:
    """Draw one nutrient subplot: bars, EMA line, and reference lines."""

    thresholds: dict = settings.get("nutrition", {}).get(settings_key, {})
    min_val = thresholds.get("min")
    max_val = thresholds.get("max")

    smoothed: list[float] = [
        v if v is not None else 0.0 for v in ema(ys, alpha)
    ]
    avg = smoothed[-1]

    if avg is None or (min_val is None and max_val is None):
        color = _COLOR_NEUTRAL
    elif (min_val is not None and avg < float(min_val)) or (
        max_val is not None and avg > float(max_val)
    ):
        color = _COLOR_BAD
    else:
        color = _COLOR_OK

    ax.bar(
        xs_num,
        [y if y is not None else 0.0 for y in ys],
        width=0.7,
        color=color,
        alpha=0.2,
    )
    ax.plot(
        xs_num,
        smoothed,
        color=color,
        linewidth=1.5,
    )
    maximum = max(y for y in ys if y)
    minimum = min(y for y in ys if y)

    if min_val:
        ax.axhspan(
            0.0,
            float(min_val),
            color="#000000",
            alpha=0.05,
            linewidth=0,
        )
    if max_val:
        ax.axhspan(
            float(max_val) * 10,
            float(max_val),
            color="#000000",
            alpha=0.05,
            linewidth=0,
        )
    for subkey, hcolor, style, hlabel in _REF_LINES:
        value = thresholds.get(subkey)
        if value is not None:
            ax.axhline(
                float(value),
                color=hcolor,
                linewidth=0.8,
                linestyle=style,
                label=hlabel,
            )

    ax.set_title(f"{label} ({unit})", fontsize=8)
    ax.set_ylabel("")
    ax.set_ylim(minimum * 0.9, maximum * 1.1)
    ax.grid(visible=False)
    ax.tick_params(axis="y", labelsize=7)
    ax.tick_params(axis="x", length=0, labelbottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)


@dataclass
class NutritionViewer:
    """Viewer for nutrition statistics."""

    timeline: Timeline

    def plot(
        self,
        path: str | None = None,
        interval: int = 0,
    ) -> None:
        """Plot nutrition per day: one subplot per macro/micro."""

        filter_ = None
        if interval != 0:
            filter_ = Timeline.get_filter(
                from_date=datetime.now(UTC) - timedelta(days=interval),
                to_date=None,
            )
        days = list(self.timeline.get_events_by_day(filter_))

        xs: list[datetime] = []
        data: dict[str, list[float | None]] = {
            key: [] for key, *_ in _NUTRIENTS
        }

        for day, _, summary in days:
            xs.append(day)
            for attr, *_ in _NUTRIENTS:
                value = getattr(summary, attr, 0.0)
                data[attr].append(value or None)
            if day > datetime.now(UTC) + timedelta(days=-1):
                break

        # Only show nutrients that have at least one recorded day.
        active = [
            n for n in _NUTRIENTS if any(v is not None for v in data[n[0]])
        ]

        if not active:
            return

        xs_num = np.array(mdates.date2num(xs))

        n_cols: int = 4
        n_rows: int = -(-len(active) // n_cols)  # ceiling division

        fig, axes_grid = plt.subplots(
            n_rows,
            n_cols,
            figsize=(1.5 * n_cols, 1 * n_rows),
        )
        # Flatten to a 1-D list and hide any unused trailing axes.
        axes_flat: list[Axes] = np.array(axes_grid).flatten().tolist()
        for ax in axes_flat[len(active) :]:
            ax.set_visible(False)

        for attr, settings_key, unit, label, alpha in active:
            ys = data[attr]
            smoothed: list[float] = [
                v if v is not None else 0.0 for v in ema(ys, alpha)
            ]
            avg = smoothed[-1] if smoothed else None
            thresholds: dict = settings.get("nutrition", {}).get(
                settings_key, {}
            )
            min_val = thresholds.get("min")
            max_val = thresholds.get("max")
            if avg is None:
                continue
            if min_val is not None and avg < float(min_val):
                diff = float(min_val) - avg
                print(
                    f"{label}: {avg:.1f} {unit} "
                    f"(below min {min_val} by {diff:.1f} {unit})"
                )
            elif max_val is not None and avg > float(max_val):
                diff = avg - float(max_val)
                print(
                    f"{label}: {avg:.1f} {unit} "
                    f"(above max {max_val} by {diff:.1f} {unit})"
                )

        for ax, (attr, settings_key, unit, label, alpha) in zip(
            axes_flat, active, strict=False
        ):
            _plot_nutrient(
                ax, xs_num, data[attr], settings_key, unit, label, alpha
            )
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

        fig.autofmt_xdate()
        fig.tight_layout()

        if path:
            fig.savefig(path)
        else:
            plt.show()
