import json
from pathlib import Path
from app.domain.models.lyrics_document import EditableWord,LyricsDocument
from app.infrastructure.repositories.lyrics_document_repository import LyricsDocumentRepository
def test_saves_unicode_document(tmp_path:Path):
 d=LyricsDocument(tmp_path/"v.wav","tl",3,(EditableWord(0,0,"Kumusta",0,1,.9),),2);p=LyricsDocumentRepository().save(d,tmp_path);data=json.loads(p.read_text(encoding="utf-8"));assert data["revision"]==2 and data["words"][0]["text"]=="Kumusta"
