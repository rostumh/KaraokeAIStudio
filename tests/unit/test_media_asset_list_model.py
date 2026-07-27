from pathlib import Path
from app.domain.models.media import AudioStream, MediaAsset, MediaKind
from app.ui.models.media_asset_list_model import MediaAssetListModel

def asset(path: Path) -> MediaAsset:
    return MediaAsset("id", path, path.name, MediaKind.AUDIO, 1, 1.0, "WAV", None, (AudioStream(0, "pcm", 44100, 2, None, None, None),), (), {})

def test_model_deduplicates_source_paths(tmp_path: Path) -> None:
    model = MediaAssetListModel(); item = asset(tmp_path / "song.wav")
    assert model.add_asset(item) == 0
    assert model.add_asset(item) == 0
    assert model.rowCount() == 1
