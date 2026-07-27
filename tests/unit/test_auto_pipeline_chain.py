from pathlib import Path

def test_auto_mode_does_not_open_separation_dialog():
    source=Path('app/ui/main_window.py').read_text(encoding='utf-8')
    body=source.split('def _start_auto_mode',1)[1].split('def _start_auto_transcription',1)[0]
    assert '_separation_controller.start' in body
    assert 'VocalSeparationDialog' not in body

def test_auto_mode_chains_vocals_to_whisper_and_alignment():
    source=Path('app/ui/main_window.py').read_text(encoding='utf-8')
    assert 'QTimer.singleShot(0,lambda:self._start_auto_transcription(value))' in source
    assert 'self._start_auto_alignment()' in source
    assert '"model":"large-v3"' in source
    assert '"language":""' in source

def test_generated_stems_do_not_reset_workflow_to_step_two():
    source=Path('app/ui/main_window.py').read_text(encoding='utf-8')
    assert 'if not generated:self._set_workflow' in source
    assert '"vocals.wav"' in source and '"no_vocals.wav"' in source

def test_version_is_current():
    assert '0.29.2' in Path('pyproject.toml').read_text(encoding='utf-8')
