# Module 4 — Audio Extraction

## Scope

Module 4 extracts a selected audio stream from any imported media asset through FFmpeg. It supports WAV PCM 16-bit, WAV PCM 24-bit, lossless FLAC, and 320 kbps MP3; source sample-rate/channel preservation or explicit conversion; deterministic stream mapping; asynchronous progress; user cancellation; atomic destination replacement; and automatic import of the resulting audio asset.

## Architecture

- `AudioExtractionService` validates output policy and creates an immutable request.
- `AudioExtractor` is an application port independent of FFmpeg and Qt.
- `FFmpegAudioExtractor` maps the request to a safe subprocess argument vector.
- `AudioExtractionController` moves blocking encoding to a dedicated QThread.
- `AudioExtractionDialog` collects stream, codec, sample-rate, channel, overwrite, and destination settings.

## Reliability

FFmpeg writes to a sibling `.part` file. Only a successful, nonempty result is atomically moved to the requested destination. Failure or cancellation removes the partial file. The source can never be selected as the destination. Existing output is preserved unless overwrite is explicitly selected. Video, subtitle, and data streams are excluded, and the selected absolute audio stream index is mapped explicitly.

Progress uses FFmpeg's machine-readable `-progress pipe:1` output and compares encoded output time with the probed source duration. The worker remains outside the GUI thread. Cancellation requests graceful termination, escalates to process kill after three seconds, and removes partial output.

## FFmpeg

Set `KAS_FFMPEG_PATH` to the full path of `ffmpeg.exe`, package it under a supported runtime path, or add the FFmpeg bin directory to PATH. Verify:

```powershell
ffmpeg -version
ffprobe -version
```

## Run

1. Import valid media.
2. Select the asset in Project Media.
3. Choose **File > Extract Audio…** or press **Ctrl+Shift+E**.
4. Choose stream, output format, optional resampling/downmix, and destination.
5. Select **Extract Audio**.

On success, the audio file is added to Project Media automatically and becomes the selected Studio asset.

## Quality

```powershell
python -m pytest
python -m ruff check .
python -m mypy app
```

Tests cover request validation, source-overwrite protection, stream mapping, PCM 24-bit selection, FLAC selection, and all previous modules.
