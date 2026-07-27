from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor
from app.domain.models.quality_validation import CheckSeverity, MediaQualityReport


class QualityCheckModel(QAbstractTableModel):
    HEADERS = ("Status", "Check", "Detail")
    def __init__(self) -> None: super().__init__(); self._report: MediaQualityReport | None = None
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return 0 if parent.isValid() or self._report is None else len(self._report.checks)
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return 3
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if not index.isValid() or self._report is None: return None
        check = self._report.checks[index.row()]
        if role == Qt.ItemDataRole.DisplayRole: return (check.severity.value.upper(), check.title, check.detail)[index.column()]
        if role == Qt.ItemDataRole.BackgroundRole:
            return {CheckSeverity.PASS: QColor("#173b2a"), CheckSeverity.WARNING: QColor("#4b3b1f"), CheckSeverity.ERROR: QColor("#4a2228")}[check.severity]
        return None
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
        return super().headerData(section, orientation, role)
    def set_report(self, report: MediaQualityReport) -> None: self.beginResetModel(); self._report=report; self.endResetModel()
