# Module 11 — Karaoke Effects

Module 11 adds a reusable ASS karaoke-effects engine and an animated desktop preview. Effects are applied during ASS generation without modifying canonical word timing.

## Presets

- **Classic Fill** uses `\k` for stepped highlighting.
- **Smooth Sweep** uses `\kf` for progressive left-to-right fill.
- **Outline Pulse** uses `\ko` to highlight the outline during each word.
- **Word Pop** uses `\kf` plus cue-relative `\t` scale transforms.
- **Neon Glow** uses `\kf`, blur, and expanded outline tags.

All presets support configurable `\fad` line entrance and exit. Effect settings are stored independently from lyric timing, so styles can be changed without rerunning transcription or alignment.

## Use

Choose **AI > Karaoke Effects…** or press **Ctrl+Alt+K**, select an effect, adjust supported parameters, and apply. Then generate ASS from **File > Generate Subtitles…**. SRT and LRC remain plain compatibility formats and intentionally do not contain ASS effects.

## Safety

The generator emits only validated numeric override parameters. User lyric text continues through ASS escaping. Line-level tags appear once per dialogue event, avoiding renderer-dependent conflicts between mutually exclusive line tags.
