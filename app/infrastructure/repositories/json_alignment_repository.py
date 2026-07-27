from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from app.domain.models.alignment import AlignedTranscript


class JsonAlignmentRepository:
    """Atomic UTF-8 persistence for canonical word-level timing data."""

    def save(self, alignment: AlignedTranscript, destination: Path) -> Path:
        path = destination / f"{alignment.source_path.stem}.alignment.json"
        temporary = path.with_name(path.name + ".part")
        payload = {
            "schema_version": 1,
            "source_path": str(alignment.source_path),
            "language": alignment.transcript.language,
            "duration_seconds": alignment.duration_seconds,
            "alignment_model": alignment.alignment_model,
            "words": [asdict(word) for word in alignment.words],
        }
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(temporary, path)
        return path
