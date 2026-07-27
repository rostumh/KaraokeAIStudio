from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path
from threading import Event

from app.application.errors import MediaImportError
from app.application.ports.audio_extractor import ProgressCallback
from app.domain.models.audio_extraction import AudioExtractionRequest, AudioExtractionResult, AudioFormat

LOGGER = logging.getLogger(__name__)


class ExtractionCancelledError(MediaImportError):
    """Raised after a user-requested extraction cancellation."""


class FFmpegAudioExtractor:
    """FFmpeg adapter with atomic output, machine-readable progress, and cancellation."""

    def __init__(self, executable: Path) -> None:
        self._executable = executable

    def extract(
        self,
        request: AudioExtractionRequest,
        progress: ProgressCallback,
        cancel_event: Event,
    ) -> AudioExtractionResult:
        temporary = request.output_path.with_name(request.output_path.name + ".part")
        temporary.unlink(missing_ok=True)
        command = self._command(request, temporary)
        started = time.monotonic()
        LOGGER.info("Starting audio extraction: source=%s output=%s", request.source_path, request.output_path)
        process: subprocess.Popen[str] | None = None
        stderr_lines: list[str] = []
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            assert process.stdout is not None
            while True:
                if cancel_event.is_set():
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    raise ExtractionCancelledError("Audio extraction was cancelled.")
                line = process.stdout.readline()
                if line:
                    key, separator, value = line.strip().partition("=")
                    if separator and key in {"out_time_us", "out_time_ms"}:
                        microseconds = int(value or 0)
                        duration_us = max(1, round(request.duration_seconds * 1_000_000))
                        progress(min(0.99, max(0.0, microseconds / duration_us)))
                    elif key == "progress" and value == "end":
                        progress(1.0)
                if process.poll() is not None:
                    break
                if not line:
                    time.sleep(0.02)
            if process.stderr is not None:
                stderr_lines = process.stderr.read().splitlines()
            if process.returncode != 0:
                detail = stderr_lines[-1] if stderr_lines else "FFmpeg returned an unknown encoding error."
                raise MediaImportError(f"Audio extraction failed: {detail}")
            if not temporary.is_file() or temporary.stat().st_size == 0:
                raise MediaImportError("FFmpeg completed without producing a valid audio file.")
            if request.output_path.exists():
                if not request.overwrite:
                    raise MediaImportError(f"The output file already exists: {request.output_path}")
                request.output_path.unlink()
            os.replace(temporary, request.output_path)
            elapsed = time.monotonic() - started
            LOGGER.info("Audio extraction completed in %.2fs: %s", elapsed, request.output_path)
            return AudioExtractionResult(request.output_path, request.output_path.stat().st_size, elapsed, request.output_format)
        except Exception:
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=3)
            temporary.unlink(missing_ok=True)
            LOGGER.exception("Audio extraction did not complete")
            raise

    def _command(self, request: AudioExtractionRequest, temporary: Path) -> list[str]:
        codec_args: list[str]
        muxer: str
        if request.output_format == AudioFormat.WAV_PCM_16:
            codec_args, muxer = ["-c:a", "pcm_s16le"], "wav"
        elif request.output_format == AudioFormat.WAV_PCM_24:
            codec_args, muxer = ["-c:a", "pcm_s24le"], "wav"
        elif request.output_format == AudioFormat.FLAC:
            codec_args, muxer = ["-c:a", "flac", "-compression_level", "8"], "flac"
        else:
            codec_args, muxer = ["-c:a", "libmp3lame", "-b:a", f"{request.mp3_bitrate_kbps}k"], "mp3"
        command = [
            str(self._executable), "-hide_banner", "-nostdin", "-loglevel", "error",
            "-y", "-i", str(request.source_path), "-map", f"0:{request.stream_index}",
            "-vn", "-sn", "-dn", *codec_args,
        ]
        if request.sample_rate is not None:
            command.extend(("-ar", str(request.sample_rate)))
        if request.channels is not None:
            command.extend(("-ac", str(request.channels)))
        command.extend(("-map_metadata", "-1", "-progress", "pipe:1", "-f", muxer, str(temporary)))
        return command
