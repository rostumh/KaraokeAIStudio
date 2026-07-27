from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from threading import Event
from typing import Protocol

from app.domain.models.update import UpdateRelease

UpdateProgress = Callable[[float, str], None]


class UpdateClient(Protocol):
    def fetch_release(self, manifest_url: str) -> UpdateRelease:
        """Fetch and validate release metadata from the configured HTTPS endpoint."""

    def download(self, release: UpdateRelease, destination: Path, progress: UpdateProgress, cancel_event: Event) -> Path:
        """Download and verify the package without executing it."""
