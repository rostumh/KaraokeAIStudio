# Module 19 — Installer

Module 19 adds reproducible Windows packaging for Karaoke AI Studio 0.19.0. PyInstaller creates a one-folder x64 desktop application; MakeAppx wraps it in an MSIX package; SignTool signs and verifies the executable and package when a certificate thumbprint is supplied. The package declares Windows Desktop build 19041 or later and the restricted `runFullTrust` capability required for a packaged desktop executable.

Release automation generates all required visual assets, embeds Windows file-version metadata, validates the full test suite, creates a four-part MSIX version, and can create the exact SHA-256/size manifest consumed by Module 18. Production private keys are never stored in the repository. See `INSTALLER.md`.
