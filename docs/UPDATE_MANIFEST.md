# Update Manifest Schema 1

The updater reads a small UTF-8 JSON document from the HTTPS URL configured in `KAS_UPDATE_MANIFEST_URL`.

```json
{
  "schema_version": 1,
  "version": "0.19.0",
  "channel": "stable",
  "published_utc": "2026-08-01T00:00:00Z",
  "download_url": "https://downloads.example.com/KaraokeAIStudio-0.19.0.msix",
  "sha256": "64 lowercase hexadecimal characters",
  "size_bytes": 12345678,
  "release_notes_url": "https://example.com/releases/0.19.0",
  "minimum_version": "0.18.0"
}
```

Manifest, package, and release-notes URLs must use HTTPS and cannot contain embedded credentials. The package size is limited to 2 GiB and must exactly match both the manifest and HTTP response. Supported package suffixes are `.msix`, `.msi`, `.exe`, and `.zip`.
