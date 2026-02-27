"""View sport statistics."""

from dataclasses import dataclass
from itertools import cycle
from typing import TYPE_CHECKING

from matplotlib import colormaps

from chronicle.timeline import Timeline
from chronicle.util import smooth

if TYPE_CHECKING:
    from datetime import datetime


COLORS = [
    "#0000FF",
    "#000088",
    "#008800",
    "#008888",
    "#880088",
    "#888800",
    "#888888",
    "#FF0000",
]


@dataclass
class SportViewer:
    """Viewer for sport statistics."""

    timeline: Timeline

    def plot_sport(self) -> None:
        from matplotlib import pyplot as plt

        days = list(self.timeline.get_events_by_day())

        types: list[str] = sorted(
            {key for _, _, summary in days for key in summary.exercises}
        )

        xs: list[datetime] = []
        ys: list[list[float | None]] = [[] for _ in types]
        ys_total: list[float | None] = []

        color_map = colormaps["tab20"]
        colors = [color_map(i / max(len(types), 1)) for i in range(len(types))]
        markers = cycle("+x|ops*^v<>1234")

        for day, _, summary in days:
            xs.append(day)
            total: float = 0.0
            for index, type_ in enumerate(types):
                value: float = summary.exercises.get(type_, 0.0)
                ys[index].append(value if value else None)
                total += value
            ys_total.append(total / len(types) if types else 0.0)

        for index, type_ in enumerate(types):
            color = colors[index]
            marker = next(markers)
            plt.plot(
                xs,  # type: ignore[arg-type]
                ys[index],  # type: ignore[arg-type]
                marker,
                color=color,
                fillstyle="none",
                label=type_,
            )
            plt.plot(
                xs,  # type: ignore[arg-type]
                smooth(ys[index], 7),
                color=color,
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
