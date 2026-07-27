from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHeaderView,QLabel,QPushButton,QTableView,QVBoxLayout,QHBoxLayout,QWidget
from app.ui.models.plugin_table_model import PluginTableModel


class PluginView(QWidget):
    refreshRequested=Signal();enabledChanged=Signal(str,bool)
    def __init__(self)->None:
        super().__init__();title=QLabel("Plugins");title.setObjectName("pageTitle");notice=QLabel("Plugins execute inside Karaoke AI Studio. Install only trusted Python distributions. Changes take effect after restart.");notice.setWordWrap(True);notice.setObjectName("muted");self.model=PluginTableModel();self.table=QTableView();self.table.setModel(self.model);self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch);self.table.horizontalHeader().setSectionResizeMode(5,QHeaderView.ResizeMode.Stretch);refresh=QPushButton("Refresh");enable=QPushButton("Enable Selected");disable=QPushButton("Disable Selected");refresh.clicked.connect(self.refreshRequested);enable.clicked.connect(lambda:self._set(True));disable.clicked.connect(lambda:self._set(False));bar=QHBoxLayout();bar.addWidget(refresh);bar.addWidget(enable);bar.addWidget(disable);bar.addStretch(1);root=QVBoxLayout(self);root.setContentsMargins(22,18,22,18);root.addWidget(title);root.addWidget(notice);root.addLayout(bar);root.addWidget(self.table,1)
    def _set(self,enabled:bool)->None:
        row=self.table.currentIndex().row()
        if 0<=row<len(self.model.records):self.enabledChanged.emit(self.model.records[row].descriptor.plugin_id,enabled)
    def set_records(self,records:object)->None:
        if isinstance(records,tuple):self.model.set_records(records)
