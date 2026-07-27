from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from app.application.errors import DependencyUnavailableError


def locate_ffmpeg() -> Path:
    """Locate FFmpeg using explicit configuration, packaged paths, then PATH."""
    candidates: list[Path] = []
    override = os.getenv("KAS_FFMPEG_PATH")
    if override:
        candidates.append(Path(override).expanduser())
    executable_dir = Path(sys.executable).resolve().parent
    bundle_root = Path(getattr(sys, "_MEIPASS", executable_dir))
    project_root = Path(__file__).resolve().parents[3]
    candidates.extend((
        executable_dir / "ffmpeg.exe",
        executable_dir / "ffmpeg" / "bin" / "ffmpeg.exe",
        executable_dir / "runtime" / "ffmpeg" / "bin" / "ffmpeg.exe",
        bundle_root / "runtime" / "ffmpeg" / "bin" / "ffmpeg.exe",
        project_root / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe",
    ))
    match = shutil.which("ffmpeg")
    if match:
        candidates.append(Path(match))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise DependencyUnavailableError(
        "The built-in media engine is missing. Reinstall Karaoke AI Studio."
    )
