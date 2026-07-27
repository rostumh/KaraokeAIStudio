from pathlib import Path

def test_render_dialog_autofill_persistence_and_background_modes():
 s=Path('app/ui/dialogs/video_render_dialog.py').read_text()
 for text in ('default_audio','default_subtitle','Random item from a folder','Built-in AI-style animated background','QSettings','random.SystemRandom().choice'):
  assert text in s

def test_renderer_supports_generated_aurora():
 s=Path('app/infrastructure/media/ffmpeg_video_renderer.py').read_text()
 assert '__generated_aurora__' in s and 'drawbox=x=mod(t*95' in s and 'gblur=sigma=95' in s

def test_main_window_uses_current_song_outputs_only():
 s=Path('app/ui/main_window.py').read_text()
 block=s.split('def _render_video',1)[1].split('def _on_video_render_progress',1)[0]
 assert 'rglob("no_vocals.*")' not in block
 assert 'glob("*.ass")' not in block
 assert 'Current Song Is Not Ready' in block
 assert 'document.source_path.stem' in block
