from __future__ import annotations

import html
import re
from dataclasses import replace
from difflib import SequenceMatcher
from pathlib import Path

from app.domain.models.lyrics_document import EditableWord, LyricsDocument

_WORD = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)


def karaoke_lines(text: str) -> list[list[str]]:
    """Return clean karaoke phrases. Line breaks are intentional segment boundaries."""
    lines: list[list[str]] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        tokens = _WORD.findall(html.unescape(raw).replace("’", "'"))
        clean = []
        for token in tokens:
            low = token.lower()
            clean.append(low.capitalize() if low in {"i", "i'm", "i'll", "i'd", "i've"} else low)
        if clean:
            lines.append(clean)
    return lines


def parse_lyrics_file(path: str | Path) -> str:
    """Read TXT/LRC/SRT/VTT/ASS lyrics and preserve one phrase per source cue/line."""
    path = Path(path)
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    suffix = path.suffix.lower()
    if suffix == ".lrc":
        out = []
        for line in raw.splitlines():
            line = re.sub(r"^(?:\[[0-9:.]+\])+", "", line).strip()
            if line and not re.match(r"^\[(ar|ti|al|by|offset):", line, re.I): out.append(line)
        raw = "\n".join(out)
    elif suffix in {".srt", ".vtt"}:
        out = []
        for block in re.split(r"\n\s*\n", raw):
            rows = [r.strip() for r in block.splitlines() if r.strip()]
            text_rows = [r for r in rows if not r.isdigit() and "-->" not in r and r.upper() != "WEBVTT" and not r.startswith(("NOTE", "STYLE"))]
            if text_rows: out.append(" ".join(re.sub(r"<[^>]+>", "", r) for r in text_rows))
        raw = "\n".join(out)
    elif suffix in {".ass", ".ssa"}:
        out = []
        for row in raw.splitlines():
            if row.startswith("Dialogue:"):
                text = row.split(",", 9)[-1]
                text = re.sub(r"\{[^}]*\}", "", text).replace(r"\N", " ").replace(r"\n", " ")
                if text.strip(): out.append(text.strip())
        raw = "\n".join(out)
    lines = karaoke_lines(raw)
    if not lines:
        raise ValueError(f"No lyric text was found in {path.name}.")
    return "\n".join(" ".join(line) for line in lines)


def realign_document(document: LyricsDocument, text: str) -> LyricsDocument:
    """Align corrected phrases to existing acoustic word timestamps using sequence anchors."""
    lines = karaoke_lines(text)
    if not lines:
        raise ValueError("Lyrics are empty.")
    tokens = [word for line in lines for word in line]
    segment_ids = [segment for segment, line in enumerate(lines) for _ in line]
    old = list(document.words)
    if not old:
        start, end = 0.0, max(document.duration_seconds, len(tokens) * 0.25)
        step = (end - start) / len(tokens)
        words = tuple(EditableWord(i, segment_ids[i], t, start+i*step, start+(i+1)*step, .5) for i,t in enumerate(tokens))
        return replace(document, words=words, revision=document.revision + 1)

    old_keys = [w.text.casefold().strip(".,!?;:\"'") for w in old]
    new_keys = [t.casefold() for t in tokens]
    matcher = SequenceMatcher(None, old_keys, new_keys, autojunk=False)
    anchors: dict[int, EditableWord] = {}
    for block in matcher.get_matching_blocks():
        for offset in range(block.size): anchors[block.b + offset] = old[block.a + offset]

    vocal_start, vocal_end = old[0].start_seconds, old[-1].end_seconds
    starts = [0.0] * len(tokens); ends = [0.0] * len(tokens); confidence = [.55] * len(tokens)
    for n, word in anchors.items():
        starts[n], ends[n], confidence[n] = word.start_seconds, word.end_seconds, max(.70, word.probability)

    anchor_indexes = sorted(anchors)
    boundaries = [-1] + anchor_indexes + [len(tokens)]
    for left, right in zip(boundaries, boundaries[1:]):
        first, last = left + 1, right - 1
        if first > last: continue
        interval_start = vocal_start if left == -1 else ends[left]
        interval_end = vocal_end if right == len(tokens) else starts[right]
        if interval_end <= interval_start:
            interval_end = interval_start + .12 * (last - first + 1)
        step = (interval_end - interval_start) / (last - first + 1)
        for idx in range(first, last + 1):
            starts[idx] = interval_start + (idx-first)*step
            ends[idx] = interval_start + (idx-first+1)*step

    words = tuple(EditableWord(i, segment_ids[i], token, starts[i], max(starts[i]+.02, ends[i]), confidence[i]) for i, token in enumerate(tokens))
    return replace(document, words=words, revision=document.revision + 1)
