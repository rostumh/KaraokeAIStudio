from __future__ import annotations

from pathlib import Path
from threading import Event

from app.application.errors import MediaImportError
from app.application.ports.alignment_repository import AlignmentRepository
from app.application.ports.word_aligner import AlignmentProgress, WordAligner
from app.domain.models.alignment import AlignedTranscript, WordTiming
from app.domain.models.transcription import Transcript


class WordAlignmentService:
    """Runs alignment, validates timeline invariants, and persists canonical output."""

    def __init__(self, aligner: WordAligner, repository: AlignmentRepository) -> None:
        self._aligner = aligner
        self._repository = repository

    def align(self, transcript: Transcript, destination: Path, progress: AlignmentProgress, cancel_event: Event) -> tuple[AlignedTranscript, Path]:
        if not transcript.segments:
            raise MediaImportError("A completed transcript is required before word alignment.")
        aligned = self._aligner.align(transcript, progress, cancel_event)
        validated = self._validate_and_normalize(aligned)
        destination.mkdir(parents=True, exist_ok=True)
        return validated, self._repository.save(validated, destination)

    @staticmethod
    def _validate_and_normalize(aligned: AlignedTranscript) -> AlignedTranscript:
        if not aligned.words:
            raise MediaImportError("Alignment completed without producing word timestamps.")
        normalized: list[WordTiming] = []
        previous_end = 0.0
        duration = max(0.0, aligned.duration_seconds)
        for index, word in enumerate(aligned.words):
            text = word.text.strip()
            if not text:
                continue
            start = max(previous_end, min(duration, max(0.0, word.start_seconds)))
            end = max(start + 0.01, min(duration, max(start, word.end_seconds)))
            if end > duration and duration > 0:
                end = duration
                start = min(start, max(0.0, end - 0.01))
            probability = min(1.0, max(0.0, word.probability))
            normalized.append(WordTiming(len(normalized), word.segment_id, text, start, end, probability))
            previous_end = end
        if not normalized:
            raise MediaImportError("Alignment contained no usable words.")
        return AlignedTranscript(aligned.source_path, aligned.transcript, tuple(normalized), aligned.alignment_model)
