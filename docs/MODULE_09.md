# Module 9 — Lyrics Editor

Module 9 converts the word alignment review screen into a validated editing environment. Users can edit word text and millisecond-resolution start/end times, search words, select multiple rows, shift timing, scale timing intervals, inspect low-confidence rows, undo and redo batch operations, and atomically save the edited document as canonical UTF-8 JSON.

## Editing rules

- Word text cannot be blank.
- Start/end times remain within media duration.
- Words cannot overlap.
- Every word lasts at least 10 milliseconds.
- Confidence remains in the 0–1 range.
- IDs are regenerated sequentially by validation.
- The aligned and transcribed source records remain unchanged; edits create a separate revisioned lyrics document.

## Output

Edited lyrics are saved under `exports/lyrics/<source>.lyrics.json`. Saving uses a sibling `.part` file and atomic replacement. Low-confidence words below 55% are highlighted for review.

## Workflow

Complete transcription and word alignment, open Lyrics Editor, double-click text or timing cells, use multi-row shift/scale tools as needed, undo/redo changes, and select **Save Lyrics**. Module 10 consumes this canonical document for subtitle generation.
