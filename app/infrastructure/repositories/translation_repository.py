from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from app.domain.models.translation import TranslationDocument


class TranslationRepository:
    """Atomic UTF-8 persistence for translated lyric lines and source timing."""

    def save(self, document: TranslationDocument, destination: Path) -> Path:
        path = destination / f"{document.source_path.stem}.{document.target_language}.translation.json"
        temporary = path.with_name(path.name + ".part")
        payload = asdict(document)
        payload["source_path"] = str(document.source_path)
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, path)
        return path
