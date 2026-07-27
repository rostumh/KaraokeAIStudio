from pathlib import Path

def test_title_timing_is_automatic_and_control_removed():
    dialog=Path("app/ui/dialogs/video_render_dialog.py").read_text()
    composer=Path("app/infrastructure/subtitles/videoke_composer.py").read_text()
    assert "Title-card seconds" not in dialog
    assert "countdown_start=max(0.8,first_lyric-count)" in composer
    assert "td=max(0.8,countdown_start-.20)" in composer

def test_modern_clean_readability_defaults():
    model=Path("app/domain/models/video_render.py").read_text()
    wizard=Path("app/ui/widgets/creation_wizard.py").read_text()
    assert "Segoe UI Semibold" in model
    assert "#FFD83D" in model
    assert "Modern Clean" in wizard

def test_generated_background_is_dynamic_not_blank_blue():
    source=Path("app/infrastructure/media/ffmpeg_video_renderer.py").read_text()
    for token in ("drawbox=x=mod(t*95", "gblur=sigma=95", "hue=h=18*sin(t/4)"):
        assert token in source

def test_render_ass_is_bound_to_current_source_and_ai_lookup_is_cleaned():
    dialog=Path("app/ui/dialogs/video_render_dialog.py").read_text()
    metadata=Path("app/application/services/song_metadata_service.py").read_text()
    assert "KaraokeAIStudio-Source-ID" in dialog
    assert "self._source_path.resolve()" in dialog
    assert "side[ _-]?[ab]" in metadata
    assert "duration_seconds" in metadata

def test_recommended_render_is_1080p_and_hardware_first():
    dialog=Path("app/ui/dialogs/video_render_dialog.py").read_text()
    assert "self.resolution.setCurrentIndex(1)" in dialog
    assert dialog.index("NVIDIA NVENC (recommended)") < dialog.index("Software fallback")
