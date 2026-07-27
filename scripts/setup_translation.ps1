$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path .\.venv\Scripts\python.exe)) { throw "Run scripts\setup_windows.ps1 first." }
& .\.venv\Scripts\python.exe -m pip install -r requirements-translation.txt
& .\.venv\Scripts\python.exe -c "import argostranslate; print('Argos Translate ready')"
Write-Host "Translation runtime installed. Install .argosmodel packages from the Translation dialog." -ForegroundColor Green
