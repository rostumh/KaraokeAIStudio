from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QListView, QVBoxLayout, QWidget

from app.ui.models.media_asset_list_model import MediaAssetListModel


class ProjectDockContent(QWidget):
    """Project media browser backed by a reusable Qt item model."""

    assetSelected = Signal(object)

    def __init__(self, model: MediaAssetListModel) -> None:
        super().__init__()
        label = QLabel("Project Media")
        label.setObjectName("sectionTitle")
        self.view = QListView()
        self.view.setModel(model)
        self.view.setAlternatingRowColors(True)
        self.view.setAccessibleName("Imported project media")
        self.view.selectionModel().currentChanged.connect(
            lambda current, previous: self.assetSelected.emit(model.asset_at(current.row()))
        )
        hint = QLabel("Imported files remain at their original locations.")
        hint.setObjectName("muted")
        hint.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(label)
        layout.addWidget(self.view, 1)
        layout.addWidget(hint)
    def current_asset(self) -> object | None:
        index = self.view.currentIndex()
        return self.view.model().data(index, MediaAssetListModel.AssetRole) if index.isValid() else None

