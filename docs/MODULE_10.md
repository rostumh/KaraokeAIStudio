# Module 10 — Subtitle Generator

Module 10 transforms the validated Module 9 lyrics document into ASS, SRT, and LRC files. Words are grouped into readable cues using maximum word count, maximum duration, and silence-gap boundaries. Optional lead-in/out values are clamped so adjacent cues never overlap.

ASS output defines a complete v4+ script, video resolution, named style, BGR-formatted colors, margins, outline, shadow, and per-word `\k` karaoke durations in centiseconds. SRT uses sequential cues and millisecond timestamps. LRC uses line timestamps in centiseconds. All outputs are UTF-8 and written atomically through sibling `.part` files.

## Use

Complete word alignment and lyrics editing, then choose **File > Generate Subtitles…** or press **Ctrl+Alt+S**. Select formats, cue grouping, lead timing, resolution, font, size, margin, weight, and colors. Outputs are written under `exports/subtitles`.

## Quality

```powershell
python -m pytest
python -m ruff check .
python -m mypy app
```
