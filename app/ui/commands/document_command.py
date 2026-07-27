from PySide6.QtGui import QUndoCommand

class ReplaceLyricsDocumentCommand(QUndoCommand):
    def __init__(self, model, before, after, label="Edit lyrics"):
        super().__init__(label); self.model=model; self.before=before; self.after=after
    def redo(self): self.model.set_document(self.after)
    def undo(self): self.model.set_document(self.before)
