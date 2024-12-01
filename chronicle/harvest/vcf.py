from pathlib import Path

from chronicle.timeline import Timeline


class VcfImporter:
    def __init__(self, file_path: Path):
        self.file_path: Path = file_path

    def import_data(self, timeline: Timeline):
        with Path(self.file_path).open() as input_file:
            for line in input_file.readlines():
                line = line[:-1]
                if line[0] == " ":
                    continue
                if line == "BEGIN:VCARD":
                    data = {}
                elif line == "END:VCARD":
                    self.add_person(timeline)
                else:
                    key, value = line.split(":", 1)
                    if key == "FN":
                        data["name"] = value

    def add_person(self, timeline: Timeline) -> None:
        pass
