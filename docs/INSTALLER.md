# Windows Installer Build

Module 19 produces a Windows x64 one-folder application using PyInstaller and can wrap that layout in MSIX. Windows builds must run on Windows because PyInstaller is not a cross-compiler.

## Portable folder

```powershell
.\scripts\build_windows_package.ps1 -Format Folder
```

## Signed MSIX

Install the Windows SDK so `makeappx.exe` and `signtool.exe` are available. Use a code-signing certificate whose subject exactly matches the manifest publisher.

```powershell
.\scripts\build_windows_package.ps1 `
  -Format MSIX `
  -Publisher "CN=Your Verified Publisher" `
  -PublisherDisplayName "Your Publisher Name" `
  -CertificateThumbprint "CERTIFICATE_THUMBPRINT"
```

The script runs tests, creates assets, builds the PyInstaller folder, signs and verifies the executable when a certificate is supplied, creates the MSIX layout, builds MSIX, then signs and verifies the package. It never creates or exports a production private key.

Generate the Module 18 release manifest after signing:

```powershell
.\scripts\create_release_manifest.ps1 `
  -PackagePath .\dist\KaraokeAIStudio-0.19.0-x64.msix `
  -DownloadUrl "https://downloads.example.com/KaraokeAIStudio-0.19.0-x64.msix" `
  -ReleaseNotesUrl "https://example.com/releases/0.19.0"
```

Test the signed package with Windows App Certification Kit on clean supported Windows hardware before publication. Store publication is preferred for consumer distribution; enterprise sideloading requires a certificate trusted on target devices.
