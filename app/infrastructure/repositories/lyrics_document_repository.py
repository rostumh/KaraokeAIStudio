from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from app.domain.models.lyrics_document import LyricsDocument


class LyricsDocumentRepository:
    """Atomic persistence for the manually edited lyrics/timing document."""

    def save(self, document: LyricsDocument, destination: Path) -> Path:
        destination.mkdir(parents=True, exist_ok=True)
        path = destination / f"{document.source_path.stem}.lyrics.json"
        temporary = path.with_name(path.name + ".part")
        payload = {
            "schema_version": 1,
            "source_path": str(document.source_path),
            "language": document.language,
            "duration_seconds": document.duration_seconds,
            "revision": document.revision,
            "words": [asdict(word) for word in document.words],
        }
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(temporary, path)
        return path
