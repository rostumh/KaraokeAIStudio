from pathlib import Path

def test_dialog_uses_safe_htdemucs_segment():
    source=Path("app/ui/dialogs/vocal_separation_dialog.py").read_text(encoding="utf-8")
    assert "setRange(5,7)" in source
    assert "setValue(7)" in source
    assert "setValue(10)" not in source

def test_runtime_clamps_legacy_htdemucs_segment():
    source=Path("app/infrastructure/ai/demucs_runtime.py").read_text(encoding="utf-8")
    assert 'request.model_name.startswith("htdemucs")' in source
    assert "min(segment, 7.8)" in source
