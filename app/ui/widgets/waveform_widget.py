from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class WaveformWidget(QWidget):
    """DPI-aware waveform overview used until decoded samples arrive in Module 3."""

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(115)
        self.setAccessibleName("Audio waveform overview")

    def paintEvent(self, event: object) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        painter.setPen(QPen(QColor("#263448"), 1))
        painter.setBrush(QColor("#0b111a"))
        painter.drawRoundedRect(bounds, 8, 8)

        center = bounds.center().y()
        path = QPainterPath(QPointF(bounds.left() + 10, center))
        usable = max(1.0, bounds.width() - 20)
        for step in range(int(usable) + 1):
            x = bounds.left() + 10 + step
            envelope = 0.28 + 0.55 * math.sin(step * 0.011) ** 2
            sample = math.sin(step * 0.19) * math.sin(step * 0.043)
            y = center - sample * envelope * bounds.height() * 0.38
            path.lineTo(x, y)
        gradient = QLinearGradient(bounds.left(), 0, bounds.right(), 0)
        gradient.setColorAt(0, QColor("#3f75e8"))
        gradient.setColorAt(0.55, QColor("#6b9cff"))
        gradient.setColorAt(1, QColor("#49c6b4"))
        painter.setPen(QPen(gradient, 1.4))
        painter.drawPath(path)
        painter.setPen(QPen(QColor("#273952"), 1, Qt.PenStyle.DashLine))
        painter.drawLine(QPointF(bounds.left() + 8, center), QPointF(bounds.right() - 8, center))
