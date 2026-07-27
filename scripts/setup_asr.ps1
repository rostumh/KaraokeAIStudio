$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path .\.venv\Scripts\python.exe)) { throw "Run scripts\setup_windows.ps1 first." }
& .\.venv\Scripts\python.exe -m pip install -r requirements-asr.txt
& .\.venv\Scripts\python.exe -c "from faster_whisper import WhisperModel; print('Faster Whisper ready')"
Write-Host "ASR setup complete. Models download on first use." -ForegroundColor Green
