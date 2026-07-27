from app.application.services.karaoke_effect_service import KaraokeEffectService
from app.domain.models.karaoke_effects import KaraokeEffect, KaraokeEffectSettings
from app.domain.models.subtitles import SubtitleCue, SubtitleWord

def cue():return SubtitleCue(1,1,3,(SubtitleWord("Hello",1,2),SubtitleWord("world",2,3)))
def test_smooth_sweep_uses_kf_and_fade():
 text=KaraokeEffectService().render_cue(cue(),KaraokeEffectSettings(KaraokeEffect.SMOOTH_SWEEP));assert r"\kf100" in text and r"\fad(140,180)" in text
def test_outline_uses_ko():
 assert r"\ko100" in KaraokeEffectService().render_cue(cue(),KaraokeEffectSettings(KaraokeEffect.OUTLINE))
def test_pop_contains_timed_scale_transforms():
 text=KaraokeEffectService().render_cue(cue(),KaraokeEffectSettings(KaraokeEffect.POP));assert r"\t(" in text and r"\fscx112" in text
def test_glow_contains_blur_and_outline():
 text=KaraokeEffectService().render_cue(cue(),KaraokeEffectSettings(KaraokeEffect.GLOW));assert r"\blur2.5" in text and r"\bord4.0" in text
