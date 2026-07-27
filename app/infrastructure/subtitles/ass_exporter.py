from __future__ import annotations

from pathlib import Path

from app.domain.models.subtitles import SubtitleDocument, SubtitleFormat
from app.infrastructure.subtitles.common import atomic_text_write
from app.application.services.karaoke_effect_service import KaraokeEffectService


class AssSubtitleExporter:
    format = SubtitleFormat.ASS

    def __init__(self) -> None:
        self._effects = KaraokeEffectService()

    def export(self, document: SubtitleDocument, destination: Path) -> Path:
        style = document.options.style
        header = (
            "[Script Info]\n"
            "ScriptType: v4.00+\n"
            f"PlayResX: {document.options.resolution_width}\n"
            f"PlayResY: {document.options.resolution_height}\n"
            "WrapStyle: 0\n"
            "ScaledBorderAndShadow: yes\n"
            "YCbCr Matrix: TV.709\n\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
            "ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
            "MarginR, MarginV, Encoding\n"
            f"Style: Karaoke,{style.font_name},{style.font_size},{self._color(style.primary_color)},"
            f"{self._color(style.highlight_color)},{self._color(style.outline_color)},&H80000000,"
            f"{-1 if style.bold else 0},0,0,0,100,100,0,0,1,{style.outline_width:.1f},"
            f"{style.shadow_depth:.1f},{style.alignment},40,40,{style.margin_vertical},1\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )
        events = []
        for cue in document.cues:
            effected_text = self._effects.render_cue(cue, style.effect_settings)
            events.append(
                f"Dialogue: 0,{self._time(cue.start_seconds)},{self._time(cue.end_seconds)},"
                f"Karaoke,,0,0,0,,{effected_text}"
            )
        return atomic_text_write(
            destination / f"{document.source_path.stem}.ass",
            header + "\n".join(events) + "\n",
        )

    @staticmethod
    def _time(seconds: float) -> str:
        centiseconds = round(max(0, seconds) * 100)
        hours, remainder = divmod(centiseconds, 360_000)
        minutes, remainder = divmod(remainder, 6000)
        whole_seconds, remainder_centiseconds = divmod(remainder, 100)
        return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{remainder_centiseconds:02d}"

    @staticmethod
    def _color(css: str) -> str:
        value = css.strip().lstrip("#")
        if len(value) != 6:
            raise ValueError(f"Invalid RGB color: {css}")
        red, green, blue = value[0:2], value[2:4], value[4:6]
        return f"&H00{blue}{green}{red}".upper()
