# Module 6 — Instrumental Cleanup

Module 6 adds a non-destructive FFmpeg-based post-separation cleanup pipeline. It is designed for a Demucs `no_vocals` stem or another selected instrumental source. The pipeline provides high/low-pass conditioning, FFT denoising, EBU R128 loudness normalization, optional true-peak limiting, 48 kHz output, WAV 24-bit or lossless FLAC delivery, presets, custom controls, background processing, progress, cancellation, atomic output, and automatic result import.

## Signal chain

```text
High-pass → Low-pass → FFT denoise → Loudness normalization → True-peak limiter
```

Presets intentionally keep denoising conservative because excessive spectral reduction can create musical-noise artifacts and damage cymbals, reverb, and stereo ambience. **Gentle** is recommended for already-clean Demucs output, **Balanced** for normal production, and **Strong** only for audible residual noise. Custom mode unlocks all parameters.

## Use

Import or select an instrumental stem, then choose **AI > Clean Instrumental…** or press **Ctrl+Shift+I**. Select a preset and destination, run cleanup, then monitor determinate status-bar progress. The generated output is automatically queued through the media import controller.

## Test

```powershell
python -m pytest
python -m ruff check .
python -m mypy app
```
