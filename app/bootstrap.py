from __future__ import annotations

import logging
import sys
import os
from pathlib import Path
from typing import Sequence

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.config import ConfigurationError, Settings, load_settings
from app.core.logging_setup import configure_logging
from app.core.paths import AppPaths
from app.ui.main_window import MainWindow
from app.infrastructure.models.model_catalog import load_model_catalog
from app.infrastructure.models.resumable_downloader import ResumableModelDownloader
from app.application.services.model_provisioning_service import ModelProvisioningService
from app.ui.dialogs.first_run_models_dialog import FirstRunModelsDialog

LOGGER = logging.getLogger(__name__)

def create_application(argv: Sequence[str] | None = None) -> tuple[QApplication, Settings, AppPaths]:
    """Build the composition root and return initialized process-wide services."""
    args = list(argv) if argv is not None else sys.argv
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(args)
    app.setApplicationName("Karaoke AI Studio")
    app.setOrganizationName("KaraokeAIStudio")
    app.setApplicationVersion("0.28.3")

    paths = AppPaths.discover()
    paths.ensure_runtime_directories()
    settings = load_settings(Path(__file__).resolve().parents[1] / "config" / "default.json", paths.config_dir / "settings.json")
    configure_logging(paths.log_dir, settings.logging)
    LOGGER.info("Application initialized; data directory=%s", paths.data_dir)
    return app, settings, paths

def main(argv: Sequence[str] | None = None) -> int:
    """Start the Qt event loop and convert startup failures into a user-facing error."""
    try:
        app, settings, paths = create_application(argv)
        resource_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
        catalog_path = resource_root / "models" / "model-catalog.json"
        if catalog_path.is_file():
            service = ModelProvisioningService(ResumableModelDownloader())
            models = load_model_catalog(catalog_path)
            models_root = paths.data_dir / "models"
            missing = service.missing_required(models, models_root)
            if missing:
                dialog = FirstRunModelsDialog(service, missing, models_root)
                if dialog.exec() != dialog.DialogCode.Accepted:
                    return 3
        window = MainWindow(settings=settings, paths=paths)
        window.show()
        return app.exec()
    except ConfigurationError as exc:
        QApplication.instance() or QApplication([])
        QMessageBox.critical(None, "Configuration Error", str(exc))
        return 2
    except Exception:
        LOGGER.exception("Fatal startup failure")
        QApplication.instance() or QApplication([])
        QMessageBox.critical(None, "Startup Error", "Karaoke AI Studio could not start. Review the application log for details.")
        return 1
