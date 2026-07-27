from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox,QFileDialog,QHBoxLayout,QHeaderView,QLabel,QPushButton,QTableView,QVBoxLayout,QWidget
from app.domain.models.batch import BatchOperation
from app.ui.models.batch_job_model import BatchJobModel

class BatchView(QWidget):
 addRequested=Signal(tuple,object);startRequested=Signal();cancelRequested=Signal();retryRequested=Signal(int);removeRequested=Signal(int)
 def __init__(self)->None:
  super().__init__();title=QLabel("Batch Queue");title.setObjectName("pageTitle");self.subtitle=QLabel("Persistent serial processing queue");self.subtitle.setObjectName("muted");self.operation=QComboBox();self.operation.addItem("Extract 24-bit WAV",BatchOperation.EXTRACT_WAV24.value);self.operation.addItem("Validate final video",BatchOperation.VALIDATE_FINAL.value);add=QPushButton("Add Files…");start=QPushButton("Start Queue");cancel=QPushButton("Cancel Current");retry=QPushButton("Retry Selected");remove=QPushButton("Remove Selected");add.clicked.connect(self._add);start.clicked.connect(self.startRequested);cancel.clicked.connect(self.cancelRequested);retry.clicked.connect(lambda:self.retryRequested.emit(self.table.currentIndex().row()));remove.clicked.connect(lambda:self.removeRequested.emit(self.table.currentIndex().row()));bar=QHBoxLayout();bar.addWidget(self.operation);[bar.addWidget(w) for w in (add,start,cancel,retry,remove)];self.model=BatchJobModel();self.table=QTableView();self.table.setModel(self.model);self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch);root=QVBoxLayout(self);root.setContentsMargins(22,18,22,18);root.addWidget(title);root.addWidget(self.subtitle);root.addLayout(bar);root.addWidget(self.table,1)
 def _add(self)->None:
  files,_=QFileDialog.getOpenFileNames(self,"Add Batch Sources",str(Path.home()),"Media (*.*)")
  if files:self.addRequested.emit(tuple(Path(x) for x in files),BatchOperation(str(self.operation.currentData())))
 def set_jobs(self,jobs:object)->None:
  if isinstance(jobs,tuple):self.model.set_jobs(jobs);self.subtitle.setText(f"{len(jobs)} job(s) • queue is saved automatically")
