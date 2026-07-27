$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
$Cache=Join-Path $Root "build\downloads";New-Item $Cache -ItemType Directory -Force|Out-Null
$Url="https://github.com/GyanD/codexffmpeg/releases/download/8.1.2/ffmpeg-8.1.2-essentials_build.zip"
$Sha="db580001caa24ac104c8cb856cd113a87b0a443f7bdf47d8c12b1d740584a2ec"
$Zip=Join-Path $Cache "ffmpeg.zip"
Invoke-WebRequest $Url -OutFile $Zip
if((Get-FileHash $Zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Sha){Remove-Item $Zip;throw "FFmpeg checksum mismatch."}
$Extract=Join-Path $Cache "ffmpeg";Remove-Item $Extract -Recurse -Force -ErrorAction SilentlyContinue;Expand-Archive $Zip $Extract
$Target=Join-Path $Root "runtime\ffmpeg\bin";New-Item $Target -ItemType Directory -Force|Out-Null
$Bin=Get-ChildItem $Extract -Recurse -Filter ffmpeg.exe|Select-Object -First 1
$Probe=Get-ChildItem $Extract -Recurse -Filter ffprobe.exe|Select-Object -First 1
Copy-Item $Bin.FullName $Target;Copy-Item $Probe.FullName $Target
Write-Host "Verified FFmpeg runtime staged." -ForegroundColor Green
