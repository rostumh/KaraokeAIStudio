from __future__ import annotations

from pathlib import Path
from threading import Event

from app.application.errors import MediaImportError
from app.application.ports.audio_extractor import AudioExtractor, ProgressCallback
from app.domain.models.audio_extraction import AudioExtractionRequest, AudioExtractionResult, AudioFormat
from app.domain.models.media import MediaAsset


class AudioExtractionService:
    """Builds and validates an extraction request before invoking infrastructure."""

    def __init__(self, extractor: AudioExtractor) -> None:
        self._extractor = extractor

    def extract(
        self,
        asset: MediaAsset,
        output_path: Path,
        output_format: AudioFormat,
        *,
        stream_index: int | None = None,
        sample_rate: int | None = None,
        channels: int | None = None,
        mp3_bitrate_kbps: int = 320,
        overwrite: bool = False,
        progress: ProgressCallback,
        cancel_event: Event,
    ) -> AudioExtractionResult:
        audio = asset.primary_audio if stream_index is None else next(
            (item for item in asset.audio_streams if item.index == stream_index), None
        )
        if audio is None:
            raise MediaImportError("The selected media has no matching audio stream.")
        destination = output_path.expanduser().resolve(strict=False)
        if destination == asset.source_path.resolve():
            raise MediaImportError("The extraction destination cannot overwrite the source media.")
        if destination.exists() and not overwrite:
            raise MediaImportError(f"The output file already exists: {destination}")
        if sample_rate is not None and sample_rate not in {22050, 32000, 44100, 48000, 88200, 96000}:
            raise MediaImportError("The selected sample rate is not supported by this extraction profile.")
        if channels is not None and channels not in {1, 2}:
            raise MediaImportError("Channel conversion must be mono or stereo.")
        if mp3_bitrate_kbps not in {128, 192, 256, 320}:
            raise MediaImportError("MP3 bitrate must be 128, 192, 256, or 320 kbps.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        request = AudioExtractionRequest(
            source_path=asset.source_path,
            output_path=destination,
            stream_index=audio.index,
            duration_seconds=asset.duration_seconds,
            output_format=output_format,
            sample_rate=sample_rate,
            channels=channels,
            mp3_bitrate_kbps=mp3_bitrate_kbps,
            overwrite=overwrite,
        )
        return self._extractor.extract(request, progress, cancel_event)
