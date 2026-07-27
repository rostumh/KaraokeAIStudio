from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Protocol

TranslationProgress = Callable[[float, str], None]


class TextTranslator(Protocol):
    @property
    def engine_name(self) -> str: ...
    def installed_pairs(self) -> tuple[tuple[str, str], ...]: ...
    def translate_lines(self, lines: tuple[str, ...], source_language: str, target_language: str, progress: TranslationProgress, cancel_event: Event) -> tuple[str, ...]:
        """Translate aligned text lines without changing their count or order."""
