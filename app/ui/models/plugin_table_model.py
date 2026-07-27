from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from app.domain.models.plugins import PluginRecord


class PluginTableModel(QAbstractTableModel):
    HEADERS = ("Plugin", "Version", "Provider", "Status", "Capabilities", "Details")
    def __init__(self) -> None: super().__init__(); self._records: tuple[PluginRecord, ...] = ()
    @property
    def records(self) -> tuple[PluginRecord, ...]: return self._records
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return 0 if parent.isValid() else len(self._records)
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if role != Qt.ItemDataRole.DisplayRole or not index.isValid(): return None
        record=self._records[index.row()]; d=record.descriptor
        return (d.name,d.version,d.provider,record.status.value.title(),", ".join(d.capabilities),record.error or d.description)[index.column()]
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
        return super().headerData(section, orientation, role)
    def set_records(self, records: tuple[PluginRecord, ...]) -> None: self.beginResetModel(); self._records=records; self.endResetModel()
