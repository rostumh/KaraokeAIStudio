from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QWidget

from app.domain.models.media import MediaAsset
from app.ui.formatters import format_bytes, format_duration


class PropertiesDockContent(QWidget):
    """Contextual media inspector populated from immutable domain metadata."""

    def __init__(self) -> None:
        super().__init__()
        self._values: dict[str, QLineEdit | QLabel] = {}
        form = QFormLayout(self)
        for key, caption in (("name", "Name"), ("type", "Type"), ("duration", "Duration"), ("size", "Size"), ("container", "Container"), ("audio", "Audio"), ("video", "Video"), ("path", "Source")):
            value = QLineEdit("—") if key in {"name", "path"} else QLabel("—")
            if isinstance(value, QLineEdit):
                value.setReadOnly(True)
                value.setCursorPosition(0)
            else:
                value.setTextInteractionFlags(
                    value.textInteractionFlags() | Qt.TextInteractionFlag.TextSelectableByMouse
                )
            form.addRow(caption, value)
            self._values[key] = value

    def show_asset(self, asset: object) -> None:
        if not isinstance(asset, MediaAsset):
            return
        audio = asset.primary_audio
        video = asset.primary_video
        audio_text = "—" if audio is None else f"{audio.codec.upper()} • {audio.sample_rate or '?'} Hz • {audio.channels or '?'} ch"
        video_text = "—" if video is None else f"{video.codec.upper()} • {video.width}×{video.height}" + (f" • {video.frame_rate:.2f} fps" if video.frame_rate else "")
        values = {
            "name": asset.display_name, "type": asset.kind.value.title(), "duration": format_duration(asset.duration_seconds),
            "size": format_bytes(asset.size_bytes), "container": asset.container, "audio": audio_text,
            "video": video_text, "path": str(asset.source_path),
        }
        for key, text in values.items():
            self._values[key].setText(text)
