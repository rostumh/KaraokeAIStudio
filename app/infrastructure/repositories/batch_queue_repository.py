from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from app.domain.models.batch import BatchJob, BatchOperation, BatchStatus


class BatchQueueRepository:
    """Atomic persistence of queue order and terminal job history."""

    def save(self, jobs: tuple[BatchJob, ...], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".part")
        payload = []
        for job in jobs:
            item = asdict(job)
            item["operation"] = job.operation.value
            item["status"] = job.status.value
            item["source_path"] = str(job.source_path)
            item["output_path"] = str(job.output_path)
            payload.append(item)
        temporary.write_text(
            json.dumps({"schema_version": 1, "jobs": payload}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, path)

    def load(self, path: Path) -> tuple[BatchJob, ...]:
        if not path.is_file():
            return ()
        payload = json.loads(path.read_text(encoding="utf-8"))
        jobs = []
        for item in payload.get("jobs", []):
            status = BatchStatus(str(item["status"]))
            status = BatchStatus.QUEUED if status == BatchStatus.RUNNING else status
            jobs.append(
                BatchJob(
                    str(item["job_id"]),
                    BatchOperation(str(item["operation"])),
                    Path(item["source_path"]),
                    Path(item["output_path"]),
                    status,
                    float(item["progress"]),
                    str(item["message"]),
                    int(item["attempts"]),
                    str(item["created_utc"]),
                    item.get("started_utc"),
                    item.get("finished_utc"),
                )
            )
        return tuple(jobs)
