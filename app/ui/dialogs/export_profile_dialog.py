from __future__ import annotations

from uuid import uuid4
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox,QDialog,QDialogButtonBox,QFormLayout,QLineEdit,QSpinBox,QVBoxLayout
from app.domain.models.export_profile import ExportProfile
from app.domain.models.video_render import RenderEncoder,VideoCodec,VideoContainer


class ExportProfileDialog(QDialog):
    profileCreated=Signal(object)
    def __init__(self,parent:object=None)->None:
        super().__init__(parent);self.setWindowTitle("Create Export Profile");self.setMinimumWidth(470)
        self.name=QLineEdit();self.description=QLineEdit();self.codec=QComboBox();self.codec.addItem("H.264","h264");self.codec.addItem("HEVC / H.265","hevc");self.container=QComboBox();self.container.addItem("MP4","mp4");self.container.addItem("MKV","mkv");self.encoder=QComboBox();[self.encoder.addItem(x.title(),x) for x in ("software","nvidia","intel","amd")];self.resolution=QComboBox();self.resolution.addItem("1280x720",(1280,720));self.resolution.addItem("1920x1080",(1920,1080));self.resolution.addItem("3840x2160",(3840,2160));self.resolution.setCurrentIndex(1);self.fps=QComboBox();[self.fps.addItem(str(x),x) for x in (24,25,30,50,60)];self.fps.setCurrentText("30");self.quality=QSpinBox();self.quality.setRange(0,51);self.quality.setValue(20);self.audio=QSpinBox();self.audio.setRange(96,512);self.audio.setValue(320);self.audio.setSuffix(" kbps")
        form=QFormLayout();form.addRow("Profile name",self.name);form.addRow("Description",self.description);form.addRow("Codec",self.codec);form.addRow("Container",self.container);form.addRow("Preferred encoder",self.encoder);form.addRow("Resolution",self.resolution);form.addRow("Frame rate",self.fps);form.addRow("Quality",self.quality);form.addRow("Audio bitrate",self.audio);buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self._save);buttons.rejected.connect(self.reject);layout=QVBoxLayout(self);layout.addLayout(form);layout.addWidget(buttons)
    def _save(self)->None:
        width,height=self.resolution.currentData();profile=ExportProfile("user."+uuid4().hex,self.name.text(),self.description.text(),VideoCodec(str(self.codec.currentData())),VideoContainer(str(self.container.currentData())),RenderEncoder(str(self.encoder.currentData())),width,height,int(self.fps.currentData()),self.quality.value(),self.audio.value());self.profileCreated.emit(profile);self.accept()
