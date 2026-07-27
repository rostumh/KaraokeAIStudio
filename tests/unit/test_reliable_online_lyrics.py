from pathlib import Path
from app.lyrics_engine.factory import create_lyrics_engine
from app.lyrics_engine.models import LyricsResult,LyricsSource,SongIdentity
from app.lyrics_engine.review_document import LyricsReviewDocumentBuilder

def test_provider_order_lrclib_then_lyrics_ovh(tmp_path):
 e=create_lyrics_engine(tmp_path);names=[p.name for p in e.providers._providers]
 assert names==['LRCLIB','Lyrics.ovh']
def test_synced_lrc_builds_reviewable_document():
 song=SongIdentity('Song','Artist',duration_seconds=10,media_path=Path('song.mp3'))
 result=LyricsResult(song,'[00:01.00]Hello world\n[00:05.00]Second line',LyricsSource.ONLINE,'LRCLIB',True)
 doc=LyricsReviewDocumentBuilder().build(result)
 assert [w.text for w in doc.words]==['Hello','world','Second','line']
 assert doc.words[0].start_seconds==1 and doc.words[2].start_seconds==5
def test_plain_online_lyrics_are_reviewable_and_continuable():
 song=SongIdentity('Song','Artist',duration_seconds=12,media_path=Path('song.mp3'))
 result=LyricsResult(song,'First line\nSecond line',LyricsSource.ONLINE,'Lyrics.ovh',False)
 doc=LyricsReviewDocumentBuilder().build(result)
 assert len(doc.words)==4 and doc.duration_seconds==12
def test_ui_source_confidence_warning_and_online_lock():
 view=Path('app/ui/views/lyrics_view.py').read_text();main=Path('app/ui/main_window.py').read_text()
 assert 'Ready to review and continue' in view and 'continue_button.setEnabled(bool(document.words))' in view
 assert 'Official Lyrics' in main and 'Lyrics Source: Whisper' in main
 assert 'Lyrics may contain transcription errors.' in main
 assert 'Discarded Whisper result because official online lyrics are locked' in main
