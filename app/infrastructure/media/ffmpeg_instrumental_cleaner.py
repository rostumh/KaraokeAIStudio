from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path
from threading import Event

from app.application.errors import MediaImportError
from app.application.ports.instrumental_cleaner import CleanupProgress
from app.domain.models.instrumental_cleanup import CleanupOutputFormat, InstrumentalCleanupRequest, InstrumentalCleanupResult
from app.infrastructure.media.ffmpeg_audio_extractor import ExtractionCancelledError

LOGGER = logging.getLogger(__name__)


class FFmpegInstrumentalCleaner:
    """Non-destructive FFmpeg cleanup pipeline with deterministic filters and atomic output."""

    def __init__(self, executable: Path) -> None:
        self._executable = executable

    def clean(self, request: InstrumentalCleanupRequest, progress: CleanupProgress, cancel_event: Event) -> InstrumentalCleanupResult:
        temporary = request.output_path.with_name(request.output_path.name + ".part")
        temporary.unlink(missing_ok=True)
        process: subprocess.Popen[str] | None = None
        started = time.monotonic()
        try:
            process = subprocess.Popen(self._command(request, temporary), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            assert process.stdout is not None
            while True:
                if cancel_event.is_set():
                    process.terminate()
                    try: process.wait(timeout=3)
                    except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=3)
                    raise ExtractionCancelledError("Instrumental cleanup was cancelled.")
                line = process.stdout.readline()
                if line:
                    key, separator, value = line.strip().partition("=")
                    if separator and key in {"out_time_us", "out_time_ms"}:
                        duration_us = max(1, round(request.duration_seconds * 1_000_000))
                        progress(min(0.99, max(0.0, int(value or 0) / duration_us)))
                    elif key == "progress" and value == "end": progress(1.0)
                if process.poll() is not None: break
                if not line: time.sleep(0.02)
            errors = process.stderr.read().splitlines() if process.stderr else []
            if process.returncode != 0:
                detail = errors[-1] if errors else "FFmpeg returned an unknown filter error."
                raise MediaImportError(f"Instrumental cleanup failed: {detail}")
            if not temporary.is_file() or temporary.stat().st_size == 0:
                raise MediaImportError("Cleanup completed without producing a valid audio file.")
            if request.output_path.exists():
                if not request.overwrite: raise MediaImportError(f"The output file already exists: {request.output_path}")
                request.output_path.unlink()
            os.replace(temporary, request.output_path)
            elapsed = time.monotonic() - started
            LOGGER.info("Instrumental cleanup completed in %.2fs: %s", elapsed, request.output_path)
            return InstrumentalCleanupResult(request.output_path, request.output_path.stat().st_size, elapsed, request.settings)
        except Exception:
            if process is not None and process.poll() is None: process.kill(); process.wait(timeout=3)
            temporary.unlink(missing_ok=True)
            LOGGER.exception("Instrumental cleanup did not complete")
            raise

    def _filter_chain(self, request: InstrumentalCleanupRequest) -> str:
        settings = request.settings
        filters = [
            f"highpass=f={settings.highpass_hz}",
            f"lowpass=f={settings.lowpass_hz}",
            f"afftdn=nr={settings.noise_reduction_db:.2f}:nf={settings.noise_floor_db:.2f}:tn=1:gs=8",
            f"loudnorm=I={settings.target_lufs:.2f}:LRA={settings.loudness_range:.2f}:TP={settings.true_peak_db:.2f}",
        ]
        if settings.limiter:
            limit = 10 ** (settings.true_peak_db / 20.0)
            filters.append(f"alimiter=limit={limit:.6f}:attack=5:release=50:level=0")
        return ",".join(filters)

    def _command(self, request: InstrumentalCleanupRequest, temporary: Path) -> list[str]:
        if request.settings.output_format == CleanupOutputFormat.FLAC:
            codec = ["-c:a", "flac", "-compression_level", "8"]; muxer = "flac"
        else:
            codec = ["-c:a", "pcm_s24le"]; muxer = "wav"
        return [str(self._executable), "-hide_banner", "-nostdin", "-loglevel", "error", "-y", "-i", str(request.source_path), "-map", f"0:{request.stream_index}", "-vn", "-sn", "-dn", "-af", self._filter_chain(request), *codec, "-ar", "48000", "-map_metadata", "-1", "-progress", "pipe:1", "-f", muxer, str(temporary)]
