from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel,QPushButton,QVBoxLayout,QWidget
class RenderSettingsView(QWidget):
 editRequested=Signal()
 def __init__(self):
  super().__init__();layout=QVBoxLayout(self);title=QLabel('Render Video Settings Editor');title.setObjectName('pageTitle');info=QLabel('Set title card, output size, filename, mastering and delivery options. Settings remain editable after every render.');info.setWordWrap(True);button=QPushButton('Open Render Settings');button.clicked.connect(self.editRequested);layout.addWidget(title);layout.addWidget(info);layout.addWidget(button);layout.addStretch()
