from __future__ import annotations

from pathlib import Path

from app.application.errors import MediaImportError, UnsupportedMediaError
from app.application.ports.media_probe import MediaProbe
from app.domain.models.media import MediaAsset

SUPPORTED_EXTENSIONS = frozenset({".mp3", ".flac", ".wav", ".aac", ".m4a", ".mp4", ".mkv", ".avi", ".mov"})


class MediaImportService:
    """Validates source policy and delegates technical inspection to a probe port."""

    def __init__(self, probe: MediaProbe, *, maximum_size_bytes: int = 200 * 1024**3) -> None:
        if maximum_size_bytes <= 0:
            raise ValueError("maximum_size_bytes must be positive")
        self._probe = probe
        self._maximum_size_bytes = maximum_size_bytes

    def import_file(self, source: Path) -> MediaAsset:
        normalized = source.expanduser().resolve(strict=False)
        if normalized.suffix.lower() not in SUPPORTED_EXTENSIONS:
            allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            raise UnsupportedMediaError(f"Unsupported file type '{normalized.suffix or '(none)'}'. Supported types: {allowed}")
        if not normalized.exists():
            raise MediaImportError(f"The selected file no longer exists: {normalized}")
        if not normalized.is_file():
            raise MediaImportError(f"The selected path is not a file: {normalized}")
        try:
            size = normalized.stat().st_size
        except OSError as exc:
            raise MediaImportError(f"The selected file cannot be accessed: {exc}") from exc
        if size == 0:
            raise MediaImportError("The selected file is empty.")
        if size > self._maximum_size_bytes:
            limit_gib = self._maximum_size_bytes / 1024**3
            raise MediaImportError(f"The selected file exceeds the {limit_gib:.0f} GiB safety limit.")
        asset = self._probe.probe(normalized)
        if not asset.audio_streams:
            raise UnsupportedMediaError("The selected media contains no decodable audio stream.")
        return asset
