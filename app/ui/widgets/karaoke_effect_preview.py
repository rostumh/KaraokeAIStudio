from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

from app.domain.models.karaoke_effects import KaraokeEffect, KaraokeEffectSettings


class KaraokeEffectPreview(QWidget):
    """Lightweight animated preview of effect timing without invoking FFmpeg."""

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(150)
        self._settings = KaraokeEffectSettings()
        self._progress = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._advance)
        self._timer.start()

    def set_settings(self, settings: KaraokeEffectSettings) -> None:
        self._settings = settings
        self.update()

    def _advance(self) -> None:
        self._progress = (self._progress + 0.008) % 1.0
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(event.rect(), QColor("#05080d"))
        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        effect = self._settings.effect
        if effect == KaraokeEffect.POP:
            font.setPointSizeF(24 * (1.0 + 0.12 * max(0.0, 1.0 - abs(self._progress - 0.5) * 8)))
        painter.setFont(font)
        text = "Sing every word"
        rect = self.rect().adjusted(20, 20, -20, -20)
        painter.setPen(QColor("#000000"))
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            painter.drawText(rect.translated(dx, dy), Qt.AlignmentFlag.AlignCenter, text)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        metrics = painter.fontMetrics()
        text_rect = metrics.boundingRect(rect, Qt.AlignmentFlag.AlignCenter, text)
        clip_width = round(text_rect.width() * self._progress)
        painter.save()
        painter.setClipRect(text_rect.left(), text_rect.top(), clip_width, text_rect.height())
        painter.setPen(QColor("#00d7ff"))
        if effect == KaraokeEffect.GLOW:
            painter.setPen(QColor("#8ff7ff"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()
