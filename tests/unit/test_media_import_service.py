from pathlib import Path
import pytest
from app.application.errors import MediaImportError, UnsupportedMediaError
from app.application.services.media_import_service import MediaImportService
from app.domain.models.media import AudioStream, MediaAsset, MediaKind

class StubProbe:
    def probe(self, source: Path) -> MediaAsset:
        return MediaAsset("id", source, source.name, MediaKind.AUDIO, source.stat().st_size, 2.5, "Waveform Audio", None, (AudioStream(0, "pcm", 44100, 2, "stereo", None, None),), (), {})

def test_import_validates_and_returns_asset(tmp_path: Path) -> None:
    media = tmp_path / "song.wav"; media.write_bytes(b"RIFF-not-empty")
    assert MediaImportService(StubProbe()).import_file(media).display_name == "song.wav"

def test_import_rejects_unknown_extension(tmp_path: Path) -> None:
    media = tmp_path / "song.txt"; media.write_text("x")
    with pytest.raises(UnsupportedMediaError): MediaImportService(StubProbe()).import_file(media)

def test_import_rejects_empty_file(tmp_path: Path) -> None:
    media = tmp_path / "song.wav"; media.touch()
    with pytest.raises(MediaImportError, match="empty"): MediaImportService(StubProbe()).import_file(media)
