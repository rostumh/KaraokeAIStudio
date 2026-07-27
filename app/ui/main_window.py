from __future__ import annotations

import logging
import json
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QByteArray, QSettings, Qt, QUrl, QTimer, QThreadPool
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QDockWidget, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QProgressBar, QStackedWidget, QStatusBar, QToolBar, QWidget

from app.application.services.audio_extraction_service import AudioExtractionService
from app.application.services.media_import_service import MediaImportService
from app.application.services.lyrics_translation_service import LyricsTranslationService
from app.application.services.final_export_service import FinalExportService
from app.application.services.video_render_service import VideoRenderService
from app.application.services.update_service import UpdateService
from app.application.services.export_profile_service import ExportProfileService
from app.application.services.subtitle_generation_service import SubtitleGenerationService
from app.application.services.word_alignment_service import WordAlignmentService
from app.application.services.transcription_service import TranscriptionService
from app.application.services.instrumental_cleanup_service import InstrumentalCleanupService
from app.application.services.vocal_separation_service import VocalSeparationService
from app.core.config import Settings
from app.core.paths import AppPaths
from app.domain.models.media import MediaAsset
from app.domain.models.workflow import AppMode,WorkflowState,WorkflowStep
from app.lyrics_engine import AutomaticLyricsSearch,create_lyrics_engine
from app.lyrics_engine.review_document import LyricsReviewDocumentBuilder
from app.lyrics_engine.ui import AutomaticLyricsWorker
from app.infrastructure.media.ffmpeg_audio_extractor import FFmpegAudioExtractor
from app.infrastructure.media.ffmpeg_locator import locate_ffmpeg
from app.infrastructure.media.ffmpeg_video_renderer import FFmpegVideoRenderer
from app.infrastructure.media.ffmpeg_instrumental_cleaner import FFmpegInstrumentalCleaner
from app.infrastructure.media.ffprobe_locator import locate_ffprobe
from app.infrastructure.batch.ffmpeg_batch_executor import FFmpegBatchJobExecutor
from app.infrastructure.repositories.batch_queue_repository import BatchQueueRepository
from app.infrastructure.media.ffmpeg_quality_validator import FFmpegQualityValidator
from app.infrastructure.repositories.quality_report_repository import QualityReportRepository
from app.infrastructure.repositories.translation_repository import TranslationRepository
from app.infrastructure.repositories.export_profile_repository import ExportProfileRepository
from app.infrastructure.plugins.plugin_context import RestrictedPluginContext
from app.infrastructure.plugins.plugin_manager import PluginManager
from app.infrastructure.repositories.plugin_state_repository import PluginStateRepository
from app.infrastructure.translation.argos_translator import ArgosTextTranslator
from app.infrastructure.update.https_update_client import HttpsUpdateClient
from app.infrastructure.ai.demucs_runtime import DemucsSourceSeparator, detect_compute_devices
from app.infrastructure.ai.faster_whisper_recognizer import FasterWhisperRecognizer, detect_whisper_devices
from app.infrastructure.ai.faster_whisper_word_aligner import FasterWhisperWordAligner
from app.infrastructure.repositories.json_alignment_repository import JsonAlignmentRepository
from app.infrastructure.repositories.json_transcript_repository import JsonTranscriptRepository
from app.infrastructure.repositories.lyrics_document_repository import LyricsDocumentRepository
from app.infrastructure.subtitles.ass_exporter import AssSubtitleExporter
from app.infrastructure.subtitles.lrc_exporter import LrcSubtitleExporter
from app.infrastructure.subtitles.srt_exporter import SrtSubtitleExporter
from app.infrastructure.media.ffprobe_media_probe import FFprobeMediaProbe
from app.ui.constants import WorkspacePage
from app.ui.controllers.audio_extraction_controller import AudioExtractionController
from app.ui.controllers.media_import_controller import MediaImportController
from app.ui.controllers.translation_controller import TranslationController
from app.ui.controllers.batch_queue_controller import BatchQueueController
from app.ui.controllers.final_export_controller import FinalExportController
from app.ui.controllers.video_render_controller import VideoRenderController
from app.ui.controllers.update_controller import UpdateController
from app.ui.controllers.transcription_controller import TranscriptionController
from app.ui.controllers.word_alignment_controller import WordAlignmentController
from app.ui.controllers.instrumental_cleanup_controller import InstrumentalCleanupController
from app.ui.controllers.vocal_separation_controller import VocalSeparationController
from app.ui.dialogs.audio_extraction_dialog import AudioExtractionDialog
from app.ui.dialogs.transcription_dialog import TranscriptionDialog
from app.ui.dialogs.translation_dialog import TranslationDialog
from app.ui.dialogs.subtitle_generation_dialog import SubtitleGenerationDialog
from app.ui.dialogs.video_render_dialog import VideoRenderDialog
from app.ui.dialogs.update_dialog import UpdateDialog
from app.ui.dialogs.export_profile_dialog import ExportProfileDialog
from app.ui.dialogs.final_export_dialog import FinalExportDialog
from app.ui.dialogs.karaoke_effect_dialog import KaraokeEffectDialog
from app.domain.models.karaoke_effects import KaraokeEffectSettings
from app.ui.dialogs.word_alignment_dialog import WordAlignmentDialog
from app.ui.dialogs.instrumental_cleanup_dialog import InstrumentalCleanupDialog
from app.ui.dialogs.vocal_separation_dialog import VocalSeparationDialog
from app.ui.dialogs.publishing_metadata_dialog import PublishingMetadataDialog
from app.ui.icons import standard_icon
from app.ui.models.media_asset_list_model import MediaAssetListModel
from app.ui.theme import DARK_STYLESHEET, LIGHT_STYLESHEET
from app.ui.viewmodels.workspace_viewmodel import WorkspaceViewModel
from app.ui.views.batch_view import BatchView
from app.ui.views.plugin_view import PluginView
from app.ui.views.history_view import HistoryView
from app.ui.views.lyrics_view import LyricsView
from app.ui.views.settings_view import SettingsView
from app.ui.views.studio_view import StudioView
from app.ui.views.render_settings_view import RenderSettingsView
from app.ui.views.visual_style_view import VisualStyleView
from app.ui.widgets.project_dock import ProjectDockContent
from app.ui.widgets.properties_dock import PropertiesDockContent
from app.ui.widgets.sidebar import Sidebar

LOGGER = logging.getLogger(__name__)
_MEDIA_FILTER = "Supported Media (*.mp3 *.flac *.wav *.aac *.m4a *.mp4 *.mkv *.avi *.mov);;Audio Files (*.mp3 *.flac *.wav *.aac *.m4a);;Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*)"


class MainWindow(QMainWindow):
    """Production workspace shell with asynchronous media ingestion."""

    def __init__(self, settings: Settings, paths: AppPaths) -> None:
        super().__init__()
        self._settings = settings
        self._paths = paths
        self._lyrics_search = AutomaticLyricsSearch(create_lyrics_engine(paths.data_dir))
        self._lyrics_worker = None
        self._online_lyrics_locked = False
        self._lyrics_review_builder = LyricsReviewDocumentBuilder()
        self._view_model = WorkspaceViewModel()
        self._app_mode = AppMode.AUTO
        self._workflow_state = WorkflowState()
        self._auto_pipeline_active = False
        self._auto_style = "Modern Clean"
        self._auto_original_asset: MediaAsset | None = None
        self._auto_instrumental_path: Path | None = None
        self._auto_waiting_for_vocals = False
        self._render_history: list[dict] = []
        self._project_generation = 0
        self._expected_transcription_source: Path | None = None
        self._asr_initialization_error: str | None = None
        self._media_model = MediaAssetListModel()
        self._current_asset: MediaAsset | None = None
        self._audio_output = QAudioOutput(self)
        self._audio_output.setVolume(1.0)
        self._player = QMediaPlayer(self)
        self._player.setAudioOutput(self._audio_output)
        self._player.positionChanged.connect(self._on_player_position)
        self._player.durationChanged.connect(self._on_player_duration)
        self._player.playbackStateChanged.connect(self._on_player_state)
        self._player.errorOccurred.connect(self._on_player_error)
        self._native_settings = QSettings(settings.application.organization, settings.application.name)
        self._import_controller: MediaImportController | None = None
        self._extraction_controller: AudioExtractionController | None = None
        self._extraction_dialog: AudioExtractionDialog | None = None
        self._separation_controller: VocalSeparationController | None = None
        self._separation_dialog: VocalSeparationDialog | None = None
        self._cleanup_controller: InstrumentalCleanupController | None = None
        self._cleanup_dialog: InstrumentalCleanupDialog | None = None
        self._transcription_controller: TranscriptionController | None = None
        self._transcription_dialog: TranscriptionDialog | None = None
        self._word_alignment_controller: WordAlignmentController | None = None
        self._word_alignment_dialog: WordAlignmentDialog | None = None
        self._current_transcript = None
        self._lyrics_repository = LyricsDocumentRepository()
        self._subtitle_service = SubtitleGenerationService((AssSubtitleExporter(), SrtSubtitleExporter(), LrcSubtitleExporter()))
        self._subtitle_dialog: SubtitleGenerationDialog | None = None
        self._karaoke_effect_settings = KaraokeEffectSettings()
        self._export_profile_repository = ExportProfileRepository(self._paths.data_dir/"export-profiles.json")
        self._user_export_profiles = self._export_profile_repository.load()
        self._update_controller = UpdateController(UpdateService(HttpsUpdateClient()))
        self._update_dialog = None
        self._video_renderer = None
        self._video_render_controller = None
        self._video_render_dialog = None
        # Final export is configured lazily, but shutdown can run before first use.
        self._final_export_controller = None
        self._final_export_dialog = None
        self._configure_video_rendering()
        self._batch_controller = None
        self._configure_batch()
        self._translation_adapter = None
        self._translation_controller = None
        self._translation_dialog = None
        self._configure_translation()
        self.setObjectName("mainWindow")
        self.setWindowTitle(settings.application.name)
        self.setMinimumSize(1100, 700)
        self.resize(1440, 900)
        saved_theme=str(QSettings(settings.application.organization,settings.application.name).value("app/theme",settings.appearance.theme));self.setStyleSheet(DARK_STYLESHEET if saved_theme=="dark" else LIGHT_STYLESHEET)
        self.setDockNestingEnabled(True)
        self.setAnimated(True)
        self._create_actions(); self._create_menu_bar(); self._create_toolbar(); self._create_workspace(); self._plugin_context = RestrictedPluginContext(); self._plugin_manager = PluginManager(PluginStateRepository(self._paths.data_dir/"plugins.json"), self._plugin_context); self.plugin_view.refreshRequested.connect(self._refresh_plugins); self.plugin_view.enabledChanged.connect(self._set_plugin_enabled); self._refresh_plugins(); self._create_docks(); self._create_status_bar(); self._connect_view_model(); self._configure_import(); self._configure_extraction(); self._configure_separation(); self._configure_cleanup(); self._configure_transcription(); self._configure_word_alignment(); self._restore_window_state()

    def _create_actions(self) -> None:
        self.new_action = QAction(standard_icon("new"), "New Project", self); self.new_action.setShortcut(QKeySequence.StandardKey.New); self.new_action.triggered.connect(self._new_project)
        self.open_action = QAction(standard_icon("open"), "Import Media…", self); self.open_action.setShortcut(QKeySequence.StandardKey.Open); self.open_action.triggered.connect(self._import_media)
        self.save_action = QAction(standard_icon("save"), "Save Project", self); self.save_action.setShortcut(QKeySequence.StandardKey.Save); self.save_action.setEnabled(False); self.save_action.triggered.connect(self._save_lyrics)
        self.align_words_action = QAction("Align Word Timestamps…", self); self.align_words_action.setShortcut(QKeySequence("Ctrl+Alt+T")); self.align_words_action.setEnabled(False); self.align_words_action.triggered.connect(self._align_words)
        self.transcribe_action = QAction("Generate or Find Lyrics…", self); self.transcribe_action.setShortcut(QKeySequence("Ctrl+Shift+T")); self.transcribe_action.setEnabled(False); self.transcribe_action.triggered.connect(self._transcribe_lyrics)
        self.translate_action = QAction("Translate Lyrics…", self); self.translate_action.setShortcut(QKeySequence("Ctrl+Alt+L")); self.translate_action.triggered.connect(self._translate_lyrics)
        self.effects_action = QAction("Karaoke Effects…", self); self.effects_action.setShortcut(QKeySequence("Ctrl+Alt+K")); self.effects_action.triggered.connect(self._configure_karaoke_effects)
        self.cleanup_action = QAction("Clean Instrumental…", self); self.cleanup_action.setShortcut(QKeySequence("Ctrl+Shift+I")); self.cleanup_action.setEnabled(False); self.transcribe_action.setEnabled(False); self.cleanup_action.triggered.connect(self._clean_instrumental)
        self.separate_action = QAction("Separate Vocals…", self); self.separate_action.setShortcut(QKeySequence("Ctrl+Shift+V")); self.separate_action.setEnabled(False); self.separate_action.triggered.connect(self._separate_vocals)
        self.validate_export_action = QAction("Validate Final Export…", self); self.validate_export_action.setShortcut(QKeySequence("Ctrl+Alt+Q")); self.validate_export_action.triggered.connect(self._validate_final_export)
        self.render_video_action = QAction("4. Render Karaoke Video…", self); self.render_video_action.setShortcut(QKeySequence("Ctrl+Alt+R")); self.render_video_action.triggered.connect(self._render_video)
        self.subtitle_action = QAction("Generate Subtitles…", self); self.subtitle_action.setShortcut(QKeySequence("Ctrl+Alt+S")); self.subtitle_action.setEnabled(False); self.subtitle_action.triggered.connect(self._generate_subtitles)
        self.extract_action = QAction("Extract Audio…", self); self.extract_action.setShortcut(QKeySequence("Ctrl+Shift+E")); self.extract_action.setEnabled(False); self.separate_action.setEnabled(False); self.cleanup_action.setEnabled(False); self.extract_action.triggered.connect(self._extract_audio)
        self.export_action = QAction(standard_icon("export"), "Export…", self); self.export_action.setShortcut(QKeySequence("Ctrl+E")); self.export_action.setEnabled(False)
        self.exit_action = QAction("Exit", self); self.exit_action.setShortcut(QKeySequence.StandardKey.Quit); self.exit_action.triggered.connect(self.close)
        self.play_action = QAction(standard_icon("play"), "Play/Pause", self); self.play_action.setShortcut(QKeySequence(Qt.Key.Key_Space)); self.play_action.triggered.connect(self._toggle_playback)
        self.stop_action = QAction(standard_icon("stop"), "Stop", self); self.stop_action.triggered.connect(self._stop_playback)
        self.reset_layout_action = QAction("Reset Workspace Layout", self); self.reset_layout_action.triggered.connect(self._reset_layout)
        self.update_action = QAction("Check for Updates…", self); self.update_action.triggered.connect(self._show_update_dialog)
        self.publishing_action = QAction("5. Create YouTube Upload Details…", self); self.publishing_action.triggered.connect(self._create_publishing_details)
        self.about_action = QAction("About Karaoke AI Studio", self); self.about_action.triggered.connect(self._show_about)

    def _create_menu_bar(self) -> None:
        file_menu = self.menuBar().addMenu("&File"); file_menu.addActions((self.new_action, self.open_action, self.save_action)); file_menu.addSeparator(); file_menu.addAction(self.extract_action); file_menu.addAction(self.subtitle_action); file_menu.addAction(self.render_video_action); file_menu.addAction(self.validate_export_action); file_menu.addAction(self.export_action); file_menu.addSeparator(); file_menu.addAction(self.exit_action)
        edit_menu = self.menuBar().addMenu("&Edit"); edit_menu.addAction("Undo").setEnabled(False); edit_menu.addAction("Redo").setEnabled(False)
        playback_menu = self.menuBar().addMenu("&Playback"); playback_menu.addActions((self.play_action, self.stop_action))
        ai_menu = self.menuBar().addMenu("&AI");auto_action=ai_menu.addAction("Create Karaoke Automatically");auto_action.triggered.connect(self._start_auto_mode);ai_menu.addSeparator();ai_menu.addAction(self.separate_action);ai_menu.addAction(self.transcribe_action);ai_menu.addAction(self.align_words_action);ai_menu.addAction(self.cleanup_action);ai_menu.addAction(self.translate_action);ai_menu.addSeparator();models_action=ai_menu.addAction("AI Models and Engines");models_action.triggered.connect(lambda:self._view_model.select_page(int(WorkspacePage.PLUGINS)))
        self.view_menu = self.menuBar().addMenu("&View"); self.view_menu.addAction(self.reset_layout_action)
        help_menu=self.menuBar().addMenu("&Help");help_menu.addAction(self.update_action);help_menu.addSeparator();help_menu.addAction(self.about_action)

    def _create_toolbar(self) -> None:
        toolbar=QToolBar("Main Toolbar",self);toolbar.setObjectName("mainToolbar");toolbar.setMovable(False);toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.undo_action=QAction("Undo",self);self.undo_action.setShortcut(QKeySequence.StandardKey.Undo);self.undo_action.setEnabled(False)
        self.redo_action=QAction("Redo",self);self.redo_action.setShortcut(QKeySequence.StandardKey.Redo);self.redo_action.setEnabled(False)
        self.settings_action=QAction("Settings",self);self.settings_action.triggered.connect(lambda:self._view_model.select_page(int(WorkspacePage.SETTINGS)))
        toolbar.addActions((self.new_action,self.open_action,self.save_action));toolbar.addSeparator();toolbar.addActions((self.undo_action,self.redo_action));toolbar.addSeparator();toolbar.addActions((self.settings_action,self.about_action));self.addToolBar(Qt.ToolBarArea.TopToolBarArea,toolbar)

    def _create_workspace(self) -> None:
        self.sidebar = Sidebar(); self.stack = QStackedWidget(); self.studio_view = StudioView()
        self._player.setVideoOutput(self.studio_view.preview.video_widget)
        self.lyrics_view = LyricsView(); self.batch_view = BatchView(); self.history_view = HistoryView(); self.plugin_view = PluginView();self.render_settings_view=RenderSettingsView();self.visual_style_view=VisualStyleView()
        self.settings_view=SettingsView(self._settings,self._paths);self.settings_view.settingsApplied.connect(self._apply_user_settings)
        for view in (self.studio_view, self.lyrics_view, self.batch_view, self.history_view, self.settings_view, self.plugin_view,self.render_settings_view,self.visual_style_view): self.stack.addWidget(view)
        container = QWidget(); layout = QHBoxLayout(container); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0); layout.addWidget(self.sidebar); layout.addWidget(self.stack, 1); self.setCentralWidget(container)
        self.undo_action.triggered.connect(self.lyrics_view.undo_stack.undo); self.redo_action.triggered.connect(self.lyrics_view.undo_stack.redo); self.lyrics_view.undo_stack.canUndoChanged.connect(self.undo_action.setEnabled); self.lyrics_view.undo_stack.canRedoChanged.connect(self.redo_action.setEnabled); self.lyrics_view.documentChanged.connect(lambda document: (self.save_action.setEnabled(True), self.subtitle_action.setEnabled(True))); self.lyrics_view.saveRequested.connect(self._save_lyrics); self.lyrics_view.continueRequested.connect(self._continue_from_lyrics)
        self.history_view.removeRequested.connect(self._remove_render_history);self.history_view.openRequested.connect(self._open_render_output);self._load_render_history()
        self.render_settings_view.editRequested.connect(self._render_video);self.visual_style_view.editRequested.connect(self._configure_karaoke_effects);self.sidebar.pageRequested.connect(self._view_model.select_page); self.studio_view.importRequested.connect(self._import_media); self.studio_view.autoCreateRequested.connect(self._start_auto_mode); self.studio_view.modeRequested.connect(self._set_app_mode); self.studio_view.retryRequested.connect(self._retry_current_step); self.studio_view.cancelRequested.connect(self._cancel_active_task); self.studio_view.playRequested.connect(self._toggle_playback); self.studio_view.stopRequested.connect(self._stop_playback); self.studio_view.seekRequested.connect(self._seek_playback)

    def _apply_user_settings(self, values: dict) -> None:
        theme=str(values.get('preview_theme',values.get('theme','dark')))
        self.setStyleSheet(DARK_STYLESHEET if theme=='dark' else LIGHT_STYLESHEET)
        if 'export_dir' in values:
            object.__setattr__(self._paths,'export_dir',Path(str(values['export_dir'])))
        if 'cache_dir' in values:
            object.__setattr__(self._paths,'cache_dir',Path(str(values['cache_dir'])))
        if 'device' in values:self.statusBar().showMessage(f"Settings saved • Device: {values['device']}",5000)

    def _create_docks(self) -> None:
        self.project_content = ProjectDockContent(self._media_model); self.project_dock = QDockWidget("Project", self); self.project_dock.setObjectName("projectDock"); self.project_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea); self.project_dock.setWidget(self.project_content); self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_dock)
        self.properties_content = PropertiesDockContent(); self.properties_dock = QDockWidget("Properties", self); self.properties_dock.setObjectName("propertiesDock"); self.properties_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea); self.properties_dock.setWidget(self.properties_content); self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)
        self.project_content.assetSelected.connect(self.properties_content.show_asset); self.project_content.assetSelected.connect(self._show_selected_asset); self.project_content.assetSelected.connect(lambda value: self.extract_action.setEnabled(isinstance(value, MediaAsset))); self.project_content.assetSelected.connect(lambda value: self.separate_action.setEnabled(isinstance(value, MediaAsset))); self.project_content.assetSelected.connect(lambda value: self.cleanup_action.setEnabled(isinstance(value, MediaAsset))); self.project_content.assetSelected.connect(lambda value: self.transcribe_action.setEnabled(isinstance(value, MediaAsset)))
        self.view_menu.addSeparator(); self.view_menu.addAction(self.project_dock.toggleViewAction()); self.view_menu.addAction(self.properties_dock.toggleViewAction())

    def _create_status_bar(self) -> None:
        status = QStatusBar(self); status.showMessage("Ready"); device = QLabel("Device: Automatic"); device.setObjectName("muted")
        self._status_progress = QProgressBar(); self._status_progress.setRange(0, 0); self._status_progress.setFixedWidth(150); self._status_progress.setVisible(False)
        status.addPermanentWidget(device); status.addPermanentWidget(self._status_progress); self.setStatusBar(status)

    def _connect_view_model(self) -> None:
        self._view_model.pageChanged.connect(self.stack.setCurrentIndex); self._view_model.pageChanged.connect(self.sidebar.set_current_page)

    def _configure_import(self) -> None:
        try:
            service = MediaImportService(FFprobeMediaProbe(locate_ffprobe()))
            self._import_controller = MediaImportController(service)
            self._import_controller.started.connect(self._on_import_started); self._import_controller.succeeded.connect(self._on_import_succeeded); self._import_controller.failed.connect(self._on_import_failed); self._import_controller.busyChanged.connect(self._on_import_busy_changed)
        except Exception as exc:
            LOGGER.warning("Media import unavailable: %s", exc)
            self.open_action.setToolTip(str(exc))

    def _configure_word_alignment(self) -> None:
        try:
            aligner=FasterWhisperWordAligner(self._paths.cache_dir/"models"/"whisper");self._word_alignment_controller=WordAlignmentController(WordAlignmentService(aligner,JsonAlignmentRepository()));self._word_alignment_controller.progressChanged.connect(self._on_alignment_progress);self._word_alignment_controller.succeeded.connect(self._on_alignment_succeeded);self._word_alignment_controller.failed.connect(self._on_alignment_failed);self._word_alignment_controller.busyChanged.connect(self._on_alignment_busy)
        except Exception as exc:LOGGER.warning("Word alignment unavailable: %s",exc);self.align_words_action.setToolTip(str(exc))

    def _align_words(self) -> None:
        from app.domain.models.transcription import Transcript
        if not isinstance(self._current_transcript,Transcript):QMessageBox.information(self,"Transcript Required","Complete Whisper transcription before aligning words.");return
        if self._word_alignment_controller is None:self._configure_word_alignment()
        if self._word_alignment_controller is None:QMessageBox.critical(self,"Alignment Unavailable","Run scripts\\setup_asr.ps1 to install Faster Whisper.");return
        dialog=WordAlignmentDialog(self._current_transcript.source_path.name,len(self._current_transcript.segments),self);dialog.startRequested.connect(lambda:self._word_alignment_controller.start(self._current_transcript,self._paths.export_dir/"transcripts"));dialog.cancelRequested.connect(self._word_alignment_controller.cancel);self._word_alignment_dialog=dialog;dialog.open()

    def _on_alignment_progress(self,value:int,text:str) -> None:
        self._status_progress.setValue(value);self.statusBar().showMessage(text)
        if self._auto_pipeline_active:self._set_workflow(self._workflow_state.update(value,text))
        if self._word_alignment_dialog:self._word_alignment_dialog.update_progress(value,text)

    def _on_alignment_succeeded(self,value:object) -> None:
        if not isinstance(value,tuple) or len(value)!=2:self._on_alignment_failed("Alignment returned an invalid result.");return
        alignment,path=value
        from app.domain.models.alignment import AlignedTranscript
        if not isinstance(alignment,AlignedTranscript):self._on_alignment_failed("Alignment data is invalid.");return
        if self._word_alignment_dialog:self._word_alignment_dialog.accept();self._word_alignment_dialog=None
        self.lyrics_view.show_alignment(alignment);self._view_model.select_page(int(WorkspacePage.LYRICS))
        try:
            auto_path=self._lyrics_repository.save(self.lyrics_view.word_model.document,self._paths.export_dir/"lyrics")
            self.lyrics_view.mark_saved(auto_path);self.statusBar().showMessage(f"Lyrics ready and auto-saved: {auto_path.name}",10000)
        except Exception as exc:
            LOGGER.exception("Lyrics auto-save failed");self.statusBar().showMessage(f"Lyrics ready, but auto-save failed: {exc}",10000)
        LOGGER.info("Word alignment saved: %s",path)
        if self._auto_pipeline_active:
            completed=self._workflow_state.completed | {WorkflowStep.REVIEW}
            self._set_workflow(WorkflowState(WorkflowStep.STYLE,completed,False,"Lyrics are ready and auto-saved. Correct uncertain words in Lyrics Editor, save, then click Create Karaoke Video.",100,None))
            self._auto_pipeline_active=False

    def _on_alignment_failed(self,message:str) -> None:
        if self._word_alignment_dialog:self._word_alignment_dialog.show_error(message)
        self.statusBar().showMessage("Word alignment did not complete",5000)
        if self._auto_pipeline_active:self._set_workflow(self._workflow_state.fail(message))

    def _on_alignment_busy(self,busy:bool) -> None:
        self.open_action.setEnabled(not busy);self.new_action.setEnabled(not busy);self.align_words_action.setEnabled(not busy and self._current_transcript is not None);self._status_progress.setRange(0,100);self._status_progress.setVisible(busy)
        if not busy:self._status_progress.setValue(0)

    def _configure_transcription(self) -> None:
        try:
            recognizer=FasterWhisperRecognizer(self._paths.cache_dir/"models"/"whisper");self._transcription_controller=TranscriptionController(TranscriptionService(recognizer,JsonTranscriptRepository()));self._transcription_controller.progressChanged.connect(self._on_transcription_progress);self._transcription_controller.succeeded.connect(self._on_transcription_succeeded);self._transcription_controller.failed.connect(self._on_transcription_failed);self._transcription_controller.busyChanged.connect(self._on_transcription_busy)
        except Exception as exc:
            LOGGER.exception("Speech recognition unavailable")
            self._asr_initialization_error=str(exc);self.transcribe_action.setToolTip(str(exc))

    def _transcribe_lyrics(self) -> None:
        asset=self.project_content.current_asset()
        if not isinstance(asset,MediaAsset):QMessageBox.information(self,"Select Vocal Audio","Select an imported vocal or song asset first.");return
        if self._transcription_controller is None:self._configure_transcription()
        if self._transcription_controller is None:QMessageBox.critical(self,"Whisper Required","Run scripts\\setup_asr.ps1 to install speech recognition.");return
        dialog=TranscriptionDialog(asset.display_name,self._paths.export_dir/"transcripts","cuda" in detect_whisper_devices(),self);dialog.requested.connect(lambda options:self._transcription_controller.start(asset,options));dialog.cancelRequested.connect(self._transcription_controller.cancel);self._transcription_dialog=dialog;dialog.open()

    def _on_transcription_progress(self,value:int,text:str) -> None:
        self._status_progress.setValue(value);self.statusBar().showMessage(text)
        if self._auto_pipeline_active:self._set_workflow(self._workflow_state.update(value,text))
        if self._transcription_dialog:self._transcription_dialog.update_progress(value,text)

    def _on_transcription_succeeded(self,value:object) -> None:
        if not isinstance(value,tuple) or len(value)!=2:self._on_transcription_failed("Transcription returned an invalid result.");return
        transcript,paths=value
        from app.domain.models.transcription import Transcript
        if not isinstance(transcript,Transcript):self._on_transcription_failed("Transcription returned invalid transcript data.");return
        if self._expected_transcription_source is None or transcript.source_path.resolve()!=self._expected_transcription_source.resolve():
            LOGGER.warning("Discarded stale transcription result source=%s expected=%s",transcript.source_path,self._expected_transcription_source);return
        if self._transcription_dialog:self._transcription_dialog.accept();self._transcription_dialog=None
        if self._online_lyrics_locked:
            LOGGER.info("Discarded Whisper result because official online lyrics are locked");return
        self._current_transcript=transcript;self.align_words_action.setEnabled(True);self.lyrics_view.show_transcript(transcript);self.lyrics_view.subtitle.setText("Lyrics Source: Whisper  |  Confidence: AI Generated Lyrics  |  Warning: Lyrics may contain transcription errors.");self.statusBar().showMessage("Lyrics generated.",8000);LOGGER.info("Transcript saved: %s",paths)
        if self._auto_pipeline_active:
            self._set_workflow(self._workflow_state.complete(WorkflowStep.LYRICS,WorkflowStep.REVIEW,"Creating word-level karaoke timing").start(WorkflowStep.REVIEW,"Creating word-level karaoke timing"))
            self._start_auto_alignment()
        else:
            self._set_workflow(self._workflow_state.complete(WorkflowStep.LYRICS,WorkflowStep.REVIEW,"Review and correct lyrics"));self._view_model.select_page(int(WorkspacePage.LYRICS))

    def _on_transcription_failed(self,message:str) -> None:
        self._current_transcript=None;self.lyrics_view.clear_document();self.subtitle_action.setEnabled(False)
        if self._transcription_dialog:self._transcription_dialog.show_error(message)
        self.statusBar().showMessage("Speech recognition did not complete",5000)
        if self._auto_pipeline_active:self._set_workflow(self._workflow_state.fail(message))

    def _on_transcription_busy(self,busy:bool) -> None:
        self.open_action.setEnabled(not busy);self.new_action.setEnabled(not busy);self.transcribe_action.setEnabled(not busy and isinstance(self.project_content.current_asset(),MediaAsset));self._status_progress.setRange(0,100);self._status_progress.setVisible(busy)
        if not busy:self._status_progress.setValue(0)

    def _configure_cleanup(self) -> None:
        try:
            self._cleanup_controller=InstrumentalCleanupController(InstrumentalCleanupService(FFmpegInstrumentalCleaner(locate_ffmpeg())))
            self._cleanup_controller.progressChanged.connect(self._status_progress.setValue);self._cleanup_controller.succeeded.connect(self._on_cleanup_succeeded);self._cleanup_controller.failed.connect(self._on_cleanup_failed);self._cleanup_controller.busyChanged.connect(self._on_cleanup_busy)
        except Exception as exc:LOGGER.warning("Instrumental cleanup unavailable: %s",exc);self.cleanup_action.setToolTip(str(exc))

    def _clean_instrumental(self) -> None:
        asset=self.project_content.current_asset()
        if not isinstance(asset,MediaAsset):QMessageBox.information(self,"Select Instrumental","Select an imported instrumental asset first.");return
        if self._cleanup_controller is None:self._configure_cleanup()
        if self._cleanup_controller is None:QMessageBox.critical(self,"FFmpeg Required","Instrumental cleanup requires FFmpeg.");return
        dialog=InstrumentalCleanupDialog(asset.display_name,self._paths.export_dir/"cleaned",self);dialog.cleanupRequested.connect(lambda options:self._cleanup_controller.start(asset,options));dialog.cancelRequested.connect(self._cleanup_controller.cancel);self._cleanup_dialog=dialog;dialog.open()

    def _on_cleanup_succeeded(self,value:object) -> None:
        from app.domain.models.instrumental_cleanup import InstrumentalCleanupResult
        if not isinstance(value,InstrumentalCleanupResult):self._on_cleanup_failed("Cleanup returned an invalid result.");return
        if self._cleanup_dialog:self._cleanup_dialog.accept();self._cleanup_dialog=None
        self.statusBar().showMessage(f"Cleaned instrumental in {value.elapsed_seconds:.1f} seconds",7000)
        if self._import_controller:self._import_controller.import_file(value.output_path)
        QTimer.singleShot(700,self._player.pause)
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        box=QMessageBox(self);box.setWindowTitle("Render Complete");box.setText(f"Finished video loaded in the player (paused).\n\n{value.output_path.name}");open_button=box.addButton("Open Output Folder",QMessageBox.ButtonRole.ActionRole);box.addButton(QMessageBox.StandardButton.Ok);box.exec()
        if box.clickedButton() is open_button:QDesktopServices.openUrl(QUrl.fromLocalFile(str(value.output_path.parent)))

    def _on_cleanup_failed(self,message:str) -> None:
        if self._cleanup_dialog:self._cleanup_dialog.show_error(message)
        self.statusBar().showMessage("Instrumental cleanup did not complete",5000)

    def _on_cleanup_busy(self,busy:bool) -> None:
        self.open_action.setEnabled(not busy);self.new_action.setEnabled(not busy);self.cleanup_action.setEnabled(not busy and isinstance(self.project_content.current_asset(),MediaAsset));self._status_progress.setRange(0,100);self._status_progress.setVisible(busy)
        if not busy:self._status_progress.setValue(0)

    def _configure_separation(self) -> None:
        try:
            self._separation_controller = VocalSeparationController(VocalSeparationService(DemucsSourceSeparator()))
            self._separation_controller.statusChanged.connect(self._on_separation_status)
            self._separation_controller.succeeded.connect(self._on_separation_succeeded)
            self._separation_controller.failed.connect(self._on_separation_failed)
            self._separation_controller.busyChanged.connect(self._on_separation_busy)
        except Exception as exc:
            LOGGER.warning("Vocal separation unavailable: %s", exc); self.separate_action.setToolTip(str(exc))

    def _separate_vocals(self) -> None:
        asset=self.project_content.current_asset()
        if not isinstance(asset,MediaAsset): QMessageBox.information(self,"Select Media","Select an imported media asset first."); return
        if self._separation_controller is None: self._configure_separation()
        if self._separation_controller is None:
            QMessageBox.critical(self, "Vocal Separation Unavailable", "The built-in vocal separation engine is missing or damaged. Reinstall Karaoke AI Studio 0.20.9 or later. No Python or manual dependency installation is required.")
            return
        dialog=VocalSeparationDialog(asset.display_name,self._paths.export_dir/"stems","cuda" in detect_compute_devices(),self); dialog.separationRequested.connect(lambda options:self._separation_controller.start(asset,options)); dialog.cancelRequested.connect(self._separation_controller.cancel); self._separation_dialog=dialog; dialog.open()

    def _on_separation_status(self,text: str) -> None:
        self.statusBar().showMessage(text)
        if self._separation_dialog: self._separation_dialog.set_status(text)
        if self._auto_pipeline_active:self._set_workflow(self._workflow_state.update(self._workflow_state.progress,text))

    def _on_separation_succeeded(self,value: object) -> None:
        from app.domain.models.separation import SeparationResult
        if not isinstance(value,SeparationResult): self._on_separation_failed("Separation returned an invalid result."); return
        if self._separation_dialog: self._separation_dialog.accept(); self._separation_dialog=None
        self.statusBar().showMessage(f"Created {len(value.stems)} stems in {value.elapsed_seconds:.1f} seconds",8000)
        if self._auto_pipeline_active:
            self._auto_instrumental_path=next((p for p in value.stems if p.stem=="no_vocals" and p.is_file()),None)
            if self._auto_instrumental_path is None:
                self._offer_original_audio_fallback("The separation engine finished but did not produce a usable instrumental file.");return
            if self.lyrics_view.word_model.document is not None:
                completed=self._workflow_state.completed | {WorkflowStep.SEPARATE,WorkflowStep.LYRICS,WorkflowStep.REVIEW}
                self._set_workflow(WorkflowState(WorkflowStep.STYLE,completed,False,"AI separation completed",100,None))
                QTimer.singleShot(0,self._accept_auto_style_and_render)
            else:
                self._auto_waiting_for_vocals=True
                self._set_workflow(self._workflow_state.complete(WorkflowStep.SEPARATE,WorkflowStep.LYRICS,"Preparing vocals for automatic lyric generation").start(WorkflowStep.LYRICS,"Preparing vocals for automatic lyric generation"))
        else:self._set_workflow(self._workflow_state.complete(WorkflowStep.SEPARATE,WorkflowStep.LYRICS,"Generate lyrics"))
        if self._import_controller:
            for stem in value.stems:self._import_controller.import_file(stem)

    def _on_separation_failed(self,message: str) -> None:
        if self._separation_dialog: self._separation_dialog.show_error(message)
        self.statusBar().showMessage("Vocal separation did not complete",5000)
        self._auto_waiting_for_vocals=False
        completed=self._workflow_state.completed & {WorkflowStep.IMPORT}
        self._set_workflow(WorkflowState(WorkflowStep.SEPARATE,frozenset(completed),False,"AI separation failed — retry or continue with original audio",0,message))
        if self._auto_pipeline_active:self._offer_original_audio_fallback(message)

    def _on_separation_busy(self,busy: bool) -> None:
        self.open_action.setEnabled(not busy); self.new_action.setEnabled(not busy); self.separate_action.setEnabled(not busy and isinstance(self.project_content.current_asset(),MediaAsset)); self._status_progress.setRange(0,0); self._status_progress.setVisible(busy)
        if not busy:self._status_progress.setRange(0,100);self._status_progress.setValue(0)

    def _configure_extraction(self) -> None:
        try:
            self._extraction_controller = AudioExtractionController(AudioExtractionService(FFmpegAudioExtractor(locate_ffmpeg())))
            self._extraction_controller.progressChanged.connect(self._status_progress.setValue)
            self._extraction_controller.succeeded.connect(self._on_extraction_succeeded)
            self._extraction_controller.failed.connect(self._on_extraction_failed)
            self._extraction_controller.busyChanged.connect(self._on_extraction_busy_changed)
        except Exception as exc:
            LOGGER.warning("Audio extraction unavailable: %s", exc)
            self.extract_action.setToolTip(str(exc))

    def _extract_audio(self) -> None:
        asset = self.project_content.current_asset()
        if not isinstance(asset, MediaAsset):
            QMessageBox.information(self, "Select Media", "Select an imported media asset before extracting audio.")
            return
        if self._extraction_controller is None:
            self._configure_extraction()
        if self._extraction_controller is None:
            QMessageBox.critical(self, "FFmpeg Required", "Audio extraction requires FFmpeg. Configure KAS_FFMPEG_PATH or add FFmpeg to PATH.")
            return
        dialog = AudioExtractionDialog(asset, self._paths.export_dir, self)
        dialog.extractionRequested.connect(lambda options: self._extraction_controller.start(asset, options))
        dialog.cancelRequested.connect(self._extraction_controller.cancel)
        self._extraction_dialog = dialog
        dialog.open()

    def _on_extraction_succeeded(self, value: object) -> None:
        from app.domain.models.audio_extraction import AudioExtractionResult
        if not isinstance(value, AudioExtractionResult):
            self._on_extraction_failed("Extraction returned an invalid result.")
            return
        if self._extraction_dialog is not None:
            self._extraction_dialog.accept()
            self._extraction_dialog = None
        self.statusBar().showMessage(f"Extracted audio: {value.output_path.name}", 7000)
        if self._import_controller is not None:
            self._import_controller.import_file(value.output_path)

    def _on_extraction_failed(self, message: str) -> None:
        if self._extraction_dialog is not None:
            self._extraction_dialog.show_error(message)
        self.statusBar().showMessage("Audio extraction did not complete", 5000)

    def _on_extraction_busy_changed(self, busy: bool) -> None:
        self.open_action.setEnabled(not busy)
        self.new_action.setEnabled(not busy)
        self.extract_action.setEnabled(not busy and isinstance(self.project_content.current_asset(), MediaAsset))
        self._status_progress.setRange(0, 100)
        self._status_progress.setVisible(busy)
        if not busy:
            self._status_progress.setValue(0)

    def _new_project(self) -> None:
        if self._import_controller and self._import_controller.busy:
            QMessageBox.warning(self, "Import in Progress", "Wait for media inspection to finish before creating a new project."); return
        self._project_generation += 1
        for controller in (self._separation_controller,self._cleanup_controller,self._transcription_controller,self._word_alignment_controller,self._video_render_controller):
            if controller is not None and getattr(controller,"busy",False): controller.cancel()
        self._lyrics_worker=None; self._online_lyrics_locked=False
        self._auto_pipeline_active=False; self._auto_waiting_for_vocals=False
        self._auto_original_asset=None; self._auto_instrumental_path=None; self._expected_transcription_source=None
        self._current_transcript=None; self._current_asset=None
        self._player.stop(); self._player.setSource(QUrl())
        self._media_model.clear(); self.studio_view.preview.clear_asset(); self.lyrics_view.clear_document()
        self.align_words_action.setEnabled(False); self.subtitle_action.setEnabled(False); self.extract_action.setEnabled(False)
        self._view_model.select_page(int(WorkspacePage.STUDIO)); self.save_action.setEnabled(False); self.export_action.setEnabled(False)
        self._set_workflow(WorkflowState());self.statusBar().showMessage("New isolated project created", 4000)

    def _import_media(self) -> None:
        if self._import_controller is None:
            try: self._configure_import()
            except Exception: LOGGER.exception("Unable to configure import")
        if self._import_controller is None:
            QMessageBox.critical(self, "Media Engine Missing", "The built-in media engine is missing or damaged. Reinstall Karaoke AI Studio 0.20.9 or later. No FFmpeg or PATH setup is required."); return
        filename, _ = QFileDialog.getOpenFileName(self, "Import Media", str(Path.home()), _MEDIA_FILTER)
        if filename: self._import_controller.import_file(Path(filename))

    def _on_import_started(self, filename: str) -> None:
        self.statusBar().showMessage(f"Inspecting {filename}…"); self._status_progress.setVisible(True)

    def _on_import_succeeded(self, value: object) -> None:
        if not isinstance(value, MediaAsset): self._on_import_failed("Import returned an invalid media object."); return
        row = self._media_model.add_asset(value); index = self._media_model.index(row, 0); self.project_content.view.setCurrentIndex(index)
        self.studio_view.show_asset(value); self.properties_content.show_asset(value); self._load_playback_asset(value)
        generated=self._auto_pipeline_active and value.source_path.name in {"vocals.wav","vocals.flac","no_vocals.wav","no_vocals.flac"}
        if not generated:self._online_lyrics_locked=False
        if not generated:self._set_workflow(self._workflow_state.complete(WorkflowStep.IMPORT,WorkflowStep.SEPARATE,"Ready to create"));self._view_model.select_page(int(WorkspacePage.STUDIO))
        self.save_action.setEnabled(True); self.export_action.setEnabled(True)
        if self._auto_pipeline_active and self._auto_waiting_for_vocals and value.source_path.stem=="vocals":
            self._auto_waiting_for_vocals=False;QTimer.singleShot(0,lambda:self._start_auto_transcription(value))
        self.statusBar().showMessage(f"Imported {value.display_name}", 6000); LOGGER.info("Imported media asset %s from %s", value.asset_id, value.source_path)
        if not generated and value.source_path.suffix.lower() in {".mp3",".mp4"}:QTimer.singleShot(0,lambda asset=value:self._start_automatic_lyrics_search(asset))

    def _start_automatic_lyrics_search(self,asset:MediaAsset)->None:
        worker=AutomaticLyricsWorker(self._lyrics_search,asset);self._lyrics_worker=worker
        worker.signals.status.connect(self._on_automatic_lyrics_status)
        worker.signals.found.connect(self._on_automatic_lyrics_found)
        worker.signals.notFound.connect(self._on_automatic_lyrics_not_found)
        worker.signals.failed.connect(lambda message:LOGGER.warning("Automatic lyrics search failed: %s",message))
        QThreadPool.globalInstance().start(worker)

    def _on_automatic_lyrics_status(self,text:str)->None:
        self.statusBar().showMessage(text);self.lyrics_view.subtitle.setText(text)

    def _on_automatic_lyrics_found(self,result:object)->None:
        from app.lyrics_engine.models import LyricsResult
        if not isinstance(result,LyricsResult):return
        self._online_lyrics_locked=True
        document=self._lyrics_review_builder.build(result)
        source="LRC" if result.synchronized else "Online"
        self.lyrics_view.show_external_lyrics(document,source,"Official Lyrics")
        self.statusBar().showMessage("Lyrics found.",8000);self._view_model.select_page(int(WorkspacePage.LYRICS));self._lyrics_worker=None
        self._set_workflow(self._workflow_state.complete(WorkflowStep.LYRICS,WorkflowStep.REVIEW,"Review official lyrics and continue"))

    def _on_automatic_lyrics_not_found(self,asset:object)->None:
        if not isinstance(asset,MediaAsset):return
        self._on_automatic_lyrics_status("Online search failed. Isolating vocals before transcription, then Running Whisper...")
        self._lyrics_worker=None
        if asset.source_path.stem=="vocals":self._start_auto_transcription(asset)
        else:self._auto_pipeline_active=True;self._auto_waiting_for_vocals=True;self._start_auto_mode(self.studio_view.wizard.style.currentText())

    def _on_import_failed(self, message: str) -> None:
        self.statusBar().showMessage("Media import failed", 5000); QMessageBox.critical(self, "Media Import Failed", message)

    def _on_import_busy_changed(self, busy: bool) -> None:
        self.open_action.setEnabled(not busy); self.new_action.setEnabled(not busy); self._status_progress.setVisible(busy)

    def _show_selected_asset(self, value: object) -> None:
        if isinstance(value, MediaAsset):
            self.studio_view.show_asset(value)
            self._load_playback_asset(value)

    def _load_playback_asset(self, asset: MediaAsset) -> None:
        if not asset.source_path.is_file():
            QMessageBox.warning(self, "Media Missing", f"The source file no longer exists:\n{asset.source_path}")
            return
        if self._current_asset is not None and self._current_asset.source_path == asset.source_path:
            return
        self._player.stop()
        self._current_asset = asset
        self._player.setSource(QUrl.fromLocalFile(str(asset.source_path.resolve())))
        expected_duration = max(0, round(asset.duration_seconds * 1000))
        self.studio_view.timeline.set_media_time(0, expected_duration)
        self.statusBar().showMessage(f"Ready to play {asset.display_name}", 4000)
        LOGGER.info("Playback source loaded: %s", asset.source_path)

    def _toggle_playback(self) -> None:
        if self._current_asset is None:
            QMessageBox.information(self, "Select Media", "Import or select an audio or video file first.")
            return
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _stop_playback(self) -> None:
        self._player.stop()
        self._player.setPosition(0)

    def _seek_playback(self, normalized_position: int) -> None:
        duration = self._player.duration()
        if duration <= 0 and self._current_asset is not None:
            duration = round(self._current_asset.duration_seconds * 1000)
        if duration > 0:
            self._player.setPosition(round(max(0, min(1000, normalized_position)) * duration / 1000))

    def _on_player_position(self, position_ms: int) -> None:
        duration = self._player.duration()
        if duration <= 0 and self._current_asset is not None:
            duration = round(self._current_asset.duration_seconds * 1000)
        self.studio_view.timeline.set_media_time(position_ms, duration)

    def _on_player_duration(self, duration_ms: int) -> None:
        self.studio_view.timeline.set_media_time(self._player.position(), duration_ms)

    def _on_player_state(self, state: QMediaPlayer.PlaybackState) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.studio_view.timeline.set_playing(playing)
        self.play_action.setText("Pause" if playing else "Play/Pause")

    def _on_player_error(self, error: QMediaPlayer.Error, message: str) -> None:
        if error == QMediaPlayer.Error.NoError:
            return
        detail = message or "The selected media could not be decoded or played."
        LOGGER.error("Playback error for %s: %s", self._current_asset.source_path if self._current_asset else None, detail)
        self.studio_view.timeline.set_playing(False)
        self.statusBar().showMessage("Playback failed", 5000)
        QMessageBox.critical(self, "Playback Error", detail)

    def _create_publishing_details(self) -> None:
        asset=self.project_content.current_asset()
        name=asset.source_path.stem if isinstance(asset,MediaAsset) else "Karaoke Song"
        dialog=PublishingMetadataDialog(name,self._paths.export_dir/"publishing",self)
        dialog.saved.connect(lambda paths:self.statusBar().showMessage(f"Saved upload details: {paths[0]}",8000))
        dialog.open()

    def _set_workflow(self,state:WorkflowState)->None:
        self._workflow_state=state;self.studio_view.set_workflow_state(state)

    def _continue_from_lyrics(self) -> None:
        self._view_model.select_page(int(WorkspacePage.STUDIO))
        completed=self._workflow_state.completed | {WorkflowStep.LYRICS,WorkflowStep.REVIEW}
        self._set_workflow(WorkflowState(WorkflowStep.STYLE,completed,False,"Lyrics saved",100,None))
        if self._app_mode==AppMode.AUTO:
            # Auto Mode must resolve separation before render, even when online lyrics arrived first.
            if WorkflowStep.SEPARATE not in completed:
                self._auto_pipeline_active=True
                self._auto_original_asset=self.project_content.current_asset()
                self.statusBar().showMessage("Lyrics saved. Starting required AI separation.",8000)
                self._start_auto_mode(self.studio_view.wizard.style.currentText())
                return
            self._accept_auto_style_and_render()
            return
        self.statusBar().showMessage("Lyrics saved. Next: choose a visual style and continue to render.",10000)

    def _accept_auto_style_and_render(self) -> None:
        """Commit the selected/recommended style and advance only after audio is resolved."""
        self._auto_style=self.studio_view.wizard.style.currentText() or "Modern Clean"
        self._native_settings.setValue("auto/visualStyle",self._auto_style);self._native_settings.sync()
        completed=self._workflow_state.completed | {WorkflowStep.LYRICS,WorkflowStep.REVIEW,WorkflowStep.STYLE}
        self._set_workflow(WorkflowState(WorkflowStep.RENDER,completed,False,f"Applied {self._auto_style}; opening final render settings",100,None))
        self.statusBar().showMessage(f"Visual style applied automatically: {self._auto_style}",6000)
        self._render_video()

    def _offer_original_audio_fallback(self, reason:str) -> None:
        """Offer a safe per-song fallback when separation cannot complete."""
        self._auto_pipeline_active=False
        original=self._auto_original_asset
        if not isinstance(original,MediaAsset):
            current=self.project_content.current_asset();original=current if isinstance(current,MediaAsset) else None
        box=QMessageBox(self);box.setIcon(QMessageBox.Icon.Warning);box.setWindowTitle("AI Separation Could Not Complete")
        box.setText("Karaoke AI Studio could not create an instrumental track.")
        box.setInformativeText(f"{reason}\n\nYou can retry, or continue this song with the original audio. Original audio may still contain the lead vocal.")
        retry=box.addButton("Retry AI Separation",QMessageBox.ButtonRole.AcceptRole)
        fallback=box.addButton("Continue with Original Audio",QMessageBox.ButtonRole.ActionRole)
        cancel=box.addButton(QMessageBox.StandardButton.Cancel);box.exec()
        if box.clickedButton() is retry:
            self._auto_pipeline_active=True;self._start_auto_mode(self._auto_style);return
        if box.clickedButton() is fallback and isinstance(original,MediaAsset) and original.source_path.is_file():
            self._auto_instrumental_path=original.source_path
            completed=self._workflow_state.completed | {WorkflowStep.SEPARATE}
            self._set_workflow(WorkflowState(WorkflowStep.STYLE,completed,False,"AI separation completed — original audio fallback",100,None))
            if self.lyrics_view.word_model.document is not None:self._accept_auto_style_and_render()
            else:
                self._auto_pipeline_active=True;self._start_auto_transcription(original)
            return
        self._set_workflow(self._workflow_state.fail("AI separation cancelled. Retry when ready."))

    def _set_app_mode(self,mode:str)->None:
        self._app_mode=AppMode(mode);professional=self._app_mode==AppMode.PROFESSIONAL
        self.sidebar.setVisible(professional);self.project_dock.setVisible(professional);self.properties_dock.setVisible(professional)
        self.statusBar().showMessage("Professional tools enabled" if professional else "Auto Mode enabled",4000)

    def _start_auto_mode(self,style:str)->None:
        asset=self.project_content.current_asset()
        if not isinstance(asset,MediaAsset):QMessageBox.information(self,"Import Required","Import a song or video first.");return
        if self._workflow_state.current==WorkflowStep.STYLE and self.lyrics_view.word_model.document is not None and WorkflowStep.SEPARATE in self._workflow_state.completed:
            self._auto_style=style;self._accept_auto_style_and_render();return
        self._auto_pipeline_active=True;self._auto_style=style;self._auto_original_asset=asset
        self._set_workflow(self._workflow_state.start(WorkflowStep.SEPARATE,f"Separating vocals — {style}"))
        if self._separation_controller is None:self._configure_separation()
        if self._separation_controller is None:self._offer_original_audio_fallback("The built-in vocal separation engine is unavailable.");return
        self._separation_controller.start(asset,{"output_root":str(self._paths.export_dir/"stems"),"model":"htdemucs","mode":"vocals","device":"auto","format":"wav24","shifts":1,"overlap":0.25,"segment":7})

    def _start_auto_transcription(self,asset:MediaAsset)->None:
        self._current_transcript=None;self._online_lyrics_locked=False;self.lyrics_view.clear_document();self._expected_transcription_source=asset.source_path.resolve()
        self._set_workflow(self._workflow_state.start(WorkflowStep.LYRICS,"Detecting language and generating lyrics"))
        if self._transcription_controller is None:self._configure_transcription()
        if self._transcription_controller is None:self._set_workflow(self._workflow_state.fail(self._asr_initialization_error or "The bundled Whisper lyric engine could not start. Reinstall Karaoke AI Studio."));return
        self._transcription_controller.start(asset,{"model":"large-v3","device":"auto","compute":"int8","language":"","task":"transcribe","beam":10,"vad":True,"context":False,"prompt":"Filipino and English song lyrics. Preserve Tagalog and Taglish spelling, contractions, repeated choruses, and complete lines. Do not translate.","destination":str(self._paths.export_dir/"transcripts")})

    def _start_auto_alignment(self)->None:
        if self._word_alignment_controller is None:self._configure_word_alignment()
        if self._word_alignment_controller is None:self._set_workflow(self._workflow_state.fail("The word-timing engine is unavailable."));return
        self._word_alignment_controller.start(self._current_transcript,self._paths.export_dir/"transcripts")

    def _retry_current_step(self)->None:
        if self._workflow_state.current==WorkflowStep.SEPARATE:self._start_auto_mode(self.studio_view.wizard.style.currentText())
        elif self._workflow_state.current==WorkflowStep.LYRICS and isinstance(self.project_content.current_asset(),MediaAsset):self._start_auto_transcription(self.project_content.current_asset())
        elif self._workflow_state.current==WorkflowStep.REVIEW:self._start_auto_alignment()
        elif self._workflow_state.current==WorkflowStep.RENDER:self._render_video()

    def _cancel_active_task(self)->None:
        for controller in (self._separation_controller,self._cleanup_controller,self._transcription_controller,self._word_alignment_controller,self._video_render_controller):
            if controller is not None and getattr(controller,"busy",False):controller.cancel()
        self._auto_pipeline_active=False
        self._set_workflow(self._workflow_state.fail("Operation cancelled. You can retry when ready."))

    def _show_update_dialog(self) -> None:
        import os
        dialog=UpdateDialog(self._settings.application.version,self);dialog.checkRequested.connect(lambda:self._update_controller.check(self._settings.application.version,os.getenv("KAS_UPDATE_MANIFEST_URL","")));dialog.downloadRequested.connect(lambda release:self._update_controller.download(release,self._paths.data_dir/"updates"));dialog.cancelRequested.connect(self._update_controller.cancel);dialog.openFolderRequested.connect(self._open_update_folder);self._update_controller.progressChanged.connect(dialog.update_progress);self._update_controller.checkSucceeded.connect(dialog.show_check);self._update_controller.downloadSucceeded.connect(dialog.show_download);self._update_controller.failed.connect(dialog.show_error);self._update_dialog=dialog;dialog.open()

    def _open_update_folder(self,path:object)->None:
        from pathlib import Path
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        if isinstance(path,Path):QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))

    def _refresh_plugins(self) -> None:
        self.plugin_view.set_records(self._plugin_manager.discover())

    def _set_plugin_enabled(self, plugin_id: str, enabled: bool) -> None:
        self._plugin_manager.set_enabled(plugin_id, enabled)
        self.statusBar().showMessage("Plugin state saved; restart Karaoke AI Studio to apply the change.", 7000)
        self._refresh_plugins()

    def _configure_translation(self) -> None:
        try:
            self._translation_adapter=ArgosTextTranslator();self._translation_controller=TranslationController(LyricsTranslationService(self._translation_adapter,TranslationRepository()));self._translation_controller.progressChanged.connect(self._on_translation_progress);self._translation_controller.succeeded.connect(self._on_translation_succeeded);self._translation_controller.failed.connect(self._on_translation_failed)
        except Exception as exc:LOGGER.warning("Translation unavailable: %s",exc);self.translate_action.setToolTip(str(exc)) if hasattr(self,"translate_action") else None

    def _translate_lyrics(self) -> None:
        document=self.lyrics_view.word_model.document
        if document is None:QMessageBox.information(self,"Edited Lyrics Required","Complete word alignment before translating lyrics.");return
        if self._translation_controller is None or self._translation_adapter is None:self._configure_translation()
        if self._translation_controller is None or self._translation_adapter is None:QMessageBox.critical(self,"Translation Runtime Required","Run scripts\\setup_translation.ps1, then restart the application.");return
        dialog=TranslationDialog(self._translation_adapter.installed_pairs(),document.language,self);dialog.translateRequested.connect(lambda options:self._translation_controller.start(document,options,self._paths.export_dir/"translations"));dialog.cancelRequested.connect(self._translation_controller.cancel);dialog.modelInstallRequested.connect(self._install_translation_model);self._translation_dialog=dialog;dialog.open()

    def _install_translation_model(self,path:object)->None:
        from pathlib import Path
        try:
            if self._translation_adapter and isinstance(path,Path):self._translation_adapter.install_model(path);self._translation_dialog.refresh_pairs(self._translation_adapter.installed_pairs()) if self._translation_dialog else None
        except Exception as exc:
            if self._translation_dialog:self._translation_dialog.show_error(str(exc))

    def _on_translation_progress(self,value:int,text:str)->None:
        self._status_progress.setRange(0,100);self._status_progress.setVisible(True);self._status_progress.setValue(value);self.statusBar().showMessage(text)
        if self._translation_dialog:self._translation_dialog.update_progress(value,text)

    def _on_translation_succeeded(self,value:object)->None:
        if not isinstance(value,tuple) or len(value)!=2:self._on_translation_failed("Translation returned invalid data.");return
        document,path=value;self.lyrics_view.show_translation(document);self._view_model.select_page(int(WorkspacePage.LYRICS));self.statusBar().showMessage(f"Translation saved: {path.name}",8000)
        if self._translation_dialog:self._translation_dialog.accept();self._translation_dialog=None
        self._status_progress.setVisible(False)

    def _on_translation_failed(self,message:str)->None:
        if self._translation_dialog:self._translation_dialog.show_error(message)
        self._status_progress.setVisible(False);self.statusBar().showMessage("Lyrics translation did not complete",5000)

    def _configure_batch(self) -> None:
        try:
            executor=FFmpegBatchJobExecutor(locate_ffmpeg(),locate_ffprobe());queue_path=self._paths.data_dir/"batch-queue.json";self._batch_controller=BatchQueueController(executor,BatchQueueRepository(),queue_path);self._batch_controller.jobsChanged.connect(self.batch_view.set_jobs);self.batch_view.set_jobs(self._batch_controller.jobs);self.batch_view.addRequested.connect(self._add_batch_jobs);self.batch_view.startRequested.connect(self._batch_controller.start);self.batch_view.cancelRequested.connect(self._batch_controller.cancel);self.batch_view.retryRequested.connect(self._batch_controller.retry);self.batch_view.removeRequested.connect(self._batch_controller.remove)
        except Exception as exc:LOGGER.warning("Batch processing unavailable: %s",exc)

    def _add_batch_jobs(self,sources:tuple,operation:object)->None:
        from app.domain.models.batch import BatchOperation
        if self._batch_controller and isinstance(operation,BatchOperation):
            root=self._paths.export_dir/"batch"/("audio" if operation==BatchOperation.EXTRACT_WAV24 else "quality");self._batch_controller.add(sources,operation,root);self._view_model.select_page(int(WorkspacePage.BATCH))

    def _configure_final_export(self) -> None:
        try:
            service=FinalExportService(FFmpegQualityValidator(locate_ffprobe(),locate_ffmpeg()),QualityReportRepository());self._final_export_controller=FinalExportController(service);self._final_export_controller.progressChanged.connect(self._on_final_export_progress);self._final_export_controller.succeeded.connect(self._on_final_export_succeeded);self._final_export_controller.failed.connect(self._on_final_export_failed);self._final_export_controller.busyChanged.connect(self._on_final_export_busy)
        except Exception as exc:LOGGER.warning("Final export validation unavailable: %s",exc)

    def _validate_final_export(self) -> None:
        if self._final_export_controller is None:self._configure_final_export()
        if self._final_export_controller is None:QMessageBox.critical(self,"Validation Unavailable","Final validation requires FFmpeg and FFprobe.");return
        dialog=FinalExportDialog(self._paths.export_dir/"quality",self);dialog.validationRequested.connect(lambda source:self._final_export_controller.start(source,self._paths.export_dir/"quality"));dialog.cancelRequested.connect(self._final_export_controller.cancel);self._final_export_dialog=dialog;dialog.open()

    def _on_final_export_progress(self,value:int,text:str)->None:
        self._status_progress.setRange(0,100);self._status_progress.setValue(value);self.statusBar().showMessage(text)
        if self._final_export_dialog:self._final_export_dialog.update_progress(value,text)

    def _on_final_export_succeeded(self,value:object)->None:
        if not isinstance(value,tuple) or len(value)!=2:self._on_final_export_failed("Quality validation returned invalid data.");return
        report,path=value
        from app.domain.models.quality_validation import MediaQualityReport
        if not isinstance(report,MediaQualityReport):self._on_final_export_failed("Quality report is invalid.");return
        if self._final_export_dialog:self._final_export_dialog.show_report(report,path)
        self.statusBar().showMessage(("Final export passed" if report.passed else "Final export failed")+f" • {report.warning_count} warning(s)",9000)

    def _on_final_export_failed(self,message:str)->None:
        if self._final_export_dialog:self._final_export_dialog.show_error(message)
        self.statusBar().showMessage("Final export validation did not complete",5000)

    def _on_final_export_busy(self,busy:bool)->None:
        self.validate_export_action.setEnabled(not busy);self._status_progress.setVisible(busy)
        if not busy:self._status_progress.setValue(0)

    def _create_export_profile(self) -> None:
        dialog=ExportProfileDialog(self);dialog.profileCreated.connect(self._save_export_profile);dialog.open()

    def _save_export_profile(self,profile:object)->None:
        from app.domain.models.export_profile import ExportProfile
        if not isinstance(profile,ExportProfile):return
        try:
            ExportProfileService.validate(profile);self._user_export_profiles=(*self._user_export_profiles,profile);self._export_profile_repository.save(self._user_export_profiles)
            if self._video_render_dialog:self._video_render_dialog.refresh_profiles(ExportProfileService.merge(self._user_export_profiles,self._plugin_context.export_profiles))
            self.statusBar().showMessage(f"Export profile saved: {profile.name}",5000)
        except Exception as exc:QMessageBox.warning(self,"Export Profile",str(exc))

    def _configure_video_rendering(self) -> None:
        try:
            self._video_renderer=FFmpegVideoRenderer(locate_ffmpeg());self._video_render_controller=VideoRenderController(VideoRenderService(self._video_renderer));self._video_render_controller.progressChanged.connect(self._on_video_render_progress);self._video_render_controller.succeeded.connect(self._on_video_render_succeeded);self._video_render_controller.failed.connect(self._on_video_render_failed);self._video_render_controller.busyChanged.connect(self._on_video_render_busy)
        except Exception as exc:LOGGER.warning("Video rendering unavailable: %s",exc)

    def _render_video(self) -> None:
        document=self.lyrics_view.word_model.document;duration=document.duration_seconds if document else 300.0
        if document is not None:
            self._save_lyrics(document)
            self._save_editable_project_snapshot(document)
        if document is None or self._current_transcript is None:
            QMessageBox.warning(self,"Current Lyrics Required","Generate and review lyrics for the current song before rendering. Previous-project lyrics are never reused.");return
        if document.source_path.resolve()!=self._current_transcript.source_path.resolve():
            QMessageBox.critical(self,"Lyrics Do Not Match Current Song","The lyric document belongs to a different source. Rendering was blocked to prevent old lyrics from appearing.");return
        if self._video_render_controller is None or self._video_renderer is None:self._configure_video_rendering()
        if self._video_render_controller is None or self._video_renderer is None:QMessageBox.critical(self,"FFmpeg Required","Video rendering requires FFmpeg with libass support.");return
        profiles=ExportProfileService.merge(self._user_export_profiles,self._plugin_context.export_profiles)
        instrumental=self._auto_instrumental_path
        if instrumental is None or not instrumental.is_file():
            QMessageBox.warning(self,"Current Song Is Not Ready","Run Separate Vocals for the current song before rendering. Old project stems will not be reused.");return
        # Always regenerate the ASS from the current in-memory lyric document.
        # Never reuse an existing same-named subtitle from another project.
        subtitle=None
        if document is not None:
            try:
                current_subtitle_dir=self._paths.export_dir/"subtitles"/document.source_path.stem
                current_subtitle_dir.mkdir(parents=True,exist_ok=True)
                from app.domain.models.subtitles import SubtitleFormat,SubtitleOptions,SubtitleStyle
                options=SubtitleOptions((SubtitleFormat.ASS,),7,5.0,.8,.15,.25,1920,1080,SubtitleStyle(font_size=78,margin_vertical=150,effect_settings=self._karaoke_effect_settings))
                _,generated=self._subtitle_service.generate(document,options,current_subtitle_dir)
                subtitle=next((p for p in generated if p.suffix.lower()==".ass"),None)
                if subtitle:self.statusBar().showMessage(f"ASS subtitles created automatically: {subtitle.name}",7000)
            except Exception as exc:
                LOGGER.exception("Automatic ASS subtitle generation failed");QMessageBox.critical(self,"Could Not Prepare Render",f"Lyrics are saved, but ASS subtitles could not be created automatically.\n\n{exc}");return
        dialog=VideoRenderDialog(duration,self._paths.export_dir,self._video_renderer.available_encoders(),profiles,self,default_audio=instrumental,default_subtitle=subtitle,default_source=(self._auto_original_asset.source_path if isinstance(self._auto_original_asset,MediaAsset) else None));dialog.renderRequested.connect(self._video_render_controller.start);dialog.cancelRequested.connect(self._video_render_controller.cancel);dialog.createProfileRequested.connect(self._create_export_profile);self._video_render_dialog=dialog;dialog.open()

    def _on_video_render_progress(self,value:int,text:str)->None:
        self._status_progress.setRange(0,100);self._status_progress.setValue(value);self.statusBar().showMessage(text)
        if self._video_render_dialog:self._video_render_dialog.update_progress(value,text)

    def _on_video_render_succeeded(self,value:object)->None:
        from app.domain.models.video_render import VideoRenderResult
        if not isinstance(value,VideoRenderResult):self._on_video_render_failed("Video renderer returned invalid data.");return
        if self._video_render_dialog:self._video_render_dialog.accept();self._video_render_dialog=None
        self.statusBar().showMessage(f"Rendered {value.output_path.name} with {value.encoder_name}",9000)
        completed=frozenset(WorkflowStep)
        self._auto_pipeline_active=False;self._auto_waiting_for_vocals=False
        self._set_workflow(WorkflowState(WorkflowStep.EXPORT,completed,False,"Video ready — lyrics, style, and render settings remain editable",100,None))
        self._record_render_history(value)
        if self._separation_dialog:self._separation_dialog.close();self._separation_dialog=None
        if self._import_controller:self._import_controller.import_file(value.output_path)
        QTimer.singleShot(700,self._player.pause)
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        box=QMessageBox(self);box.setWindowTitle("Render Complete");box.setText(f"Finished video loaded in the player (paused).\n\n{value.output_path.name}");open_button=box.addButton("Open Output Folder",QMessageBox.ButtonRole.ActionRole);box.addButton(QMessageBox.StandardButton.Ok);box.exec()
        if box.clickedButton() is open_button:QDesktopServices.openUrl(QUrl.fromLocalFile(str(value.output_path.parent)))

    def _project_snapshot_path(self) -> Path:
        return self._paths.data_dir/"autosave"/"current-project.json"

    def _save_editable_project_snapshot(self,document:object)->None:
        path=self._project_snapshot_path();path.parent.mkdir(parents=True,exist_ok=True)
        payload={"version":"0.29.2","source":str(getattr(document,"source_path","")),"lyrics":str(self._paths.export_dir/"lyrics"),"instrumental":str(self._auto_instrumental_path or ""),"style":self._auto_style,"workflow":self._workflow_state.current.value,"saved_at":datetime.now().isoformat(timespec="seconds")}
        temporary=path.with_suffix(".tmp");temporary.write_text(json.dumps(payload,indent=2),encoding="utf-8");temporary.replace(path)

    def _history_path(self)->Path:return self._paths.data_dir/"render-history.json"
    def _load_render_history(self)->None:
        try:self._render_history=json.loads(self._history_path().read_text(encoding="utf-8"))
        except (OSError,ValueError):self._render_history=[]
        self.history_view.set_records(self._render_history)
    def _save_render_history(self)->None:
        path=self._history_path();path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(self._render_history,indent=2),encoding="utf-8");self.history_view.set_records(self._render_history)
    def _record_render_history(self,value:object)->None:
        source=self._auto_original_asset.source_path.stem if isinstance(self._auto_original_asset,MediaAsset) else getattr(value.output_path,"stem","Karaoke")
        self._render_history.insert(0,{"project":source,"completed":datetime.now().isoformat(timespec="minutes"),"duration":f"{getattr(value,'elapsed_seconds',0):.1f}s","encoder":getattr(value,"encoder_name",""),"output":str(value.output_path)})
        self._save_render_history()
    def _remove_render_history(self,row:int)->None:
        if 0<=row<len(self._render_history):self._render_history.pop(row);self._save_render_history()
    def _open_render_output(self,path:object)->None:
        from PySide6.QtGui import QDesktopServices
        if isinstance(path,Path) and path.exists():QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _on_video_render_failed(self,message:str)->None:
        if self._video_render_dialog:self._video_render_dialog.show_error(message)
        self.statusBar().showMessage("Video rendering did not complete",5000)

    def _on_video_render_busy(self,busy:bool)->None:
        self._status_progress.setVisible(busy);self.render_video_action.setEnabled(not busy)
        if not busy:self._status_progress.setValue(0)

    def _configure_karaoke_effects(self) -> None:
        dialog=KaraokeEffectDialog(self._karaoke_effect_settings,self);dialog.settingsApplied.connect(self._apply_karaoke_effects);dialog.open()

    def _apply_karaoke_effects(self,settings:object) -> None:
        from app.domain.models.karaoke_effects import KaraokeEffectSettings
        if isinstance(settings,KaraokeEffectSettings):
            self._karaoke_effect_settings=settings;self.statusBar().showMessage(f"Karaoke effect selected: {settings.effect.value.replace('_',' ').title()}",5000)

    def _generate_subtitles(self) -> None:
        from app.domain.models.lyrics_document import LyricsDocument
        document=self.lyrics_view.word_model.document
        if not isinstance(document,LyricsDocument):QMessageBox.information(self,"Edited Lyrics Required","Complete word alignment before generating subtitles.");return
        dialog=SubtitleGenerationDialog(document.source_path.name,self._paths.export_dir/"subtitles",self);dialog.generationRequested.connect(lambda options:self._run_subtitle_generation(document,options));self._subtitle_dialog=dialog;dialog.open()

    def _run_subtitle_generation(self,document:object,options:object) -> None:
        from app.domain.models.lyrics_document import LyricsDocument
        from app.domain.models.subtitles import SubtitleOptions
        if not isinstance(document,LyricsDocument) or not isinstance(options,SubtitleOptions):return
        from dataclasses import replace
        options=replace(options,style=replace(options.style,effect_settings=self._karaoke_effect_settings))
        try:
            subtitle_document,paths=self._subtitle_service.generate(document,options,current_subtitle_dir);
            if self._subtitle_dialog:self._subtitle_dialog.accept();self._subtitle_dialog=None
            names=", ".join(path.name for path in paths);self.statusBar().showMessage(f"Generated {len(paths)} subtitle file(s): {names}",9000);LOGGER.info("Generated %d cues to %s",len(subtitle_document.cues),paths)
        except (RuntimeError,OSError,ValueError) as exc:
            LOGGER.exception("Subtitle generation failed")
            if self._subtitle_dialog:self._subtitle_dialog.show_error(str(exc))

    def _save_lyrics(self, value: object = None) -> None:
        from app.domain.models.lyrics_document import LyricsDocument
        document=value if isinstance(value,LyricsDocument) else self.lyrics_view.word_model.document
        if not isinstance(document,LyricsDocument):
            QMessageBox.information(self,"No Edited Lyrics","Complete word alignment before saving lyrics.");return
        try:
            path=self._lyrics_repository.save(document,self._paths.export_dir/"lyrics");self.lyrics_view.mark_saved(path);self.statusBar().showMessage(f"Lyrics saved: {path.name}",7000);LOGGER.info("Lyrics document saved: %s",path)
        except OSError as exc:
            LOGGER.exception("Lyrics save failed");QMessageBox.critical(self,"Save Lyrics Failed",str(exc))

    def _show_about(self) -> None:
        QMessageBox.about(self, "About Karaoke AI Studio", "<b>Karaoke AI Studio</b><br>Version 0.29.2<br><br>A professional AI-powered karaoke production environment.<br><br><b>Created by Rostum Hernandez</b><br>All rights reserved © 2026")

    def _reset_layout(self) -> None:
        self.project_dock.show(); self.properties_dock.show(); self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_dock); self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock); self.resize(1440, 900); self.statusBar().showMessage("Workspace layout reset", 3000)

    def _restore_window_state(self) -> None:
        geometry = self._native_settings.value("window/geometry"); state = self._native_settings.value("window/state")
        if isinstance(geometry, QByteArray): self.restoreGeometry(geometry)
        if isinstance(state, QByteArray): self.restoreState(state)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._update_controller and not self._update_controller.shutdown():
            QMessageBox.warning(self,"Update Operation Running","The application is waiting for the update operation to stop.");event.ignore();return
        if self._translation_controller and not self._translation_controller.shutdown():
            QMessageBox.warning(self,"Translation Still Running","The application is waiting for translation to stop.");event.ignore();return
        if self._batch_controller and not self._batch_controller.shutdown():
            QMessageBox.warning(self,"Batch Job Running","The application is waiting for the current batch job to stop.");event.ignore();return
        if getattr(self, "_final_export_controller", None) and not self._final_export_controller.shutdown():
            QMessageBox.warning(self,"Validation Still Running","The application is waiting for final validation to stop.");event.ignore();return
        if self._video_render_controller and not self._video_render_controller.shutdown():
            QMessageBox.warning(self,"Render Still Running","The application is waiting for video rendering to stop.");event.ignore();return
        if self._word_alignment_controller and not self._word_alignment_controller.shutdown():
            QMessageBox.warning(self,"Alignment Still Running","The application is waiting for word alignment to stop.");event.ignore();return
        if self._transcription_controller and not self._transcription_controller.shutdown():
            QMessageBox.warning(self,"Transcription Still Running","The application is waiting for speech recognition to stop.");event.ignore();return
        if self._cleanup_controller and not self._cleanup_controller.shutdown():
            QMessageBox.warning(self,"Cleanup Still Running","The application is waiting for instrumental cleanup to stop.");event.ignore();return
        if self._separation_controller and not self._separation_controller.shutdown():
            QMessageBox.warning(self,"Separation Still Running","The application is waiting for AI separation to stop."); event.ignore(); return
        if self._extraction_controller and not self._extraction_controller.shutdown():
            QMessageBox.warning(self, "Extraction Still Running", "The application is waiting for audio extraction to stop."); event.ignore(); return
        if self._import_controller and not self._import_controller.shutdown():
            QMessageBox.warning(self, "Import Still Running", "The application is waiting for media inspection to stop."); event.ignore(); return
        self._plugin_manager.deactivate_all()
        self._native_settings.setValue("window/geometry", self.saveGeometry()); self._native_settings.setValue("window/state", self.saveState()); self._native_settings.sync(); LOGGER.info("Window state saved; application closing"); super().closeEvent(event)
