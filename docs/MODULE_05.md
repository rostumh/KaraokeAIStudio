# Module 5 — Demucs Vocal Separation

Module 5 adds asynchronous AI source separation through Demucs. It supports the balanced `htdemucs` and slower fine-tuned `htdemucs_ft` models, two-stem vocals/instrumental output, full four-stem output, CPU or CUDA device selection, 24-bit WAV or FLAC stems, configurable shifts, overlap, segmentation, cancellation, output validation, logging, and automatic import of every generated stem.

## Install

Run the normal setup first. For CPU AI dependencies:

```powershell
.\scripts\setup_ai_cpu.ps1
```

For NVIDIA acceleration, use the current command produced by the official PyTorch selector for Windows/Pip/your CUDA platform, then run:

```powershell
python -m pip install -r requirements-ai.txt
```

Do not install both CPU and CUDA PyTorch wheels. The first Demucs run downloads the selected model into the user's PyTorch cache and therefore requires network access. Later runs use the cache.

## Workflow

Import media, select it in Project Media, and choose **AI > Separate Vocals…**. Select model, output mode, device, stem format, shifts, overlap, and segment length. The output is written under the per-user exports directory in `stems/MODEL/TRACK`. Completed stem files are queued through the existing Module 3 import workflow. The import controller serializes the queue so all stems are probed without launching overlapping FFprobe workers.

## Resource guidance

CUDA is selected automatically when PyTorch reports it available. CPU remains supported but is slower. Lower segment length reduces peak GPU memory. More shifts can improve stabilization but increase processing time. The fine-tuned model performs multiple model passes and is materially slower.

## Safety and reliability

Demucs runs in an isolated child process so cancellation and GPU-memory recovery are more reliable than running inference inside the GUI process. Output files must exist and be nonempty before success is reported. The process receives an explicit argument vector without a command shell. Shutdown cancels active work and waits for the worker.

## Test

```powershell
python -m pytest
python -m ruff check .
python -m mypy app
```
