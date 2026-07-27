from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class UpdateChannel(StrEnum):
    STABLE = "stable"
    BETA = "beta"


@dataclass(frozen=True, slots=True)
class UpdateRelease:
    version: str
    channel: UpdateChannel
    published_utc: str
    download_url: str
    sha256: str
    size_bytes: int
    release_notes_url: str
    minimum_version: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateCheckResult:
    current_version: str
    release: UpdateRelease
    update_available: bool


@dataclass(frozen=True, slots=True)
class UpdateDownloadResult:
    release: UpdateRelease
    package_path: Path
