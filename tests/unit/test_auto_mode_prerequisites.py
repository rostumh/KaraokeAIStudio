from pathlib import Path

SOURCE=Path('app/ui/main_window.py').read_text()

def test_auto_mode_requires_separation_before_style_render():
    assert 'WorkflowStep.SEPARATE not in completed' in SOURCE
    assert 'Starting required AI separation' in SOURCE
    assert 'WorkflowStep.SEPARATE in self._workflow_state.completed' in SOURCE

def test_auto_mode_commits_recommended_style():
    assert 'def _accept_auto_style_and_render' in SOURCE
    assert 'auto/visualStyle' in SOURCE
    assert 'WorkflowStep.STYLE' in SOURCE
    assert 'Visual style applied automatically' in SOURCE

def test_separation_failure_offers_original_audio_for_current_song():
    assert 'def _offer_original_audio_fallback' in SOURCE
    assert 'Continue with Original Audio' in SOURCE
    assert 'original audio fallback' in SOURCE
    assert 'may still contain the lead vocal' in SOURCE

def test_render_accepts_resolved_original_audio_path():
    assert 'self._auto_instrumental_path=original.source_path' in SOURCE
