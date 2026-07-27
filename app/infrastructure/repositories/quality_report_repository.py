from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from app.domain.models.quality_validation import MediaQualityReport


class QualityReportRepository:
    """Persists machine-readable and auditable final-delivery reports."""

    def save(self, report: MediaQualityReport, destination: Path) -> Path:
        path = destination / f"{report.source_path.stem}.quality-report.json"
        temporary = path.with_name(path.name + ".part")
        payload = asdict(report)
        payload["source_path"] = str(report.source_path)
        payload["passed"] = report.passed
        payload["warning_count"] = report.warning_count
        for check in payload["checks"]:
            severity = check["severity"]
            check["severity"] = severity.value if hasattr(severity, "value") else severity
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, path)
        return path
