from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.constants import WorkspacePage


class Sidebar(QWidget):
    """Primary application navigation with exclusive keyboard-accessible buttons."""

    pageRequested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(210)
        brand = QLabel("Karaoke AI Studio")
        brand.setObjectName("brandTitle")
        caption = QLabel("CREATE • SYNC • PERFORM")
        caption.setObjectName("brandCaption")
        group = QButtonGroup(self)
        group.setExclusive(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 20, 14, 14)
        layout.addWidget(brand)
        layout.addWidget(caption)
        layout.addSpacing(25)
        entries: Iterable[tuple[str, WorkspacePage]] = (
            ("Studio", WorkspacePage.STUDIO),
            ("Lyrics Editor", WorkspacePage.LYRICS),
            ("Render Video Settings", WorkspacePage.RENDER_SETTINGS),
            ("Visual Style Editor", WorkspacePage.VISUAL_STYLE),
            ("Batch Queue", WorkspacePage.BATCH),
            ("Job History", WorkspacePage.HISTORY),
            ("Settings", WorkspacePage.SETTINGS),
            ("Plugins", WorkspacePage.PLUGINS),
        )
        for index, (label, page) in enumerate(entries):
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(lambda checked=False, value=int(page): self.pageRequested.emit(value))
            group.addButton(button, int(page))
            layout.addWidget(button)
            if index == 0:
                button.setChecked(True)
        layout.addStretch(1)
        version = QLabel("Version 0.29.2")
        version.setObjectName("muted")
        layout.addWidget(version)
        self._group = group

    def set_current_page(self, page: int) -> None:
        button = self._group.button(page)
        if button is not None:
            button.setChecked(True)
