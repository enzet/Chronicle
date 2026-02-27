"""View sport statistics."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from chronicle.timeline import Timeline
from chronicle.util import smooth

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class SportViewer:
    """Viewer for sport statistics."""

    timeline: Timeline

    def plot_sport(self) -> None:
        from matplotlib import pyplot as plt

        xs: list[datetime] = []

        points: str = "+x|ops*"
        types: list[str] = [
            "chin_ups",
            "push_ups",
            "abs",
            "jumping_jacks",
            "squats",
            "russian_twists",
            "dips",
        ]
        colors: list[str] = [
            "#FF0000",
            "#0000FF",
            "#008800",
            "#888800",
            "#008888",
            "#880088",
            "#888888",
        ]

        ys: list[list[float | None]] = [[] for _ in types]
        ys_total: list[float | None] = []
        for day, _, summary in self.timeline.get_events_by_day():
            xs.append(day)
            total: float = 0.0
            for index, type_ in enumerate(types):
                value: float = summary.exercises.get(type_, 0.0)
                ys[index].append(value if value else None)
                total += value
            ys_total.append(total / len(types))

        for index, type_ in enumerate(types):
            plt.plot(
                xs,  # type: ignore[arg-type]
                ys[index],  # type: ignore[arg-type]
                points[index],
                color=colors[index],
                fillstyle="none",
                label=type_,
            )
            plt.plot(
                xs,  # type: ignore[arg-type]
                smooth(ys[index], 7),
                color=colors[index],
                alpha=0.1,
                linewidth=1,
            )
        plt.plot(
            xs,  # type: ignore[arg-type]
            smooth(ys_total, 7),
            color="#000000",
            linewidth=1,
        )
        plt.ylim(0, None)
        plt.legend()
        plt.show()
