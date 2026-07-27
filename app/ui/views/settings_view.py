from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import QSettings,Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QCheckBox,QComboBox,QFileDialog,QFormLayout,QFrame,QGroupBox,QHBoxLayout,QLabel,QLineEdit,QMessageBox,QPushButton,QScrollArea,QSpinBox,QVBoxLayout,QWidget
from app.core.config import Settings
from app.core.paths import AppPaths
class SettingsView(QWidget):
    settingsApplied=Signal(dict)
    def __init__(self,settings:Settings,paths:AppPaths)->None:
        super().__init__();self._store=QSettings(settings.application.organization,settings.application.name);self._defaults={'theme':settings.appearance.theme,'export':str(paths.export_dir),'cache':str(paths.cache_dir),'device':'Automatic','workers':2,'hardware':True};self._dirty=False
        title=QLabel('Settings');title.setObjectName('pageTitle');subtitle=QLabel('Changes are previewed immediately. Save to use them on the next launch.');subtitle.setObjectName('muted');self.status=QLabel('Settings loaded');self.status.setObjectName('muted')
        appearance=QGroupBox('Appearance');af=QFormLayout(appearance);self.theme=QComboBox();self.theme.addItems(('Dark','Light'));self.theme.setCurrentText(str(self._store.value('app/theme',self._defaults['theme'])).title());language=QComboBox();language.addItem('English (United States)','en-US');af.addRow('Theme',self.theme);af.addRow('Language',language)
        processing=QGroupBox('Processing');pf=QFormLayout(processing);self.device=QComboBox();self.device.addItems(('Automatic','CPU','NVIDIA CUDA'));self.device.setCurrentText(str(self._store.value('app/device','Automatic')));self.workers=QSpinBox();self.workers.setRange(1,32);self.workers.setValue(self._safe_int(self._store.value('app/workers',2),2));self.hardware=QCheckBox('Prefer hardware video encoding when available');self.hardware.setChecked(str(self._store.value('app/hardware','true')).lower()=='true');pf.addRow('Compute device',self.device);pf.addRow('Concurrent jobs',self.workers);pf.addRow('Video encoding',self.hardware)
        storage=QGroupBox('Storage');sf=QFormLayout(storage);self.export_path=QLineEdit(str(self._store.value('app/exportDir',self._defaults['export'])));self.cache_path=QLineEdit(str(self._store.value('app/cacheDir',self._defaults['cache'])));sf.addRow('Export directory',self._folder_row(self.export_path,'Choose export directory'));sf.addRow('Cache directory',self._folder_row(self.cache_path,'Choose cache directory'))
        self.save=QPushButton('Save Settings');self.save.setObjectName('primaryButton');self.save.clicked.connect(self._save);reset=QPushButton('Restore Defaults');reset.clicked.connect(self._reset);buttons=QHBoxLayout();buttons.addWidget(reset);buttons.addStretch();buttons.addWidget(self.save)
        for control in (self.theme,self.device,self.workers,self.hardware,self.export_path,self.cache_path):
            signal=getattr(control,'currentTextChanged',None) or getattr(control,'valueChanged',None) or getattr(control,'toggled',None) or getattr(control,'textChanged',None);signal.connect(self._changed)
        self.theme.currentTextChanged.connect(lambda value:self.settingsApplied.emit({'preview_theme':value.lower()}))
        content=QWidget();cl=QVBoxLayout(content);cl.addWidget(appearance);cl.addWidget(processing);cl.addWidget(storage);cl.addWidget(self.status);cl.addStretch();cl.addLayout(buttons);scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QFrame.Shape.NoFrame);scroll.setWidget(content);root=QVBoxLayout(self);root.setContentsMargins(22,18,22,18);root.addWidget(title);root.addWidget(subtitle);root.addWidget(scroll,1)
    @staticmethod
    def _safe_int(value,default):
        try:return int(value)
        except (TypeError,ValueError):return default
    def _folder_row(self,edit,title):
        row=QHBoxLayout();browse=QPushButton('Browse...');open_=QPushButton('Open Folder');browse.clicked.connect(lambda:self._browse(edit,title));open_.clicked.connect(lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(edit.text())));row.addWidget(edit,1);row.addWidget(browse);row.addWidget(open_);return row
    def _browse(self,edit,title):
        path=QFileDialog.getExistingDirectory(self,title,edit.text());
        if path:edit.setText(path)
    def _changed(self,*_):self._dirty=True;self.status.setText('Unsaved changes');self.status.setStyleSheet('color:#F6C85F;font-weight:600')
    def _save(self):
        try:
            export=Path(self.export_path.text()).expanduser();cache=Path(self.cache_path.text()).expanduser();export.mkdir(parents=True,exist_ok=True);cache.mkdir(parents=True,exist_ok=True)
            for folder in (export,cache):
                probe=folder/'.karaoke_write_test';probe.write_text('ok');probe.unlink()
            values={'theme':self.theme.currentText().lower(),'export_dir':str(export),'cache_dir':str(cache),'device':self.device.currentText(),'workers':self.workers.value(),'hardware':self.hardware.isChecked()}
            for key,value in values.items():self._store.setValue('app/'+({'export_dir':'exportDir','cache_dir':'cacheDir'}.get(key,key)),value)
            self._store.sync();self._dirty=False;self.status.setText('Settings saved');self.status.setStyleSheet('color:#45D483;font-weight:600');self.settingsApplied.emit(values)
        except OSError as exc:QMessageBox.warning(self,'Could Not Save Settings',f'The selected folder is not writable.\n\n{exc}')
    def _reset(self):
        self.theme.setCurrentText(self._defaults['theme'].title());self.device.setCurrentText('Automatic');self.workers.setValue(2);self.hardware.setChecked(True);self.export_path.setText(self._defaults['export']);self.cache_path.setText(self._defaults['cache']);self._changed()
