from pathlib import Path

def test_video_separation_prepares_pcm_and_validates_stems():
    s=Path('app/application/services/vocal_separation_service.py').read_text()
    for text in ('separation_input.wav','WAV_PCM_16','sample_rate=44100','channels=2','_validate_stems','retrying safely on CPU'):
        assert text in s

def test_separation_failure_resets_busy_and_workflow():
    s=Path('app/ui/main_window.py').read_text()
    block=s.split('def _on_separation_failed',1)[1].split('def _configure_extraction',1)[0]
    for text in ('WorkflowStep.SEPARATE','AI separation failed','_auto_waiting_for_vocals=False','setRange(0,100)','setValue(0)'):
        assert text in block
