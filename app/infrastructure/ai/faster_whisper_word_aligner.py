from __future__ import annotations

import gc
import importlib.util
import logging
from pathlib import Path
from threading import Event

from app.application.errors import DependencyUnavailableError, MediaImportError
from app.application.ports.word_aligner import AlignmentProgress
from app.domain.models.alignment import AlignedTranscript, WordTiming
from app.domain.models.transcription import Transcript
from app.infrastructure.ai.faster_whisper_recognizer import detect_whisper_devices
from app.infrastructure.media.ffmpeg_audio_extractor import ExtractionCancelledError

LOGGER = logging.getLogger(__name__)


class FasterWhisperWordAligner:
    """Re-decodes audio with Faster Whisper's cross-attention word timestamps."""

    def __init__(self, model_cache: Path) -> None:
        if importlib.util.find_spec("faster_whisper") is None:
            raise DependencyUnavailableError("Faster Whisper is not installed. Run scripts\\setup_asr.ps1.")
        self._cache = model_cache
        self._cache.mkdir(parents=True, exist_ok=True)

    def align(self, transcript: Transcript, progress: AlignmentProgress, cancel_event: Event) -> AlignedTranscript:
        from faster_whisper import WhisperModel

        options = transcript.options
        device = self._resolve_device(options.device.value)
        compute = self._resolve_compute(device, options.compute_type)
        model = None
        progress(0.0, f"Loading {options.model_name} alignment model on {device.upper()}…")
        try:
            model = WhisperModel(options.model_name, device=device, compute_type=compute, download_root=str(self._cache), local_files_only=False)
            segments, _ = model.transcribe(
                str(transcript.source_path), language=transcript.language or options.language,
                task=options.task.value, beam_size=options.beam_size, vad_filter=options.vad_filter,
                word_timestamps=True, condition_on_previous_text=False,
                initial_prompt=options.initial_prompt or None,
                temperature=0.0, vad_parameters={"min_silence_duration_ms": 250, "speech_pad_ms": 120},
                hallucination_silence_threshold=1.0,
            )
            words: list[WordTiming] = []
            for segment in segments:
                if cancel_event.is_set():
                    raise ExtractionCancelledError("Word alignment was cancelled.")
                for raw in segment.words or ():
                    words.append(WordTiming(len(words), int(segment.id), str(raw.word).strip(), float(raw.start), float(raw.end), float(raw.probability)))
                ratio = min(0.99, max(0.0, float(segment.end) / max(0.001, transcript.duration_seconds)))
                progress(ratio, f"Aligning words at {self._clock(float(segment.end))} / {self._clock(transcript.duration_seconds)}")
            progress(1.0, "Word alignment complete")
            return AlignedTranscript(transcript.source_path, transcript, tuple(words), f"faster-whisper:{options.model_name}")
        except ExtractionCancelledError:
            raise
        except Exception as exc:
            detail = str(exc)
            if "cuda" in detail.lower() and "memory" in detail.lower():
                detail += " Select CPU/INT8 or use a smaller Whisper model."
            raise MediaImportError(f"Word alignment failed: {detail}") from exc
        finally:
            del model
            gc.collect()

    @staticmethod
    def _resolve_device(requested: str) -> str:
        available = detect_whisper_devices()
        if requested == "auto":
            return available[0]
        if requested not in available:
            raise MediaImportError(f"Requested alignment device '{requested}' is unavailable.")
        return requested

    @staticmethod
    def _resolve_compute(device: str, compute: str) -> str:
        return "int8" if device == "cpu" and compute in {"float16", "int8_float16"} else compute

    @staticmethod
    def _clock(seconds: float) -> str:
        minutes, whole = divmod(max(0, int(seconds)), 60)
        return f"{minutes:02d}:{whole:02d}"
