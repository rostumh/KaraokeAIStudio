# Module 3 — Import Media

## Scope

Module 3 implements secure, asynchronous local-media ingestion for MP3, FLAC, WAV, AAC, M4A, MP4, MKV, AVI, and MOV files. It validates source policy, locates FFprobe, gathers container and stream metadata as JSON, maps external data to immutable domain models, and updates the Project, Preview, Properties, toolbar, and status interfaces without blocking the GUI thread.

## Architecture

1. `MediaImportService` applies business validation and depends only on the `MediaProbe` port.
2. `FFprobeMediaProbe` is the infrastructure adapter that executes FFprobe with an argument list, no shell, a timeout, hidden Windows console, captured UTF-8 output, and explicit return-code handling.
3. `MediaImportController` moves blocking work to a dedicated `QThread` and emits started, succeeded, failed, and busy state signals.
4. `MediaAssetListModel` exposes immutable assets to Qt views and deduplicates imports by normalized source path.
5. Views render domain metadata but never launch processes or inspect files.

## FFmpeg dependency

Install a current 64-bit FFmpeg build for Windows and ensure `ffprobe.exe` is available by one of these methods, in precedence order:

1. Set `KAS_FFPROBE_PATH` to the full executable path.
2. Place `ffprobe.exe` beside the packaged application.
3. Place a packaged runtime under `ffmpeg/bin` or `tools/ffmpeg/bin`.
4. Add FFmpeg's `bin` directory to the Windows `PATH`.

Verify in PowerShell:

```powershell
ffprobe -version
```

## Validation and safety

- Only explicitly supported filename extensions enter the probe workflow.
- Paths are normalized and checked for existence, file type, readability, nonzero size, and a default 200 GiB safety limit.
- A successful extension check is not trusted as proof of media validity; FFprobe must decode container metadata and report at least one audio stream.
- The source file is never modified or copied.
- FFprobe receives the path as a dedicated subprocess argument, preventing shell command injection.
- Import has a 45-second probe timeout and surfaces decoder diagnostics without exposing a Python traceback.

## Run

```powershell
.\\.venv\\Scripts\\Activate.ps1
python main.py
```

Select **File > Import Media**, press **Ctrl+O**, or choose **Import Media** in Studio. The UI displays an indeterminate progress indicator while inspection runs. A valid source appears in Project Media, metadata appears in Properties, and the Studio preview displays its name, dimensions, duration, and container.

## Test

```powershell
python -m pytest
python -m ruff check .
python -m mypy app
```

Unit coverage includes extension/empty-file validation, FFprobe payload mapping, duration/size formatting, and model deduplication. Existing integration tests continue to verify application composition and UI construction.

## Expected errors

- **FFprobe Required**: install FFmpeg or configure `KAS_FFPROBE_PATH`.
- **Unsupported file type**: select one of the product's supported formats.
- **No decodable audio stream**: the file is not a usable karaoke source.
- **Inspection exceeded 45 seconds**: the source may be remote, damaged, or unusually complex.
- **File could not be recognized**: inspect the FFprobe detail in the dialog and rotating application log.
