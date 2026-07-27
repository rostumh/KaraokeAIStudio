from pathlib import Path
from app.domain.models.media import MediaKind
from app.infrastructure.media.ffprobe_media_probe import FFprobeMediaProbe

def test_parser_maps_audio_and_video_streams(tmp_path: Path) -> None:
    source = tmp_path / "clip.mp4"; source.write_bytes(b"media")
    payload = {"format": {"format_name": "mov,mp4", "format_long_name": "QuickTime / MOV", "duration": "12.5", "bit_rate": "1000000", "tags": {"title": "Demo"}}, "streams": [{"index": 0, "codec_type": "video", "codec_name": "h264", "width": 1920, "height": 1080, "avg_frame_rate": "30000/1001", "pix_fmt": "yuv420p"}, {"index": 1, "codec_type": "audio", "codec_name": "aac", "sample_rate": "48000", "channels": 2, "channel_layout": "stereo", "tags": {"language": "eng"}}]}
    asset = FFprobeMediaProbe(Path("ffprobe"))._parse(source, payload)
    assert asset.kind == MediaKind.VIDEO
    assert asset.duration_seconds == 12.5
    assert asset.primary_video and asset.primary_video.width == 1920
    assert asset.primary_audio and asset.primary_audio.sample_rate == 48000
