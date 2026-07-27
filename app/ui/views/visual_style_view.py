from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel,QPushButton,QVBoxLayout,QWidget
class VisualStyleView(QWidget):
 editRequested=Signal()
 def __init__(self):
  super().__init__();layout=QVBoxLayout(self);title=QLabel('Visual Style Settings Editor');title.setObjectName('pageTitle');info=QLabel('Edit lyric highlighting, fonts, colors, positions, title-card motion, background motion and watermark styling, then re-render without repeating AI separation or transcription.');info.setWordWrap(True);button=QPushButton('Edit Visual Style');button.clicked.connect(self.editRequested);layout.addWidget(title);layout.addWidget(info);layout.addWidget(button);layout.addStretch()
