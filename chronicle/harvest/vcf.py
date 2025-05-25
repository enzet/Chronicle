"""Importer for VCF files."""

from dataclasses import dataclass
from pathlib import Path
from typing import override

from chronicle.harvest.core import Importer
from chronicle.timeline import Timeline


@dataclass
class VcfImporter(Importer):
    """Importer for VCF files."""

    path: Path
    """Path to the file containing VCF data."""

    @override
    def import_data(self, timeline: Timeline) -> None:
        with self.path.open(encoding="utf-8") as input_file:
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
        # TODO(enzet): Implement.
        pass
