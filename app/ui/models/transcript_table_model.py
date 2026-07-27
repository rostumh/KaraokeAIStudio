from __future__ import annotations
import math
from PySide6.QtCore import QAbstractTableModel,QModelIndex,Qt,Signal
from app.domain.models.transcription import Transcript,TranscriptSegment,TranscriptionOptions,TranscriptionTask,WhisperDevice
from app.domain.models.lyrics_document import LyricsDocument
from app.ui.formatters import format_duration
class TranscriptTableModel(QAbstractTableModel):
    HEADERS=('Start','End','Text','Confidence');segmentTextChanged=Signal(int,str)
    def __init__(self)->None:super().__init__();self._transcript:Transcript|None=None
    def rowCount(self,parent=QModelIndex()):return 0 if parent.isValid() or self._transcript is None else len(self._transcript.segments)
    def columnCount(self,parent=QModelIndex()):return 4
    def data(self,index,role=Qt.ItemDataRole.DisplayRole):
        if role not in (Qt.ItemDataRole.DisplayRole,Qt.ItemDataRole.EditRole) or not index.isValid() or self._transcript is None:return None
        s=self._transcript.segments[index.row()];vals=(format_duration(s.start_seconds),format_duration(s.end_seconds),s.text,f'{min(1,max(0,math.exp(s.average_log_probability)))*100:.0f}%');return vals[index.column()]
    def headerData(self,section,orientation,role=Qt.ItemDataRole.DisplayRole):return self.HEADERS[section] if role==Qt.ItemDataRole.DisplayRole and orientation==Qt.Orientation.Horizontal else super().headerData(section,orientation,role)
    def flags(self,index):return super().flags(index)|(Qt.ItemFlag.ItemIsEditable if index.isValid() and index.column()==2 else Qt.ItemFlag.NoItemFlags)
    def setData(self,index,value,role=Qt.ItemDataRole.EditRole):
        if role!=Qt.ItemDataRole.EditRole or not index.isValid() or index.column()!=2:return False
        text=str(value).strip()
        if not text:return False
        self.segmentTextChanged.emit(index.row(),text);return True
    def set_transcript(self,transcript):self.beginResetModel();self._transcript=transcript;self.endResetModel()
    def set_document(self,document:LyricsDocument):
        groups=[]
        for segment_id in sorted({w.segment_id for w in document.words}):
            words=[w for w in document.words if w.segment_id==segment_id]
            if words:groups.append(TranscriptSegment(segment_id,words[0].start_seconds,words[-1].end_seconds,' '.join(w.text for w in words),0.0,0.0))
        options=TranscriptionOptions('external',WhisperDevice.CPU,'default',document.language,TranscriptionTask.TRANSCRIBE,1,False,False,None)
        self.set_transcript(Transcript(document.source_path,document.language,1.0,document.duration_seconds,options,tuple(groups)))
