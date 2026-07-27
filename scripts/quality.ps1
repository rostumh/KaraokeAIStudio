$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
& .\.venv\Scripts\python.exe -m ruff check .
& .\.venv\Scripts\python.exe -m mypy app
& .\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
