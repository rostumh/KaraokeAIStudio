from __future__ import annotations

import json
from pathlib import Path
import pytest
from app.core.config import ConfigurationError, load_settings

def valid_payload() -> dict[str, object]:
    return {"schema_version": 1, "application": {"name": "Karaoke AI Studio", "organization": "KaraokeAIStudio", "version": "0.1.0"}, "appearance": {"theme": "dark", "language": "en-US"}, "logging": {"level": "INFO", "max_bytes": 1000, "backup_count": 2}, "database": {"filename": "app.sqlite3"}}

def test_user_values_override_defaults(tmp_path: Path) -> None:
    default = tmp_path / "default.json"; user = tmp_path / "user" / "settings.json"
    default.write_text(json.dumps(valid_payload()), encoding="utf-8")
    user.parent.mkdir(); user.write_text(json.dumps({"appearance": {"theme": "light"}}), encoding="utf-8")
    assert load_settings(default, user).appearance.theme == "light"

def test_missing_user_config_is_created(tmp_path: Path) -> None:
    default = tmp_path / "default.json"; user = tmp_path / "user" / "settings.json"
    default.write_text(json.dumps(valid_payload()), encoding="utf-8")
    load_settings(default, user)
    assert user.is_file()

def test_invalid_log_level_is_rejected(tmp_path: Path) -> None:
    payload = valid_payload(); payload["logging"] = {"level": "TRACE", "max_bytes": 1000, "backup_count": 2}
    default = tmp_path / "default.json"; default.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ConfigurationError): load_settings(default, tmp_path / "settings.json")
