from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout,QLabel,QWidget
from app.domain.models.workflow import WorkflowState,WorkflowStep

_LABELS=("Import","Separate","Lyrics","Review","Style","Render","Export")
class WorkflowHeader(QWidget):
    def __init__(self)->None:
        super().__init__();self.setObjectName("workflowHeader");layout=QHBoxLayout(self);layout.setContentsMargins(18,10,18,10);self._labels=[]
        for i,text in enumerate(_LABELS):
            label=QLabel(f"{i+1}  {text}");label.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(label);self._labels.append(label)
            if i<len(_LABELS)-1:arrow=QLabel("›");arrow.setObjectName("muted");layout.addWidget(arrow)
        self.set_state(WorkflowState())
    def set_state(self,state:WorkflowState)->None:
        for i,label in enumerate(self._labels):
            step=WorkflowStep(i)
            if step in state.completed: label.setStyleSheet("color:#45D483;font-weight:600")
            elif step==state.current: label.setStyleSheet("color:#68A0FF;font-weight:700")
            else: label.setStyleSheet("color:#718096")
