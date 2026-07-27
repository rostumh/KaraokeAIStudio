from __future__ import annotations

from PySide6.QtGui import QUndoCommand

from app.application.services.lyrics_editing_service import LyricsEditingService
from app.domain.models.lyrics_document import LyricsDocument
from app.ui.models.editable_lyrics_model import EditableLyricsModel


class ReplaceDocumentCommand(QUndoCommand):
    def __init__(self, model: EditableLyricsModel, before: LyricsDocument, after: LyricsDocument, description: str) -> None:
        super().__init__(description)
        self._model, self._before, self._after = model, before, after

    def redo(self) -> None:
        self._model.set_document(self._after)

    def undo(self) -> None:
        self._model.set_document(self._before)


class ShiftWordsCommand(ReplaceDocumentCommand):
    def __init__(self, model: EditableLyricsModel, rows: tuple[int, ...], delta_seconds: float) -> None:
        before = model.document
        if before is None:
            raise RuntimeError("No lyrics document is loaded.")
        after = LyricsEditingService.shift_words(before, rows, delta_seconds)
        super().__init__(model, before, after, f"Shift {len(rows)} words by {delta_seconds:+.3f}s")


class ScaleWordsCommand(ReplaceDocumentCommand):
    def __init__(self, model: EditableLyricsModel, rows: tuple[int, ...], factor: float) -> None:
        before = model.document
        if before is None:
            raise RuntimeError("No lyrics document is loaded.")
        after = LyricsEditingService.scale_interval(before, rows, factor)
        super().__init__(model, before, after, f"Scale {len(rows)} word timings")
