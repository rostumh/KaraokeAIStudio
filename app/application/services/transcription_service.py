from __future__ import annotations

from pathlib import Path
from threading import Event
from app.application.errors import MediaImportError
from app.application.ports.speech_recognizer import SpeechRecognizer, TranscriptionProgress
from app.application.ports.transcript_repository import TranscriptRepository
from app.domain.models.media import MediaAsset
from app.domain.models.transcription import Transcript, TranscriptionOptions
from app.lyrics_engine.filipino import FilipinoLyricsPostProcessor
from app.lyrics_engine.quality import SingingTranscriptQualityGate

ALLOWED_MODELS=frozenset({"tiny","base","small","medium","large-v3","distil-large-v3"})


class TranscriptionService:
    """Validates recognition policy, invokes ASR, and persists reproducible output."""
    def __init__(self,recognizer:SpeechRecognizer,repository:TranscriptRepository)->None:
        self._recognizer=recognizer;self._repository=repository;self._post=FilipinoLyricsPostProcessor();self._quality=SingingTranscriptQualityGate()
    def transcribe(self,asset:MediaAsset,options:TranscriptionOptions,destination:Path,progress:TranscriptionProgress,cancel_event:Event)->tuple[Transcript,tuple[Path,Path]]:
        if not asset.audio_streams:raise MediaImportError("The selected asset has no audio stream.")
        if options.model_name not in ALLOWED_MODELS:raise MediaImportError(f"Unsupported Whisper model: {options.model_name}")
        if not 1<=options.beam_size<=10:raise MediaImportError("Beam size must be between 1 and 10.")
        if options.compute_type not in {"int8","int8_float16","float16","float32"}:raise MediaImportError("Unsupported Whisper compute type.")
        destination.mkdir(parents=True,exist_ok=True)
        transcript=self._post.process(self._recognizer.transcribe(asset.source_path,asset.duration_seconds,options,progress,cancel_event))
        quality=self._quality.evaluate(transcript)
        if not quality.accepted:raise MediaImportError("Whisper output failed the lyrics quality check. Try a better vocal separation or review the source audio.")
        if quality.warning:progress(.99,quality.warning)
        return transcript,self._repository.save(transcript,destination)
