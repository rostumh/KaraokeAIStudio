from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot

from app.ui.constants import WorkspacePage


class WorkspaceViewModel(QObject):
    """Presentation state for page navigation and transport controls."""

    pageChanged = Signal(int)
    playingChanged = Signal(bool)
    positionChanged = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._page = WorkspacePage.STUDIO
        self._playing = False
        self._position = 0

    @Property(int, notify=pageChanged)
    def page(self) -> int:
        return int(self._page)

    @Property(bool, notify=playingChanged)
    def playing(self) -> bool:
        return self._playing

    @Property(int, notify=positionChanged)
    def position(self) -> int:
        return self._position

    @Slot(int)
    def select_page(self, page: int) -> None:
        requested = WorkspacePage(page)
        if requested != self._page:
            self._page = requested
            self.pageChanged.emit(int(requested))

    @Slot()
    def toggle_playback(self) -> None:
        self._playing = not self._playing
        self.playingChanged.emit(self._playing)

    @Slot()
    def stop_playback(self) -> None:
        if self._playing:
            self._playing = False
            self.playingChanged.emit(False)
        if self._position != 0:
            self._position = 0
            self.positionChanged.emit(0)

    @Slot(int)
    def seek(self, position: int) -> None:
        bounded = max(0, min(1000, position))
        if bounded != self._position:
            self._position = bounded
            self.positionChanged.emit(bounded)
