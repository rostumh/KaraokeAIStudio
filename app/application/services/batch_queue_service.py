from __future__ import annotations

from pathlib import Path

from app.application.errors import MediaImportError
from app.domain.models.batch import BatchJob, BatchOperation, BatchStatus


class BatchQueueService:
    """Pure queue policy for creation, retry, cancellation, and duplicate prevention."""

    @staticmethod
    def add_jobs(existing: tuple[BatchJob, ...], sources: tuple[Path, ...], operation: BatchOperation, output_root: Path) -> tuple[BatchJob, ...]:
        output_root.mkdir(parents=True, exist_ok=True)
        jobs = list(existing)
        identities = {(job.operation, job.source_path) for job in jobs if job.status in {BatchStatus.QUEUED, BatchStatus.RUNNING}}
        for source in sources:
            normalized = source.expanduser().resolve(strict=False)
            if not normalized.is_file():
                raise MediaImportError(f"Batch source does not exist: {normalized}")
            if (operation, normalized) in identities:
                continue
            output = BatchQueueService.output_for(normalized, operation, output_root)
            jobs.append(BatchJob.create(operation, normalized, output))
            identities.add((operation, normalized))
        return tuple(jobs)

    @staticmethod
    def output_for(source: Path, operation: BatchOperation, root: Path) -> Path:
        if operation == BatchOperation.EXTRACT_WAV24:
            return root / f"{source.stem}_audio.wav"
        return root / f"{source.stem}.quality-report.json"

    @staticmethod
    def retry(job: BatchJob) -> BatchJob:
        if job.status not in {BatchStatus.FAILED, BatchStatus.CANCELLED}:
            raise MediaImportError("Only failed or cancelled jobs can be retried.")
        return job.update(status=BatchStatus.QUEUED, progress=0.0, message="Queued for retry", started_utc=None, finished_utc=None)
