from __future__ import annotations

import gc
import logging
from pathlib import Path
from threading import Event

from app.application.errors import DependencyUnavailableError,MediaImportError
from app.application.ports.speech_recognizer import TranscriptionProgress
from app.domain.models.transcription import Transcript,TranscriptSegment,TranscriptionOptions,WhisperDevice
from app.infrastructure.media.ffmpeg_audio_extractor import ExtractionCancelledError
LOGGER=logging.getLogger(__name__)


def detect_whisper_devices()->tuple[str,...]:
    devices=["cpu"]
    try:
        import ctranslate2
        if "cuda" in ctranslate2.get_supported_compute_types("cuda"):devices.insert(0,"cuda")
    except Exception:pass
    return tuple(devices)


class FasterWhisperRecognizer:
    """Lazy CTranslate2 Whisper adapter with VAD, device policy, and cancellable segment iteration."""
    def __init__(self,model_cache:Path)->None:
        try:
            from faster_whisper import WhisperModel as _WhisperModel
            import ctranslate2
            import av
        except Exception as exc:
            raise DependencyUnavailableError(
                "The bundled Whisper runtime is missing or damaged. Reinstall Karaoke AI Studio 0.21.2 or later. "
                f"Technical detail: {type(exc).__name__}: {exc}"
            ) from exc
        self._cache=model_cache;self._cache.mkdir(parents=True,exist_ok=True)
    def transcribe(self,source:Path,duration_seconds:float,options:TranscriptionOptions,progress:TranscriptionProgress,cancel_event:Event)->Transcript:
        from faster_whisper import WhisperModel
        device=self._resolve_device(options.device);compute=self._resolve_compute(device,options.compute_type)
        progress(0.0,f"Loading Whisper {options.model_name} on {device.upper()}…")
        LOGGER.info("Loading Whisper model=%s device=%s compute=%s",options.model_name,device,compute)
        model=None
        try:
            model=WhisperModel(options.model_name,device=device,compute_type=compute,download_root=str(self._cache),local_files_only=False)
            raw_segments,info=model.transcribe(str(source),language=options.language,task=options.task.value,beam_size=options.beam_size,vad_filter=options.vad_filter,word_timestamps=True,condition_on_previous_text=options.condition_on_previous_text,initial_prompt=options.initial_prompt or None,temperature=[0.0,0.2,0.4],compression_ratio_threshold=2.2,log_prob_threshold=-1.0,no_speech_threshold=0.55,hallucination_silence_threshold=1.5)
            segments=[]
            for raw in raw_segments:
                if cancel_event.is_set():raise ExtractionCancelledError("Speech recognition was cancelled.")
                segment=TranscriptSegment(int(raw.id),float(raw.start),float(raw.end),str(raw.text).strip(),float(raw.avg_logprob),float(raw.no_speech_prob));segments.append(segment)
                ratio=min(0.99,max(0.0,segment.end_seconds/max(.001,duration_seconds)));progress(ratio,f"Transcribing {self._clock(segment.end_seconds)} / {self._clock(duration_seconds)}")
            progress(1.0,"Transcription complete")
            return Transcript(source.resolve(),str(info.language),float(info.language_probability),duration_seconds,options,tuple(segments))
        except ExtractionCancelledError:raise
        except Exception as exc:
            detail=str(exc)
            if "cuda" in detail.lower() and ("memory" in detail.lower() or "cublas" in detail.lower() or "cudnn" in detail.lower()):detail += " Select CPU/int8 or install compatible CUDA 12 cuBLAS and cuDNN 9 libraries."
            raise MediaImportError(f"Speech recognition failed: {detail}") from exc
        finally:
            del model;gc.collect()
    def _resolve_device(self,requested:WhisperDevice)->str:
        available=detect_whisper_devices()
        if requested==WhisperDevice.AUTO:return available[0]
        if requested.value not in available:raise MediaImportError(f"Requested Whisper device '{requested.value}' is unavailable.")
        return requested.value
    @staticmethod
    def _resolve_compute(device:str,requested:str)->str:
        if device=="cpu" and requested in {"float16","int8_float16"}:return "int8"
        return requested
    @staticmethod
    def _clock(seconds:float)->str:
        minutes,whole=divmod(max(0,int(seconds)),60);return f"{minutes:02d}:{whole:02d}"
