from __future__ import annotations

from app.application.errors import MediaImportError
from app.domain.models.lyrics_document import EditableWord, LyricsDocument


class LyricsEditingService:
    """Pure validation and transformation rules for editable karaoke words."""

    @staticmethod
    def replace_word(document: LyricsDocument, row: int, word: EditableWord) -> LyricsDocument:
        words = list(document.words)
        if not 0 <= row < len(words):
            raise MediaImportError("The selected lyric row no longer exists.")
        words[row] = word
        return LyricsEditingService.validate(LyricsDocument(document.source_path, document.language, document.duration_seconds, tuple(words), document.revision + 1))

    @staticmethod
    def shift_words(document: LyricsDocument, rows: tuple[int, ...], delta_seconds: float) -> LyricsDocument:
        selected = set(rows)
        words = [
            EditableWord(w.word_id, w.segment_id, w.text, w.start_seconds + delta_seconds, w.end_seconds + delta_seconds, w.probability)
            if index in selected else w
            for index, w in enumerate(document.words)
        ]
        return LyricsEditingService.validate(LyricsDocument(document.source_path, document.language, document.duration_seconds, tuple(words), document.revision + 1))

    @staticmethod
    def scale_interval(document: LyricsDocument, rows: tuple[int, ...], factor: float) -> LyricsDocument:
        if factor <= 0:
            raise MediaImportError("Timing scale must be positive.")
        selected = set(rows)
        if not selected:
            return document
        anchor = min(document.words[row].start_seconds for row in selected)
        words = []
        for index, word in enumerate(document.words):
            if index in selected:
                start = anchor + (word.start_seconds - anchor) * factor
                end = anchor + (word.end_seconds - anchor) * factor
                words.append(EditableWord(word.word_id, word.segment_id, word.text, start, end, word.probability))
            else:
                words.append(word)
        return LyricsEditingService.validate(LyricsDocument(document.source_path, document.language, document.duration_seconds, tuple(words), document.revision + 1))

    @staticmethod
    def validate(document: LyricsDocument) -> LyricsDocument:
        if not document.words:
            raise MediaImportError("The lyrics document contains no words.")
        previous_end = 0.0
        normalized: list[EditableWord] = []
        for index, word in enumerate(document.words):
            text = word.text.strip()
            if not text:
                raise MediaImportError(f"Word {index + 1} cannot be empty.")
            start = word.start_seconds
            end = word.end_seconds
            if start < 0 or end > document.duration_seconds:
                raise MediaImportError(f"Word {index + 1} is outside the media duration.")
            if start < previous_end - 0.0005:
                raise MediaImportError(f"Word {index + 1} overlaps the previous word.")
            if end - start < 0.01:
                raise MediaImportError(f"Word {index + 1} must be at least 10 ms long.")
            normalized.append(EditableWord(index, word.segment_id, text, start, end, min(1.0, max(0.0, word.probability))))
            previous_end = end
        return LyricsDocument(document.source_path, document.language, document.duration_seconds, tuple(normalized), document.revision)
