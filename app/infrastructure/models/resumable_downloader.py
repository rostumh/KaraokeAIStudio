from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from threading import Event
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from huggingface_hub import get_hf_file_metadata

from app.application.errors import MediaImportError

Progress = Callable[[int, int, str], None]


@dataclass(frozen=True, slots=True)
class RemoteFileMetadata:
    algorithm: str
    digest: str
    size: int
    location: str | None = None


class ResumableModelDownloader:
    """HTTPS downloader with Range resume, checksum verification, and offline markers."""

    def download(self, url: str, destination: Path, progress: Progress, cancel: Event) -> Path:
        if not url.startswith("https://"):
            raise MediaImportError("Model URL must use HTTPS.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        part = destination.with_name(destination.name + ".part")
        metadata = self._metadata(url)

        if part.is_file() and part.stat().st_size == metadata.size:
            if self.digest_file(part, metadata.algorithm) == metadata.digest:
                os.replace(part, destination)
                self._write_marker(destination, metadata)
                progress(metadata.size, metadata.size, destination.name)
                return destination
            part.unlink()
        elif part.is_file() and part.stat().st_size > metadata.size:
            part.unlink()

        restarted_without_range = False
        while True:
            offset = part.stat().st_size if part.exists() else 0
            headers = {"User-Agent": "KaraokeAIStudio-ModelManager/1"}
            if offset:
                headers["Range"] = f"bytes={offset}-"
            try:
                download_url = metadata.location or url
                response = urlopen(Request(download_url, headers=headers), timeout=60)
            except HTTPError as exc:
                if exc.code == 416 and offset and not restarted_without_range:
                    part.unlink(missing_ok=True)
                    restarted_without_range = True
                    continue
                raise MediaImportError(f"Model download failed with HTTP {exc.code}: {exc.reason}") from exc
            except Exception as exc:
                raise MediaImportError(f"Unable to download {destination.name}: {exc}") from exc

            with response:
                status = getattr(response, "status", response.getcode())
                if offset and status != 206:
                    offset = 0
                    mode = "wb"
                else:
                    mode = "ab" if offset else "wb"
                received = offset
                with part.open(mode) as output:
                    while True:
                        if cancel.is_set():
                            raise MediaImportError("Model download cancelled.")
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        output.write(chunk)
                        received += len(chunk)
                        progress(received, metadata.size, destination.name)
            break

        actual_size = part.stat().st_size if part.exists() else 0
        if actual_size != metadata.size:
            raise MediaImportError(
                f"Downloaded size mismatch for {destination.name}: received {actual_size} of {metadata.size} bytes."
            )
        actual = self.digest_file(part, metadata.algorithm)
        if actual != metadata.digest:
            part.unlink(missing_ok=True)
            raise MediaImportError(f"Checksum verification failed for {destination.name}. Please retry.")
        os.replace(part, destination)
        self._write_marker(destination, metadata)
        progress(metadata.size, metadata.size, destination.name)
        return destination

    def verify(self, url: str, path: Path) -> bool:
        if not path.is_file():
            return False
        marker = self._read_marker(path)
        if marker is not None:
            return path.stat().st_size == marker.size and self.digest_file(path, marker.algorithm) == marker.digest
        metadata = self._metadata(url)
        valid = path.stat().st_size == metadata.size and self.digest_file(path, metadata.algorithm) == metadata.digest
        if valid:
            self._write_marker(path, metadata)
        return valid

    @staticmethod
    def digest_file(path: Path, algorithm: str) -> str:
        if algorithm == "git-sha1":
            digest = hashlib.sha1()
            digest.update(f"blob {path.stat().st_size}\0".encode("ascii"))
        else:
            digest = hashlib.new(algorithm)
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def sha256(path: Path) -> str:
        return ResumableModelDownloader.digest_file(path, "sha256")

    @staticmethod
    def _metadata(url: str) -> RemoteFileMetadata:
        try:
            metadata = get_hf_file_metadata(url, timeout=30)
        except Exception as exc:
            raise MediaImportError(f"Unable to contact the model server: {exc}") from exc
        etag = str(metadata.etag or "").strip().strip('"').lower()
        size = int(metadata.size or 0)
        location = str(metadata.location or url)
        if re.fullmatch(r"[0-9a-f]{64}", etag):
            algorithm = "sha256"
        elif re.fullmatch(r"[0-9a-f]{40}", etag):
            algorithm = "git-sha1"
        else:
            raise MediaImportError("Model server did not provide a usable checksum.")
        if size <= 0:
            raise MediaImportError("Model server did not provide a usable file size.")
        if not location.startswith("https://"):
            raise MediaImportError("Model server returned an unsafe download location.")
        return RemoteFileMetadata(algorithm, etag, size, location)

    @staticmethod
    def _marker_path(path: Path) -> Path:
        return path.with_name(path.name + ".verified.json")

    @classmethod
    def _write_marker(cls, path: Path, metadata: RemoteFileMetadata) -> None:
        marker = cls._marker_path(path)
        temporary = marker.with_name(marker.name + ".part")
        temporary.write_text(
            json.dumps({"schema_version": 1, "algorithm": metadata.algorithm, "digest": metadata.digest, "size": metadata.size}, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, marker)

    @classmethod
    def _read_marker(cls, path: Path) -> RemoteFileMetadata | None:
        marker = cls._marker_path(path)
        if not marker.is_file():
            return None
        try:
            payload = json.loads(marker.read_text(encoding="utf-8"))
            algorithm = str(payload["algorithm"])
            digest = str(payload["digest"]).lower()
            size = int(payload["size"])
            expected_length = 64 if algorithm == "sha256" else 40 if algorithm == "git-sha1" else 0
            if expected_length == 0 or not re.fullmatch(rf"[0-9a-f]{{{expected_length}}}", digest) or size <= 0:
                return None
            return RemoteFileMetadata(algorithm, digest, size)
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            return None
