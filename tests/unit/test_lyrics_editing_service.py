from pathlib import Path
import pytest
from app.application.errors import MediaImportError
from app.application.services.lyrics_editing_service import LyricsEditingService
from app.domain.models.lyrics_document import EditableWord, LyricsDocument

def document():return LyricsDocument(Path("song.wav"),"en",10,(EditableWord(0,0,"hello",0,1,.9),EditableWord(1,0,"world",1,2,.8)),0)
def test_shift_selected_words():
 result=LyricsEditingService.shift_words(document(),(1,),.5);assert result.words[1].start_seconds==1.5 and result.revision==1
def test_rejects_overlap():
 with pytest.raises(MediaImportError,match="overlaps"):LyricsEditingService.shift_words(document(),(1,),-.5)
def test_scale_selected_interval():
 d=LyricsDocument(Path("x"),"en",10,(EditableWord(0,0,"a",1,2,.9),EditableWord(1,0,"b",2,3,.9)),0);r=LyricsEditingService.scale_interval(d,(0,1),2);assert r.words[1].end_seconds==5
