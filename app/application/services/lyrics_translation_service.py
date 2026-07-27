from __future__ import annotations

from pathlib import Path
from threading import Event

from app.application.errors import MediaImportError
from app.application.ports.text_translator import TextTranslator, TranslationProgress
from app.domain.models.lyrics_document import LyricsDocument
from app.domain.models.translation import TranslatedLine, TranslationDocument, TranslationOptions
from app.infrastructure.repositories.translation_repository import TranslationRepository


class LyricsTranslationService:
    """Groups timed words into phrases, translates text, and preserves timing boundaries."""

    def __init__(self, translator: TextTranslator, repository: TranslationRepository) -> None:
        self._translator = translator
        self._repository = repository

    def translate(self, lyrics: LyricsDocument, options: TranslationOptions, destination: Path, progress: TranslationProgress, cancel_event: Event) -> tuple[TranslationDocument, Path]:
        if options.source_language == options.target_language:
            raise MediaImportError("Source and target languages must be different.")
        pairs = set(self._translator.installed_pairs())
        if (options.source_language, options.target_language) not in pairs:
            raise MediaImportError(f"No installed offline model supports {options.source_language} → {options.target_language}.")
        grouped = self._group_by_segment(lyrics)
        source_lines = tuple(text for _, _, text in grouped)
        translated = self._translator.translate_lines(source_lines, options.source_language, options.target_language, progress, cancel_event)
        if len(translated) != len(grouped):
            raise MediaImportError("Translation engine returned a different number of lyric lines.")
        lines = tuple(TranslatedLine(index, start, end, source, target.strip()) for index, ((start, end, source), target) in enumerate(zip(grouped, translated, strict=True)))
        if any(not line.translated_text for line in lines):
            raise MediaImportError("Translation produced one or more empty lyric lines.")
        document = TranslationDocument(lyrics.source_path, options.source_language, options.target_language, self._translator.engine_name, lines)
        destination.mkdir(parents=True, exist_ok=True)
        return document, self._repository.save(document, destination)

    @staticmethod
    def _group_by_segment(lyrics: LyricsDocument) -> tuple[tuple[float, float, str], ...]:
        groups: list[tuple[float, float, str]] = []
        current_segment: int | None = None
        words = []
        start = end = 0.0
        for word in lyrics.words:
            if current_segment is not None and word.segment_id != current_segment:
                groups.append((start, end, " ".join(words)))
                words = []
            if not words:
                start = word.start_seconds
            current_segment = word.segment_id
            end = word.end_seconds
            words.append(word.text)
        if words:
            groups.append((start, end, " ".join(words)))
        return tuple(groups)
