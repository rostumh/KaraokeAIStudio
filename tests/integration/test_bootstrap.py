from __future__ import annotations

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from app.bootstrap import create_application

def test_composition_root_builds() -> None:
    app, settings, paths = create_application(["karaoke-ai-studio-test"])
    assert app.applicationName() == "Karaoke AI Studio"
    assert settings.schema_version == 1
    assert paths.data_dir.is_dir()
    app.quit()
