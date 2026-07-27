from __future__ import annotations

import json
import os
from pathlib import Path


class PluginStateRepository:
    """Persists explicit enablement; newly discovered plugins remain disabled."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> dict[str, bool]:
        if not self._path.is_file():
            return {}
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        return {str(key): bool(value) for key, value in payload.get("enabled", {}).items()}

    def save(self, states: dict[str, bool]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_name(self._path.name + ".part")
        temporary.write_text(
            json.dumps({"schema_version": 1, "enabled": states}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, self._path)
