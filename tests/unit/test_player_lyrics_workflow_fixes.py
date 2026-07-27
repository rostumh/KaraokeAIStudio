from pathlib import Path

def test_real_video_surface_is_connected_to_player():
 preview=Path('app/ui/widgets/video_preview.py').read_text()
 main=Path('app/ui/main_window.py').read_text()
 assert 'QVideoWidget' in preview and 'self.video_widget' in preview
 assert 'setVideoOutput(self.studio_view.preview.video_widget)' in main

def test_render_dialog_has_persistent_automatic_lyric_adjusters():
 s=Path('app/ui/dialogs/video_render_dialog.py').read_text()
 for text in ('Lyric text size','Subtitle position','render/lyricSize','_styled_subtitle','fields[2]','fields[21]'):
  assert text in s
 assert 'Lyric height' not in s
 assert 'render/lyricHeight' not in s

def test_success_marks_style_render_export_completed():
 s=Path('app/ui/main_window.py').read_text()
 block=s.split('def _on_video_render_succeeded',1)[1].split('def _on_video_render_failed',1)[0]
 assert 'completed=frozenset(WorkflowStep)' in block
 assert 'Video ready' in block
