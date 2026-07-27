from __future__ import annotations

import importlib.util
from pathlib import Path
from threading import Event

from app.application.errors import DependencyUnavailableError, MediaImportError
from app.application.ports.text_translator import TranslationProgress
from app.infrastructure.media.ffmpeg_audio_extractor import ExtractionCancelledError


class ArgosTextTranslator:
    """Privacy-preserving offline neural translation through installed Argos packages."""

    def __init__(self) -> None:
        if importlib.util.find_spec("argostranslate") is None:
            raise DependencyUnavailableError(r"Argos Translate is not installed. Run scripts\setup_translation.ps1.")

    @property
    def engine_name(self) -> str:
        return "Argos Translate"

    def installed_pairs(self) -> tuple[tuple[str, str], ...]:
        from argostranslate import translate
        pairs = set()
        languages = translate.get_installed_languages()
        for source in languages:
            for target in languages:
                if source.code != target.code:
                    try:
                        source.get_translation(target)
                        pairs.add((source.code, target.code))
                    except Exception:
                        continue
        return tuple(sorted(pairs))

    def install_model(self, path: Path) -> None:
        if path.suffix.lower() != ".argosmodel" or not path.is_file():
            raise MediaImportError("Select a valid .argosmodel translation package.")
        from argostranslate import package
        package.install_from_path(path)

    def translate_lines(self, lines: tuple[str, ...], source_language: str, target_language: str, progress: TranslationProgress, cancel_event: Event) -> tuple[str, ...]:
        from argostranslate import translate
        languages = translate.get_installed_languages()
        source = next((language for language in languages if language.code == source_language), None)
        target = next((language for language in languages if language.code == target_language), None)
        if source is None or target is None:
            raise MediaImportError("The selected translation languages are not installed.")
        translation = source.get_translation(target)
        results = []
        for index, line in enumerate(lines):
            if cancel_event.is_set():
                raise ExtractionCancelledError("Lyrics translation was cancelled.")
            results.append(translation.translate(line))
            progress((index + 1) / max(1, len(lines)), f"Translating line {index + 1} of {len(lines)}")
        return tuple(results)
