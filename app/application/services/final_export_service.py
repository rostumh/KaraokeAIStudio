from __future__ import annotations

from pathlib import Path
from threading import Event

from app.application.errors import MediaImportError
from app.application.ports.media_quality_validator import MediaQualityValidator, ValidationProgress
from app.domain.models.quality_validation import MediaQualityReport
from app.infrastructure.repositories.quality_report_repository import QualityReportRepository


class FinalExportService:
    """Runs quality control and persists a report beside an approved export."""

    def __init__(self, validator: MediaQualityValidator, repository: QualityReportRepository) -> None:
        self._validator = validator
        self._repository = repository

    def validate(self, source: Path, destination: Path, progress: ValidationProgress, cancel_event: Event) -> tuple[MediaQualityReport, Path]:
        normalized = source.expanduser().resolve(strict=False)
        if not normalized.is_file():
            raise MediaImportError(f"The rendered video does not exist: {normalized}")
        if normalized.suffix.lower() not in {".mp4", ".mkv", ".mov"}:
            raise MediaImportError("Final quality validation requires a rendered video file.")
        report = self._validator.validate(normalized, progress, cancel_event)
        destination.mkdir(parents=True, exist_ok=True)
        return report, self._repository.save(report, destination)
