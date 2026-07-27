from __future__ import annotations

import os
from pathlib import Path


def atomic_text_write(path: Path, content: str) -> Path:
    temporary = path.with_name(path.name + ".part")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)
    return path


def escape_ass_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", "\\N")
