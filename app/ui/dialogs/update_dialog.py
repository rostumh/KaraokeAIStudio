from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QProgressBar, QPushButton, QVBoxLayout

from app.domain.models.update import UpdateCheckResult, UpdateDownloadResult


class UpdateDialog(QDialog):
    checkRequested = Signal()
    downloadRequested = Signal(object)
    cancelRequested = Signal()
    openFolderRequested = Signal(object)

    def __init__(self, current_version: str, parent: object = None) -> None:
        super().__init__(parent)
        self.current = current_version
        self.release = None
        self.package = None
        self.setWindowTitle("Karaoke AI Studio Updates")
        self.setMinimumWidth(540)
        self.status = QLabel(
            f"Installed version: {current_version}\n\n"
            "Select Check for Updates to query the configured HTTPS release manifest."
        )
        self.status.setWordWrap(True)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.check = QPushButton("Check for Updates")
        self.download = QPushButton("Download Verified Package")
        self.download.setEnabled(False)
        self.open_folder = QPushButton("Open Download Folder")
        self.open_folder.setEnabled(False)
        self.check.clicked.connect(self._check)
        self.download.clicked.connect(lambda: self.downloadRequested.emit(self.release))
        self.open_folder.clicked.connect(lambda: self.openFolderRequested.emit(self.package))
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel Operation")
        self.buttons.rejected.connect(self.cancelRequested)
        self.buttons.accepted.connect(self.accept)
        layout = QVBoxLayout(self)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        layout.addWidget(self.check)
        layout.addWidget(self.download)
        layout.addWidget(self.open_folder)
        layout.addWidget(self.buttons)

    def _check(self) -> None:
        self.check.setEnabled(False)
        self.status.setText("Checking for updates…")
        self.checkRequested.emit()

    def show_check(self, result: UpdateCheckResult) -> None:
        self.release = result.release
        self.check.setEnabled(True)
        self.download.setEnabled(result.update_available)
        if result.update_available:
            self.status.setText(
                f"Version {result.release.version} is available.\n"
                f"Published: {result.release.published_utc}\n"
                f"Channel: {result.release.channel.value}\n"
                f"Package: {result.release.size_bytes:,} bytes"
            )
        else:
            self.status.setText(f"Karaoke AI Studio {result.current_version} is up to date.")

    def show_download(self, result: UpdateDownloadResult) -> None:
        self.package = result.package_path
        self.open_folder.setEnabled(True)
        self.download.setEnabled(False)
        self.status.setText(
            f"Verified package saved to:\n{result.package_path}\n\n"
            "The app will not run installers automatically. Close your work, inspect the publisher "
            "signature, then install manually."
        )

    def update_progress(self, value: int, text: str) -> None:
        self.progress.setValue(value)
        self.status.setText(text)

    def show_error(self, text: str) -> None:
        self.check.setEnabled(True)
        self.status.setText(text)
