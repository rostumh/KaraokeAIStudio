from __future__ import annotations

from app.application.errors import MediaImportError


class RestrictedPluginContext:
    """Narrow contribution registry; no window, filesystem, model, or process objects are exposed."""

    def __init__(self) -> None:
        self.export_profiles: dict[str, tuple[str, dict[str, object]]] = {}
        self.translation_labels: dict[str, str] = {}

    def register_export_profile(self, profile_id: str, label: str, values: dict[str, object]) -> None:
        if not profile_id.startswith("plugin.") or profile_id in self.export_profiles:
            raise MediaImportError("Plugin export-profile IDs must be unique and begin with 'plugin.'.")
        safe = {key: value for key, value in values.items() if key in {"codec", "container", "width", "height", "frame_rate", "quality", "audio_bitrate_kbps"}}
        if not safe:
            raise MediaImportError("Plugin export profile did not provide supported values.")
        self.export_profiles[profile_id] = (label.strip() or profile_id, safe)

    def register_translation_language_label(self, code: str, label: str) -> None:
        normalized = code.strip().lower()
        if not normalized or normalized in self.translation_labels:
            raise MediaImportError("Translation language labels require a unique language code.")
        self.translation_labels[normalized] = label.strip() or normalized
