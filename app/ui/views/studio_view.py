from __future__ import annotations
from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QFrame,QHBoxLayout,QLabel,QSplitter,QVBoxLayout,QWidget
from app.domain.models.media import MediaAsset
from app.domain.models.workflow import WorkflowState
from app.ui.widgets.creation_wizard import CreationWizard
from app.ui.widgets.timeline_widget import TimelineWidget
from app.ui.widgets.video_preview import VideoPreview
from app.ui.widgets.workflow_header import WorkflowHeader

class StudioView(QWidget):
    importRequested=Signal();playRequested=Signal();stopRequested=Signal();seekRequested=Signal(int);separateRequested=Signal();lyricsRequested=Signal();renderRequested=Signal();autoCreateRequested=Signal(str);modeRequested=Signal(str);retryRequested=Signal();cancelRequested=Signal()
    def __init__(self)->None:
        super().__init__();root=QVBoxLayout(self);root.setContentsMargins(18,14,18,14);self.header=WorkflowHeader();root.addWidget(self.header)
        heading=QHBoxLayout();title=QLabel("Create Karaoke Video");title.setObjectName("pageTitle");subtitle=QLabel("Import once, choose a style, and let Karaoke AI Studio do the rest.");subtitle.setObjectName("muted");heading.addWidget(title);heading.addStretch();heading.addWidget(subtitle);root.addLayout(heading)
        preview_frame=QFrame();preview_frame.setObjectName("panel");pl=QVBoxLayout(preview_frame);self.preview=VideoPreview();pl.addWidget(self.preview)
        self.wizard=CreationWizard();self.wizard.importRequested.connect(self.importRequested);self.wizard.createRequested.connect(lambda:self.autoCreateRequested.emit(self.wizard.style.currentText()));self.wizard.modeRequested.connect(self.modeRequested);self.wizard.retryRequested.connect(self.retryRequested);self.wizard.cancelRequested.connect(self.cancelRequested)
        split=QSplitter(Qt.Orientation.Horizontal);split.addWidget(preview_frame);split.addWidget(self.wizard);split.setStretchFactor(0,1);split.setSizes([900,320]);root.addWidget(split,1)
        self.timeline=TimelineWidget();self.timeline.playRequested.connect(self.playRequested);self.timeline.stopRequested.connect(self.stopRequested);self.timeline.seekRequested.connect(self.seekRequested);root.addWidget(self.timeline)
    def show_asset(self,asset:MediaAsset)->None:self.preview.show_asset(asset)
    def set_workflow_state(self,state:WorkflowState)->None:self.header.set_state(state);self.wizard.set_state(state)
