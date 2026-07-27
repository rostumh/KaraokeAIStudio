from pathlib import Path

def test_render_numeric_arrows_and_auto_lyric_position():
    source=Path('app/ui/dialogs/video_render_dialog.py').read_text()
    assert 'UpDownArrows' in source
    assert 'Lyric height (custom)' not in source
    assert 'lyric_height' not in source

def test_render_never_falls_back_to_previous_song_stem():
    source=Path('app/ui/main_window.py').read_text()
    render=source[source.index('    def _render_video'):source.index('    def _on_video_render_progress')]
    assert 'Current Song Is Not Ready' in render
    assert 'rglob("no_vocals.*")' not in render
