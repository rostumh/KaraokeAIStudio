from pathlib import Path
from threading import Event
import pytest
from app.application.errors import MediaImportError
from app.application.services.audio_extraction_service import AudioExtractionService
from app.domain.models.audio_extraction import AudioExtractionResult, AudioFormat
from app.domain.models.media import AudioStream, MediaAsset, MediaKind

class StubExtractor:
    def extract(self, request, progress, cancel_event):
        progress(1.0)
        return AudioExtractionResult(request.output_path, 10, 0.1, request.output_format)

def make_asset(path: Path) -> MediaAsset:
    return MediaAsset("id", path, path.name, MediaKind.VIDEO, 10, 60.0, "MP4", None, (AudioStream(2, "aac", 48000, 2, "stereo", None, None),), (), {})

def test_service_builds_valid_request(tmp_path: Path) -> None:
    source=tmp_path/"input.mp4"; source.write_bytes(b"media")
    result=AudioExtractionService(StubExtractor()).extract(make_asset(source), tmp_path/"out.wav", AudioFormat.WAV_PCM_24, progress=lambda value: None, cancel_event=Event())
    assert result.output_path.name == "out.wav"

def test_service_prevents_source_overwrite(tmp_path: Path) -> None:
    source=tmp_path/"input.mp4"; source.write_bytes(b"media")
    with pytest.raises(MediaImportError, match="source"):
        AudioExtractionService(StubExtractor()).extract(make_asset(source), source, AudioFormat.WAV_PCM_16, progress=lambda value: None, cancel_event=Event())
