"""Viewer for travel events."""

import json
import threading
import webbrowser
from dataclasses import dataclass
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from math import (
    acos,
    atan2,
    ceil,
    cos,
    degrees,
    log,
    pi,
    radians,
    sin,
    sqrt,
    tan,
)
from pathlib import Path
from typing import TYPE_CHECKING

from chronicle.event.transport import TransportEvent
from chronicle.timeline import Timeline

EARTH_RADIUS_KM: float = 6371.0
MAX_SEGMENT_LENGTH_KM: float = 100.0
SVG_WIDTH: int = 3000
SVG_HEIGHT: int = 2984
MAX_SVG_LATITUDE: float = 85.0
MIN_POLYLINE_POINTS: int = 2
_MERCATOR_TOP: float = log(tan(pi / 4.0 + radians(MAX_SVG_LATITUDE) / 2.0))
_MERCATOR_BOTTOM: float = log(tan(pi / 4.0 + radians(-MAX_SVG_LATITUDE) / 2.0))


if TYPE_CHECKING:
    from argparse import Namespace

    from chronicle.objects.core import Objects, Place


@dataclass
class TravelServer:
    """Server for travel visualization."""

    lines: list[list[tuple[float, float]]]
    points: dict[str, tuple[str, int]]

    def serve(self) -> None:
        """Serve interactive map with travel lines."""
        html: bytes = self._create_html().encode("utf-8")

        class TravelRequestHandler(BaseHTTPRequestHandler):
            """Handle HTTP requests for travel map."""

            def do_GET(self) -> None:  # noqa: N802
                if self.path not in ("/", "/index.html"):
                    self.send_response(404)
                    self.end_headers()
                    return

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)

            def log_message(self, _message_format: str, *_args: object) -> None:
                """Suppress default logging."""
                return

        host: str = "127.0.0.1"
        with ThreadingHTTPServer((host, 0), TravelRequestHandler) as httpd:
            port: int = httpd.server_address[1]
            url: str = f"http://{host}:{port}/"
            message: str = (
                f"Travel map is available at {url}. Press Ctrl+C to stop."
            )
            print(message)
            webbrowser.open(url)

            server_thread = threading.Thread(
                target=httpd.serve_forever, daemon=True
            )
            server_thread.start()

            try:
                server_thread.join()
            except KeyboardInterrupt:
                print("Stopping travel server.")
            finally:
                httpd.shutdown()
                server_thread.join()

    def _create_html(self) -> str:
        """Create HTML page with Leaflet map."""
        lines_json: str = json.dumps(self.lines)
        points_json: str = json.dumps(self.points)
        template: str = (files("chronicle.view") / "travel.html").read_text(
            encoding="utf-8"
        )
        return template.replace("__LINES_JSON__", lines_json).replace(
            "__POINT_LABELS__", points_json
        )


class TravelViewer:
    """Viewer for travel events."""

    def __init__(self, timeline: Timeline) -> None:
        self.timeline: Timeline = timeline

    def process_command(self, _arguments: "Namespace") -> None:
        objects: Objects = self.timeline.objects

        lines: list[list[tuple[float, float]]] = []
        points: dict[str, tuple[str, int]] = {}

        for event in self.timeline.get_events():
            if isinstance(event, TransportEvent):
                places: list[Place] = [
                    objects.get_object(place_id) for place_id in event.place_ids
                ]
                if len(places) > 1:
                    segments = self._build_lines(
                        places, is_transit=event.is_transit, points=points
                    )
                    lines.extend(segments)
                else:
                    print(event)

        svg_output: str | None = getattr(_arguments, "svg_output", None)

        if svg_output:
            write_travel_svg(lines, points, Path(svg_output))
        else:
            server = TravelServer(lines, points)
            server.serve()

    def _build_lines(
        self,
        places: list["Place"],
        *,
        is_transit: bool,
        points: dict[str, tuple[str, int]],
    ) -> list[list[tuple[float, float]]]:
        """Build great-circle polyline between places."""
        lines: list[list[tuple[float, float]]] = []
        previous_place: Place | None = None

        for place in places:
            point: tuple[float, float] = (place.latitude, place.longitude)
            key: str = _point_key(point)
            visits: int = points[key][1] if key in points else 0
            if previous_place and not is_transit:
                visits += 1
            points[key] = (place.name or place.id, visits)

            if previous_place is None:
                lines.append([point])
                previous_place = place
                continue

            segment: list[tuple[float, float]] = interpolate_great_circle(
                (previous_place.latitude, previous_place.longitude),
                point,
            )
            lines.append(segment)
            previous_place = place

        return lines


def interpolate_great_circle(
    start: tuple[float, float],
    end: tuple[float, float],
    max_segment_length_km: float = MAX_SEGMENT_LENGTH_KM,
) -> list[tuple[float, float]]:
    """Interpolate great-circle path between two points."""

    start_lat_rad: float = radians(start[0])
    start_lon_rad: float = radians(start[1])
    end_lat_rad: float = radians(end[0])
    end_lon_rad: float = radians(end[1])

    start_vector: tuple[float, float, float] = _to_vector(
        start_lat_rad, start_lon_rad
    )
    end_vector: tuple[float, float, float] = _to_vector(
        end_lat_rad, end_lon_rad
    )

    dot_product: float = (
        start_vector[0] * end_vector[0]
        + start_vector[1] * end_vector[1]
        + start_vector[2] * end_vector[2]
    )
    dot_product = max(-1.0, min(1.0, dot_product))
    central_angle: float = acos_safe(dot_product)

    if central_angle == 0.0:
        return [start, end]

    segment_count: int = max(
        1, ceil((central_angle * EARTH_RADIUS_KM) / max_segment_length_km)
    )

    points: list[tuple[float, float]] = []
    sin_total: float = sin(central_angle)
    if sin_total == 0.0:
        return [start, end]

    for index in range(segment_count + 1):
        fraction: float = index / segment_count
        a: float = sin((1.0 - fraction) * central_angle) / sin_total
        b: float = sin(fraction * central_angle) / sin_total

        x: float = a * start_vector[0] + b * end_vector[0]
        y: float = a * start_vector[1] + b * end_vector[1]
        z: float = a * start_vector[2] + b * end_vector[2]

        latitude: float = degrees(atan2(z, sqrt(x * x + y * y)))
        longitude: float = degrees(atan2(y, x))

        points.append((latitude, longitude))

    return points


def _to_vector(latitude: float, longitude: float) -> tuple[float, float, float]:
    """Convert spherical coordinates to unit vector."""
    return (
        cos(latitude) * cos(longitude),
        cos(latitude) * sin(longitude),
        sin(latitude),
    )


def acos_safe(value: float) -> float:
    """Compute arccos with domain clamping."""
    if value <= -1.0:
        return pi
    if value >= 1.0:
        return 0.0
    return acos(value)


def _point_key(point: tuple[float, float]) -> str:
    """Produce a stable key for map point."""
    return f"{point[0]:.6f}_{point[1]:.6f}"


def _project_to_svg(point: tuple[float, float]) -> tuple[float, float]:
    """Project geographic point to Mercator SVG coordinates."""
    latitude, longitude = point
    longitude_normalized: float = ((longitude + 180.0) % 360.0) - 180.0
    x: float = ((longitude_normalized + 180.0) / 360.0) * SVG_WIDTH

    clamped_latitude: float = max(
        min(latitude, MAX_SVG_LATITUDE), -MAX_SVG_LATITUDE
    )
    mercator_value: float = log(tan(pi / 4.0 + radians(clamped_latitude) / 2.0))
    y_ratio: float = (_MERCATOR_TOP - mercator_value) / (
        _MERCATOR_TOP - _MERCATOR_BOTTOM
    )
    y: float = y_ratio * SVG_HEIGHT

    return (x, y)


def write_travel_svg(
    lines: list[list[tuple[float, float]]],
    points: dict[str, tuple[str, int]],
    output_path: Path,
) -> None:
    """Write travel overlay as SVG file."""
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    line_elements: list[str] = []
    for line in lines:
        if len(line) < MIN_POLYLINE_POINTS:
            continue
        projected_points: list[tuple[float, float]] = [
            _project_to_svg(point) for point in line
        ]
        points_attribute: str = " ".join(
            f"{point[0]:.2f},{point[1]:.2f}" for point in projected_points
        )
        element: str = (
            '<polyline points="'
            f"{points_attribute}"
            '" stroke="#000000" stroke-width="2" fill="none" '
            'stroke-opacity="0.2"/>'
        )
        line_elements.append(element)

    unique_points: set[str] = set()
    point_elements: list[str] = []

    for line in lines:
        if not line:
            continue
        endpoints: tuple[tuple[float, float], tuple[float, float]] = (
            line[0],
            line[-1],
        )
        for endpoint in endpoints:
            key: str = _point_key(endpoint)
            if key in unique_points:
                continue
            unique_points.add(key)
            label, visits = points.get(key, ("", 0))
            if visits <= 0:
                continue
            x_coordinate, y_coordinate = _project_to_svg(endpoint)
            circle_parts: list[str] = [
                (
                    f'<circle cx="{x_coordinate:.2f}" '
                    f'cy="{y_coordinate:.2f}" r="4"'
                ),
                'stroke="#000000"',
                'stroke-width="1"',
                'fill="#000000"',
                'fill-opacity="0.6"',
            ]
            circle: str = " ".join(circle_parts) + ">"
            if label:
                circle += f"<title>{escape(label)}</title>"
            circle += "</circle>"
            point_elements.append(circle)

    svg_parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" '
            f'height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">'
        ),
        (
            '    <g id="travel-lines" stroke-linecap="round" '
            'stroke-linejoin="round">'
        ),
    ]
    svg_parts.extend(f"        {element}" for element in line_elements)
    svg_parts.append("    </g>")
    svg_parts.append('    <g id="travel-points">')
    svg_parts.extend(f"        {element}" for element in point_elements)
    svg_parts.append("    </g>")
    svg_parts.append("</svg>")

    svg_content: str = "\n".join(svg_parts) + "\n"
    output_path.write_text(svg_content, encoding="utf-8")
    print(f"Travel overlay SVG saved to {output_path}.")
