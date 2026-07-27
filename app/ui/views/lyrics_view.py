from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QAbstractItemView, QDoubleSpinBox, QHeaderView, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPlainTextEdit, QPushButton, QFileDialog, QTabWidget, QTableView, QVBoxLayout, QWidget

from app.domain.models.alignment import AlignedTranscript
from app.domain.models.lyrics_document import LyricsDocument
from app.domain.models.transcription import Transcript
from app.ui.commands.lyrics_commands import ScaleWordsCommand, ShiftWordsCommand
from app.ui.commands.document_command import ReplaceLyricsDocumentCommand
from app.application.services.lyrics_realign_service import parse_lyrics_file, realign_document
from app.ui.delegates.time_delegate import TimeSecondsDelegate
from app.ui.models.editable_lyrics_model import EditableLyricsModel
from app.ui.models.transcript_table_model import TranscriptTableModel
from app.ui.models.translation_table_model import TranslationTableModel


class LyricsView(QWidget):
    """Professional word timing editor with validation, batch tools, and undo history."""

    documentChanged = Signal(object)
    saveRequested = Signal(object)
    continueRequested = Signal()

    def __init__(self) -> None:
        super().__init__()
        title = QLabel("Review Lyrics")
        title.setObjectName("pageTitle")
        self.subtitle = QLabel("Run Whisper speech recognition to create timestamped lyrics.")
        self.subtitle.setObjectName("muted")
        self.save_status = QLabel("Not saved yet")
        self.save_status.setStyleSheet("color:#F6C85F;font-weight:600")
        self.next_step = QLabel("STEP 4 OF 7  •  Review the orange words, then continue to choose a style.")
        self.next_step.setWordWrap(True)
        self.next_step.setStyleSheet("background:#18365f;color:#ffffff;padding:12px;border-radius:6px;font-size:14px;font-weight:600")
        self.undo_stack = QUndoStack(self)
        self.segment_model = TranscriptTableModel();self.segment_model.segmentTextChanged.connect(self._apply_segment_text)
        segment_table = QTableView()
        segment_table.setModel(self.segment_model)
        segment_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.word_model = EditableLyricsModel()
        self.word_model.documentChanged.connect(self._on_document_changed)
        self.word_model.editRequested.connect(self._push_document_edit)
        self.word_model.validationFailed.connect(lambda message: QMessageBox.warning(self, "Invalid Lyrics Edit", message))
        self.word_table = QTableView()
        self.word_table.setModel(self.word_model)
        self.word_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.word_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.word_table.setItemDelegateForColumn(1, TimeSecondsDelegate(self.word_table))
        self.word_table.setItemDelegateForColumn(2, TimeSecondsDelegate(self.word_table))
        self.word_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.word_table.setAlternatingRowColors(True)
        tabs = QTabWidget()
        tabs.addTab(self.word_table, "Review Words")
        tabs.addTab(segment_table, "Advanced: Segments")
        self.translation_model = TranslationTableModel()
        translation_table = QTableView(); translation_table.setModel(self.translation_model); translation_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch); translation_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch); tabs.addTab(translation_table, "Translation")
        self.tabs = tabs
        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(False)
        self.editor.setPlaceholderText("Correct spelling here, then click Apply Text Corrections. Word timing is preserved.")
        self.editor.setToolTip("Fast lyrics correction: edit words as normal text. Keep the same number of words for spelling-only corrections, or use Align These Lyrics when phrases/word count changed.")
        self._updating_editor = False
        self.search = QLineEdit()
        self.search.setPlaceholderText("Find word")
        find_next = QPushButton("Find Next")
        find_next.clicked.connect(self._find_next)
        self.shift = QDoubleSpinBox()
        self.shift.setDecimals(3)
        self.shift.setRange(-10.0, 10.0)
        self.shift.setSingleStep(0.01)
        self.shift.setSuffix(" s")
        shift_button = QPushButton("Shift Selected")
        shift_button.clicked.connect(self._shift_selected)
        self.scale = QDoubleSpinBox()
        self.scale.setDecimals(3)
        self.scale.setRange(0.1, 10.0)
        self.scale.setValue(1.0)
        scale_button = QPushButton("Scale Selected")
        scale_button.clicked.connect(self._scale_selected)
        undo = QPushButton("Undo")
        redo = QPushButton("Redo")
        undo.clicked.connect(self.undo_stack.undo)
        redo.clicked.connect(self.undo_stack.redo)
        undo.setEnabled(False); redo.setEnabled(False)
        self.undo_stack.canUndoChanged.connect(undo.setEnabled)
        self.undo_stack.canRedoChanged.connect(redo.setEnabled)
        low_confidence = QPushButton("Next Uncertain Word")
        low_confidence.clicked.connect(self._next_low_confidence)
        apply_text = QPushButton("Apply Text Corrections")
        apply_text.clicked.connect(self._apply_text_corrections)
        replace_text = QPushButton("Align These Lyrics")
        replace_text.setObjectName("primaryButton")
        replace_text.setToolTip("Paste or import one lyric phrase per line. Matching words keep acoustic timestamps; corrected words are fitted between them.")
        replace_text.clicked.connect(self._replace_full_lyrics)
        import_text = QPushButton("Import Lyrics File")
        import_text.clicked.connect(self._import_lyrics_file)
        self.save_button = QPushButton("Save")
        self.save_button.setShortcut("Ctrl+S")
        self.save_button.clicked.connect(self._request_save)
        self.continue_button = QPushButton("Save and Continue to Choose Style  →")
        self.continue_button.setObjectName("primaryButton")
        self.continue_button.setMinimumHeight(48)
        self.continue_button.clicked.connect(self._save_and_continue)
        controls = QHBoxLayout()
        for widget in (self.search, find_next, low_confidence, undo, redo, apply_text, replace_text, import_text, self.save_button):
            controls.addWidget(widget)
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.addWidget(title)
        root.addWidget(self.next_step)
        root.addWidget(self.subtitle)
        root.addWidget(self.save_status)
        root.addLayout(controls)
        root.addWidget(tabs, 3)
        help_text = QLabel("Tip: use one phrase per line below. Double-click any Word, Start, End, or segment Text cell to edit. Align These Lyrics preserves matched timings. Every edit supports Undo/Redo. Ctrl+S saves.")
        help_text.setObjectName("muted")
        help_text.setWordWrap(True)
        root.addWidget(help_text)
        root.addWidget(self.editor, 2)
        root.addWidget(self.continue_button)

    def clear_document(self) -> None:
        """Remove every lyric artifact so a new project cannot inherit an old song."""
        self.undo_stack.clear()
        self.word_model.set_document(None)
        self.segment_model.set_transcript(None)
        self.translation_model.clear() if hasattr(self.translation_model, "clear") else None
        self.editor.clear()
        self.subtitle.setText("Import a song to generate new lyrics.")
        self.save_status.setText("Not saved yet")
        self.continue_button.setEnabled(False)

    def show_transcript(self, transcript: Transcript) -> None:
        self.segment_model.set_transcript(transcript)
        self.editor.setPlainText(transcript.text)
        self.subtitle.setText(f"Detected language: {transcript.language} ({transcript.language_probability * 100:.1f}% confidence) • {len(transcript.segments)} segments")

    def show_external_lyrics(self, document: LyricsDocument, source: str, confidence: str, warning: str = "") -> None:
        self.undo_stack.clear();self.word_model.set_document(document);self.segment_model.set_document(document);self.tabs.setCurrentIndex(0)
        self.editor.setPlainText(self._document_text(document));self.editor.document().setModified(False)
        detail=f"Lyrics Source: {source}  |  Confidence: {confidence}"
        if warning:detail+=f"  |  Warning: {warning}"
        self.subtitle.setText(detail);self.save_status.setText("Ready to review and continue")
        self.save_status.setStyleSheet("color:#43e6a0;font-weight:600");self.continue_button.setEnabled(bool(document.words))
        self.documentChanged.emit(document)

    def show_alignment(self, alignment: AlignedTranscript) -> None:
        self.undo_stack.clear()
        self.word_model.set_document(LyricsDocument.from_alignment(alignment));self.segment_model.set_document(self.word_model.document)
        self.tabs.setCurrentIndex(0)
        self.editor.setPlainText(self._document_text(self.word_model.document))
        self.editor.document().setModified(False)
        self.continue_button.setEnabled(bool(alignment.words))
        self.subtitle.setText(f"Editing {len(alignment.words)} aligned words • low-confidence rows are highlighted")
        self.save_status.setText("Ready to save")

    def _apply_segment_text(self, segment_id: int, text: str) -> None:
        from dataclasses import replace
        document=self.word_model.document
        if document is None:return
        rows=[i for i,w in enumerate(document.words) if w.segment_id==segment_id];tokens=text.split()
        if len(tokens)!=len(rows):
            QMessageBox.information(self,'Keep Segment Timing',f'This segment has {len(rows)} timed words. Enter {len(rows)} words to preserve timing, or edit individual words in Review Words.')
            return
        words=list(document.words)
        for row,token in zip(rows,tokens):words[row]=replace(words[row],text=token)
        updated=replace(document,words=tuple(words),revision=document.revision+1)
        self.undo_stack.push(ReplaceLyricsDocumentCommand(self.word_model, document, updated, "Edit segment text"))

    def _document_text(self, document: LyricsDocument) -> str:
        lines=[]; current=None
        for word in document.words:
            if word.segment_id != current:
                lines.append([]); current=word.segment_id
            lines[-1].append(word.text)
        return "\n".join(" ".join(line) for line in lines)

    def _push_document_edit(self, before: LyricsDocument, after: LyricsDocument, label: str) -> None:
        self.undo_stack.push(ReplaceLyricsDocumentCommand(self.word_model, before, after, label))

    def _selected_rows(self) -> tuple[int, ...]:
        return tuple(sorted({index.row() for index in self.word_table.selectionModel().selectedRows()}))

    def _shift_selected(self) -> None:
        rows = self._selected_rows()
        if not rows:
            QMessageBox.information(self, "Select Words", "Select one or more word rows to shift.")
            return
        try:
            self.undo_stack.push(ShiftWordsCommand(self.word_model, rows, self.shift.value()))
        except RuntimeError as exc:
            QMessageBox.warning(self, "Invalid Timing Change", str(exc))

    def _scale_selected(self) -> None:
        rows = self._selected_rows()
        if not rows:
            QMessageBox.information(self, "Select Words", "Select one or more word rows to scale.")
            return
        try:
            self.undo_stack.push(ScaleWordsCommand(self.word_model, rows, self.scale.value()))
        except RuntimeError as exc:
            QMessageBox.warning(self, "Invalid Timing Change", str(exc))

    def _find_next(self) -> None:
        term = self.search.text().strip().casefold()
        document = self.word_model.document
        if not term or document is None:
            return
        current = self.word_table.currentIndex().row()
        for offset in range(1, len(document.words) + 1):
            row = (current + offset) % len(document.words)
            if term in document.words[row].text.casefold():
                self.word_table.selectRow(row)
                self.word_table.scrollTo(self.word_model.index(row, 3))
                return

    def _on_document_changed(self, document: object) -> None:
        if isinstance(document, LyricsDocument):
            if not self._updating_editor:
                self._updating_editor = True
                self.editor.setPlainText(self._document_text(document))
                self._updating_editor = False
            self.segment_model.set_document(document)
            self.save_status.setText("Unsaved changes")
            self.save_status.setStyleSheet("color:#F6C85F;font-weight:600")
            self.documentChanged.emit(document)


    def _save_and_continue(self) -> None:
        if self.editor.document().isModified() and not self._apply_text_corrections():
            return
        document = self.word_model.document
        if document is None:
            QMessageBox.information(self, "Lyrics Required", "Generate lyrics before continuing.")
            return
        self.saveRequested.emit(document)
        self.continueRequested.emit()

    def _request_save(self) -> None:
        if self.editor.document().isModified():
            if not self._apply_text_corrections():
                return
        document = self.word_model.document
        if document is None:
            QMessageBox.information(self, "Nothing to Save", "Generate and review lyrics first.")
            return
        self.saveRequested.emit(document)
        self.editor.document().setModified(False)

    def _apply_text_corrections(self) -> bool:
        document = self.word_model.document
        if document is None:
            return False
        corrected = self.editor.toPlainText().split()
        if len(corrected) != len(document.words):
            choice=QMessageBox.question(self,"Word Count Changed",f"The corrected text has {len(corrected)} words, but the timed lyrics have {len(document.words)}.\n\nUse full replacement and rebuild timing now?")
            return self._replace_full_lyrics() if choice==QMessageBox.StandardButton.Yes else False
        from dataclasses import replace
        words = tuple(replace(word, text=text) for word, text in zip(document.words, corrected))
        updated=replace(document, words=words, revision=document.revision + 1)
        self._updating_editor = True
        self.undo_stack.push(ReplaceLyricsDocumentCommand(self.word_model, document, updated, "Correct lyric text"))
        self._updating_editor = False
        self.editor.document().setModified(False)
        self.subtitle.setText(f"Applied spelling corrections to {len(words)} timed words")
        return True

    def _import_lyrics_file(self) -> None:
        path,_=QFileDialog.getOpenFileName(self,"Import Correct Lyrics","","Lyrics (*.txt *.lrc *.srt *.vtt *.ass *.ssa);;All Files (*)")
        if not path:return
        try:
            text=parse_lyrics_file(path)
            self.editor.setPlainText(text); self.editor.document().setModified(True)
            if self.word_model.document is None:
                QMessageBox.information(self,"Lyrics Imported","Lyrics loaded. Generate a transcription first, then click Align These Lyrics.")
                return
            self._replace_full_lyrics(confirm=False, label=f"Import {Path(path).name}")
            self.subtitle.setText(f"Imported and aligned {Path(path).name}. Line breaks were preserved as lyric segments.")
        except (OSError, UnicodeError, ValueError) as exc:
            QMessageBox.warning(self,"Import Lyrics Failed",f"{Path(path).name} could not be imported.\n\n{exc}")

    def _replace_full_lyrics(self, confirm: bool = True, label: str = "Align corrected lyrics") -> bool:
        """Phrase-aware realignment that preserves matched acoustic word timestamps."""
        document=self.word_model.document
        if document is None:return False
        text=self.editor.toPlainText()
        if not text.strip():
            QMessageBox.information(self,"Lyrics Required","Paste or import the complete corrected lyrics first.")
            return False
        if confirm:
            answer=QMessageBox.question(self,"Align Corrected Lyrics","Use each non-empty line as one lyric segment and align its words to the existing acoustic timestamps?\n\nMatched words keep their detected timing. New or corrected words are interpolated between matched words. This change can be undone.")
            if answer!=QMessageBox.StandardButton.Yes:return False
        try: updated=realign_document(document,text)
        except ValueError as exc:
            QMessageBox.warning(self,"Lyrics Alignment Failed",str(exc)); return False
        self._updating_editor=True
        self.undo_stack.push(ReplaceLyricsDocumentCommand(self.word_model,document,updated,label))
        self._updating_editor=False
        self.editor.setPlainText(self._document_text(updated));self.editor.document().setModified(False)
        self.subtitle.setText(f"Aligned {len(updated.words)} words in {len(set(w.segment_id for w in updated.words))} phrases. Matched acoustic timing was preserved.")
        return True

    def _next_low_confidence(self) -> None:
        document = self.word_model.document
        if document is None:
            return
        current = self.word_table.currentIndex().row()
        for offset in range(1, len(document.words) + 1):
            row = (current + offset) % len(document.words)
            if document.words[row].probability < 0.70:
                self.word_table.selectRow(row)
                index = self.word_model.index(row, 3)
                self.word_table.scrollTo(index)
                self.word_table.edit(index)
                return
        QMessageBox.information(self, "Review Complete", "No more low-confidence words were found.")

    def mark_saved(self, path: object) -> None:
        self.save_status.setText(f"[SAVED] {path}")
        self.save_status.setStyleSheet("color:#45D483;font-weight:600")
        self.editor.document().setModified(False)

    def show_translation(self, document: object) -> None:
        from app.domain.models.translation import TranslationDocument
        if isinstance(document, TranslationDocument):
            self.translation_model.set_document(document); self.tabs.setCurrentIndex(2); self.subtitle.setText(f"Translated {len(document.lines)} lines • {document.source_language} → {document.target_language} • {document.engine}")
