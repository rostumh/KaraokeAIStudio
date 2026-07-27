from __future__ import annotations

import random
from pathlib import Path
from PySide6.QtCore import QSettings, Signal, QTimer
from PySide6.QtWidgets import (QAbstractSpinBox,QCheckBox,QComboBox,QDialog,QDialogButtonBox,QFileDialog,QFormLayout,QHBoxLayout,QLabel,QLineEdit,QProgressBar,QPushButton,QSpinBox,QVBoxLayout,QScrollArea,QWidget,QDoubleSpinBox)
from app.domain.models.export_profile import ExportProfile
from app.domain.models.video_render import RenderEncoder,VideoCodec,VideoContainer,VideoRenderRequest,VideokePresentation
from app.application.services.song_metadata_service import OnlineSongMetadataService

_MEDIA={'.mp4','.mkv','.mov','.avi','.webm','.jpg','.jpeg','.png','.webp','.bmp'}
class VideoRenderDialog(QDialog):
    renderRequested=Signal(object);cancelRequested=Signal();createProfileRequested=Signal()
    def __init__(self,duration:float,default_dir:Path,encoders:tuple[str,...],profiles:tuple[ExportProfile,...]=(),parent:object=None,default_audio:Path|None=None,default_subtitle:Path|None=None,default_source:Path|None=None)->None:
        super().__init__(parent);self.duration=duration;self._source_path=default_source;self._profiles={p.profile_id:p for p in profiles};self._settings=QSettings('KaraokeAIStudio','KaraokeAIStudio');self.setWindowTitle('Render Karaoke Video');self.setMinimumWidth(760);self.resize(860,760);self.setMaximumHeight(900)
        intro=QLabel('Required project files are filled automatically. Choose a background source, review the summary, then render.');intro.setWordWrap(True)
        self.profile=QComboBox();self.profile.addItem('Recommended settings',None)
        for p in profiles:self.profile.addItem(p.name,p.profile_id)
        new_profile=QPushButton('Save as profile...');new_profile.clicked.connect(self.createProfileRequested);profile_row=QHBoxLayout();profile_row.addWidget(self.profile,1);profile_row.addWidget(new_profile)
        self.background_mode=QComboBox();self.background_mode.addItem('Single video or image','file');self.background_mode.addItem('Random item from a folder','folder');self.background_mode.addItem('Built-in AI-style animated background','ai')
        self.background=QLineEdit();self.background.setPlaceholderText('Choose a video, image, or background folder')
        self.audio=QLineEdit(str(default_audio or ''));self.audio.setReadOnly(True);self.audio.setPlaceholderText('Created automatically after vocal separation')
        self.subtitle=QLineEdit(str(default_subtitle or ''));self.subtitle.setReadOnly(True);self.subtitle.setPlaceholderText('Created automatically from reviewed lyrics')
        self.song_title=QLineEdit();self.artist=QLineEdit();self.songwriter=QLineEdit();self.release_year=QLineEdit();self.cta=QLineEdit('Please Subscribe to Our Channel');self.countdown=QCheckBox('Show countdown');self.countdown.setChecked(True);self.countdown_start=QSpinBox();self.countdown_start.setRange(1,10);self.countdown_start.setValue(3);self.countdown_start.setSuffix(' to 1');self.countdown_seconds=QDoubleSpinBox();self.countdown_seconds.setRange(1.0,15.0);self.countdown_seconds.setSingleStep(.5);self.countdown_seconds.setValue(3.0);self.countdown_seconds.setSuffix(' seconds total');self.countdown_style=QComboBox();self.countdown_style.addItem('Bounce / pulse','bounce');self.countdown_style.addItem('Smooth scale','scale');self.countdown_style.addItem('Soft fade','fade');self.ambient=QCheckBox('Subtle ambient background motion');self.ambient.setChecked(True);self.watermark=QLineEdit();self.watermark_text=QLineEdit();self.watermark_text.setPlaceholderText('Optional channel name or @handle');self.watermark_position=QComboBox();[self.watermark_position.addItem(a,b) for a,b in (('Bottom right','bottom-right'),('Bottom left','bottom-left'),('Top right','top-right'),('Top left','top-left'),('Center','center'))];self.watermark_opacity=QSpinBox();self.watermark_opacity.setRange(10,100);self.watermark_opacity.setValue(75);self.watermark_opacity.setSuffix('%')
        self.output=QLineEdit(str(default_dir/'karaoke_video.mp4'));self.codec=QComboBox();self.codec.addItem('H.264 (recommended)',VideoCodec.H264.value);self.codec.addItem('HEVC / H.265',VideoCodec.HEVC.value);self.container=QComboBox();self.container.addItem('MP4',VideoContainer.MP4.value);self.container.addItem('MKV',VideoContainer.MKV.value);self.encoder=QComboBox()
        if any('nvenc' in x for x in encoders):self.encoder.addItem('NVIDIA NVENC (recommended)',RenderEncoder.NVIDIA.value)
        if any('qsv' in x for x in encoders):self.encoder.addItem('Intel Quick Sync (recommended)',RenderEncoder.INTEL.value)
        if any('amf' in x for x in encoders):self.encoder.addItem('AMD AMF (recommended)',RenderEncoder.AMD.value)
        self.encoder.addItem('Software fallback',RenderEncoder.SOFTWARE.value)
        self.resolution=QComboBox();self.resolution.addItem('4K UHD - Computer / TV (3840 x 2160)',(3840,2160));self.resolution.addItem('Full HD - Computer / TV (1920 x 1080)',(1920,1080));self.resolution.addItem('HD - Computer / TV, smaller file (1280 x 720)',(1280,720));self.resolution.addItem('Vertical Full HD - TikTok / Reels / Shorts (1080 x 1920)',(1080,1920));self.resolution.addItem('Vertical HD - Social Media Lite (720 x 1280)',(720,1280));self.resolution.addItem('Vertical 4K - TikTok / Reels / Shorts (2160 x 3840)',(2160,3840));self.resolution.setCurrentIndex(1);self.fps=QComboBox();[self.fps.addItem(str(x),x) for x in (24,25,30,50,60)];self.fps.setCurrentText('30');self.quality=QSpinBox();self.quality.setRange(0,51);self.quality.setValue(20);self.audio_bitrate=QSpinBox();self.audio_bitrate.setRange(96,512);self.audio_bitrate.setValue(320);self.audio_bitrate.setSuffix(' kbps');self.overwrite=QCheckBox('Replace existing destination');self.lyric_size=QSpinBox();self.lyric_size.setRange(32,160);self.lyric_size.setValue(112);self.lyric_size.setSuffix(' px');self.lyric_position=QComboBox();self.lyric_position.addItem('Center (recommended)','center');self.lyric_position.addItem('Slightly below center','lower-center');self.lyric_position.addItem('Bottom safe area','bottom')
        form=QFormLayout();self.metadata_button=QPushButton('Identify Song Intelligently');self.metadata_button.clicked.connect(self._autofill_metadata);form.addRow('Song information',self.metadata_button);form.addRow('Song title',self.song_title);form.addRow('Artist',self.artist);form.addRow('Songwriter credit',self.songwriter);form.addRow('Release year',self.release_year);form.addRow('Title card',QLabel('Automatic: starts at 00:00 and fades immediately before countdown'));form.addRow('Countdown',self.countdown);form.addRow('Countdown animation',self.countdown_style);form.addRow('End call-to-action',self.cta);form.addRow('Background motion',self.ambient);form.addRow('Export profile',profile_row);form.addRow('Background source',self.background_mode);form.addRow('Background location',self._background_row());form.addRow('Instrumental audio (automatic)',self.audio);form.addRow('ASS subtitles (automatic)',self.subtitle);form.addRow('Watermark logo (optional)',self._path_row(self.watermark,'Watermark',False));form.addRow('Text watermark (optional)',self.watermark_text);form.addRow('Watermark position',self.watermark_position);form.addRow('Watermark opacity',self.watermark_opacity);form.addRow('Destination',self._path_row(self.output,'Output',True));form.addRow('Codec',self.codec);form.addRow('Container',self.container);form.addRow('Encoder',self.encoder);form.addRow('Resolution',self.resolution);form.addRow('Frame rate',self.fps);form.addRow('Quality',self.quality);form.addRow('Audio bitrate',self.audio_bitrate);form.addRow('Lyric text size',self.lyric_size);form.addRow('Subtitle position',self.lyric_position);form.addRow('Overwrite',self.overwrite)
        self.status=QLabel();self.status.setWordWrap(True);self.progress=QProgressBar();self.progress.setRange(0,100);self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText('Render Video');self.buttons.accepted.connect(self._submit);self.buttons.rejected.connect(self._cancel)
        content=QWidget();content.setLayout(form);scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QScrollArea.Shape.NoFrame);scroll.setWidget(content);layout=QVBoxLayout(self);layout.setContentsMargins(10,10,10,10);layout.setSpacing(6);layout.addWidget(intro);layout.addWidget(scroll,1);layout.addWidget(self.status);layout.addWidget(self.progress);layout.addWidget(self.buttons)
        [w.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows) for w in self.findChildren(QAbstractSpinBox)];[w.setAccelerated(True) for w in self.findChildren(QAbstractSpinBox)];self.container.currentIndexChanged.connect(self._extension);self.profile.currentIndexChanged.connect(self._apply_profile);self.background_mode.currentIndexChanged.connect(self._background_mode_changed);self._restore();self._background_mode_changed();self._update_summary();QTimer.singleShot(250,self._autofill_metadata)
    def _safe_name(self,text):
        import re
        return re.sub(r'[^A-Za-z0-9._-]+','_',text.strip()).strip('_')
    def _refresh_output_name(self):
        title=self._safe_name(self.song_title.text());artist=self._safe_name(self.artist.text());parts=[x for x in (artist,title,'videoke') if x];name='_'.join(parts)+'.'+str(self.container.currentData());self.output.setText(str(Path(self.output.text()).with_name(name)))
    def _autofill_metadata(self):
        self.metadata_button.setText('Searching verified music metadata...');result=OnlineSongMetadataService().lookup(self._source_path or (Path(self.audio.text()) if self.audio.text() else None),self.song_title.text(),self.artist.text(),self.duration)
        # Always apply safe filename/tag-derived title and artist; online confidence only governs verified extras.
        if result.title:self.song_title.setText(result.title)
        if result.artist:self.artist.setText(result.artist)
        if result.confidence>=72 and result.songwriter:self.songwriter.setText(result.songwriter)
        if result.confidence>=72 and result.release_year:self.release_year.setText(result.release_year)
        self.metadata_button.setText('Identify Song Intelligently');self.status.setText(result.message);self._refresh_output_name()
    def _background_row(self):
        row=QHBoxLayout();button=QPushButton('Browse...');button.clicked.connect(self._browse_background);row.addWidget(self.background,1);row.addWidget(button);return row
    def _browse_background(self):
        if self.background_mode.currentData()=='folder':path=QFileDialog.getExistingDirectory(self,'Background folder',self.background.text())
        else:path,_=QFileDialog.getOpenFileName(self,'Background video or image',self.background.text(),'Backgrounds (*.mp4 *.mkv *.mov *.avi *.webm *.jpg *.jpeg *.png *.webp *.bmp)')
        if path:self.background.setText(path);self._update_summary()
    def _background_mode_changed(self):
        ai=self.background_mode.currentData()=='ai';self.background.setEnabled(not ai)
        if ai:self.background.setText('Built-in cinematic dynamic lights (generated locally)')
        elif self.background.text().startswith('Built-in'):self.background.clear()
        self._update_summary()
    def _path_row(self,edit,label,save):
        row=QHBoxLayout();button=QPushButton('Browse...');button.clicked.connect(lambda:self._browse(edit,label,save));row.addWidget(edit,1);row.addWidget(button);return row
    def _browse(self,edit,label,save):
        path,_=(QFileDialog.getSaveFileName(self,label,edit.text(),'Video (*.mp4 *.mkv)') if save else QFileDialog.getOpenFileName(self,label,edit.text(),'Media (*.*)'))
        if path:edit.setText(path)
    def _restore(self):
        mode=str(self._settings.value('render/backgroundMode','file'));i=self.background_mode.findData(mode);self.background_mode.setCurrentIndex(max(0,i));self.background.setText(str(self._settings.value('render/backgroundPath','')));self.watermark.setText(str(self._settings.value('render/watermark','')));self.watermark_text.setText(str(self._settings.value('render/watermarkText','')));self.overwrite.setChecked(str(self._settings.value('render/overwrite','false')).lower()=='true');self.lyric_size.setValue(int(self._settings.value('render/lyricSize',112)))
    def _save(self):
        self._settings.setValue('render/backgroundMode',self.background_mode.currentData());self._settings.setValue('render/backgroundPath',self.background.text());self._settings.setValue('render/watermark',self.watermark.text());self._settings.setValue('render/watermarkText',self.watermark_text.text());self._settings.setValue('render/overwrite',self.overwrite.isChecked());self._settings.setValue('render/lyricSize',self.lyric_size.value());self._settings.sync()
    def _resolve_background(self)->Path:
        mode=self.background_mode.currentData()
        if mode=='ai':return Path('__generated_aurora__')
        path=Path(self.background.text())
        if mode=='folder':
            files=[p for p in path.iterdir() if p.is_file() and p.suffix.lower() in _MEDIA] if path.is_dir() else []
            if not files:raise ValueError('The selected background folder contains no supported video or image files.')
            return random.SystemRandom().choice(files)
        return path
    def _update_summary(self):
        missing=[]
        if not self.audio.text():missing.append('instrumental audio')
        if not self.subtitle.text():missing.append('ASS subtitles')
        self.status.setText('Ready to render.' if not missing else 'Complete the workflow first; missing: '+', '.join(missing)+'.')
    def refresh_profiles(self,profiles):self._profiles={p.profile_id:p for p in profiles}
    def _apply_profile(self):
        p=self._profiles.get(self.profile.currentData())
        if not p:return
        for w,v in ((self.codec,p.codec.value),(self.container,p.container.value),(self.encoder,p.encoder.value),(self.resolution,(p.width,p.height)),(self.fps,p.frame_rate)):
            i=w.findData(v)
            if i>=0:w.setCurrentIndex(i)
        self.quality.setValue(p.quality);self.audio_bitrate.setValue(p.audio_bitrate_kbps)
    def _extension(self):self.output.setText(str(Path(self.output.text()).with_suffix('.'+str(self.container.currentData()))))
    def _styled_subtitle(self)->Path:
        source=Path(self.subtitle.text())
        text=source.read_text(encoding='utf-8-sig')
        lines=[]
        for line in text.splitlines():
            if line.startswith('Style: Karaoke,'):
                fields=line.split(',')
                if len(fields)>21:
                    fields[2]=str(self.lyric_size.value());positions={'center':500,'lower-center':390,'bottom':150};fields[21]=str(positions.get(str(self.lyric_position.currentData()),500));line=','.join(fields)
            lines.append(line)
        target=Path(self.output.text()).with_name(Path(self.output.text()).stem+'_lyrics.ass')
        target.parent.mkdir(parents=True,exist_ok=True);
        import hashlib
        source_id=''
        if self._source_path and self._source_path.is_file():
            stat=self._source_path.stat();source_id=hashlib.sha256(f'{self._source_path.resolve()}|{stat.st_size}|{stat.st_mtime_ns}'.encode()).hexdigest()
        lines.insert(0,f'; KaraokeAIStudio-Source-ID: {source_id}')
        target.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        return target
    @staticmethod
    def _safe_int(value,default,label,repairs):
        try:
            result=int(value)
            if result<=0:raise ValueError
            return result
        except (TypeError,ValueError):repairs.append(f'{label} was unavailable and was changed to {default}.');return default
    def _submit(self):
        repairs=[]
        try:bg=self._resolve_background()
        except (ValueError,OSError) as exc:self.show_error('Background setting needs attention: '+str(exc)+' Suggested fix: choose a supported image/video or Built-in background.');return
        audio=Path(self.audio.text());subtitle=Path(self.subtitle.text());output=Path(self.output.text())
        problems=[]
        if not audio.is_file():problems.append('Instrumental audio is missing. Run Separate Vocals first.')
        if not subtitle.is_file():problems.append('ASS subtitles are missing. Save reviewed lyrics first.')
        if output.suffix.lower() not in ('.mp4','.mkv'):problems.append('Destination must end in .mp4 or .mkv.')
        if problems:self.show_error('Cannot render yet:\n• '+'\n• '.join(problems));return
        fps=self._safe_int(self.fps.currentData(),30,'Frame rate',repairs);w,h=self.resolution.currentData() if isinstance(self.resolution.currentData(),tuple) else (3840,2160)
        if not isinstance(w,int) or not isinstance(h,int):w,h=3840,2160;repairs.append('Resolution was invalid and was changed to 4K UHD.')
        self._refresh_output_name();self._save()
        if self._source_path is None or not self._source_path.is_file():self.show_error('Current source song is unavailable. Re-import the song before rendering.');return
        try:styled_subtitle=self._styled_subtitle()
        except (OSError,UnicodeError) as exc:self.show_error(f'Subtitles could not be prepared: {exc}. Save the lyrics again, then retry.');return
        if repairs:self.status.setText('Automatically repaired settings: '+' '.join(repairs))
        r=VideoRenderRequest(bg,audio,styled_subtitle,Path(self.output.text()),max(1.0,float(self.duration)),w,h,fps,VideoCodec(str(self.codec.currentData())),VideoContainer(str(self.container.currentData())),RenderEncoder(str(self.encoder.currentData())),self.quality.value(),self.audio_bitrate.value(),self.overwrite.isChecked(),Path(self.watermark.text()) if self.watermark.text().strip() else None,str(self.watermark_position.currentData()),self.watermark_opacity.value(),self.watermark_text.text().strip(),VideokePresentation(title=self.song_title.text(),artist=self.artist.text(),songwriter=self.songwriter.text(),release_year=self.release_year.text(),title_duration=0.0,countdown_duration=float(self.countdown_seconds.value()),countdown_enabled=self.countdown.isChecked(),countdown_style=str(self.countdown_style.currentData()),countdown_start=self.countdown_start.value(),cta_text=self.cta.text(),lyric_font_size=self.lyric_size.value(),ambient_motion=self.ambient.isChecked()))
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False);self.renderRequested.emit(r)
    def update_progress(self,value,text):self.progress.setValue(value);self.status.setText(text)
    def show_error(self,text):self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True);self.status.setText(text)
    def _cancel(self):
        if not self.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled():self.cancelRequested.emit();self.status.setText('Cancelling render...')
        else:self.reject()
