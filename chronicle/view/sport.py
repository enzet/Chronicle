"""View sport statistics."""

from dataclasses import dataclass

from chronicle.event.sport import ExerciseEvent
from chronicle.timeline import Timeline


@dataclass
class SportViewer:
    """Viewer for sport statistics."""

    timeline: Timeline

    @staticmethod
    def get_html_exercises() -> str:
        rows = []
        for class_ in sorted(
            ExerciseEvent.__subclasses__(), key=lambda c: c.arguments.command
        ):
            groups = ", ".join(sorted(class_.muscle_groups))
            equip = ", ".join(sorted(class_.equipment))
            rows.append(
                f"<tr><td>{class_.arguments.command.replace('_', ' ')}</td>"
                f"<td>{groups}</td>"
                f"<td>{equip}</td></tr>"
            )
        header = (
            "<tr><th>Exercise</th><th>Muscle groups</th><th>Equipment</th></tr>"
        )
        return f"<table>{header}{''.join(rows)}</table>"
