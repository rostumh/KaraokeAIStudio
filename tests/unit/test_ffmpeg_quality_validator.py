from pathlib import Path
from app.infrastructure.media.ffmpeg_quality_validator import FFmpegQualityValidator
def test_metadata_checks_flag_missing_audio(tmp_path):
 p=tmp_path/"x.mp4";p.write_bytes(b"x"*2000);v={"width":1920,"height":1080,"pix_fmt":"yuv420p"};checks=FFmpegQualityValidator(Path("ffprobe"),Path("ffmpeg"))._metadata_checks(p,{},v,{},10);assert any(c.code=="audio_stream" and c.severity.value=="error" for c in checks)
def test_rate_parses_fraction():assert FFmpegQualityValidator._rate("30000/1001") is not None
