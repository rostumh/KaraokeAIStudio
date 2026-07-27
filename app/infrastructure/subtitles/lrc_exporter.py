from __future__ import annotations

from pathlib import Path

from app.domain.models.subtitles import SubtitleDocument, SubtitleFormat
from app.infrastructure.subtitles.common import atomic_text_write


class LrcSubtitleExporter:
    format = SubtitleFormat.LRC

    def export(self, document: SubtitleDocument, destination: Path) -> Path:
        lines = ["[re:Karaoke AI Studio]", f"[length:{self._time(document.duration_seconds)}]"]
        lines.extend(f"[{self._time(cue.start_seconds)}]{cue.text}" for cue in document.cues)
        return atomic_text_write(
            destination / f"{document.source_path.stem}.lrc",
            "\n".join(lines) + "\n",
        )

    @staticmethod
    def _time(seconds: float) -> str:
        centiseconds = round(max(0, seconds) * 100)
        minutes, remainder = divmod(centiseconds, 6000)
        whole_seconds, remainder_centiseconds = divmod(remainder, 100)
        return f"{minutes:02d}:{whole_seconds:02d}.{remainder_centiseconds:02d}"
