from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QLabel, QStackedLayout, QVBoxLayout, QWidget

from app.domain.models.media import MediaAsset
from app.ui.formatters import format_duration


class VideoPreview(QWidget):
    """Real video-output surface with a friendly metadata placeholder for audio media."""

    doubleClicked = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(480, 270)
        self.setAccessibleName("Karaoke video preview")
        self.video_widget = QVideoWidget(self)
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.video_widget.setStyleSheet("background:#05080d")
        placeholder = QWidget(self)
        self._title = QLabel("Preview")
        self._title.setObjectName("emptyTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption = QLabel("Import a media file to begin your project")
        self._caption.setObjectName("emptyText")
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setWordWrap(True)
        content = QVBoxLayout(placeholder)
        content.addStretch(1); content.addWidget(self._title); content.addWidget(self._caption); content.addStretch(1)
        self._stack = QStackedLayout(self)
        self._stack.setContentsMargins(0, 0, 0, 0)
        self._stack.addWidget(placeholder)
        self._stack.addWidget(self.video_widget)

    def show_asset(self, asset: MediaAsset) -> None:
        self._title.setText(asset.display_name)
        video = asset.primary_video
        dimensions = f"{video.width}x{video.height}" if video else "Audio only"
        self._caption.setText(f"{dimensions}  -  {format_duration(asset.duration_seconds)}  -  {asset.container}")
        self._stack.setCurrentWidget(self.video_widget if video else self._stack.widget(0))
        self.setToolTip(str(asset.source_path))

    def clear_asset(self) -> None:
        self._stack.setCurrentIndex(0)
        self._title.setText("Preview")
        self._caption.setText("Import a media file to begin your project")
        self.setToolTip("")

    def mouseDoubleClickEvent(self, event: object) -> None:
        del event
        self.doubleClicked.emit()
