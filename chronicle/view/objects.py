from pathlib import Path
from chronicle.timeline import Timeline


class ObjectsHtmlViewer:
    def __init__(self, timeline: Timeline) -> None:
        self.timeline = timeline

    def write_html(self, output_path: Path) -> None:
        with output_path.open("w+") as output_file:
            output_file.write(
                """
            <html>
            <style>
    table {
        border-collapse: collapse;
    }

    table tr td.image {
        text-align: center;
        height: 120px;
    }

    table tr td {
        padding: 4px 7px;
        border-top: 0.5px solid black;
        border-bottom: 0.5px solid black;
    }

    body {
        font-family: "SF Pro";
    }

    p {
        margin: 0;
    }

    .object-text {
        display: flex;
        align-items: center;
    }

    code {
        font-family: "Iosevka Custom Extended";
    }

    a {
        text-decoration: none;
        color: blue;
    }

    .object-container {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
    }

    .object {
        display: flex;
        flex-direction: row;
        height: 100px;
        border-radius: 10px;
        margin: 10px;
        box-shadow: 0px 2px 10px #DDD;
    }

    .object-image {
        width: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .object-text {
        width: 200px;
        vertical-align: middle;
        margin: 10px;
    }
            </style>
            """
            )
        output_file.write(
            self.timeline.get_objects_html(Path.home() / "Raster" / "thing")
        )
        print(f"Output HTML was written into {output_path}.")
