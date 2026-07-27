# Module 8 — Word Timestamp Alignment

Module 8 adds word-level timestamps and confidence values to the completed Module 7 transcript. The implementation reuses Faster Whisper with `word_timestamps=True`, supplies the recognized transcript as context, validates every returned time interval, enforces monotonic ordering, clamps timestamps to media duration, persists canonical UTF-8 JSON, and displays words in a dedicated Lyrics Editor timing tab.

## Workflow

1. Complete Whisper transcription.
2. Choose **AI > Align Word Timestamps…** or press **Ctrl+Alt+T**.
3. Start alignment and monitor progress.
4. Review word start, end, text, and confidence in Lyrics Editor.

The result is saved under `exports/transcripts` as `<source>.alignment.json`. Cancellation is cooperative at segment boundaries. Model/device/compute settings are inherited from the transcript, so alignment is reproducible.

## Accuracy boundary

Whisper word times are inference-derived alignment estimates rather than manually verified phoneme boundaries. They are appropriate for automatic karaoke timing and later editing, but should remain editable. Module 9 introduces professional timing correction and undo/redo. The service guards against negative, overlapping, reversed, over-duration, blank, and out-of-range word records.

## Test

```powershell
python -m pytest
python -m ruff check .
python -m mypy app
```
