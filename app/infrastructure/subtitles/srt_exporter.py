from __future__ import annotations

from pathlib import Path

from app.domain.models.subtitles import SubtitleDocument, SubtitleFormat
from app.infrastructure.subtitles.common import atomic_text_write


class SrtSubtitleExporter:
    format = SubtitleFormat.SRT

    def export(self, document: SubtitleDocument, destination: Path) -> Path:
        blocks = []
        for cue in document.cues:
            blocks.append(
                f"{cue.cue_id}\n"
                f"{self._time(cue.start_seconds)} --> {self._time(cue.end_seconds)}\n"
                f"{cue.text}"
            )
        return atomic_text_write(
            destination / f"{document.source_path.stem}.srt",
            "\n\n".join(blocks) + "\n",
        )

    @staticmethod
    def _time(seconds: float) -> str:
        millis = round(max(0, seconds) * 1000)
        hours, remainder = divmod(millis, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        whole_seconds, milliseconds = divmod(remainder, 1000)
        return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"
