import pytest
from app.domain.models.karaoke_effects import KaraokeEffectSettings
def test_rejects_invalid_pop_scale():
 with pytest.raises(ValueError):KaraokeEffectSettings(pop_scale_percent=99).validate()
def test_default_settings_are_valid():assert KaraokeEffectSettings().validate().fade_in_ms==140
