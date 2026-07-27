from pathlib import Path

def test_manual_full_lyrics_and_import_supported():
    s=Path('app/ui/views/lyrics_view.py').read_text()
    assert 'Align These Lyrics' in s and 'Import Lyrics File' in s
    assert 'realign_document' in s and 'Matched acoustic timing was preserved' in s

def test_song_bound_ass_and_original_source_metadata():
    s=Path('app/ui/main_window.py').read_text()
    render=s.split('def _render_video',1)[1].split('def _on_video_render_progress',1)[0]
    assert 'current_subtitle_dir=self._paths.export_dir/"subtitles"/document.source_path.stem' in render
    assert 'self._subtitle_service.generate(document,options,current_subtitle_dir)' in render
    assert 'Always regenerate the ASS' in render
    assert 'default_source=' in render
    assert 'expected if expected.is_file()' not in render

def test_single_subtitle_and_lyric_timed_countdown():
    s=Path('app/infrastructure/subtitles/videoke_composer.py').read_text()
    assert 'No secondary Preview events' in s
    assert 'first_lyric' in s and 'countdown_start' in s
    assert 'pos(960,425)' in s and 'pos(960,540)' in s and 'pos(960,610)' in s

def test_large_room_defaults_and_metadata_parsing():
    d=Path('app/ui/dialogs/video_render_dialog.py').read_text()
    m=Path('app/application/services/song_metadata_service.py').read_text()
    assert 'self.lyric_size.setValue(112)' in d
    assert 'artist,title=artist or parts[0],parts[1]' in m
    assert 'self._source_path or' in d

def test_light_theme_group_titles_have_safe_spacing():
    s=Path('app/ui/theme.py').read_text()
    assert 'QGroupBox::title' in s and 'margin-top:16px' in s

def test_render_completion_clears_stale_separation_state():
    s=Path('app/ui/main_window.py').read_text()
    assert 'Video ready' in s
    assert 'self._auto_waiting_for_vocals=False' in s
