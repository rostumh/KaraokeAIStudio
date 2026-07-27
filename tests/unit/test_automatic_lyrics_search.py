from pathlib import Path
from app.lyrics_engine.automatic import AutomaticLyricsSearch
from app.lyrics_engine.identity import SongIdentityResolver
from app.lyrics_engine.models import LyricsResult,LyricsSource,SearchOutcome
class Engine:
 def __init__(self,match=1):self.calls=[];self.match=match
 def search(self,song,progress,allow_whisper):
  self.calls.append((song,allow_whisper))
  result=LyricsResult(song,'lyrics',LyricsSource.ONLINE,'LRCLIB',True) if len(self.calls)==self.match else None
  return SearchOutcome(result,not result,0)
def test_metadata_wins_over_filename():
 p=SongIdentityResolver().resolve(Path('Wrong - Name.mp3'),{'TITLE':'Real Title','ARTIST':'Real Artist','ALBUM':'Album'},180)
 assert (p.primary.title,p.primary.artist,p.primary.album)==('Real Title','Real Artist','Album')
def test_artist_title_and_underscore_filename_candidates():
 r=SongIdentityResolver();p=r.resolve(Path('Artist - Title.mp3'),{},10)
 assert (p.primary.artist,p.primary.title)==('Artist','Title') and (p.alternatives[0].artist,p.alternatives[0].title)==('Title','Artist')
 p=r.resolve(Path('Artist_Title.mp3'),{},10);assert (p.primary.artist,p.primary.title)==('Artist','Title')
def test_automatic_search_tries_reversed_format_without_whisper():
 e=Engine(match=2);statuses=[];result,song=AutomaticLyricsSearch(e).search(Path('Title - Artist.mp3'),{},100,statuses.append)
 assert result and len(e.calls)==2 and all(not allow for _,allow in e.calls)
 assert statuses==['Reading filename...','Searching online lyrics...','Lyrics found.']
def test_no_result_returns_asset_identity_and_status():
 e=Engine(match=99);statuses=[];result,song=AutomaticLyricsSearch(e).search(Path('Artist - Song.mp4'),{},100,statuses.append)
 assert result is None and song.artist=='Artist' and statuses[-1]=='Online search failed.'
def test_main_window_starts_search_and_whisper_fallback():
 s=Path('app/ui/main_window.py').read_text()
 assert '_start_automatic_lyrics_search(asset)' in s
 assert 'Running Whisper...' in s and '_start_auto_transcription(asset)' in s
 assert 'Lyrics generated.' in s
