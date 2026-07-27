from __future__ import annotations

from app.domain.models.karaoke_effects import KaraokeEffect, KaraokeEffectSettings
from app.domain.models.subtitles import SubtitleCue
from app.infrastructure.subtitles.common import escape_ass_text


class KaraokeEffectService:
    """Builds deterministic ASS override tags for supported karaoke effect presets."""

    def render_cue(self, cue: SubtitleCue, settings: KaraokeEffectSettings) -> str:
        settings.validate()
        prefix = f"{{\\fad({settings.fade_in_ms},{settings.fade_out_ms})}}"
        if settings.effect == KaraokeEffect.GLOW:
            prefix += f"{{\\blur{settings.glow_blur:.1f}\\bord{settings.glow_outline:.1f}}}"
        parts: list[str] = []
        for word in cue.words:
            duration_cs = max(1, round((word.end_seconds - word.start_seconds) * 100))
            tag = self._word_tag(settings.effect, duration_cs, word.start_seconds - cue.start_seconds, settings)
            parts.append(f"{tag}{escape_ass_text(word.text)}")
        return prefix + " ".join(parts)

    @staticmethod
    def _word_tag(effect: KaraokeEffect, duration_cs: int, offset_seconds: float, settings: KaraokeEffectSettings) -> str:
        if effect == KaraokeEffect.CLASSIC:
            return f"{{\\k{duration_cs}}}"
        if effect in {KaraokeEffect.SMOOTH_SWEEP, KaraokeEffect.GLOW}:
            return f"{{\\kf{duration_cs}}}"
        if effect == KaraokeEffect.OUTLINE:
            return f"{{\\ko{duration_cs}}}"
        start_ms = max(0, round(offset_seconds * 1000))
        peak_ms = start_ms + min(120, max(30, duration_cs * 5))
        settle_ms = min(start_ms + duration_cs * 10, peak_ms + 140)
        scale = settings.pop_scale_percent
        return (
            f"{{\\kf{duration_cs}"
            f"\\t({start_ms},{peak_ms},\\fscx{scale}\\fscy{scale})"
            f"\\t({peak_ms},{settle_ms},\\fscx100\\fscy100)}}"
        )
