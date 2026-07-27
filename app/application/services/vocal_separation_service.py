from __future__ import annotations

import logging
from pathlib import Path
from threading import Event

from app.application.errors import MediaImportError
from app.application.ports.source_separator import SourceSeparator, StatusCallback
from app.domain.models.audio_extraction import AudioExtractionRequest, AudioFormat
from app.domain.models.media import MediaAsset, MediaKind
from app.domain.models.separation import ComputeDevice, SeparationMode, SeparationRequest, SeparationResult, StemFormat
from app.infrastructure.media.ffmpeg_audio_extractor import FFmpegAudioExtractor
from app.infrastructure.media.ffmpeg_locator import locate_ffmpeg

LOGGER = logging.getLogger(__name__)
ALLOWED_MODELS = frozenset({"htdemucs", "htdemucs_ft"})


class VocalSeparationService:
    """Prepare deterministic PCM input, run Demucs, and validate job-bound outputs."""

    def __init__(self, separator: SourceSeparator, extractor: FFmpegAudioExtractor | None = None) -> None:
        self._separator = separator
        self._extractor = extractor

    def separate(
        self, asset: MediaAsset, output_root: Path, *, model_name: str, mode: SeparationMode,
        device: ComputeDevice, stem_format: StemFormat, shifts: int, overlap: float,
        segment_seconds: int | None, status: StatusCallback, cancel_event: Event,
    ) -> SeparationResult:
        if not asset.audio_streams:
            raise MediaImportError("The selected asset contains no audio stream.")
        if model_name not in ALLOWED_MODELS:
            raise MediaImportError(f"Unsupported Demucs model: {model_name}")
        if not 1 <= shifts <= 10:
            raise MediaImportError("Quality shifts must be between 1 and 10.")
        if not 0.1 <= overlap <= 0.75:
            raise MediaImportError("Segment overlap must be between 0.10 and 0.75.")
        if segment_seconds is not None and not 5 <= segment_seconds <= 30:
            raise MediaImportError("Segment length must be between 5 and 30 seconds.")

        destination = output_root.expanduser().resolve(strict=False)
        destination.mkdir(parents=True, exist_ok=True)
        source = self._prepare_pcm_input(asset, destination, status, cancel_event)
        request = SeparationRequest(source, destination, model_name, mode, device, stem_format, shifts, overlap, segment_seconds)
        try:
            result = self._separator.separate(request, status, cancel_event)
        except Exception as exc:
            # AUTO normally chooses CUDA. Retry once on CPU for packaged-PC reliability.
            if device == ComputeDevice.AUTO and "cuda" in str(exc).lower() and not cancel_event.is_set():
                LOGGER.warning("CUDA separation failed; retrying on CPU: %s", exc)
                status("GPU separation failed; retrying safely on CPU…")
                request = SeparationRequest(source, destination, model_name, mode, ComputeDevice.CPU, stem_format, shifts, overlap, segment_seconds)
                result = self._separator.separate(request, status, cancel_event)
            else:
                raise
        self._validate_stems(result.stems)
        # Preserve the user's original media path while retaining exact job-bound stem paths.
        return SeparationResult(asset.source_path, result.output_directory, result.stems, result.model_name, result.device, result.elapsed_seconds)

    def _prepare_pcm_input(self, asset: MediaAsset, destination: Path, status: StatusCallback, cancel_event: Event) -> Path:
        if asset.kind == MediaKind.AUDIO and asset.source_path.suffix.lower() == ".wav":
            return asset.source_path
        input_dir = destination / "_inputs" / asset.asset_id
        input_dir.mkdir(parents=True, exist_ok=True)
        wav_path = input_dir / "separation_input.wav"
        if wav_path.is_file() and wav_path.stat().st_size > 44:
            status("Using prepared PCM audio for separation…")
            return wav_path
        status("Extracting clean stereo audio for AI separation…")
        extractor = self._extractor or FFmpegAudioExtractor(locate_ffmpeg())
        stream = asset.primary_audio
        assert stream is not None
        request = AudioExtractionRequest(asset.source_path, wav_path, stream.index, asset.duration_seconds, AudioFormat.WAV_PCM_16, sample_rate=44100, channels=2, overwrite=True)
        extractor.extract(request, lambda value: status(f"Preparing audio… {round(value * 100)}%"), cancel_event)
        if not wav_path.is_file() or wav_path.stat().st_size <= 44:
            raise MediaImportError("FFmpeg did not create a valid PCM separation input.")
        return wav_path

    @staticmethod
    def _validate_stems(stems: tuple[Path, ...]) -> None:
        invalid = [path.name for path in stems if not path.is_file() or path.stat().st_size < 1024]
        if invalid:
            raise MediaImportError(f"Separation outputs are missing or invalid: {', '.join(invalid)}")
