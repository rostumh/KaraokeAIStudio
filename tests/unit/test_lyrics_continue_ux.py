from pathlib import Path

def test_lyrics_editor_has_obvious_next_step():
 s=Path('app/ui/views/lyrics_view.py').read_text()
 for text in ('STEP 4 OF 7','Save and Continue to Choose Style','continueRequested','_save_and_continue','Review Words'):
  assert text in s

def test_continue_returns_to_studio_style_step():
 s=Path('app/ui/main_window.py').read_text()
 assert 'continueRequested.connect(self._continue_from_lyrics)' in s
 block=s.split('def _continue_from_lyrics',1)[1].split('def _set_app_mode',1)[0]
 assert 'WorkspacePage.STUDIO' in block and 'WorkflowStep.STYLE' in block
