from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStyle


_ICON_MAP: dict[str, QStyle.StandardPixmap] = {
    "new": QStyle.StandardPixmap.SP_FileIcon,
    "open": QStyle.StandardPixmap.SP_DialogOpenButton,
    "save": QStyle.StandardPixmap.SP_DialogSaveButton,
    "export": QStyle.StandardPixmap.SP_DialogApplyButton,
    "play": QStyle.StandardPixmap.SP_MediaPlay,
    "pause": QStyle.StandardPixmap.SP_MediaPause,
    "stop": QStyle.StandardPixmap.SP_MediaStop,
    "previous": QStyle.StandardPixmap.SP_MediaSkipBackward,
    "next": QStyle.StandardPixmap.SP_MediaSkipForward,
    "settings": QStyle.StandardPixmap.SP_FileDialogDetailedView,
    "folder": QStyle.StandardPixmap.SP_DirIcon,
    "add": QStyle.StandardPixmap.SP_DialogYesButton,
    "remove": QStyle.StandardPixmap.SP_DialogNoButton,
    "information": QStyle.StandardPixmap.SP_MessageBoxInformation,
}


def standard_icon(name: str) -> QIcon:
    """Return a native, DPI-aware Qt icon without filesystem assumptions."""
    application = QApplication.instance()
    if application is None:
        return QIcon()
    style = application.style()
    return style.standardIcon(_ICON_MAP[name])
