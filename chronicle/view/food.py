"""View food statistics."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

import matplotlib.dates as mdates
import numpy as np
from matplotlib import pyplot as plt

from chronicle.settings import Settings
from chronicle.timeline import Timeline
from chronicle.util import smooth

KCAL_PER_G_PROTEIN: float = 4.0
KCAL_PER_G_CARBS: float = 4.0
KCAL_PER_G_FAT: float = 9.0

settings: Settings = Settings(Path().home() / ".chronicle" / "settings.json")

HEIGHT: float = settings.get("height")
WEIGHT: float = settings.get("weight")
AGE: float = settings.get("age")
SEX: Literal["male", "female"] = settings.get("sex")


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


def compute_recommended(
    height: float,
    weight: float,
    age: float,
    sex: Literal["male", "female"] = "male",
    activity: float = 1.2,
) -> Recommended:
    """Compute recommended daily kcal and macronutrients.

    Uses the Mifflin-St Jeor equation for basal metabolic rate (BMR),
    multiplied by an activity factor for total daily energy expenditure.

    :param height: height in centimetres.
    :param weight: weight in kilograms.
    :param age: age in years.
    :param sex: biological sex, either `male` or `female`.
    :param activity: activity multiplier (1.2 sedentary - 1.9 very active).
    """
    bmr: float = 10.0 * weight + 6.25 * height - 5.0 * age
    bmr += 5.0 if sex == "male" else -161.0
    energy: float = bmr * activity

    protein: float = 1.2 * weight
    fat: float = energy * 0.30 / KCAL_PER_G_FAT
    carbohydrates: float = (
        energy - protein * KCAL_PER_G_PROTEIN - fat * KCAL_PER_G_FAT
    ) / KCAL_PER_G_CARBS

    return Recommended(
        energy=round(energy, 1),
        carbohydrates=round(carbohydrates, 1),
        protein=round(protein, 1),
        fat=round(fat, 1),
    )


@dataclass
class FoodViewer:
    """Viewer for food statistics."""

    timeline: Timeline

    def plot_kcal(
        self,
        path: str | None = None,
        interval: int = 0,
        *,
        percent: bool = False,
    ) -> None:
        """Plot average eaten kcal per day."""

        filter_ = None
        if interval != 0:
            filter_ = Timeline.get_filter(
                from_date=datetime.now(UTC) - timedelta(days=interval),
                to_date=None,
            )
        days = list(self.timeline.get_events_by_day(filter_))[:-1]

        xs: list[datetime] = []
        ys_energy: list[float | None] = []
        ys_carbs: list[float | None] = []
        ys_protein: list[float | None] = []
        ys_fat: list[float | None] = []
        ys_liquid: list[float | None] = []

        for day, _, summary in days:
            xs.append(day)
            ys_energy.append(summary.energy or None)
            ys_carbs.append(summary.carbohydrates or None)
            ys_protein.append(summary.protein or None)
            ys_fat.append(summary.fat or None)
            ys_liquid.append(summary.liquid or None)

        if percent:
            rec = compute_recommended(HEIGHT, WEIGHT, AGE, SEX)
            print(f"{rec=}")

            def to_pct(
                values: list[float | None], norm: float
            ) -> list[float | None]:
                if norm == 0.0:
                    return values
                return [
                    v / norm * 100.0 if v is not None else None for v in values
                ]

            ys_energy = to_pct(ys_energy, rec.energy)
            ys_carbs = to_pct(ys_carbs, rec.carbohydrates)
            ys_protein = to_pct(ys_protein, rec.protein)
            ys_fat = to_pct(ys_fat, rec.fat)
            ys_liquid = to_pct(ys_liquid, 1500.0)

        fig, ax1 = plt.subplots(figsize=(10, 4.5), dpi=100)

        # Convert datetimes to numeric positions for grouped bars.
        xs_num = np.array(mdates.date2num(xs))
        width = 0.2  # bar width in days
        offsets = [-2.0, -1.0, 0.0, 1.0, 2.0]

        if percent:
            ax2 = ax1
            ax3 = ax1
            energy_label = "kcal (%)"
            carbs_label = "carbohydrates (%)"
            protein_label = "protein (%)"
            fat_label = "fat (%)"
            liquid_label = "liquid (%)"
            ylabel_left = "%"
            ylabel_right = None
            ylabel_liquid = None
        else:
            ax2 = ax1.twinx()
            ax3 = ax1.twinx()
            ax3.spines["right"].set_position(("outward", 60))
            energy_label = "kcal per day"
            carbs_label = "carbohydrates (g)"
            protein_label = "protein (g)"
            fat_label = "fat (g)"
            liquid_label = "liquid (ml)"
            ylabel_left = "kcal"
            ylabel_right = "g"
            ylabel_liquid = "ml"

        ax1.bar(
            xs_num + offsets[0] * width,
            [y if y is not None else 0.0 for y in ys_energy],
            width=width,
            color="black",
            linewidth=0.5,
            label=energy_label,
            alpha=0.1,
        )
        ax2.bar(
            xs_num + offsets[1] * width,
            [y or 0.0 for y in ys_carbs],
            width=width,
            label=carbs_label,
            linewidth=0.5,
            color="green",
            edgecolor="green",
            alpha=0.1,
        )
        ax2.bar(
            xs_num + offsets[2] * width,
            [y or 0.0 for y in ys_protein],
            width=width,
            label=protein_label,
            linewidth=0.5,
            color="blue",
            edgecolor="blue",
            alpha=0.1,
        )
        ax2.bar(
            xs_num + offsets[3] * width,
            [y or 0.0 for y in ys_fat],
            width=width,
            label=fat_label,
            linewidth=0.5,
            color="red",
            edgecolor="red",
            alpha=0.1,
        )
        ax3.bar(
            xs_num + offsets[4] * width,
            [y or 0.0 for y in ys_liquid],
            width=width,
            label=liquid_label,
            linewidth=0.5,
            color="cyan",
            edgecolor="cyan",
            alpha=0.1,
        )
        step: int = 7

        ax1.plot(
            xs_num,
            smooth(ys_energy, step),  # type: ignore[arg-type]
            color="black",
            linewidth=2,
            label=f"kcal {step}-day average",
        )
        ax2.plot(
            xs_num,
            smooth(ys_carbs, step),  # type: ignore[arg-type]
            color="green",
            linewidth=1,
            label=f"carbohydrates {step}-day average",
        )
        ax2.plot(
            xs_num,
            smooth(ys_protein, step),  # type: ignore[arg-type]
            color="blue",
            linewidth=1,
            label=f"protein {step}-day average",
        )
        ax2.plot(
            xs_num,
            smooth(ys_fat, step),  # type: ignore[arg-type]
            color="red",
            linewidth=1,
            label=f"fat {step}-day average",
        )
        ax3.plot(
            xs_num,
            smooth(ys_liquid, step),  # type: ignore[arg-type]
            color="cyan",
            linewidth=1,
            label=f"liquid {step}-day average",
        )

        if percent:
            ax1.axhline(100.0, color="black", linewidth=0.5)
            ax1.axhline(125.0, color="black", linewidth=0.5)

        ax1.set_ylim(0, None)
        ax1.set_ylabel(ylabel_left)
        if ylabel_right:
            ax2.set_ylim(0, None)
            ax2.set_ylabel(ylabel_right)
        if ylabel_liquid:
            ax3.set_ylim(0, None)
            ax3.set_ylabel(ylabel_liquid)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        fig.autofmt_xdate()

        lines1, labels1 = ax1.get_legend_handles_labels()
        if ax2 is not ax1:
            lines2, labels2 = ax2.get_legend_handles_labels()
            lines3, labels3 = ax3.get_legend_handles_labels()
            lines = lines1 + lines2 + lines3
            labels = labels1 + labels2 + labels3
        else:
            lines, labels = lines1, labels1
        ax1.legend(
            lines,
            labels,
            loc="upper left",
            bbox_to_anchor=(1.05, 1),
            borderaxespad=0,
            frameon=False,
        )
        fig.tight_layout()

        if path:
            fig.savefig(path)
        else:
            plt.show()
