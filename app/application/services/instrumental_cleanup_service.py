from __future__ import annotations

from pathlib import Path
from threading import Event

from app.application.errors import MediaImportError
from app.application.ports.instrumental_cleaner import CleanupProgress, InstrumentalCleaner
from app.domain.models.instrumental_cleanup import CleanupSettings, InstrumentalCleanupRequest, InstrumentalCleanupResult
from app.domain.models.media import MediaAsset


class InstrumentalCleanupService:
    """Validates non-destructive cleanup settings and delegates signal processing."""

    def __init__(self, cleaner: InstrumentalCleaner) -> None:
        self._cleaner = cleaner

    def clean(self, asset: MediaAsset, output_path: Path, settings: CleanupSettings, *, overwrite: bool, progress: CleanupProgress, cancel_event: Event) -> InstrumentalCleanupResult:
        audio = asset.primary_audio
        if audio is None:
            raise MediaImportError("The selected asset contains no audio stream.")
        destination = output_path.expanduser().resolve(strict=False)
        if destination == asset.source_path.resolve():
            raise MediaImportError("Cleanup output cannot overwrite the source audio.")
        if destination.exists() and not overwrite:
            raise MediaImportError(f"The output file already exists: {destination}")
        if not 0.01 <= settings.noise_reduction_db <= 30.0:
            raise MediaImportError("Noise reduction must be between 0.01 and 30 dB.")
        if not -80.0 <= settings.noise_floor_db <= -20.0:
            raise MediaImportError("Noise floor must be between -80 and -20 dB.")
        if not 10 <= settings.highpass_hz < settings.lowpass_hz <= 22000:
            raise MediaImportError("High-pass frequency must be below low-pass frequency within 10–22000 Hz.")
        if not -24.0 <= settings.target_lufs <= -8.0:
            raise MediaImportError("Target loudness must be between -24 and -8 LUFS.")
        if not -9.0 <= settings.true_peak_db <= -0.1:
            raise MediaImportError("True-peak target must be between -9 and -0.1 dBTP.")
        if not 1.0 <= settings.loudness_range <= 20.0:
            raise MediaImportError("Loudness range must be between 1 and 20 LU.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        request = InstrumentalCleanupRequest(asset.source_path, destination, audio.index, asset.duration_seconds, settings, overwrite)
        return self._cleaner.clean(request, progress, cancel_event)
