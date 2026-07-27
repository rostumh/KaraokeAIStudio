from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal

from app.application.services.lyrics_editing_service import LyricsEditingService
from app.domain.models.lyrics_document import EditableWord, LyricsDocument
from app.ui.formatters import format_duration


class EditableLyricsModel(QAbstractTableModel):
    """Editable table model; every accepted change replaces the immutable document."""

    documentChanged = Signal(object)
    validationFailed = Signal(str)
    editRequested = Signal(object, object, str)
    HEADERS = ("#", "Start", "End", "Word", "Confidence")

    def __init__(self) -> None:
        super().__init__()
        self._document: LyricsDocument | None = None

    @property
    def document(self) -> LyricsDocument | None:
        return self._document

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() or self._document is None else len(self._document.words)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if not index.isValid() or self._document is None:
            return None
        word = self._document.words[index.row()]
        if role in {Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole}:
            if role == Qt.ItemDataRole.EditRole:
                values = (word.word_id + 1, word.start_seconds, word.end_seconds, word.text, word.probability)
            else:
                values = (word.word_id + 1, format_duration(word.start_seconds), format_duration(word.end_seconds), word.text, f"{word.probability * 100:.1f}%")
            return values[index.column()]
        if role == Qt.ItemDataRole.BackgroundRole and word.probability < 0.55:
            from PySide6.QtGui import QColor
            return QColor("#4a2b24")
        if role == Qt.ItemDataRole.ToolTipRole and word.probability < 0.55:
            return "Low-confidence word: review text and timing."
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)
        return flags | Qt.ItemFlag.ItemIsEditable if index.column() in {1, 2, 3} else flags

    def setData(self, index: QModelIndex, value: object, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if role != Qt.ItemDataRole.EditRole or self._document is None or index.column() not in {1, 2, 3}:
            return False
        old = self._document.words[index.row()]
        try:
            if index.column() == 1:
                replacement = EditableWord(old.word_id, old.segment_id, old.text, float(value), old.end_seconds, old.probability)
            elif index.column() == 2:
                replacement = EditableWord(old.word_id, old.segment_id, old.text, old.start_seconds, float(value), old.probability)
            else:
                replacement = EditableWord(old.word_id, old.segment_id, str(value), old.start_seconds, old.end_seconds, old.probability)
            updated = LyricsEditingService.replace_word(self._document, index.row(), replacement)
        except (ValueError, TypeError, RuntimeError) as exc:
            self.validationFailed.emit(str(exc))
            return False
        label = "Edit word" if index.column() == 3 else "Adjust word timing"
        self.editRequested.emit(self._document, updated, label)
        return True

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)

    def set_document(self, document: LyricsDocument) -> None:
        self.beginResetModel()
        self._document = document
        self.endResetModel()
        self.documentChanged.emit(document)
