from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox,QComboBox,QDialog,QDialogButtonBox,QFormLayout,QLabel,QLineEdit,QPlainTextEdit,QProgressBar,QSpinBox,QVBoxLayout
from app.domain.models.transcription import TranscriptionTask,WhisperDevice

class TranscriptionDialog(QDialog):
    requested=Signal(dict);cancelRequested=Signal()
    def __init__(self,source:str,destination:Path,cuda:bool,parent:object=None)->None:
        super().__init__(parent);self.setWindowTitle("Whisper Speech Recognition");self.setMinimumWidth(590)
        self.model=QComboBox();[(self.model.addItem(label,value)) for label,value in (("Small — Recommended","small"),("Medium — Higher accuracy","medium"),("Large v3 — Best multilingual accuracy","large-v3"),("Distil Large v3 — Faster English","distil-large-v3"),("Base — Fast preview","base"),("Tiny — Fastest preview","tiny"))]
        self.device=QComboBox();self.device.addItem("Automatic",WhisperDevice.AUTO.value);self.device.addItem("CPU",WhisperDevice.CPU.value)
        if cuda:self.device.addItem("NVIDIA CUDA",WhisperDevice.CUDA.value)
        self.compute=QComboBox();self.compute.addItem("INT8 — Lowest memory","int8");self.compute.addItem("INT8 + FP16 — GPU efficient","int8_float16");self.compute.addItem("FP16 — GPU quality/performance","float16");self.compute.addItem("FP32 — Highest memory","float32")
        self.language=QComboBox();self.language.addItem("Automatic detection","");[(self.language.addItem(n,c)) for n,c in (("English","en"),("Filipino / Tagalog","tl"),("Spanish","es"),("Japanese","ja"),("Korean","ko"),("Chinese","zh"))]
        self.task=QComboBox();self.task.addItem("Transcribe in original language",TranscriptionTask.TRANSCRIBE.value);self.task.addItem("Translate speech to English",TranscriptionTask.TRANSLATE.value)
        self.beam=QSpinBox();self.beam.setRange(1,10);self.beam.setValue(5);self.vad=QCheckBox("Remove long non-speech regions with VAD");self.vad.setChecked(True);self.context=QCheckBox("Use previous segment as context");self.context.setChecked(True);self.prompt=QPlainTextEdit();self.prompt.setPlaceholderText("Optional artist names, uncommon terms, or expected lyric vocabulary");self.prompt.setMaximumHeight(80)
        self.status=QLabel("The model downloads on first use and is cached for later runs.");self.status.setWordWrap(True);self.progress=QProgressBar();self.progress.setRange(0,100);self.progress.hide();self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Transcribe")
        form=QFormLayout();form.addRow("Source",QLabel(source));form.addRow("Model",self.model);form.addRow("Device",self.device);form.addRow("Compute type",self.compute);form.addRow("Language",self.language);form.addRow("Task",self.task);form.addRow("Beam size",self.beam);form.addRow("Silence handling",self.vad);form.addRow("Context",self.context);form.addRow("Initial prompt",self.prompt);form.addRow("Output folder",QLabel(str(destination)))
        layout=QVBoxLayout(self);layout.addLayout(form);layout.addWidget(self.status);layout.addWidget(self.progress);layout.addWidget(self.buttons);self.buttons.accepted.connect(lambda:self._submit(destination));self.buttons.rejected.connect(self._cancel)
    def _submit(self,destination:Path)->None:
        self.set_busy(True);self.requested.emit({"model":self.model.currentData(),"device":self.device.currentData(),"compute":self.compute.currentData(),"language":self.language.currentData(),"task":self.task.currentData(),"beam":self.beam.value(),"vad":self.vad.isChecked(),"context":self.context.isChecked(),"prompt":self.prompt.toPlainText().strip(),"destination":str(destination)})
    def set_busy(self,busy:bool)->None:self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(not busy);self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel Transcription" if busy else "Cancel");self.progress.setVisible(busy)
    def update_progress(self,value:int,text:str)->None:self.progress.setValue(value);self.status.setText(text)
    def show_error(self,text:str)->None:self.set_busy(False);self.status.setText(text)
    def _cancel(self)->None:
        if self.progress.isVisible():self.cancelRequested.emit();self.status.setText("Cancelling after the current segment…")
        else:self.reject()
