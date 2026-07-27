from pathlib import Path

def test_main_window_uses_real_qt_media_engine():
    source = Path("app/ui/main_window.py").read_text(encoding="utf-8")
    assert "QMediaPlayer" in source
    assert "QAudioOutput" in source
    assert "setAudioOutput" in source
    assert "setSource(QUrl.fromLocalFile" in source
    assert "self._player.play()" in source
    assert "self._player.pause()" in source
    assert "self._player.stop()" in source
    assert "errorOccurred.connect" in source
