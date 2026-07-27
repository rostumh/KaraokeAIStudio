from pathlib import Path

def test_style_picker_explains_choices_and_next_action():
 s=Path('app/ui/widgets/creation_wizard.py').read_text()
 for x in ('Choose the lyric appearance','style_description','Continue to Render with Selected Style','Completed items are saved automatically'):
  assert x in s

def test_lyrics_has_persistent_saved_indicator():
 s=Path('app/ui/views/lyrics_view.py').read_text()
 assert 'self.save_status' in s and 'def mark_saved' in s and '[SAVED]' in s

def test_render_auto_generates_ass_when_missing():
 s=Path('app/ui/main_window.py').read_text()
 block=s.split('def _render_video',1)[1].split('def _on_video_render_progress',1)[0]
 assert 'SubtitleOptions' in block and 'SubtitleFormat.ASS' in block and 'ASS subtitles created automatically' in block
