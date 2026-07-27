from pathlib import Path
def test_filter_graph_has_no_empty_filter():
 s=Path('app/infrastructure/media/ffmpeg_video_renderer.py').read_text();assert "filters=[" in s and "','.join(part for part in filters if part.strip())" in s;assert 'motion=",zoompan' not in s
def test_countdown_is_three_after_one_second_gap():
 s=Path('app/infrastructure/subtitles/videoke_composer.py').read_text();assert 'count=3;step=1.0' in s and 'start=td+1.0+i*step' in s
def test_left_editors_and_completion_actions():
 s=Path('app/ui/widgets/sidebar.py').read_text();assert 'Render Video Settings' in s and 'Visual Style Editor' in s
 m=Path('app/ui/main_window.py').read_text();assert 'Open Output Folder' in m and 'self._player.pause' in m and 'Created by Rostum Hernandez' in m
def test_metadata_filename_and_mastering():
 d=Path('app/ui/dialogs/video_render_dialog.py').read_text();assert 'Identify Song Intelligently' in d and "'videoke'" in d
 r=Path('app/infrastructure/media/ffmpeg_video_renderer.py').read_text();assert 'loudnorm=I=-14' in r and 'alimiter=limit=0.95' in r
