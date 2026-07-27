from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from threading import Event

from app.application.errors import MediaImportError
from app.application.ports.batch_job_executor import BatchProgress
from app.domain.models.batch import BatchJob, BatchOperation
from app.infrastructure.media.ffmpeg_audio_extractor import ExtractionCancelledError
from app.infrastructure.media.ffmpeg_quality_validator import FFmpegQualityValidator
from app.infrastructure.repositories.quality_report_repository import QualityReportRepository


class FFmpegBatchJobExecutor:
    """Executes stable FFmpeg-based batch operations without touching Qt."""

    def __init__(self, ffmpeg: Path, ffprobe: Path) -> None:
        self._ffmpeg = ffmpeg
        self._validator = FFmpegQualityValidator(ffprobe, ffmpeg)
        self._reports = QualityReportRepository()

    def execute(self, job: BatchJob, progress: BatchProgress, cancel_event: Event) -> str:
        if job.operation == BatchOperation.VALIDATE_FINAL:
            report = self._validator.validate(job.source_path, progress, cancel_event)
            self._reports.save(report, job.output_path.parent)
            if not report.passed:
                raise MediaImportError("Final video failed one or more required quality checks.")
            return f"Validated with {report.warning_count} warning(s)"
        return self._extract(job, progress, cancel_event)

    def _extract(self, job: BatchJob, progress: BatchProgress, cancel_event: Event) -> str:
        temporary = job.output_path.with_name(job.output_path.name + ".part")
        temporary.unlink(missing_ok=True)
        process = subprocess.Popen([
            str(self._ffmpeg), "-hide_banner", "-nostdin", "-loglevel", "error", "-y",
            "-i", str(job.source_path), "-map", "0:a:0", "-vn", "-sn", "-dn",
            "-c:a", "pcm_s24le", "-ar", "48000", "-map_metadata", "-1",
            "-progress", "pipe:1", "-f", "wav", str(temporary),
        ], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        assert process.stdout is not None
        try:
            while True:
                if cancel_event.is_set():
                    process.terminate()
                    try: process.wait(timeout=3)
                    except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=3)
                    raise ExtractionCancelledError("Batch job was cancelled.")
                line = process.stdout.readline()
                if line:
                    key, separator, value = line.strip().partition("=")
                    if separator and key in {"out_time_us", "out_time_ms"}:
                        microseconds = int(value or 0)
                        progress(min(0.95, microseconds / max(1, microseconds + 5_000_000)), "Extracting 24-bit audio")
                    elif key == "progress" and value == "end": progress(1.0, "Audio extraction complete")
                if process.poll() is not None: break
                if not line: time.sleep(0.02)
            error = process.stderr.read().strip() if process.stderr else ""
            if process.returncode != 0:
                raise MediaImportError(f"Batch audio extraction failed: {error.splitlines()[-1] if error else 'unknown FFmpeg error'}")
            if not temporary.is_file() or temporary.stat().st_size == 0:
                raise MediaImportError("Batch extraction did not produce a valid WAV file.")
            if job.output_path.exists(): job.output_path.unlink()
            os.replace(temporary, job.output_path)
            return f"Created {job.output_path.name}"
        except Exception:
            if process.poll() is None: process.kill(); process.wait(timeout=3)
            temporary.unlink(missing_ok=True)
            raise
