from pathlib import Path


def test_windows_setup_installs_asr_by_default():
    source=Path('scripts/setup_windows.ps1').read_text(encoding='utf-8')
    assert 'requirements-asr.txt' in source
    assert 'import torch, torchaudio, demucs, faster_whisper, ctranslate2, av' in source


def test_pyinstaller_collects_complete_asr_runtime():
    source=Path('packaging/KaraokeAIStudio.spec').read_text(encoding='utf-8')
    for package in ('faster_whisper','ctranslate2','av','tokenizers','huggingface_hub','onnxruntime'):
        assert f'"{package}"' in source
        assert package in source


def test_build_fails_when_frozen_asr_is_missing():
    source=Path('scripts/build_windows_package.ps1').read_text(encoding='utf-8')
    assert 'Frozen package is missing faster_whisper' in source
    assert 'Frozen package is missing CTranslate2' in source


def test_runtime_reports_damaged_component():
    source=Path('app/infrastructure/ai/faster_whisper_recognizer.py').read_text(encoding='utf-8')
    assert 'Technical detail:' in source
    assert 'Reinstall Karaoke AI Studio 0.21.2 or later' in source


def test_no_manual_asr_setup_message_in_auto_path():
    source=Path('app/ui/main_window.py').read_text(encoding='utf-8')
    auto=source.split('def _start_auto_transcription',1)[1].split('def _start_auto_alignment',1)[0]
    assert 'setup_asr.ps1' not in auto
    assert '_asr_initialization_error' in auto
