from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import LoggingSettings

def configure_logging(log_dir: Path, settings: LoggingSettings) -> None:
    """Configure deterministic console and bounded file logging."""
    log_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    file_handler = RotatingFileHandler(log_dir / "karaoke-ai-studio.log", maxBytes=settings.max_bytes, backupCount=settings.backup_count, encoding="utf-8", delay=True)
    stream_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter); stream_handler.setFormatter(formatter)
    root = logging.getLogger(); root.handlers.clear(); root.setLevel(getattr(logging, settings.level)); root.addHandler(file_handler); root.addHandler(stream_handler)
