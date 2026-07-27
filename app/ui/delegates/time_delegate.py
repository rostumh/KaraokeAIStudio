from __future__ import annotations

from PySide6.QtWidgets import QDoubleSpinBox, QStyledItemDelegate, QWidget


class TimeSecondsDelegate(QStyledItemDelegate):
    """Precise seconds editor with millisecond resolution."""

    def createEditor(self, parent: QWidget, option: object, index: object) -> QWidget:
        del option, index
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(3)
        editor.setRange(0.0, 86_400.0)
        editor.setSingleStep(0.01)
        editor.setSuffix(" s")
        return editor
