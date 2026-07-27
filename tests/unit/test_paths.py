from pathlib import Path
from app.core.paths import AppPaths

def test_runtime_directories_are_created(tmp_path: Path) -> None:
    paths = AppPaths(*(tmp_path / name for name in ("config", "data", "cache", "logs", "temp", "exports", "plugins")))
    paths.ensure_runtime_directories()
    assert all(path.is_dir() for path in paths.__dict__.values()) if hasattr(paths, "__dict__") else all(getattr(paths, name).is_dir() for name in paths.__dataclass_fields__)
