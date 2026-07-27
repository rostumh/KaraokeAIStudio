$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot;Set-Location $Root
& .\scripts\fetch_runtime_dependencies.ps1
& .\.venv\Scripts\python.exe packaging\generate_assets.py
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean packaging\KaraokeAIStudio.spec
$Runtime=Join-Path $Root "dist\KaraokeAIStudio\runtime\ffmpeg\bin";New-Item $Runtime -ItemType Directory -Force|Out-Null
Copy-Item "runtime\ffmpeg\bin\*.exe" $Runtime -Force
$Models=Join-Path $Root "dist\KaraokeAIStudio\models";New-Item $Models -ItemType Directory -Force|Out-Null;Copy-Item "models\model-catalog.json" $Models -Force
$Compiler=(Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source
$Candidates=@(
  $Compiler,
  (Join-Path $env:ProgramFiles "Inno Setup 7\ISCC.exe"),
  (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 7\ISCC.exe"),
  (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 7\ISCC.exe")
)
$Compiler=$Candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if(-not $Compiler){throw "Inno Setup Compiler 7 was not found. Install Inno Setup 7 and retry."}
& $Compiler "packaging\inno\KaraokeAIStudio.iss"
$Setup=Join-Path $Root "dist\installer\KaraokeAIStudioSetup.exe"
if(-not(Test-Path $Setup)){throw "Setup.exe was not created."}
Write-Host "One-click installer created: $Setup" -ForegroundColor Green
