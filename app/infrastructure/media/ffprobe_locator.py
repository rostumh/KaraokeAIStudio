from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from app.application.errors import DependencyUnavailableError


def locate_ffprobe() -> Path:
    """Locate ffprobe from an override, packaged runtime, or the system PATH."""
    candidates: list[Path] = []
    override = os.getenv("KAS_FFPROBE_PATH")
    if override:
        candidates.append(Path(override).expanduser())
    executable_dir = Path(sys.executable).resolve().parent
    bundle_root = Path(getattr(sys, "_MEIPASS", executable_dir))
    candidates.extend((
        executable_dir / "ffprobe.exe",
        executable_dir / "ffmpeg" / "bin" / "ffprobe.exe",
        executable_dir / "runtime" / "ffmpeg" / "bin" / "ffprobe.exe",
        bundle_root / "runtime" / "ffmpeg" / "bin" / "ffprobe.exe",
        Path(__file__).resolve().parents[3] / "tools" / "ffmpeg" / "bin" / "ffprobe.exe",
    ))
    system_match = shutil.which("ffprobe")
    if system_match:
        candidates.append(Path(system_match))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise DependencyUnavailableError(
        "The built-in media inspection engine is missing. Reinstall Karaoke AI Studio."
    )
