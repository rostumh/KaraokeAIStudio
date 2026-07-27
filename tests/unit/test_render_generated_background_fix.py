from pathlib import Path

def test_generated_background_uses_portable_color_source():
 s=Path('app/infrastructure/media/ffmpeg_video_renderer.py').read_text()
 block=s.split('def _command',1)[1]
 assert 'color=c=0x061126' in block and 'drawbox=x=mod(t*95' in block and 'gblur=sigma=95' in block
 assert 'gradients=s=' not in block
 assert 'd={request.duration_seconds:.3f}' in block

def test_render_validates_every_file_before_ffmpeg():
 s=Path('app/infrastructure/media/ffmpeg_video_renderer.py').read_text()
 for text in ('Instrumental audio:', 'ASS subtitles:', 'Background:', 'Watermark:', 'Render input file is missing'):
  assert text in s

def test_render_reports_useful_ffmpeg_context():
 s=Path('app/infrastructure/media/ffmpeg_video_renderer.py').read_text()
 assert 'errors[-6:]' in s and 'Unknown FFmpeg error' in s


def test_input_validation_is_render_boundary_not_command_builder():
 s=Path('app/infrastructure/media/ffmpeg_video_renderer.py').read_text()
 render=s.split('def render',1)[1].split('def _discover_encoders',1)[0]
 command=s.split('def _command',1)[1]
 assert 'self._validate_inputs(request)' in render
 assert 'missing=[]' not in command
