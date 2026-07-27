from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox,QDialog,QDialogButtonBox,QFileDialog,QFormLayout,QLabel,QProgressBar,QPushButton,QVBoxLayout
from app.domain.models.translation import TranslationOptions

class TranslationDialog(QDialog):
 translateRequested=Signal(object);cancelRequested=Signal();modelInstallRequested=Signal(object)
 def __init__(self,pairs:tuple[tuple[str,str],...],source_hint:str,parent:object=None)->None:
  super().__init__(parent);self.setWindowTitle("Translate Lyrics Offline");self.setMinimumWidth(560);self.source=QComboBox();self.target=QComboBox();languages=sorted({x for pair in pairs for x in pair})
  for code in languages:self.source.addItem(code,code);self.target.addItem(code,code)
  if self.source.findData(source_hint)>=0:self.source.setCurrentIndex(self.source.findData(source_hint))
  self._pairs=set(pairs);self.source.currentIndexChanged.connect(self._targets);self._targets();install=QPushButton("Install .argosmodel…");install.clicked.connect(self._install);form=QFormLayout();form.addRow("Source language",self.source);form.addRow("Target language",self.target);form.addRow("Offline models",install);self.status=QLabel("Translation runs locally using installed Argos language packages. Review translated lyrics before publishing.");self.status.setWordWrap(True);self.progress=QProgressBar();self.progress.setRange(0,100);self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Translate Lyrics");self.buttons.accepted.connect(self._start);self.buttons.rejected.connect(self._cancel);layout=QVBoxLayout(self);layout.addLayout(form);layout.addWidget(self.status);layout.addWidget(self.progress);layout.addWidget(self.buttons)
 def _targets(self)->None:
  source=str(self.source.currentData() or "");current=self.target.currentData();self.target.clear()
  for a,b in sorted(self._pairs):
   if a==source:self.target.addItem(b,b)
  if current and self.target.findData(current)>=0:self.target.setCurrentIndex(self.target.findData(current))
 def _install(self)->None:
  path,_=QFileDialog.getOpenFileName(self,"Install Argos Model","","Argos model (*.argosmodel)")
  if path:self.modelInstallRequested.emit(Path(path))
 def refresh_pairs(self,pairs:tuple[tuple[str,str],...])->None:self._pairs=set(pairs);self._targets();self.status.setText("Translation model installed.")
 def _start(self)->None:
  if self.target.currentData() is None:self.status.setText("Install or select a compatible source-to-target model.");return
  self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False);self.translateRequested.emit(TranslationOptions(str(self.source.currentData()),str(self.target.currentData())))
 def update_progress(self,v:int,t:str)->None:self.progress.setValue(v);self.status.setText(t)
 def show_error(self,t:str)->None:self.status.setText(t);self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
 def _cancel(self)->None:
  if not self.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled():self.cancelRequested.emit();self.status.setText("Cancelling translation…")
  else:self.reject()
