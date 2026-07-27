from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from threading import Event, Thread

from app.application.errors import MediaImportError
from app.application.ports.media_quality_validator import ValidationProgress
from app.domain.models.quality_validation import CheckSeverity, MediaQualityReport, QualityCheck
from app.infrastructure.media.ffmpeg_audio_extractor import ExtractionCancelledError


class FFmpegQualityValidator:
    """Combines FFprobe metadata checks with a strict full-file FFmpeg decode scan."""

    def __init__(self, ffprobe: Path, ffmpeg: Path) -> None:
        self._ffprobe = ffprobe
        self._ffmpeg = ffmpeg

    def validate(self, source: Path, progress: ValidationProgress, cancel_event: Event) -> MediaQualityReport:
        progress(0.02, "Inspecting final media metadata…")
        payload = self._probe(source)
        streams = payload.get("streams", [])
        format_data = payload.get("format", {})
        video = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
        audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), {})
        duration = self._number(format_data.get("duration"), 0.0)
        checks = list(self._metadata_checks(source, format_data, video, audio, duration))
        progress(0.1, "Scanning the complete video for decode errors…")
        decode_detail = self._decode_scan(source, duration, progress, cancel_event)
        checks.append(QualityCheck("decode", CheckSeverity.PASS if decode_detail is None else CheckSeverity.ERROR, "Full decode scan", decode_detail or "Every packet decoded without a fatal FFmpeg error."))
        return MediaQualityReport(
            source.resolve(), datetime.now(timezone.utc).isoformat(), duration, source.stat().st_size,
            str(format_data.get("format_long_name") or format_data.get("format_name") or source.suffix),
            str(video.get("codec_name")) if video else None, str(audio.get("codec_name")) if audio else None,
            self._integer(video.get("width")), self._integer(video.get("height")), self._rate(video.get("avg_frame_rate")),
            self._integer(audio.get("sample_rate")), self._integer(audio.get("channels")), tuple(checks),
        )

    def _probe(self, source: Path) -> dict[str, object]:
        result = subprocess.run([str(self._ffprobe), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", "--", str(source)], capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), check=False)
        if result.returncode != 0:
            raise MediaImportError(f"FFprobe could not inspect the final video: {result.stderr.strip() or 'unknown error'}")
        try:
            payload = json.loads(result.stdout)
            return payload if isinstance(payload, dict) else {}
        except json.JSONDecodeError as exc:
            raise MediaImportError(f"FFprobe returned invalid quality-control metadata: {exc}") from exc

    def _decode_scan(self, source: Path, duration: float, progress: ValidationProgress, cancel_event: Event) -> str | None:
        process = subprocess.Popen([str(self._ffmpeg), "-hide_banner", "-nostdin", "-v", "error", "-xerror", "-i", str(source), "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-", "-progress", "pipe:1"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        assert process.stdout is not None
        while True:
            if cancel_event.is_set():
                process.terminate()
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=3)
                raise ExtractionCancelledError("Final quality validation was cancelled.")
            line = process.stdout.readline()
            if line:
                key, separator, value = line.strip().partition("=")
                if separator and key in {"out_time_us", "out_time_ms"}:
                    ratio = int(value or 0) / max(1, round(duration * 1_000_000))
                    progress(0.1 + min(0.89, max(0.0, ratio * 0.89)), f"Decode scan {min(100, ratio * 100):.0f}%")
            if process.poll() is not None: break
        errors = process.stderr.read().strip() if process.stderr else ""
        return None if process.returncode == 0 else (errors.splitlines()[-1] if errors else "FFmpeg reported a fatal decode error.")

    def _metadata_checks(self, source: Path, fmt: dict, video: dict, audio: dict, duration: float) -> tuple[QualityCheck, ...]:
        checks: list[QualityCheck] = []
        checks.append(QualityCheck("video_stream", CheckSeverity.PASS if video else CheckSeverity.ERROR, "Video stream", "A video stream is present." if video else "No video stream was found."))
        checks.append(QualityCheck("audio_stream", CheckSeverity.PASS if audio else CheckSeverity.ERROR, "Audio stream", "An audio stream is present." if audio else "No audio stream was found."))
        checks.append(QualityCheck("duration", CheckSeverity.PASS if duration > 0 else CheckSeverity.ERROR, "Duration", f"Duration is {duration:.3f} seconds." if duration > 0 else "Container duration is missing or zero."))
        width, height = self._integer(video.get("width")), self._integer(video.get("height"))
        resolution_ok = bool(width and height and width >= 1280 and height >= 720)
        checks.append(QualityCheck("resolution", CheckSeverity.PASS if resolution_ok else CheckSeverity.WARNING, "Resolution", f"Output resolution is {width}x{height}." if width and height else "Resolution metadata is missing."))
        pixel = str(video.get("pix_fmt") or "")
        checks.append(QualityCheck("pixel_format", CheckSeverity.PASS if pixel == "yuv420p" else CheckSeverity.WARNING, "Pixel format", f"Pixel format is {pixel or 'unknown'}; yuv420p provides broad compatibility."))
        sample_rate = self._integer(audio.get("sample_rate"))
        checks.append(QualityCheck("sample_rate", CheckSeverity.PASS if sample_rate == 48000 else CheckSeverity.WARNING, "Audio sample rate", f"Audio sample rate is {sample_rate or 'unknown'} Hz; the project delivery target is 48000 Hz."))
        size_ok = source.stat().st_size >= 1024
        checks.append(QualityCheck("file_size", CheckSeverity.PASS if size_ok else CheckSeverity.ERROR, "File size", f"Final file size is {source.stat().st_size} bytes."))
        return tuple(checks)

    @staticmethod
    def _integer(value: object) -> int | None:
        try: return int(value) if value not in (None, "", "N/A") else None
        except (TypeError, ValueError): return None

    @staticmethod
    def _number(value: object, default: float) -> float:
        try: return float(value)
        except (TypeError, ValueError): return default

    @staticmethod
    def _rate(value: object) -> float | None:
        try:
            rate = float(Fraction(str(value)))
            return rate if rate > 0 else None
        except (ValueError, ZeroDivisionError): return None
