from pathlib import Path

def test_demucs_is_built_in_and_uses_helper_exe():
    setup = Path("scripts/setup_windows.ps1").read_text(encoding="utf-8")
    spec = Path("packaging/KaraokeAIStudio.spec").read_text(encoding="utf-8")
    runtime = Path("app/infrastructure/ai/demucs_runtime.py").read_text(encoding="utf-8")
    assert "pip install \"demucs>=4.1,<5\" SoundFile" in setup
    assert 'collect_all("demucs")' not in spec  # packages are collected through the package loop
    assert '"demucs", "torch", "torchaudio", "soundfile"' in spec
    assert "DemucsRunner.exe" in runtime
    assert "setup_ai_cpu.ps1" not in Path("app/ui/main_window.py").read_text(encoding="utf-8")
