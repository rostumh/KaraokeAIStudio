from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

class ConfigurationError(RuntimeError):
    """Raised when configuration cannot be decoded or validated."""

@dataclass(frozen=True, slots=True)
class ApplicationSettings:
    name: str
    organization: str
    version: str

@dataclass(frozen=True, slots=True)
class AppearanceSettings:
    theme: str
    language: str

@dataclass(frozen=True, slots=True)
class LoggingSettings:
    level: str
    max_bytes: int
    backup_count: int

@dataclass(frozen=True, slots=True)
class DatabaseSettings:
    filename: str

@dataclass(frozen=True, slots=True)
class Settings:
    schema_version: int
    application: ApplicationSettings
    appearance: AppearanceSettings
    logging: LoggingSettings
    database: DatabaseSettings

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def _read_json(path: Path, *, required: bool) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise ConfigurationError(f"Required configuration file is missing: {path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Unable to read valid JSON from {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConfigurationError(f"Configuration root must be a JSON object: {path}")
    return payload

def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        current = result.get(key)
        result[key] = _deep_merge(current, value) if isinstance(current, Mapping) and isinstance(value, Mapping) else value
    return result

def _validate(data: Mapping[str, Any]) -> Settings:
    try:
        logging_data = dict(data["logging"]); appearance = dict(data["appearance"]); database = dict(data["database"]); application = dict(data["application"])
        level = str(logging_data["level"]).upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}: raise ValueError("logging.level is invalid")
        if appearance["theme"] not in {"dark", "light"}: raise ValueError("appearance.theme must be 'dark' or 'light'")
        max_bytes = int(logging_data["max_bytes"]); backup_count = int(logging_data["backup_count"]); schema_version = int(data["schema_version"])
        if min(max_bytes, backup_count, schema_version) < 1: raise ValueError("numeric configuration values must be positive")
        return Settings(schema_version, ApplicationSettings(str(application["name"]), str(application["organization"]), str(application["version"])), AppearanceSettings(str(appearance["theme"]), str(appearance["language"])), LoggingSettings(level, max_bytes, backup_count), DatabaseSettings(str(database["filename"])))
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(f"Configuration validation failed: {exc}") from exc

def load_settings(default_path: Path, user_path: Path) -> Settings:
    merged = _deep_merge(_read_json(default_path, required=True), _read_json(user_path, required=False))
    env_level = os.getenv("KAS_LOG_LEVEL")
    if env_level: merged = _deep_merge(merged, {"logging": {"level": env_level}})
    settings = _validate(merged)
    if not user_path.exists():
        user_path.parent.mkdir(parents=True, exist_ok=True)
        user_path.write_text(json.dumps(settings.to_dict(), indent=2) + "\n", encoding="utf-8")
    return settings
