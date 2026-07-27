$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
Set-Location (Split-Path -Parent $PSScriptRoot)

function Invoke-Checked {
    param([Parameter(Mandatory=$true)][scriptblock]$Command, [Parameter(Mandatory=$true)][string]$Step)
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "$Step failed with exit code $LASTEXITCODE. Setup stopped; no build should be created." }
}

$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) { throw "Python Launcher (py.exe) was not found. Install 64-bit Python 3.12 from python.org." }
Invoke-Checked { py -3.12 -m venv .venv } "Creating Python environment"
$venv = ".\\.venv\\Scripts\\python.exe"
Invoke-Checked { & $venv -m pip install --upgrade pip setuptools wheel } "Updating build tools"
Invoke-Checked { & $venv -m pip install -r requirements-dev.txt } "Installing application dependencies"
Write-Host "Installing the built-in CPU vocal separation engine..." -ForegroundColor Cyan
Invoke-Checked { & $venv -m pip install --upgrade torch torchaudio --index-url https://download.pytorch.org/whl/cpu } "Installing PyTorch"
Invoke-Checked { & $venv -m pip install "demucs>=4.1,<5" SoundFile } "Installing Demucs"
Write-Host "Installing the built-in CPU Whisper lyric engine..." -ForegroundColor Cyan
Invoke-Checked { & $venv -m pip install -r requirements-asr.txt } "Installing Whisper"
Invoke-Checked { & $venv -c "import torch, torchaudio, demucs, faster_whisper, ctranslate2, av, tokenizers, onnxruntime; print('AI engines ready:', torch.__version__, faster_whisper.__version__, ctranslate2.__version__)" } "Validating AI engines"
Invoke-Checked { & $venv -m pytest -q } "Automated test suite"
Write-Host "Setup complete: all tests passed. Run: .\\.venv\\Scripts\\Activate.ps1; python main.py" -ForegroundColor Green
