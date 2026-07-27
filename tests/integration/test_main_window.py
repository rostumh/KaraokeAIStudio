from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.core.config import (
    AppearanceSettings,
    ApplicationSettings,
    DatabaseSettings,
    LoggingSettings,
    Settings,
)
from app.core.paths import AppPaths
from app.ui.main_window import MainWindow


def build_settings() -> Settings:
    return Settings(
        1,
        ApplicationSettings("Karaoke AI Studio Test", "KaraokeAIStudioTest", "0.2.0"),
        AppearanceSettings("dark", "en-US"),
        LoggingSettings("INFO", 1000, 1),
        DatabaseSettings("test.sqlite3"),
    )


def test_main_window_builds_all_workspace_pages(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    paths = AppPaths(*(tmp_path / name for name in ("config", "data", "cache", "logs", "temp", "exports", "plugins")))
    paths.ensure_runtime_directories()
    window = MainWindow(build_settings(), paths)
    assert window.stack.count() == 8
    assert window.project_dock.widget() is not None
    assert window.properties_dock.widget() is not None
    assert window.statusBar().currentMessage() == "Ready"
    window.close()
    app.processEvents()
