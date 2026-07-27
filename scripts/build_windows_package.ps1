param(
  [ValidateSet("Folder", "MSIX")][string]$Format = "Folder",
  [string]$Publisher = "CN=Karaoke AI Studio Development",
  [string]$PublisherDisplayName = "Karaoke AI Studio",
  [string]$CertificateThumbprint = "",
  [string]$TimestampUrl = "http://timestamp.acs.microsoft.com"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw "Run scripts\setup_windows.ps1 first." }
& $Python -m pip install -e ".[dev]"
& $Python packaging\generate_assets.py
& $Python -m pytest -q
& $Python -m PyInstaller --noconfirm --clean packaging\KaraokeAIStudio.spec
$AppExe = Join-Path $Root "dist\KaraokeAIStudio\KaraokeAIStudio.exe"
if (-not (Test-Path $AppExe)) { throw "PyInstaller did not create KaraokeAIStudio.exe." }
$AsrProbe = Join-Path $Root "dist\KaraokeAIStudio\WhisperProbe.exe"
if (-not (Test-Path (Join-Path $Root "dist\KaraokeAIStudio\_internal\faster_whisper"))) { throw "Frozen package is missing faster_whisper." }
if (-not (Test-Path (Join-Path $Root "dist\KaraokeAIStudio\_internal\ctranslate2"))) { throw "Frozen package is missing CTranslate2." }
Write-Host "Verified bundled Whisper and CTranslate2 runtime." -ForegroundColor Green
if ($CertificateThumbprint) {
  & signtool.exe sign /sha1 $CertificateThumbprint /fd SHA256 /tr $TimestampUrl /td SHA256 $AppExe
  & signtool.exe verify /pa /v $AppExe
}
if ($Format -eq "Folder") {
  Write-Host "Portable application created: dist\KaraokeAIStudio" -ForegroundColor Green
  exit 0
}
$Version = (& $Python -c "import app; print(app.__version__)").Trim()
$Version4 = (& $Python -c "from app.infrastructure.packaging.windows_package import msix_version; print(msix_version('$Version'))").Trim()
$Layout = Join-Path $Root "build\msix-layout"
Remove-Item $Layout -Recurse -Force -ErrorAction SilentlyContinue
New-Item (Join-Path $Layout "KaraokeAIStudio") -ItemType Directory -Force | Out-Null
New-Item (Join-Path $Layout "Assets") -ItemType Directory -Force | Out-Null
Copy-Item "dist\KaraokeAIStudio\*" (Join-Path $Layout "KaraokeAIStudio") -Recurse -Force
Copy-Item "packaging\assets\*.png" (Join-Path $Layout "Assets") -Force
$Manifest = (Get-Content "packaging\AppxManifest.xml.in" -Raw).Replace("__PUBLISHER__",$Publisher).Replace("__PUBLISHER_DISPLAY_NAME__",$PublisherDisplayName).Replace("__VERSION4__",$Version4)
Set-Content (Join-Path $Layout "AppxManifest.xml") $Manifest -Encoding UTF8
$Package = Join-Path $Root "dist\KaraokeAIStudio-$Version-x64.msix"
Remove-Item $Package -Force -ErrorAction SilentlyContinue
& makeappx.exe pack /d $Layout /p $Package /o
if (-not $CertificateThumbprint) { throw "MSIX was built but is unsigned. Re-run with -CertificateThumbprint for an installable package." }
& signtool.exe sign /sha1 $CertificateThumbprint /fd SHA256 /tr $TimestampUrl /td SHA256 $Package
& signtool.exe verify /pa /v $Package
Write-Host "Signed MSIX created: $Package" -ForegroundColor Green
