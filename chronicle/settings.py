"""User settings loaded from a JSON file."""

import json
from pathlib import Path
from typing import Any


class Settings:
    """User settings backed by a JSON file.

    If the file does not exist, all lookups return ``None``.
    """

    def __init__(self, path: Path) -> None:
        self._path: Path = path
        self._data: dict[str, Any] = {}

        if path.exists():
            with path.open() as f:
                self._data = json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for *key*, or *default* if absent."""
        return self._data.get(key, default)
