# Module 15 — Translation

Module 15 adds offline lyric translation through Argos Translate. It groups the corrected Module 9 words by original segment, translates each phrase locally, preserves the source start/end timing, presents original and translated lines side by side, and stores canonical UTF-8 JSON. Translation does not alter the original transcript, word alignment, or edited lyrics.

Install the runtime with `scripts/setup_translation.ps1`, then install one or more `.argosmodel` packages from **AI > Translate Lyrics…**. Available source/target choices come only from installed models. Argos may pivot through intermediate installed languages; review all translated lyrics for meaning, singability, cultural context, line length, and rights compliance before publication.

The translation output is stored under `exports/translations/<source>.<target>.translation.json`. Cancellation is checked between lines. Model installation is explicit and local; normal translation does not send lyric text to a cloud service.
