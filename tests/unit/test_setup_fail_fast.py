from pathlib import Path


def test_setup_stops_on_native_command_failure():
    source=Path("scripts/setup_windows.ps1").read_text(encoding="utf-8")
    assert "$PSNativeCommandUseErrorActionPreference = $true" in source
    assert "if ($LASTEXITCODE -ne 0)" in source
    assert "Automated test suite" in source
    assert source.index("Automated test suite") < source.index("Setup complete: all tests passed")


def test_demucs_command_tolerates_legacy_test_double():
    source=Path("app/infrastructure/ai/demucs_runtime.py").read_text(encoding="utf-8")
    assert 'getattr(self, "_runner", None)' in source
