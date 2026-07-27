from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.domain.models.media import MediaAsset


class MediaProbe(Protocol):
    """Technology-independent boundary for inspecting a local media file."""

    def probe(self, source: Path) -> MediaAsset:
        """Inspect source and return validated metadata without modifying the file."""
