# Module 1 — Project Planning and Initial Setup

## Deliverables

This module establishes the repository, package metadata, Clean Architecture boundaries, application composition root, typed JSON configuration, environment override, Windows-safe runtime paths, bounded rotating logs, dark PySide6 startup shell, automated tests, linting, static typing, and setup scripts.

## Design decisions

Python 3.12 is the recommended development interpreter because it offers a mature package ecosystem while remaining compatible with current Qt, PyTorch, and PyInstaller lines. The package accepts 3.11 through 3.14, but later AI modules may narrow the range if upstream Whisper or Demucs wheels require it.

Heavy media and AI dependencies are deliberately not installed in Module 1. They will be pinned in dedicated dependency groups when their integration code and hardware tests are introduced. This reduces setup failures and keeps the foundational CI fast.

## Run

From PowerShell at the repository root:

```powershell
.\scripts\setup_windows.ps1
.\.venv\Scripts\Activate.ps1
python main.py
```

## Test and inspect quality

```powershell
.\scripts\quality.ps1
```

Tests cover configuration merge/validation, first-run configuration creation, runtime directory creation, and composition-root startup using Qt's offscreen backend.

## Operational output

On first launch, the app creates per-user directories. Logs rotate at 5 MiB and retain five backups by default. The UI opens at 1280×800 with a 960×600 minimum and a status of `Ready`.

## Troubleshooting

- **`py.exe` not found**: install 64-bit Python 3.12 and enable the Python Launcher.
- **PowerShell blocks scripts**: execute `Set-ExecutionPolicy -Scope Process Bypass` in the same terminal.
- **Qt platform plugin error**: delete `.venv`, rerun setup, and do not mix global Qt packages with the virtual environment.
- **Invalid settings error**: correct or remove the per-user `settings.json`; the app recreates it from validated defaults.
- **No log file**: the rotating handler opens lazily; start the app and inspect the per-user log directory reported at startup.

## Completion criteria

Module 1 is complete when setup succeeds, all tests pass, linting and type checks pass, and the dark application shell opens without writing into the source tree.
