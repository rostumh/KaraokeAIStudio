from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from platformdirs import PlatformDirs

@dataclass(frozen=True, slots=True)
class AppPaths:
    config_dir: Path
    data_dir: Path
    cache_dir: Path
    log_dir: Path
    temp_dir: Path
    export_dir: Path
    plugin_dir: Path

    @classmethod
    def discover(cls) -> "AppPaths":
        dirs = PlatformDirs(appname="KaraokeAIStudio", appauthor="KaraokeAIStudio", roaming=False, ensure_exists=False)
        data = Path(dirs.user_data_path)
        return cls(Path(dirs.user_config_path), data, Path(dirs.user_cache_path), Path(dirs.user_log_path), Path(dirs.user_cache_path) / "temp", data / "exports", data / "plugins")

    def ensure_runtime_directories(self) -> None:
        for path in (self.config_dir, self.data_dir, self.cache_dir, self.log_dir, self.temp_dir, self.export_dir, self.plugin_dir): path.mkdir(parents=True, exist_ok=True)
