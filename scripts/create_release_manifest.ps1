param(
  [Parameter(Mandatory=$true)][string]$PackagePath,
  [Parameter(Mandatory=$true)][string]$DownloadUrl,
  [Parameter(Mandatory=$true)][string]$ReleaseNotesUrl,
  [ValidateSet("stable","beta")][string]$Channel="stable"
)
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
$Python=Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $PackagePath)) { throw "Package not found: $PackagePath" }
$Version=(& $Python -c "import sys;sys.path.insert(0,r'$Root');import app;print(app.__version__)").Trim()
$Hash=(Get-FileHash $PackagePath -Algorithm SHA256).Hash.ToLowerInvariant()
$Item=Get-Item $PackagePath
$Manifest=[ordered]@{schema_version=1;version=$Version;channel=$Channel;published_utc=(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ");download_url=$DownloadUrl;sha256=$Hash;size_bytes=$Item.Length;release_notes_url=$ReleaseNotesUrl;minimum_version="0.18.0"}
$Path=Join-Path $Item.DirectoryName "$($Item.BaseName).update.json"
$Manifest|ConvertTo-Json|Set-Content $Path -Encoding UTF8
Write-Host "Update manifest created: $Path" -ForegroundColor Green
