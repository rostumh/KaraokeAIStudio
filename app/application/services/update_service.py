from __future__ import annotations

from pathlib import Path
from threading import Event

from packaging.version import InvalidVersion, Version

from app.application.errors import MediaImportError
from app.application.ports.update_client import UpdateClient, UpdateProgress
from app.domain.models.update import UpdateCheckResult, UpdateDownloadResult


class UpdateService:
    """Compares PEP 440 versions and delegates verified package download."""

    def __init__(self, client: UpdateClient) -> None:
        self._client = client

    def check(self, current_version: str, manifest_url: str) -> UpdateCheckResult:
        if not manifest_url:
            raise MediaImportError("No update manifest URL is configured. Set KAS_UPDATE_MANIFEST_URL.")
        release = self._client.fetch_release(manifest_url)
        try:
            available = Version(release.version) > Version(current_version)
        except InvalidVersion as exc:
            raise MediaImportError(f"Update manifest contains an invalid version: {exc}") from exc
        return UpdateCheckResult(current_version, release, available)

    def download(self, release: object, destination: Path, progress: UpdateProgress, cancel_event: Event) -> UpdateDownloadResult:
        from app.domain.models.update import UpdateRelease
        if not isinstance(release, UpdateRelease):
            raise MediaImportError("No valid update release is selected.")
        return UpdateDownloadResult(release, self._client.download(release, destination, progress, cancel_event))
