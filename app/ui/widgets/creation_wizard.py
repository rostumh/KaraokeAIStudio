from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox,QFrame,QLabel,QProgressBar,QPushButton,QVBoxLayout
from app.domain.models.workflow import WorkflowState,WorkflowStep

_LABELS=("Import media","AI separation","Generate lyrics","Review and save lyrics","Choose visual style","Render video","Export files")
_STYLES=(
 ("Modern Clean","Warm white lyrics with golden highlighting, strong contrast and a clear modern font."),
 ("Classic Highlight","Familiar high-contrast karaoke highlighting; easy to read."),
 ("Minimal Clean","Simple typography with subtle highlighting and fewer effects."),
 ("Bold Pop","Large energetic text with vivid colors for upbeat songs."),
)
class CreationWizard(QFrame):
    importRequested=Signal();createRequested=Signal();retryRequested=Signal();cancelRequested=Signal();modeRequested=Signal(str)
    def __init__(self)->None:
        super().__init__();self.setObjectName("card");self.setMinimumWidth(340);layout=QVBoxLayout(self);title=QLabel("Create Karaoke Video");title.setObjectName("sectionTitle");layout.addWidget(title)
        intro=QLabel("Follow the highlighted step. Completed items are saved automatically.");intro.setWordWrap(True);intro.setObjectName("muted");layout.addWidget(intro)
        self.mode=QComboBox();self.mode.addItem("Auto Mode — recommended","auto");self.mode.addItem("Professional Mode","professional");self.mode.currentIndexChanged.connect(lambda:self.modeRequested.emit(str(self.mode.currentData())));layout.addWidget(self.mode)
        self.steps=[]
        for text in _LABELS:label=QLabel(text);label.setWordWrap(True);layout.addWidget(label);self.steps.append(label)
        style_label=QLabel("Choose the lyric appearance");style_label.setObjectName("sectionTitle");layout.addWidget(style_label)
        self.style=QComboBox()
        for name,description in _STYLES:self.style.addItem(name,name)
        layout.addWidget(self.style)
        self.style_description=QLabel();self.style_description.setWordWrap(True);self.style_description.setObjectName("muted");layout.addWidget(self.style_description);self.style.currentIndexChanged.connect(self._describe_style);self._describe_style()
        self.operation=QLabel("Choose a song or video");self.operation.setWordWrap(True);layout.addWidget(self.operation);self.progress=QProgressBar();self.progress.setRange(0,100);layout.addWidget(self.progress)
        self.import_button=QPushButton("1. Import Song or Video");self.import_button.clicked.connect(self.importRequested);layout.addWidget(self.import_button)
        self.create_button=QPushButton("Start Automatic Creation");self.create_button.setObjectName("primaryButton");self.create_button.setEnabled(False);self.create_button.clicked.connect(self.createRequested);layout.addWidget(self.create_button)
        self.retry_button=QPushButton("Retry Current Step");self.retry_button.hide();self.retry_button.clicked.connect(self.retryRequested);layout.addWidget(self.retry_button)
        self.cancel_button=QPushButton("Stop Current Task");self.cancel_button.hide();self.cancel_button.clicked.connect(self.cancelRequested);layout.addWidget(self.cancel_button);layout.addStretch(1);self.set_state(WorkflowState())
    def _describe_style(self)->None:
        self.style_description.setText(_STYLES[self.style.currentIndex()][1])
    def set_state(self,state:WorkflowState)->None:
        for i,label in enumerate(self.steps):
            step=WorkflowStep(i);prefix="✓" if step in state.completed else "▶" if step==state.current else "○";color="#45D483" if step in state.completed else "#68A0FF" if step==state.current else "#718096";label.setText(f"{prefix}  {i+1}. {_LABELS[i]}");label.setStyleSheet(f"color:{color};padding:3px")
        self.operation.setText(state.error or state.operation);self.progress.setVisible(state.running);self.progress.setValue(state.progress);self.cancel_button.setVisible(state.running);self.retry_button.setVisible(bool(state.error));self.import_button.setEnabled(not state.running)
        ready=not state.running and WorkflowStep.IMPORT in state.completed;self.create_button.setEnabled(ready);self.style.setEnabled(not state.running)
        if state.current==WorkflowStep.STYLE:self.create_button.setText("Continue to Render with Selected Style")
        elif WorkflowStep.IMPORT not in state.completed:self.create_button.setText("Import a Song First")
        elif state.running:self.create_button.setText("Working...")
        else:self.create_button.setText("Start Automatic Creation")
