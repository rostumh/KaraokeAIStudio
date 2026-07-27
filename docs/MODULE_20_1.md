# Module 20.1 — Model Download Compatibility Fix

Fixes first-launch model provisioning for Hugging Face repositories where Git-managed files expose a 40-character SHA-1 ETag while LFS model files expose a 64-character SHA-256 ETag. Both checksum forms are now validated. Verified sidecar markers permit subsequent offline launches without contacting the model server. The PyInstaller project-root error and Inno Setup discovery paths are also corrected.
