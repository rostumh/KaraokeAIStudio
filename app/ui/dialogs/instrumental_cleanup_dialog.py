from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox,QComboBox,QDialog,QDialogButtonBox,QDoubleSpinBox,QFileDialog,QFormLayout,QHBoxLayout,QLabel,QLineEdit,QMessageBox,QPushButton,QSpinBox,QVBoxLayout
from app.domain.models.instrumental_cleanup import CleanupOutputFormat,CleanupPreset

_PRESETS={
 CleanupPreset.GENTLE:(6.0,-55.0,25,20000,-16.0,-1.5,11.0),
 CleanupPreset.BALANCED:(10.0,-50.0,30,19000,-16.0,-1.5,9.0),
 CleanupPreset.STRONG:(16.0,-45.0,40,18000,-15.0,-1.5,7.0),
}

class InstrumentalCleanupDialog(QDialog):
    cleanupRequested=Signal(dict);cancelRequested=Signal()
    def __init__(self,source_name:str,default_directory:Path,parent:object=None)->None:
        super().__init__(parent);self.setWindowTitle("Instrumental Cleanup");self.setMinimumWidth(590);self._default_directory=default_directory;self._source_name=source_name
        self._preset=QComboBox();self._preset.addItem("Gentle",CleanupPreset.GENTLE.value);self._preset.addItem("Balanced",CleanupPreset.BALANCED.value);self._preset.addItem("Strong",CleanupPreset.STRONG.value);self._preset.addItem("Custom",CleanupPreset.CUSTOM.value);self._preset.setCurrentIndex(1)
        self._nr=QDoubleSpinBox();self._nr.setRange(.01,30);self._nr.setSuffix(" dB");self._nf=QDoubleSpinBox();self._nf.setRange(-80,-20);self._nf.setSuffix(" dB")
        self._hp=QSpinBox();self._hp.setRange(10,1000);self._hp.setSuffix(" Hz");self._lp=QSpinBox();self._lp.setRange(4000,22000);self._lp.setSuffix(" Hz")
        self._lufs=QDoubleSpinBox();self._lufs.setRange(-24,-8);self._lufs.setSuffix(" LUFS");self._peak=QDoubleSpinBox();self._peak.setRange(-9,-.1);self._peak.setSuffix(" dBTP");self._lra=QDoubleSpinBox();self._lra.setRange(1,20);self._lra.setSuffix(" LU")
        self._limiter=QCheckBox("Apply final true-peak limiter");self._limiter.setChecked(True);self._format=QComboBox();self._format.addItem("WAV 24-bit",CleanupOutputFormat.WAV_24.value);self._format.addItem("FLAC lossless",CleanupOutputFormat.FLAC.value)
        self._output=QLineEdit(str(default_directory/(Path(source_name).stem+"_clean.wav")));browse=QPushButton("Browse…");row=QHBoxLayout();row.addWidget(self._output,1);row.addWidget(browse);self._overwrite=QCheckBox("Replace existing destination")
        form=QFormLayout();form.addRow("Source",QLabel(source_name));form.addRow("Preset",self._preset);form.addRow("Noise reduction",self._nr);form.addRow("Noise floor",self._nf);form.addRow("High-pass",self._hp);form.addRow("Low-pass",self._lp);form.addRow("Target loudness",self._lufs);form.addRow("True peak",self._peak);form.addRow("Loudness range",self._lra);form.addRow("Protection",self._limiter);form.addRow("Output format",self._format);form.addRow("Destination",row);form.addRow("Overwrite",self._overwrite)
        self._status=QLabel("Cleanup is non-destructive; the source file is never modified.");self._status.setWordWrap(True);self._buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);self._buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Clean Instrumental")
        layout=QVBoxLayout(self);layout.addLayout(form);layout.addWidget(self._status);layout.addWidget(self._buttons);self._preset.currentIndexChanged.connect(self._apply_preset);self._format.currentIndexChanged.connect(self._update_extension);browse.clicked.connect(self._browse);self._buttons.accepted.connect(self._submit);self._buttons.rejected.connect(self._cancel_or_close);self._apply_preset()
    def _apply_preset(self)->None:
        preset=CleanupPreset(str(self._preset.currentData()))
        if preset in _PRESETS:
            values=_PRESETS[preset]
            for widget,value in zip((self._nr,self._nf,self._hp,self._lp,self._lufs,self._peak,self._lra),values):widget.setValue(value)
        custom=preset==CleanupPreset.CUSTOM
        for widget in (self._nr,self._nf,self._hp,self._lp,self._lufs,self._peak,self._lra):widget.setEnabled(custom)
    def _extension(self)->str:return ".flac" if self._format.currentData()==CleanupOutputFormat.FLAC.value else ".wav"
    def _update_extension(self)->None:self._output.setText(str(Path(self._output.text()).with_suffix(self._extension())))
    def _browse(self)->None:
        filename,_=QFileDialog.getSaveFileName(self,"Cleanup Destination",self._output.text(),f"Audio (*{self._extension()})")
        if filename:self._output.setText(filename)
    def _submit(self)->None:
        output=Path(self._output.text().strip())
        if not output.name:QMessageBox.warning(self,"Destination Required","Choose an output filename.");return
        if output.exists() and not self._overwrite.isChecked():QMessageBox.warning(self,"Destination Exists","Enable overwrite or choose another destination.");return
        self.set_busy(True);self.cleanupRequested.emit({"preset":self._preset.currentData(),"noise_reduction":self._nr.value(),"noise_floor":self._nf.value(),"highpass":self._hp.value(),"lowpass":self._lp.value(),"target_lufs":self._lufs.value(),"true_peak":self._peak.value(),"lra":self._lra.value(),"limiter":self._limiter.isChecked(),"format":self._format.currentData(),"output_path":str(output),"overwrite":self._overwrite.isChecked()})
    def set_busy(self,busy:bool)->None:
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(not busy);self._buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel Cleanup" if busy else "Cancel")
    def show_error(self,message:str)->None:self.set_busy(False);self._status.setText(message)
    def _cancel_or_close(self)->None:
        if not self._buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled():self.cancelRequested.emit();self._status.setText("Cancelling…")
        else:self.reject()
