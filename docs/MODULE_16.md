# Module 16 — Plugin System

Module 16 adds installed-distribution plugin discovery using Python package entry points. Plugins are disabled by default, validated against API 1.0, isolated individually during discovery, and activated with a restricted contribution context. Supported contributions are export-profile metadata and translation-language labels. Enable/disable changes are persisted atomically and take effect after restart.

Open the **Plugins** workspace to review provider, version, status, capabilities, and failures. Plugin code runs in the main process and is not sandboxed; install only trusted distributions. See `PLUGIN_SDK.md` for the entry-point declaration and contract.
