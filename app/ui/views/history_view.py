from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView,QHeaderView,QHBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QVBoxLayout,QWidget

class HistoryView(QWidget):
    removeRequested=Signal(int)
    openRequested=Signal(object)
    def __init__(self)->None:
        super().__init__();title=QLabel("Job History");title.setObjectName("pageTitle")
        subtitle=QLabel("Successful renders remain available and can be removed from this list.");subtitle.setObjectName("muted")
        self.table=QTableWidget(0,5);self.table.setHorizontalHeaderLabels(("Project","Completed","Duration","Encoder","Output"));self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch);self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        open_button=QPushButton("Open Output");remove_button=QPushButton("Remove Selected");open_button.clicked.connect(self._open);remove_button.clicked.connect(self._remove)
        buttons=QHBoxLayout();buttons.addWidget(open_button);buttons.addWidget(remove_button);buttons.addStretch()
        root=QVBoxLayout(self);root.setContentsMargins(22,18,22,18);root.addWidget(title);root.addWidget(subtitle);root.addLayout(buttons);root.addWidget(self.table,1)
    def set_records(self,records:list[dict])->None:
        self.table.setRowCount(len(records))
        for r,record in enumerate(records):
            values=(record.get("project",""),record.get("completed",""),record.get("duration",""),record.get("encoder",""),record.get("output",""))
            for c,value in enumerate(values):self.table.setItem(r,c,QTableWidgetItem(str(value)))
    def _remove(self)->None:
        row=self.table.currentRow()
        if row>=0:self.removeRequested.emit(row)
    def _open(self)->None:
        row=self.table.currentRow()
        if row>=0 and self.table.item(row,4):self.openRequested.emit(Path(self.table.item(row,4).text()))
