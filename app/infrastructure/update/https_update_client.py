from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from threading import Event
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.application.errors import MediaImportError
from app.application.ports.update_client import UpdateProgress
from app.domain.models.update import UpdateChannel, UpdateRelease
from app.infrastructure.media.ffmpeg_audio_extractor import ExtractionCancelledError


class HttpsUpdateClient:
    """HTTPS-only manifest and package client with size limits and SHA-256 verification."""

    MANIFEST_LIMIT = 1_048_576
    PACKAGE_LIMIT = 2_147_483_648

    def fetch_release(self, manifest_url: str) -> UpdateRelease:
        self._require_https(manifest_url, "manifest")
        request = Request(manifest_url, headers={"Accept": "application/json", "User-Agent": "KaraokeAIStudio-Updater/1"})
        try:
            with urlopen(request, timeout=15) as response:
                content_type = response.headers.get_content_type()
                if content_type not in {"application/json", "text/json", "text/plain"}:
                    raise MediaImportError(f"Update manifest has an unexpected content type: {content_type}")
                data = response.read(self.MANIFEST_LIMIT + 1)
        except MediaImportError:
            raise
        except Exception as exc:
            raise MediaImportError(f"Unable to check for updates: {exc}") from exc
        if len(data) > self.MANIFEST_LIMIT:
            raise MediaImportError("Update manifest exceeds the 1 MiB safety limit.")
        try:
            payload = json.loads(data.decode("utf-8"))
            if int(payload.get("schema_version", 0)) != 1:
                raise ValueError("unsupported schema_version")
            release = UpdateRelease(
                str(payload["version"]), UpdateChannel(str(payload.get("channel", "stable"))),
                str(payload["published_utc"]), str(payload["download_url"]),
                str(payload["sha256"]).lower(), int(payload["size_bytes"]),
                str(payload["release_notes_url"]),
                str(payload["minimum_version"]) if payload.get("minimum_version") else None,
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise MediaImportError(f"Update manifest is invalid: {exc}") from exc
        self._validate_release(release)
        return release

    def download(self, release: UpdateRelease, destination: Path, progress: UpdateProgress, cancel_event: Event) -> Path:
        self._validate_release(release)
        destination.mkdir(parents=True, exist_ok=True)
        name = Path(urlparse(release.download_url).path).name
        if not name or Path(name).suffix.lower() not in {".msix", ".msi", ".exe", ".zip"}:
            raise MediaImportError("Update package URL does not contain a supported filename.")
        final = destination / name
        temporary = final.with_name(final.name + ".part")
        temporary.unlink(missing_ok=True)
        digest = hashlib.sha256()
        received = 0
        request = Request(release.download_url, headers={"Accept": "application/octet-stream", "User-Agent": "KaraokeAIStudio-Updater/1"})
        try:
            with urlopen(request, timeout=30) as response, temporary.open("wb") as output:
                declared = int(response.headers.get("Content-Length", release.size_bytes))
                if declared > self.PACKAGE_LIMIT or declared != release.size_bytes:
                    raise MediaImportError("Update package size does not match the manifest.")
                while True:
                    if cancel_event.is_set():
                        raise ExtractionCancelledError("Update download was cancelled.")
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    received += len(chunk)
                    if received > self.PACKAGE_LIMIT or received > release.size_bytes:
                        raise MediaImportError("Update package exceeded its declared size.")
                    output.write(chunk); digest.update(chunk)
                    progress(received / max(1, release.size_bytes), f"Downloading update {received * 100 / max(1, release.size_bytes):.0f}%")
            if received != release.size_bytes:
                raise MediaImportError("Downloaded update size does not match the manifest.")
            if digest.hexdigest() != release.sha256:
                raise MediaImportError("Downloaded update failed SHA-256 verification.")
            os.replace(temporary, final)
            progress(1.0, "Update package verified")
            return final
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    def _validate_release(self, release: UpdateRelease) -> None:
        self._require_https(release.download_url, "package")
        self._require_https(release.release_notes_url, "release notes")
        if len(release.sha256) != 64 or any(ch not in "0123456789abcdef" for ch in release.sha256):
            raise MediaImportError("Update manifest SHA-256 value is invalid.")
        if not 1 <= release.size_bytes <= self.PACKAGE_LIMIT:
            raise MediaImportError("Update package size is outside the supported range.")

    @staticmethod
    def _require_https(url: str, label: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme.lower() != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise MediaImportError(f"Update {label} URL must use HTTPS without embedded credentials.")
