from __future__ import annotations

from typing import Protocol, runtime_checkable
from app.domain.models.plugins import PluginDescriptor


@runtime_checkable
class KaraokeStudioPlugin(Protocol):
    @property
    def descriptor(self) -> PluginDescriptor: ...

    def activate(self, context: "PluginContext") -> None:
        """Register contributions using the restricted host context."""

    def deactivate(self) -> None:
        """Release plugin-owned resources."""


@runtime_checkable
class PluginContext(Protocol):
    def register_export_profile(self, profile_id: str, label: str, values: dict[str, object]) -> None: ...
    def register_translation_language_label(self, code: str, label: str) -> None: ...
