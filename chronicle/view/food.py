"""View food statistics."""

from dataclasses import dataclass

from chronicle.objects.core import Dish, Drink
from chronicle.timeline import Timeline

MACROS: list[tuple[str, str, str]] = [
    ("carbohydrates", "Carbs", "g"),
    ("protein", "Protein", "g"),
    ("fat", "Fat", "g"),
    ("saturated_fat", "Sat. fat", "g"),
    ("fiber", "Fiber", "g"),
    ("sugar", "Sugar", "g"),
    ("omega3", "Omega-3", "g"),
]

MICROS: list[tuple[str, str, str]] = [
    ("calcium", "Ca", "mg"),
    ("iron", "Fe", "mg"),
    ("vitamin_d", "Vit. D", "IU"),
    ("magnesium", "Mg", "mg"),
    ("zinc", "Zn", "mg"),
    ("potassium", "K", "mg"),
    ("sodium", "Na", "mg"),
    ("vitamin_c", "Vit. C", "mg"),
    ("vitamin_b12", "Vit. B12", "μg"),
]


def _fmt(value: float) -> str:
    return f"{value:.3g}"


def _cell_color(value: float, col_min: float, col_max: float) -> str:
    t = 0.5 if col_max == col_min else (value - col_min) / (col_max - col_min)
    return f"hsl({int(t * 120)}, 70%, 85%)"


@dataclass
class FoodViewer:
    """Viewer for food statistics."""

    timeline: Timeline

    def get_html_food(self) -> str:
        nutrients = MACROS + MICROS

        food_objects: list[Dish | Drink] = sorted(
            (
                obj
                for obj in self.timeline.objects.objects.values()
                if isinstance(obj, (Dish, Drink))
            ),
            key=lambda o: (o.id or "").lower(),
        )

        col_values: list[list[float]] = [[] for _ in nutrients]
        kcal_abs_values: list[float] = []
        kcal_per_g_values: list[float] = []
        row_data: list[
            tuple[str, str, float | None, float | None, list[float | None]]
        ] = []
        for obj in food_objects:
            weight_obj = getattr(obj, "weight", None)
            if not weight_obj:
                continue
            weight = weight_obj.value
            name = obj.title or obj.id or "?"
            kind = "dish" if isinstance(obj, Dish) else "drink"
            kcal_abs: float | None = None
            kcal_per_g: float | None = None
            if obj.energy is not None:
                kcal_abs = obj.energy
                kcal_per_g = obj.energy / weight
                kcal_abs_values.append(obj.energy)
                kcal_per_g_values.append(obj.energy / weight)
            values: list[float | None] = []
            for i, (field, *_) in enumerate(nutrients):
                nutrient = getattr(obj, field, None)
                if nutrient is not None:
                    v = nutrient.value / weight
                    values.append(v)
                    col_values[i].append(v)
                else:
                    values.append(None)
            row_data.append((name, kind, kcal_abs, kcal_per_g, values))

        col_min = [min(vs) if vs else 0.0 for vs in col_values]
        col_max = [max(vs) if vs else 0.0 for vs in col_values]
        kcal_abs_min = min(kcal_abs_values) if kcal_abs_values else 0.0
        kcal_abs_max = max(kcal_abs_values) if kcal_abs_values else 0.0
        kcal_per_g_min = min(kcal_per_g_values) if kcal_per_g_values else 0.0
        kcal_per_g_max = max(kcal_per_g_values) if kcal_per_g_values else 0.0

        header_cells = "".join(
            f"<th>{label}<br><small>{unit}/g</small></th>"
            for _, label, unit in nutrients
        )
        kcal_headers = (
            "<th>kcal<br><small>kcal</small></th>"
            "<th>kcal<br><small>kcal/g</small></th>"
        )
        header = f"<tr><th>Food</th>{kcal_headers}{header_cells}</tr>"

        rows = []
        for name, _kind, kcal_abs, kcal_per_g, values in row_data:
            cells = []
            if kcal_abs is not None:
                color = _cell_color(kcal_abs, kcal_abs_min, kcal_abs_max)
                cells.append(
                    f'<td style="background:{color}">{_fmt(kcal_abs)}</td>'
                )
            else:
                cells.append("<td></td>")
            if kcal_per_g is not None:
                color = _cell_color(kcal_per_g, kcal_per_g_min, kcal_per_g_max)
                cells.append(
                    f'<td style="background:{color}">{_fmt(kcal_per_g)}</td>'
                )
            else:
                cells.append("<td></td>")
            for i, v in enumerate(values):
                if v is not None:
                    color = _cell_color(v, col_min[i], col_max[i])
                    cells.append(
                        f'<td style="background:{color}">{_fmt(v)}</td>'
                    )
                else:
                    cells.append("<td></td>")
            rows.append(f"<tr><td>{name}</td>{''.join(cells)}</tr>")

        return f"<table>{header}{''.join(rows)}</table>"
