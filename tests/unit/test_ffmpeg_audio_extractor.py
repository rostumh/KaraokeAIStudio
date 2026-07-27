from pathlib import Path
from app.domain.models.audio_extraction import AudioExtractionRequest, AudioFormat
from app.infrastructure.media.ffmpeg_audio_extractor import FFmpegAudioExtractor

def request(tmp_path: Path, fmt: AudioFormat) -> AudioExtractionRequest:
    return AudioExtractionRequest(tmp_path/"in.mp4", tmp_path/"out.wav", 1, 10.0, fmt, 48000, 2, 320, False)

def test_wav_24_command_maps_explicit_stream_and_disables_video(tmp_path: Path) -> None:
    extractor=FFmpegAudioExtractor(Path("ffmpeg")); command=extractor._command(request(tmp_path, AudioFormat.WAV_PCM_24), tmp_path/"out.part")
    assert command[command.index("-map")+1] == "0:1"
    assert "pcm_s24le" in command and "-vn" in command and "pipe:1" in command

def test_flac_command_uses_lossless_encoder(tmp_path: Path) -> None:
    command=FFmpegAudioExtractor(Path("ffmpeg"))._command(request(tmp_path, AudioFormat.FLAC), tmp_path/"out.part")
    assert "flac" in command and "-compression_level" in command
