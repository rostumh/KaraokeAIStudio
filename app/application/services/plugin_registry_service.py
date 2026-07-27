from __future__ import annotations

from app.application.errors import MediaImportError
from app.domain.models.plugins import PLUGIN_API_VERSION, PluginDescriptor


class PluginRegistryService:
    """Validates plugin identity, compatibility, and contribution uniqueness."""

    @staticmethod
    def validate_descriptor(descriptor: PluginDescriptor) -> PluginDescriptor:
        if not descriptor.plugin_id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789.-_" for ch in descriptor.plugin_id):
            raise MediaImportError("Plugin ID must use lowercase letters, digits, dots, dashes, or underscores.")
        if not descriptor.name.strip() or not descriptor.version.strip():
            raise MediaImportError("Plugin name and version are required.")
        if descriptor.api_version != PLUGIN_API_VERSION:
            raise MediaImportError(f"Plugin requires API {descriptor.api_version}; host provides {PLUGIN_API_VERSION}.")
        allowed = {"export_profiles", "translation_labels"}
        unsupported = set(descriptor.capabilities) - allowed
        if unsupported:
            raise MediaImportError(f"Unsupported plugin capabilities: {', '.join(sorted(unsupported))}")
        return descriptor
