from __future__ import annotations

import hashlib
from pathlib import Path

from packaging.version import InvalidVersion, Version

from app.application.errors import MediaImportError


def msix_version(version: str) -> str:
    """Convert a final PEP 440 release into MSIX's four-part numeric version."""
    try:
        parsed = Version(version)
    except InvalidVersion as exc:
        raise MediaImportError(f"Invalid application version: {version}") from exc
    if parsed.is_prerelease or parsed.is_devrelease or parsed.local is not None:
        raise MediaImportError("MSIX release builds require a final public version.")
    release = list(parsed.release)
    if len(release) > 4 or any(part > 65535 for part in release):
        raise MediaImportError("MSIX version components must fit four unsigned 16-bit integers.")
    return ".".join(str(part) for part in (release + [0, 0, 0, 0])[:4])


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
