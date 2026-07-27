from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog,QDialogButtonBox,QFileDialog,QHeaderView,QHBoxLayout,QLabel,QLineEdit,QProgressBar,QPushButton,QTableView,QVBoxLayout
from app.domain.models.quality_validation import MediaQualityReport
from app.ui.models.quality_check_model import QualityCheckModel

class FinalExportDialog(QDialog):
 validationRequested=Signal(object);cancelRequested=Signal()
 def __init__(self,report_dir:Path,parent:object=None)->None:
  super().__init__(parent);self.report_dir=report_dir;self.setWindowTitle("Final Export & Quality Validation");self.setMinimumSize(760,520);self.path=QLineEdit();browse=QPushButton("Browse…");browse.clicked.connect(self._browse);row=QHBoxLayout();row.addWidget(self.path,1);row.addWidget(browse);self.status=QLabel("Select a rendered video. The complete file will be decoded to detect fatal media errors.");self.status.setWordWrap(True);self.progress=QProgressBar();self.progress.setRange(0,100);self.model=QualityCheckModel();self.table=QTableView();self.table.setModel(self.model);self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Stretch);self.summary=QLabel("No validation report yet.");self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Validate Final Export");self.buttons.accepted.connect(self._start);self.buttons.rejected.connect(self._cancel);layout=QVBoxLayout(self);layout.addLayout(row);layout.addWidget(self.status);layout.addWidget(self.progress);layout.addWidget(self.summary);layout.addWidget(self.table,1);layout.addWidget(self.buttons)
 def _browse(self)->None:
  path,_=QFileDialog.getOpenFileName(self,"Select Rendered Video",self.path.text(),"Video (*.mp4 *.mkv *.mov)")
  if path:self.path.setText(path)
 def _start(self)->None:self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False);self.validationRequested.emit(Path(self.path.text()))
 def update_progress(self,value:int,text:str)->None:self.progress.setValue(value);self.status.setText(text)
 def show_report(self,report:MediaQualityReport,path:Path)->None:self.model.set_report(report);self.summary.setText(("PASS" if report.passed else "FAILED")+f" • {report.warning_count} warning(s) • Report: {path.name}");self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True);self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Validate Again")
 def show_error(self,text:str)->None:self.status.setText(text);self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
 def _cancel(self)->None:
  if not self.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled():self.cancelRequested.emit();self.status.setText("Cancelling validation…")
  else:self.reject()
