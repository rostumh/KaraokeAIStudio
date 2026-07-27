from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.ui.icons import standard_icon
from app.ui.widgets.waveform_widget import WaveformWidget


class TimelineWidget(QWidget):
    """Transport and audio timeline with a normalized 0–1000 position."""

    playRequested = Signal()
    stopRequested = Signal()
    seekRequested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("transportBar")
        self._play_button = QPushButton()
        self._play_button.setIcon(standard_icon("play"))
        self._play_button.setToolTip("Play or pause (Space)")
        self._play_button.setAccessibleName("Play")
        self._play_button.clicked.connect(self.playRequested)
        stop = QPushButton()
        stop.setIcon(standard_icon("stop"))
        stop.setToolTip("Stop playback")
        stop.clicked.connect(self.stopRequested)
        self._position = QSlider(Qt.Orientation.Horizontal)
        self._position.setRange(0, 1000)
        self._position.setAccessibleName("Timeline position")
        self._position.sliderMoved.connect(self.seekRequested)
        self._duration_ms = 0
        self._position_ms = 0
        self._time = QLabel("00:00.000 / 00:00.000")
        self._time.setObjectName("timeLabel")

        controls = QHBoxLayout()
        controls.addWidget(self._play_button)
        controls.addWidget(stop)
        controls.addWidget(self._position, 1)
        controls.addWidget(self._time)
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 10)
        root.addLayout(controls)
        root.addWidget(WaveformWidget())

    def set_playing(self, playing: bool) -> None:
        self._play_button.setIcon(standard_icon("pause" if playing else "play"))
        self._play_button.setAccessibleName("Pause" if playing else "Play")

    def set_position(self, position: int) -> None:
        self._position.setValue(position)

    @staticmethod
    def _format_time(milliseconds: int) -> str:
        milliseconds = max(0, int(milliseconds))
        minutes, remainder = divmod(milliseconds, 60_000)
        seconds, millis = divmod(remainder, 1_000)
        return f"{minutes:02d}:{seconds:02d}.{millis:03d}"

    def set_media_time(self, position_ms: int, duration_ms: int) -> None:
        self._position_ms = max(0, int(position_ms))
        self._duration_ms = max(0, int(duration_ms))
        normalized = 0 if self._duration_ms <= 0 else round(self._position_ms * 1000 / self._duration_ms)
        self._position.setValue(max(0, min(1000, normalized)))
        self._time.setText(
            f"{self._format_time(self._position_ms)} / {self._format_time(self._duration_ms)}"
        )
