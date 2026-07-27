from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from app.application.errors import MediaProbeError
from app.domain.models.media import AudioStream, MediaAsset, MediaKind, VideoStream

LOGGER = logging.getLogger(__name__)


class FFprobeMediaProbe:
    """Safe subprocess adapter that converts ffprobe JSON into domain metadata."""

    def __init__(self, executable: Path, *, timeout_seconds: float = 45.0) -> None:
        self._executable = executable
        self._timeout_seconds = timeout_seconds

    def probe(self, source: Path) -> MediaAsset:
        command = [
            str(self._executable), "-v", "error", "-print_format", "json",
            "-show_format", "-show_streams", "--", str(source),
        ]
        LOGGER.info("Probing media metadata: %s", source)
        try:
            result = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self._timeout_seconds,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except subprocess.TimeoutExpired as exc:
            raise MediaProbeError(f"Media inspection exceeded {self._timeout_seconds:.0f} seconds.") from exc
        except OSError as exc:
            raise MediaProbeError(f"FFprobe could not be started: {exc}") from exc
        if result.returncode != 0:
            detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "Unknown decoder error"
            raise MediaProbeError(f"The file could not be recognized as supported media. FFprobe: {detail}")
        try:
            payload = json.loads(result.stdout)
            if not isinstance(payload, dict):
                raise TypeError("root is not an object")
            return self._parse(source, payload)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise MediaProbeError(f"FFprobe returned incomplete or invalid metadata: {exc}") from exc

    def _parse(self, source: Path, payload: Mapping[str, Any]) -> MediaAsset:
        raw_format = _mapping(payload.get("format"))
        raw_streams = payload.get("streams", [])
        if not isinstance(raw_streams, list):
            raise TypeError("streams is not a list")
        audio: list[AudioStream] = []
        video: list[VideoStream] = []
        for raw in raw_streams:
            stream = _mapping(raw)
            stream_type = str(stream.get("codec_type", ""))
            if stream_type == "audio":
                audio.append(AudioStream(
                    index=_integer(stream.get("index"), 0), codec=str(stream.get("codec_name") or "unknown"),
                    sample_rate=_optional_int(stream.get("sample_rate")), channels=_optional_int(stream.get("channels")),
                    channel_layout=_optional_text(stream.get("channel_layout")), bit_rate=_optional_int(stream.get("bit_rate")),
                    language=_optional_text(_mapping(stream.get("tags")).get("language")),
                ))
            elif stream_type == "video" and _integer(_mapping(stream.get("disposition")).get("attached_pic"), 0) == 0:
                video.append(VideoStream(
                    index=_integer(stream.get("index"), 0), codec=str(stream.get("codec_name") or "unknown"),
                    width=_integer(stream.get("width"), 0), height=_integer(stream.get("height"), 0),
                    frame_rate=_frame_rate(stream.get("avg_frame_rate") or stream.get("r_frame_rate")),
                    pixel_format=_optional_text(stream.get("pix_fmt")), bit_rate=_optional_int(stream.get("bit_rate")),
                ))
        duration = _optional_float(raw_format.get("duration"))
        if duration is None:
            durations = [_optional_float(_mapping(s).get("duration")) for s in raw_streams]
            duration = max((value for value in durations if value is not None), default=0.0)
        resolved = source.resolve()
        identity = hashlib.sha256(f"{resolved}\0{source.stat().st_size}\0{source.stat().st_mtime_ns}".encode()).hexdigest()[:24]
        tags = {str(key): str(value) for key, value in _mapping(raw_format.get("tags")).items()}
        return MediaAsset(
            asset_id=identity, source_path=resolved, display_name=source.name,
            kind=MediaKind.VIDEO if video else MediaKind.AUDIO, size_bytes=source.stat().st_size,
            duration_seconds=max(0.0, duration), container=str(raw_format.get("format_long_name") or raw_format.get("format_name") or source.suffix.lstrip(".")),
            bit_rate=_optional_int(raw_format.get("bit_rate")), audio_streams=tuple(audio), video_streams=tuple(video), tags=tags,
        )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, dict) else {}


def _optional_text(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None


def _integer(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value not in (None, "", "N/A") else None
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "", "N/A") else None
    except (TypeError, ValueError):
        return None


def _frame_rate(value: Any) -> float | None:
    try:
        rate = float(Fraction(str(value)))
        return rate if rate > 0 else None
    except (ValueError, ZeroDivisionError):
        return None
