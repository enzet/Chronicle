"""View sport statistics."""

from collections import defaultdict

from chronicle.event.sport import ExerciseEvent
from chronicle.timeline import Timeline

_HOME_EQUIPMENT = {"dumbbell"}


class SportViewer:
    """Viewer for sport statistics."""

    def __init__(self, timeline: Timeline) -> None:
        self.timeline: Timeline = timeline

        self.by_group: dict[str, tuple[list[str], list[str]]] = defaultdict(
            lambda: ([], [])
        )
        self.name_to_command: dict[str, str] = {}

        for class_ in sorted(
            ExerciseEvent.__subclasses__(), key=lambda c: c.arguments.command
        ):
            command = class_.arguments.command
            name = command.replace("_", " ")
            self.name_to_command[name] = command
            is_home = class_.equipment <= _HOME_EQUIPMENT
            for group in sorted(class_.muscle_groups):
                home, gym = self.by_group[group]
                (home if is_home else gym).append(name)

    def linked(self, names: list[str]) -> str:
        return ", ".join(
            f'<a href="#ex-{self.name_to_command[n]}">{n}</a>'
            for n in sorted(set(names))
        )

    def get_html_exercises(self) -> str:
        rows = []
        for class_ in sorted(
            ExerciseEvent.__subclasses__(), key=lambda c: c.arguments.command
        ):
            command = class_.arguments.command
            groups = ", ".join(sorted(class_.muscle_groups))
            equip = ", ".join(sorted(class_.equipment))
            rows.append(
                f'<tr id="ex-{command}"><td>{command.replace("_", " ")}</td>'
                f"<td>{groups}</td>"
                f"<td>{equip}</td></tr>"
            )
        header = (
            "<tr><th>Exercise</th><th>Muscle groups</th><th>Equipment</th></tr>"
        )
        return f"<table>{header}{''.join(rows)}</table>"

    def get_subgroup_row(self, group: str) -> str:
        home, gym = self.by_group[group]
        return (
            f"<td>{group}</td>"
            f"<td>{self.linked(home)}</td>"
            f"<td>{self.linked(gym)}</td>"
        )

    def get_html_exercises_by_subgroup(self) -> str:
        rows = [
            ("<tr>" + self.get_subgroup_row(group) + "</tr>")
            for group in sorted(self.by_group)
        ]
        header = (
            "<tr><th>Muscle subgroup</th>"
            "<th>No/home equipment</th>"
            "<th>Gym equipment</th></tr>"
        )
        return f"<table>{header}{''.join(rows)}</table>"
