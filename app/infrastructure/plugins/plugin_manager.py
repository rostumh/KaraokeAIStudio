from __future__ import annotations

import logging
from importlib.metadata import EntryPoint, entry_points

from app.application.ports.plugin_contract import KaraokeStudioPlugin
from app.application.services.plugin_registry_service import PluginRegistryService
from app.domain.models.plugins import PluginDescriptor, PluginRecord, PluginStatus
from app.infrastructure.plugins.plugin_context import RestrictedPluginContext
from app.infrastructure.repositories.plugin_state_repository import PluginStateRepository

LOGGER = logging.getLogger(__name__)
ENTRY_POINT_GROUP = "karaoke_ai_studio.plugins"


class PluginManager:
    """Discovers installed distribution entry points and isolates individual load failures."""

    def __init__(self, repository: PluginStateRepository, context: RestrictedPluginContext) -> None:
        self._repository = repository
        self.context = context
        self._instances: dict[str, KaraokeStudioPlugin] = {}

    def discover(self) -> tuple[PluginRecord, ...]:
        self.deactivate_all()
        self.context.export_profiles.clear()
        self.context.translation_labels.clear()
        states = self._repository.load()
        records: list[PluginRecord] = []
        seen: set[str] = set()
        for point in sorted(entry_points(group=ENTRY_POINT_GROUP), key=lambda item: item.name):
            try:
                plugin = self._load(point)
                descriptor = PluginRegistryService.validate_descriptor(plugin.descriptor)
                if descriptor.plugin_id in seen:
                    raise ValueError(f"Duplicate plugin ID: {descriptor.plugin_id}")
                seen.add(descriptor.plugin_id)
                enabled = states.get(descriptor.plugin_id, False)
                status = PluginStatus.ENABLED if enabled else PluginStatus.DISABLED
                if enabled:
                    plugin.activate(self.context)
                    self._instances[descriptor.plugin_id] = plugin
                records.append(PluginRecord(descriptor, status, point.value))
            except Exception as exc:
                LOGGER.exception("Plugin entry point failed: %s", point.name)
                descriptor = PluginDescriptor(point.name, point.name, "unknown", "Plugin could not be loaded.", point.dist.name if point.dist else "unknown", "unknown", ())
                records.append(PluginRecord(descriptor, PluginStatus.FAILED, point.value, str(exc)))
        return tuple(records)

    def set_enabled(self, plugin_id: str, enabled: bool) -> None:
        states = self._repository.load()
        states[plugin_id] = enabled
        self._repository.save(states)

    def deactivate_all(self) -> None:
        for plugin_id, plugin in tuple(self._instances.items()):
            try: plugin.deactivate()
            except Exception: LOGGER.exception("Plugin deactivation failed: %s", plugin_id)
        self._instances.clear()

    @staticmethod
    def _load(point: EntryPoint) -> KaraokeStudioPlugin:
        factory = point.load()
        plugin = factory() if callable(factory) else factory
        if not isinstance(plugin, KaraokeStudioPlugin):
            raise TypeError("Entry point does not implement KaraokeStudioPlugin.")
        return plugin
