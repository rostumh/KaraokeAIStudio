from pathlib import Path
from app.lyrics_engine.filipino import FilipinoLyricsPostProcessor
from app.lyrics_engine.models import LyricsResult,LyricsSource,SongIdentity
from app.lyrics_engine.providers.manager import LyricsProviderManager
from app.lyrics_engine.validation import LyricsMatchValidator
class P:
 def __init__(self,name,result):self._name=name;self.result=result
 @property
 def name(self):return self._name
 def search(self,song):return self.result
def result(song,text,synced=False,provider='p'):return LyricsResult(song,text,LyricsSource.ONLINE,provider,synced)
def test_anak_metadata_candidate_validates_without_embedding_copyrighted_lyrics():
 song=SongIdentity('Anak','Freddie Aguilar',duration_seconds=235)
 sample=' '.join(['sample']*150)
 score=LyricsMatchValidator().score(song,result(song,sample))
 assert score.accepted and score.confidence>.8
def test_wrong_song_rejected_even_if_long():
 requested=SongIdentity('Anak','Freddie Aguilar',duration_seconds=235)
 wrong=SongIdentity('Completely Different','Another Artist',duration_seconds=235)
 assert not LyricsMatchValidator().score(requested,result(wrong,'word '*500)).accepted
def test_lrc_wins_over_plain_even_when_plain_provider_runs_first():
 song=SongIdentity('Anak','Freddie Aguilar',duration_seconds=235);text='salita '*150
 plain=result(song,text,False,'plain');lrc=result(song,'[00:01.00]'+text,True,'lrc')
 found=LyricsProviderManager([P('plain',plain),P('lrc',lrc)]).search(song)
 assert found and found.synchronized and found.provider=='lrc'
def test_taglish_cleanup_is_conservative():
 cleaned=FilipinoLyricsPostProcessor().clean_text('diba mahal kita, dont let me go')
 assert cleaned=="'Di ba mahal kita, dont let me go"
def test_ui_separates_vocals_before_whisper_and_uses_large_v3():
 source=Path('app/ui/main_window.py').read_text()
 assert 'Isolating vocals before transcription' in source
 assert '_auto_waiting_for_vocals=True' in source
 assert '"model":"large-v3"' in source and '"language":""' in source
