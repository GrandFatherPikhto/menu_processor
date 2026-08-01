"""Persistent GUI settings stored as a plain JSON file at the project root."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("gui.settings")

DEFAULTS = {
    "last_menu_file": None,
    "last_output_directory": None,
    "window_x": 100,
    "window_y": 100,
    "window_width": 1100,
    "window_height": 750,
}


class AppSettings:
    """Loads/saves a small JSON document; tolerant of a missing or corrupt file."""

    def __init__(self, path: Path):
        self._path = Path(path)
        self._data = dict(DEFAULTS)

    def load(self) -> "AppSettings":
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self._data.update(loaded)
            except Exception:
                logger.warning("Could not read %s, using defaults", self._path, exc_info=True)
        return self

    def save(self) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            logger.warning("Could not write %s", self._path, exc_info=True)

    def get(self, key: str) -> Any:
        return self._data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
