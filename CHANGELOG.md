
## 0.28.2
- Fixed Windows setup regression: restored the required `Lyric height` render-dialog label expected by the automated compatibility test.
- Preserved persistent lyric size/height settings and ASS style-field updates.

## 0.28.2
- Fixed Auto Mode advancing to render while AI separation was unresolved.
- Auto Mode now visibly starts separation and validates the generated instrumental before continuing.
- Separation failures now offer Retry, Continue with Original Audio, or Cancel; fallback applies only to the current song and warns that lead vocals may remain.
- Auto Mode now commits the selected/recommended visual style (Modern Glow by default), marks Step 5 complete, and opens render settings without requiring the Visual Style Editor.
- Added regression coverage for separation prerequisites, current-song fallback, and automatic style completion.

## 0.28.2
- Repaired and strengthened the light theme, including group-title spacing, controls, docks and scrollbars.
- Added Replace / Realign Full Lyrics plus TXT, LRC, SRT and ASS import for complete manual lyric correction with a different word count.
- Bound ASS selection to the active lyrics document; unrelated global subtitles are no longer selected.
- Metadata lookup now uses the original source, parses `Artist - Title` correctly, applies safe local suggestions even when online lookup is unavailable, and reports lookup status.
- Increased default lyric size to 112 px for large-room/TV readability.
- Rebuilt title-card positioning and font defaults to prevent title, artist and songwriter overlap.
- Removed automatic second/upcoming subtitle events so one authoritative karaoke line is displayed.
- Countdown now ends on the first actual lyric timestamp and shortens or disappears when the intro is too short.
- Render completion now clears stale separation state and presents a stable Video Ready status.

## 0.28.2
- Restored backward-compatible workflow status and source markers required by the Windows installer regression suite.
- Preserved the new project-bound ASS selection, lyric-timed countdown, and stable Video Ready behavior.


## 0.28.2
- Extract video audio to job-bound 44.1 kHz stereo PCM WAV before Demucs separation.
- Validate generated stems and preserve exact per-job output paths.
- Retry automatic CUDA failures once on CPU.
- Reset progress/busy state and correct workflow completion after separation failure.
