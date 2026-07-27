from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel,QModelIndex,Qt
from app.domain.models.translation import TranslationDocument
from app.ui.formatters import format_duration
class TranslationTableModel(QAbstractTableModel):
 HEADERS=("Start","End","Original","Translation")
 def __init__(self)->None:super().__init__();self._document:TranslationDocument|None=None
 def rowCount(self,parent:QModelIndex=QModelIndex())->int:return 0 if parent.isValid() or self._document is None else len(self._document.lines)
 def columnCount(self,parent:QModelIndex=QModelIndex())->int:return 4
 def data(self,index:QModelIndex,role:int=Qt.ItemDataRole.DisplayRole)->object|None:
  if role!=Qt.ItemDataRole.DisplayRole or not index.isValid() or self._document is None:return None
  line=self._document.lines[index.row()];return (format_duration(line.start_seconds),format_duration(line.end_seconds),line.source_text,line.translated_text)[index.column()]
 def headerData(self,section:int,orientation:Qt.Orientation,role:int=Qt.ItemDataRole.DisplayRole)->object|None:
  if role==Qt.ItemDataRole.DisplayRole and orientation==Qt.Orientation.Horizontal:return self.HEADERS[section]
  return super().headerData(section,orientation,role)
 def set_document(self,d:TranslationDocument)->None:self.beginResetModel();self._document=d;self.endResetModel()
