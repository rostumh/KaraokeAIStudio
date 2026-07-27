from __future__ import annotations

import importlib.util
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from threading import Event, Thread

from app.application.errors import DependencyUnavailableError, MediaImportError
from app.application.ports.source_separator import StatusCallback
from app.domain.models.separation import ComputeDevice, SeparationMode, SeparationRequest, SeparationResult, StemFormat
from app.infrastructure.media.ffmpeg_audio_extractor import ExtractionCancelledError

LOGGER = logging.getLogger(__name__)


def detect_compute_devices() -> tuple[str, ...]:
    devices = ["cpu"]
    try:
        import torch
        if torch.cuda.is_available():
            devices.insert(0, "cuda")
    except ImportError:
        pass
    return tuple(devices)


class DemucsSourceSeparator:
    """Isolated Demucs CLI adapter with cancellation, output validation, and clean process trees."""

    def __init__(self, python_executable: Path | None = None) -> None:
        self._python = python_executable or Path(sys.executable)
        self._runner: Path | None = None
        if getattr(sys, "frozen", False):
            candidate = Path(sys.executable).with_name("DemucsRunner.exe")
            if not candidate.is_file():
                raise DependencyUnavailableError("The built-in vocal separation engine is missing. Reinstall Karaoke AI Studio.")
            self._runner = candidate
        elif importlib.util.find_spec("demucs") is None:
            raise DependencyUnavailableError("The vocal separation engine is not installed in this development environment.")

    def separate(self, request: SeparationRequest, status: StatusCallback, cancel_event: Event) -> SeparationResult:
        device = self._resolve_device(request.device)
        command = self._command(request, device)
        started = time.monotonic()
        status(f"Loading {request.model_name} on {device.upper()}…")
        LOGGER.info("Starting Demucs: model=%s device=%s source=%s", request.model_name, device, request.source_path)
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        if os.name == "nt": flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", creationflags=flags, bufsize=1)
        lines: list[str] = []
        assert process.stdout is not None
        try:
            while True:
                if cancel_event.is_set():
                    process.terminate()
                    try: process.wait(timeout=5)
                    except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=3)
                    raise ExtractionCancelledError("Vocal separation was cancelled.")
                line = process.stdout.readline()
                if line:
                    clean = line.strip(); lines.append(clean)
                    if clean: status(clean[-180:])
                if process.poll() is not None: break
                if not line: time.sleep(0.05)
            if process.returncode != 0:
                detail = next((line for line in reversed(lines) if line), "Demucs returned an unknown error.")
                if "out of memory" in detail.lower() or "cuda" in detail.lower() and "memory" in detail.lower():
                    detail += " Reduce segment length, use fewer shifts, or select CPU."
                raise MediaImportError(f"Vocal separation failed: {detail}")
            output_dir = request.output_root / request.model_name / request.source_path.stem
            extension = ".flac" if request.stem_format == StemFormat.FLAC else ".wav"
            expected = ("vocals", "no_vocals") if request.mode == SeparationMode.VOCALS else ("vocals", "drums", "bass", "other")
            stems = tuple(output_dir / f"{name}{extension}" for name in expected)
            missing = [path.name for path in stems if not path.is_file() or path.stat().st_size == 0]
            if missing: raise MediaImportError(f"Demucs completed but required stems are missing: {', '.join(missing)}")
            elapsed = time.monotonic() - started
            status("Separation complete")
            LOGGER.info("Demucs completed in %.2fs: %s", elapsed, output_dir)
            return SeparationResult(request.source_path, output_dir, stems, request.model_name, device, elapsed)
        except Exception:
            if process.poll() is None: process.kill(); process.wait(timeout=3)
            LOGGER.exception("Demucs separation did not complete")
            raise

    def _resolve_device(self, requested: ComputeDevice) -> str:
        available = detect_compute_devices()
        if requested == ComputeDevice.AUTO: return available[0]
        if requested.value not in available: raise MediaImportError(f"Requested compute device '{requested.value}' is unavailable.")
        return requested.value

    def _command(self, request: SeparationRequest, device: str) -> list[str]:
        runner = getattr(self, "_runner", None)
        python = getattr(self, "_python", Path(sys.executable))
        command = ([str(runner)] if runner is not None else [str(python), "-m", "demucs"]) + ["--name", request.model_name, "--device", device, "--out", str(request.output_root), "--shifts", str(request.shifts), "--overlap", str(request.overlap), "--jobs", "0", "--clip-mode", "rescale"]
        if request.segment_seconds is not None:
            segment = request.segment_seconds
            if request.model_name.startswith("htdemucs"):
                segment = min(segment, 7.8)
            command.extend(("--segment", str(segment)))
        if request.mode == SeparationMode.VOCALS: command.extend(("--two-stems", "vocals"))
        if request.stem_format == StemFormat.FLAC: command.append("--flac")
        else: command.append("--int24")
        command.extend(("--", str(request.source_path)))
        return command
