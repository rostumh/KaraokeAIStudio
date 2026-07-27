from __future__ import annotations

import json
from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog,QDialogButtonBox,QFormLayout,QLabel,QLineEdit,QPlainTextEdit,QVBoxLayout

class PublishingMetadataDialog(QDialog):
    saved = Signal(object)
    def __init__(self, suggested_name:str, output_dir:Path, parent:object=None)->None:
        super().__init__(parent);self.setWindowTitle("Publishing Details");self.setMinimumSize(720,650);self._output_dir=output_dir
        self.song=QLineEdit(suggested_name);self.artist=QLineEdit();self.writer=QLineEdit();self.publisher=QLineEdit();self.license=QLineEdit();self.permission=QLineEdit();self.channel=QLineEdit();self.keywords=QLineEdit("karaoke, karaoke lyrics, sing along, instrumental")
        note=QLabel("Enter only information you have verified. This tool creates an upload draft; it does not grant music rights or determine copyright ownership.");note.setWordWrap(True)
        form=QFormLayout();
        for label,field in (("Song title",self.song),("Original artist",self.artist),("Writer/composer",self.writer),("Publisher/rightsholder",self.publisher),("License or permission",self.license),("Permission/reference ID",self.permission),("Channel/brand",self.channel),("Keywords (comma-separated)",self.keywords)):form.addRow(label,field)
        self.preview=QPlainTextEdit();self.preview.setReadOnly(True)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel);buttons.button(QDialogButtonBox.StandardButton.Save).setText("Save YouTube Upload Package");buttons.accepted.connect(self._save);buttons.rejected.connect(self.reject)
        layout=QVBoxLayout(self);layout.addWidget(note);layout.addLayout(form);layout.addWidget(QLabel("Generated preview"));layout.addWidget(self.preview,1);layout.addWidget(buttons)
        for field in (self.song,self.artist,self.writer,self.publisher,self.license,self.permission,self.channel,self.keywords):field.textChanged.connect(self._refresh)
        self._refresh()
    def _data(self)->dict[str,object]:
        song=self.song.text().strip() or "Karaoke Song";artist=self.artist.text().strip();brand=self.channel.text().strip();title=f"{song} - Karaoke Version with Lyrics" + (f" | {brand}" if brand else "");title=title[:100]
        tags=[x.strip() for x in self.keywords.text().split(',') if x.strip()];tags += [x for x in (song,artist,f"{song} karaoke",f"{artist} karaoke" if artist else "") if x];tags=list(dict.fromkeys(tags));
        while len(', '.join(tags))>500:tags.pop()
        rights="\n".join(x for x in (f"Original artist: {artist}" if artist else "",f"Writer/composer: {self.writer.text().strip()}" if self.writer.text().strip() else "",f"Publisher/rightsholder: {self.publisher.text().strip()}" if self.publisher.text().strip() else "",f"License/permission: {self.license.text().strip()}" if self.license.text().strip() else "",f"Reference ID: {self.permission.text().strip()}" if self.permission.text().strip() else "") if x) or "Rights information: Complete and verify before publishing."
        description=(f"Sing along with this karaoke version of {song}" + (f" by {artist}" if artist else "") + ".\n\nIncludes synchronized lyrics and an instrumental backing track.\n\nCREDITS AND RIGHTS\n"+rights+"\n\nIMPORTANT: This draft is not proof of permission. Confirm all music, composition, master-recording, artwork, font, logo, and video rights before upload.\n\n#karaoke #lyrics #singalong")[:5000]
        return {"title":title,"description":description,"tags":tags,"song_title":song,"artist":artist,"writer":self.writer.text().strip(),"publisher":self.publisher.text().strip(),"license":self.license.text().strip(),"permission_reference":self.permission.text().strip(),"channel":brand}
    def _refresh(self)->None:
        d=self._data();self.preview.setPlainText(f"TITLE ({len(str(d['title']))}/100)\n{d['title']}\n\nDESCRIPTION ({len(str(d['description']))}/5000)\n{d['description']}\n\nTAGS ({len(', '.join(d['tags']))}/500)\n{', '.join(d['tags'])}")
    def _save(self)->None:
        self._output_dir.mkdir(parents=True,exist_ok=True);d=self._data();base='youtube-upload-package';json_path=self._output_dir/f'{base}.json';txt_path=self._output_dir/f'{base}.txt';json_path.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8');txt_path.write_text(self.preview.toPlainText(),encoding='utf-8');self.saved.emit((json_path,txt_path));self.accept()
