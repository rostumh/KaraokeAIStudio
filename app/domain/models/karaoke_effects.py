from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class KaraokeEffect(StrEnum):
    CLASSIC = "classic"
    SMOOTH_SWEEP = "smooth_sweep"
    OUTLINE = "outline"
    POP = "pop"
    GLOW = "glow"


@dataclass(frozen=True, slots=True)
class KaraokeEffectSettings:
    effect: KaraokeEffect = KaraokeEffect.SMOOTH_SWEEP
    fade_in_ms: int = 140
    fade_out_ms: int = 180
    pop_scale_percent: int = 112
    glow_blur: float = 2.5
    glow_outline: float = 4.0

    def validate(self) -> "KaraokeEffectSettings":
        if not 0 <= self.fade_in_ms <= 2000 or not 0 <= self.fade_out_ms <= 2000:
            raise ValueError("Effect fade durations must be between 0 and 2000 milliseconds.")
        if not 100 <= self.pop_scale_percent <= 160:
            raise ValueError("Pop scale must be between 100% and 160%.")
        if not 0 <= self.glow_blur <= 10 or not 0 <= self.glow_outline <= 12:
            raise ValueError("Glow blur or outline is outside the supported range.")
        return self
