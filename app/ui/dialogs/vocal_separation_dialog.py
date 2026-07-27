from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox,QDialog,QDialogButtonBox,QFormLayout,QLabel,QProgressBar,QSpinBox,QDoubleSpinBox,QVBoxLayout
from app.domain.models.separation import ComputeDevice,SeparationMode,StemFormat


class VocalSeparationDialog(QDialog):
    separationRequested=Signal(dict); cancelRequested=Signal()
    def __init__(self, source_name: str, output_root: Path, cuda_available: bool, parent: object=None) -> None:
        super().__init__(parent); self.setWindowTitle("AI Vocal Separation"); self.setMinimumWidth(540); self._output_root=output_root
        self._model=QComboBox(); self._model.addItem("HTDemucs — Balanced", "htdemucs"); self._model.addItem("HTDemucs Fine-tuned — Highest quality, slower", "htdemucs_ft")
        self._mode=QComboBox(); self._mode.addItem("Vocals + Instrumental",SeparationMode.VOCALS.value); self._mode.addItem("Vocals + Drums + Bass + Other",SeparationMode.FOUR_STEMS.value)
        self._device=QComboBox(); self._device.addItem("Automatic",ComputeDevice.AUTO.value); self._device.addItem("CPU",ComputeDevice.CPU.value)
        if cuda_available: self._device.addItem("NVIDIA CUDA",ComputeDevice.CUDA.value)
        self._format=QComboBox(); self._format.addItem("WAV 24-bit",StemFormat.WAV_24.value); self._format.addItem("FLAC lossless",StemFormat.FLAC.value)
        self._shifts=QSpinBox(); self._shifts.setRange(1,10); self._shifts.setValue(1); self._shifts.setToolTip("More shifts can improve quality but increase processing time proportionally.")
        self._overlap=QDoubleSpinBox(); self._overlap.setRange(0.10,0.75); self._overlap.setSingleStep(0.05); self._overlap.setValue(0.25)
        self._segment=QSpinBox(); self._segment.setRange(5,7); self._segment.setValue(7); self._segment.setSuffix(" seconds"); self._segment.setToolTip("HTDemucs supports segments up to 7.8 seconds. Seven seconds is a safe default.")
        self._status=QLabel("Ready"); self._status.setWordWrap(True); self._progress=QProgressBar(); self._progress.setRange(0,0); self._progress.hide()
        form=QFormLayout(); form.addRow("Source",QLabel(source_name)); form.addRow("Model",self._model); form.addRow("Stems",self._mode); form.addRow("Compute device",self._device); form.addRow("Stem format",self._format); form.addRow("Quality shifts",self._shifts); form.addRow("Overlap",self._overlap); form.addRow("Segment length",self._segment); form.addRow("Output root",QLabel(str(output_root)))
        self._buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel); self._buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Separate Vocals"); self._buttons.accepted.connect(self._submit); self._buttons.rejected.connect(self._cancel_or_close)
        intro=QLabel("Karaoke AI Studio will create two new audio tracks: vocals and instrumental. The first run downloads the Demucs model automatically and can take several minutes. Recommended settings are already selected. The safe 7-second segment limit is enforced for HTDemucs."); intro.setWordWrap(True)
        layout=QVBoxLayout(self); layout.addWidget(intro); layout.addLayout(form); layout.addWidget(self._status); layout.addWidget(self._progress); layout.addWidget(self._buttons)
    def _submit(self) -> None:
        self.set_busy(True); self.separationRequested.emit({"output_root":str(self._output_root),"model":self._model.currentData(),"mode":self._mode.currentData(),"device":self._device.currentData(),"format":self._format.currentData(),"shifts":self._shifts.value(),"overlap":self._overlap.value(),"segment":self._segment.value()})
    def set_busy(self,busy: bool) -> None:
        for widget in (self._model,self._mode,self._device,self._format,self._shifts,self._overlap,self._segment): widget.setEnabled(not busy)
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(not busy); self._buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel Separation" if busy else "Cancel"); self._progress.setVisible(busy)
    def set_status(self,text: str) -> None: self._status.setText(text)
    def show_error(self,text: str) -> None: self.set_busy(False); self._status.setText(text)
    def _cancel_or_close(self) -> None:
        if self._progress.isVisible(): self.cancelRequested.emit(); self._status.setText("Cancelling…")
        else: self.reject()
