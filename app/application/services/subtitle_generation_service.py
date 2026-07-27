from __future__ import annotations

from pathlib import Path

from app.application.errors import MediaImportError
from app.application.ports.subtitle_exporter import SubtitleExporter
from app.domain.models.lyrics_document import LyricsDocument
from app.domain.models.subtitles import SubtitleCue, SubtitleDocument, SubtitleFormat, SubtitleOptions, SubtitleWord


class SubtitleGenerationService:
    """Groups edited words into readable cues and dispatches format exporters."""

    def __init__(self, exporters: tuple[SubtitleExporter, ...]) -> None:
        self._exporters = {exporter.format: exporter for exporter in exporters}

    def generate(self, lyrics: LyricsDocument, options: SubtitleOptions, destination: Path) -> tuple[SubtitleDocument, tuple[Path, ...]]:
        self._validate_options(options)
        cues = self._group_words(lyrics, options)
        if not cues:
            raise MediaImportError("No subtitle cues could be generated from the lyrics document.")
        document = SubtitleDocument(lyrics.source_path, lyrics.language, lyrics.duration_seconds, cues, options)
        destination.mkdir(parents=True, exist_ok=True)
        outputs = []
        for subtitle_format in options.formats:
            exporter = self._exporters.get(subtitle_format)
            if exporter is None:
                raise MediaImportError(f"No exporter is registered for {subtitle_format.value.upper()}.")
            outputs.append(exporter.export(document, destination))
        return document, tuple(outputs)

    @staticmethod
    def _validate_options(options: SubtitleOptions) -> None:
        if not options.formats:
            raise MediaImportError("Select at least one subtitle format.")
        if not 1 <= options.max_words_per_line <= 20:
            raise MediaImportError("Words per line must be between 1 and 20.")
        if not 0.5 <= options.max_line_duration <= 20:
            raise MediaImportError("Maximum cue duration must be between 0.5 and 20 seconds.")
        if not 0 <= options.gap_threshold <= 10:
            raise MediaImportError("Gap threshold must be between 0 and 10 seconds.")
        if options.resolution_width < 320 or options.resolution_height < 240:
            raise MediaImportError("Subtitle resolution is too small.")
        if options.style.alignment not in range(1, 10):
            raise MediaImportError("ASS alignment must be between 1 and 9.")

    @staticmethod
    def _group_words(lyrics: LyricsDocument, options: SubtitleOptions) -> tuple[SubtitleCue, ...]:
        cues: list[SubtitleCue] = []
        current: list[SubtitleWord] = []
        for editable in lyrics.words:
            word = SubtitleWord(editable.text, editable.start_seconds, editable.end_seconds)
            if current:
                gap = word.start_seconds - current[-1].end_seconds
                duration = word.end_seconds - current[0].start_seconds
                boundary = len(current) >= options.max_words_per_line or gap > options.gap_threshold or duration > options.max_line_duration
                if boundary:
                    cues.append(SubtitleGenerationService._cue(len(cues), current, lyrics.duration_seconds, options))
                    current = []
            current.append(word)
        if current:
            cues.append(SubtitleGenerationService._cue(len(cues), current, lyrics.duration_seconds, options))
        normalized = []
        for index, cue in enumerate(cues):
            next_start = cues[index + 1].start_seconds if index + 1 < len(cues) else lyrics.duration_seconds
            end = min(cue.end_seconds, max(cue.start_seconds + 0.01, next_start))
            normalized.append(SubtitleCue(index + 1, cue.start_seconds, end, cue.words))
        return tuple(normalized)

    @staticmethod
    def _cue(index: int, words: list[SubtitleWord], duration: float, options: SubtitleOptions) -> SubtitleCue:
        start = max(0.0, words[0].start_seconds - options.lead_in_seconds)
        end = min(duration, words[-1].end_seconds + options.lead_out_seconds)
        return SubtitleCue(index + 1, start, max(start + 0.01, end), tuple(words))
