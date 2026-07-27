from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from app.domain.models.export_profile import ExportProfile
from app.domain.models.video_render import RenderEncoder, VideoCodec, VideoContainer


class ExportProfileRepository:
    """Atomic persistence for user-created export profiles."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> tuple[ExportProfile, ...]:
        if not self._path.is_file():
            return ()
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        return tuple(
            ExportProfile(
                str(item["profile_id"]), str(item["name"]), str(item.get("description", "")),
                VideoCodec(str(item["codec"])), VideoContainer(str(item["container"])),
                RenderEncoder(str(item.get("encoder", "software"))), int(item["width"]), int(item["height"]),
                int(item["frame_rate"]), int(item["quality"]), int(item["audio_bitrate_kbps"]), False,
            )
            for item in payload.get("profiles", [])
        )

    def save(self, profiles: tuple[ExportProfile, ...]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_name(self._path.name + ".part")
        values = []
        for profile in profiles:
            item = asdict(profile)
            item["codec"] = profile.codec.value; item["container"] = profile.container.value; item["encoder"] = profile.encoder.value
            values.append(item)
        temporary.write_text(json.dumps({"schema_version": 1, "profiles": values}, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(temporary, self._path)
