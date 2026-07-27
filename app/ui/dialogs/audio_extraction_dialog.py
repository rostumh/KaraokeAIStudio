from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.domain.models.audio_extraction import AudioFormat
from app.domain.models.media import MediaAsset


class AudioExtractionDialog(QDialog):
    extractionRequested = Signal(dict)
    cancelRequested = Signal()

    def __init__(self, asset: MediaAsset, default_directory: Path, parent: object = None) -> None:
        super().__init__(parent)
        self._asset = asset
        self.setWindowTitle("Extract Audio")
        self.setMinimumWidth(560)
        self._format = QComboBox()
        self._format.addItem("WAV — PCM 16-bit", AudioFormat.WAV_PCM_16.value)
        self._format.addItem("WAV — PCM 24-bit", AudioFormat.WAV_PCM_24.value)
        self._format.addItem("FLAC — Lossless", AudioFormat.FLAC.value)
        self._format.addItem("MP3 — 320 kbps", AudioFormat.MP3.value)
        self._stream = QComboBox()
        for stream in asset.audio_streams:
            description = f"Stream {stream.index}: {stream.codec.upper()} • {stream.sample_rate or '?'} Hz • {stream.channels or '?'} ch"
            self._stream.addItem(description, stream.index)
        self._sample_rate = QComboBox()
        self._sample_rate.addItem("Preserve source", None)
        for rate in (44100, 48000, 96000): self._sample_rate.addItem(f"{rate} Hz", rate)
        self._channels = QComboBox()
        self._channels.addItem("Preserve source", None)
        self._channels.addItem("Mono", 1)
        self._channels.addItem("Stereo", 2)
        self._output = QLineEdit()
        self._browse = QPushButton("Browse…")
        self._overwrite = QCheckBox("Replace an existing destination file")
        output_row = QHBoxLayout(); output_row.addWidget(self._output, 1); output_row.addWidget(self._browse)
        form = QFormLayout(); form.addRow("Source", QLabel(asset.display_name)); form.addRow("Audio stream", self._stream); form.addRow("Output format", self._format); form.addRow("Sample rate", self._sample_rate); form.addRow("Channels", self._channels); form.addRow("Destination", output_row); form.addRow("Overwrite", self._overwrite)
        self._buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self._buttons.button(QDialogButtonBox.StandardButton.Save).setText("Extract Audio")
        root = QVBoxLayout(self); root.addLayout(form); root.addWidget(self._buttons)
        self._default_directory = default_directory
        self._format.currentIndexChanged.connect(self._update_default_path)
        self._browse.clicked.connect(self._browse_output)
        self._buttons.accepted.connect(self._submit)
        self._buttons.rejected.connect(self._cancel_or_close)
        self._update_default_path()

    def _extension(self) -> str:
        value = AudioFormat(str(self._format.currentData()))
        return ".wav" if value in {AudioFormat.WAV_PCM_16, AudioFormat.WAV_PCM_24} else f".{value.value}"

    def _update_default_path(self) -> None:
        stem = self._asset.source_path.stem + "_audio"
        current = Path(self._output.text()) if self._output.text() else self._default_directory / stem
        self._output.setText(str(current.with_suffix(self._extension())))

    def _browse_output(self) -> None:
        extension = self._extension()[1:].upper()
        filename, _ = QFileDialog.getSaveFileName(self, "Audio Extraction Destination", self._output.text(), f"{extension} Audio (*{self._extension()})")
        if filename: self._output.setText(filename)

    def _submit(self) -> None:
        output = Path(self._output.text().strip())
        if not output.name:
            QMessageBox.warning(self, "Destination Required", "Choose an output filename before extracting audio."); return
        if output.exists() and not self._overwrite.isChecked():
            QMessageBox.warning(self, "Destination Exists", "Enable overwrite or choose a different destination."); return
        options: dict[str, object] = {
            "output_path": str(output), "output_format": str(self._format.currentData()),
            "stream_index": int(self._stream.currentData()), "sample_rate": self._sample_rate.currentData(),
            "channels": self._channels.currentData(), "mp3_bitrate_kbps": 320,
            "overwrite": self._overwrite.isChecked(),
        }
        self.set_busy(True)
        self.extractionRequested.emit(options)

    def set_busy(self, busy: bool) -> None:
        for widget in (self._format, self._stream, self._sample_rate, self._channels, self._output, self._browse, self._overwrite): widget.setEnabled(not busy)
        self._buttons.button(QDialogButtonBox.StandardButton.Save).setEnabled(not busy)
        self._buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel Extraction" if busy else "Cancel")

    def show_error(self, message: str) -> None:
        self.set_busy(False)
        QMessageBox.critical(self, "Audio Extraction Failed", message)

    def _cancel_or_close(self) -> None:
        if not self._buttons.button(QDialogButtonBox.StandardButton.Save).isEnabled(): self.cancelRequested.emit()
        else: self.reject()
