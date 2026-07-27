from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from app.domain.models.media import MediaAsset


class MediaAssetListModel(QAbstractListModel):
    AssetRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self) -> None:
        super().__init__()
        self._assets: list[MediaAsset] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._assets)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self._assets):
            return None
        asset = self._assets[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return asset.display_name
        if role == Qt.ItemDataRole.ToolTipRole:
            return str(asset.source_path)
        if role == self.AssetRole:
            return asset
        return None

    def add_asset(self, asset: MediaAsset) -> int:
        for row, existing in enumerate(self._assets):
            if existing.source_path == asset.source_path:
                return row
        row = len(self._assets)
        self.beginInsertRows(QModelIndex(), row, row)
        self._assets.append(asset)
        self.endInsertRows()
        return row

    def asset_at(self, row: int) -> MediaAsset | None:
        return self._assets[row] if 0 <= row < len(self._assets) else None

    def clear(self) -> None:
        if not self._assets:
            return
        self.beginResetModel()
        self._assets.clear()
        self.endResetModel()
