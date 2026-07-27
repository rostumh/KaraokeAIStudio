from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QProgressBar, QVBoxLayout


class WordAlignmentDialog(QDialog):
    startRequested = Signal()
    cancelRequested = Signal()

    def __init__(self, source_name: str, segment_count: int, parent: object = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Word Timestamp Alignment")
        self.setMinimumWidth(520)
        explanation = QLabel(
            f"Source: {source_name}\nSegments: {segment_count}\n\n"
            "The Whisper model will re-decode the vocal audio with word timestamps enabled. "
            "Existing transcript text is supplied as alignment context."
        )
        explanation.setWordWrap(True)
        self.status = QLabel("Ready to align words.")
        self.status.setWordWrap(True)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Align Words")
        self.buttons.accepted.connect(self._start)
        self.buttons.rejected.connect(self._cancel)
        layout = QVBoxLayout(self)
        layout.addWidget(explanation)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        layout.addWidget(self.buttons)

    def _start(self) -> None:
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel Alignment")
        self.startRequested.emit()

    def update_progress(self, value: int, text: str) -> None:
        self.progress.setValue(value)
        self.status.setText(text)

    def show_error(self, text: str) -> None:
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        self.status.setText(text)

    def _cancel(self) -> None:
        if not self.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled():
            self.cancelRequested.emit()
            self.status.setText("Cancelling after the current segment…")
        else:
            self.reject()
