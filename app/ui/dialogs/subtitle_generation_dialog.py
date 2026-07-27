from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QCheckBox,QColorDialog,QComboBox,QDialog,QDialogButtonBox,QDoubleSpinBox,QFormLayout,QHBoxLayout,QLabel,QPushButton,QSpinBox,QVBoxLayout
from app.domain.models.subtitles import SubtitleFormat,SubtitleOptions,SubtitleStyle

class SubtitleGenerationDialog(QDialog):
    generationRequested=Signal(object)
    def __init__(self,source_name:str,destination:Path,parent:object=None)->None:
        super().__init__(parent);self.setWindowTitle("Generate Subtitles");self.setMinimumWidth(590);self._destination=destination
        self.ass=QCheckBox("ASS karaoke");self.ass.setChecked(True);self.srt=QCheckBox("SRT captions");self.srt.setChecked(True);self.lrc=QCheckBox("LRC lyrics")
        formats=QHBoxLayout();[formats.addWidget(w) for w in (self.ass,self.srt,self.lrc)]
        self.words=QSpinBox();self.words.setRange(1,20);self.words.setValue(7);self.duration=QDoubleSpinBox();self.duration.setRange(.5,20);self.duration.setValue(5);self.duration.setSuffix(" s");self.gap=QDoubleSpinBox();self.gap.setRange(0,10);self.gap.setValue(.8);self.gap.setSuffix(" s");self.lead_in=QDoubleSpinBox();self.lead_in.setRange(0,2);self.lead_in.setValue(.15);self.lead_in.setSuffix(" s");self.lead_out=QDoubleSpinBox();self.lead_out.setRange(0,2);self.lead_out.setValue(.25);self.lead_out.setSuffix(" s")
        self.resolution=QComboBox();self.resolution.addItem("1920×1080",(1920,1080));self.resolution.addItem("1280×720",(1280,720));self.resolution.addItem("3840×2160",(3840,2160));self.font=QComboBox();self.font.addItems(("Arial","Segoe UI","Tahoma","Verdana"));self.size=QSpinBox();self.size.setRange(16,160);self.size.setValue(54);self.margin=QSpinBox();self.margin.setRange(0,500);self.margin.setValue(54);self.bold=QCheckBox("Bold");self.bold.setChecked(True)
        self.primary="#FFFFFF";self.highlight="#00D7FF";self.outline="#000000";primary=QPushButton("Normal Color");highlight=QPushButton("Highlight Color");outline=QPushButton("Outline Color");primary.clicked.connect(lambda:self._choose("primary"));highlight.clicked.connect(lambda:self._choose("highlight"));outline.clicked.connect(lambda:self._choose("outline"));colors=QHBoxLayout();[colors.addWidget(w) for w in (primary,highlight,outline)]
        form=QFormLayout();form.addRow("Source",QLabel(source_name));form.addRow("Formats",formats);form.addRow("Maximum words per cue",self.words);form.addRow("Maximum cue duration",self.duration);form.addRow("New cue after gap",self.gap);form.addRow("Lead in",self.lead_in);form.addRow("Lead out",self.lead_out);form.addRow("Video resolution",self.resolution);form.addRow("ASS font",self.font);form.addRow("ASS font size",self.size);form.addRow("Bottom margin",self.margin);form.addRow("Weight",self.bold);form.addRow("ASS colors",colors);form.addRow("Output folder",QLabel(str(destination)))
        self.status=QLabel("ASS includes per-word karaoke timing; SRT and LRC contain cue-level text.");self.status.setWordWrap(True);self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Generate Subtitles");self.buttons.accepted.connect(self._submit);self.buttons.rejected.connect(self.reject);layout=QVBoxLayout(self);layout.addLayout(form);layout.addWidget(self.status);layout.addWidget(self.buttons)
    def _choose(self,name:str)->None:
        current=getattr(self,name);color=QColorDialog.getColor(QColor(current),self,"Choose Subtitle Color")
        if color.isValid():setattr(self,name,color.name().upper())
    def _submit(self)->None:
        formats=tuple(fmt for enabled,fmt in ((self.ass.isChecked(),SubtitleFormat.ASS),(self.srt.isChecked(),SubtitleFormat.SRT),(self.lrc.isChecked(),SubtitleFormat.LRC)) if enabled);width,height=self.resolution.currentData();style=SubtitleStyle(self.font.currentText(),self.size.value(),self.primary,self.highlight,self.outline,3.0,1.5,self.margin.value(),self.bold.isChecked(),2);options=SubtitleOptions(formats,self.words.value(),self.duration.value(),self.gap.value(),self.lead_in.value(),self.lead_out.value(),width,height,style);self.generationRequested.emit(options)
    def show_error(self,message:str)->None:self.status.setText(message)
