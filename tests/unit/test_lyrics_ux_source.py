from pathlib import Path

def test_fast_text_correction_and_save_ux():
 s=Path('app/ui/views/lyrics_view.py').read_text()
 for text in ('Apply Text Corrections','Next Uncertain Word','setShortcut("Ctrl+S")','_apply_text_corrections','Word Count Changed'):
  assert text in s

def test_alignment_autosaves_and_does_not_jump_to_render():
 s=Path('app/ui/main_window.py').read_text()
 handler=s.split('def _on_alignment_succeeded',1)[1].split('def _on_alignment_failed',1)[0]
 assert '_lyrics_repository.save' in handler
 assert 'select_page(int(WorkspacePage.LYRICS))' in handler
 assert '_render_video()' not in handler

def test_transcription_uses_higher_accuracy_defaults():
 s=Path('app/ui/main_window.py').read_text()
 assert '"model":"large-v3"' in s and '"beam":10' in s
