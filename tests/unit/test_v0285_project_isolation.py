from pathlib import Path

def test_new_project_fully_clears_song_state():
    s=Path('app/ui/main_window.py').read_text()
    block=s.split('def _new_project',1)[1].split('def _import_media',1)[0]
    for text in ('_auto_original_asset=None','_auto_instrumental_path=None','_expected_transcription_source=None','lyrics_view.clear_document()','controller.cancel()'):
        assert text in block

def test_stale_transcript_and_subtitle_are_blocked():
    s=Path('app/ui/main_window.py').read_text()
    assert 'Discarded stale transcription result' in s
    assert 'Lyrics Do Not Match Current Song' in s
    render=s.split('def _render_video',1)[1].split('def _on_video_render_progress',1)[0]
    assert 'Always regenerate the ASS' in render
    assert 'expected if expected.is_file()' not in render

def test_hardware_encoder_has_automatic_software_fallback():
    s=Path('app/application/services/video_render_service.py').read_text()
    assert 'hardware_failure' in s and 'RenderEncoder.SOFTWARE' in s

def test_build_identity_is_current():
    assert 'Version 0.29.2' in Path('app/ui/widgets/sidebar.py').read_text()
    assert 'Version 0.29.2' in Path('app/ui/main_window.py').read_text()
