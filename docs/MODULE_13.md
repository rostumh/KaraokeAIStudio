# Module 13 — Final Export & Quality Validation

Module 13 performs final delivery quality control. It validates the rendered file with FFprobe, checks required streams, duration, resolution, pixel format, audio sample rate, and file size, then runs a strict complete-file FFmpeg decode scan using `-xerror`. Results are displayed as pass/warning/error rows and saved atomically as JSON under `exports/quality`.

Use **File > Validate Final Export…** or Ctrl+Alt+Q. A report passes only when no ERROR check exists; warnings identify delivery choices that remain playable but differ from the recommended 720p+, yuv420p, 48 kHz profile. Cancellation terminates the decode scan and does not produce a completed report.
