from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from app.domain.models.alignment import AlignedTranscript
from app.ui.formatters import format_duration


class WordTimingTableModel(QAbstractTableModel):
    HEADERS = ("#", "Start", "End", "Word", "Confidence")

    def __init__(self) -> None:
        super().__init__()
        self._alignment: AlignedTranscript | None = None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() or self._alignment is None else len(self._alignment.words)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if role != Qt.ItemDataRole.DisplayRole or not index.isValid() or self._alignment is None:
            return None
        word = self._alignment.words[index.row()]
        values = (word.word_id + 1, format_duration(word.start_seconds), format_duration(word.end_seconds), word.text, f"{word.probability * 100:.1f}%")
        return values[index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)

    def set_alignment(self, alignment: AlignedTranscript) -> None:
        self.beginResetModel()
        self._alignment = alignment
        self.endResetModel()
