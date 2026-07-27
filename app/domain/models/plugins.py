from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


PLUGIN_API_VERSION = "1.0"


class PluginStatus(StrEnum):
    DISCOVERED = "discovered"
    ENABLED = "enabled"
    DISABLED = "disabled"
    INCOMPATIBLE = "incompatible"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    plugin_id: str
    name: str
    version: str
    description: str
    provider: str
    api_version: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PluginRecord:
    descriptor: PluginDescriptor
    status: PluginStatus
    entry_point: str
    error: str | None = None
