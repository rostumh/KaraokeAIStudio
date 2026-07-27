from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel,QModelIndex,Qt
from app.domain.models.batch import BatchJob

class BatchJobModel(QAbstractTableModel):
 HEADERS=("Operation","Source","Status","Progress","Message")
 def __init__(self)->None:super().__init__();self._jobs:tuple[BatchJob,...]=()
 @property
 def jobs(self)->tuple[BatchJob,...]:return self._jobs
 def rowCount(self,parent:QModelIndex=QModelIndex())->int:return 0 if parent.isValid() else len(self._jobs)
 def columnCount(self,parent:QModelIndex=QModelIndex())->int:return len(self.HEADERS)
 def data(self,index:QModelIndex,role:int=Qt.ItemDataRole.DisplayRole)->object|None:
  if role!=Qt.ItemDataRole.DisplayRole or not index.isValid():return None
  j=self._jobs[index.row()];return (j.operation.value.replace("_"," ").title(),j.source_path.name,j.status.value.title(),f"{j.progress*100:.0f}%",j.message)[index.column()]
 def headerData(self,section:int,orientation:Qt.Orientation,role:int=Qt.ItemDataRole.DisplayRole)->object|None:
  if role==Qt.ItemDataRole.DisplayRole and orientation==Qt.Orientation.Horizontal:return self.HEADERS[section]
  return super().headerData(section,orientation,role)
 def set_jobs(self,jobs:tuple[BatchJob,...])->None:self.beginResetModel();self._jobs=jobs;self.endResetModel()
