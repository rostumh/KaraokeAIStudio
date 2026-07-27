# Module 20 — One-Click Windows Setup

Module 20 supersedes source-based end-user installation. The public artifact is `KaraokeAIStudioSetup.exe`, built from a PyInstaller one-folder application and wrapped by Inno Setup. The setup wizard installs per user by default, supports a custom folder, creates Start Menu and optional Desktop shortcuts, registers a complete uninstaller, and launches the app on Finish.

The build pipeline downloads a pinned FFmpeg 8.1.2 essentials archive, verifies its published SHA-256, and bundles `ffmpeg.exe` plus `ffprobe.exe`. First launch detects and verifies the pinned Faster Whisper Tiny model. Missing files download over HTTPS with Range resume, progress, remote SHA-256 metadata verification, and atomic `.part` promotion. No terminal, Python, FFmpeg, Git, CUDA, environment variable, or manual configuration is required on the end-user PC.
