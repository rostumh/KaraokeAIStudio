$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path .\.venv\Scripts\python.exe)) { throw "Run scripts\setup_windows.ps1 first." }
& .\.venv\Scripts\python.exe -m pip install --upgrade torch torchaudio --index-url https://download.pytorch.org/whl/cpu
& .\.venv\Scripts\python.exe -m pip install -r requirements-ai.txt
& .\.venv\Scripts\python.exe -c "import torch, demucs; print('PyTorch', torch.__version__, 'CUDA', torch.cuda.is_available()); print('Demucs ready')"
