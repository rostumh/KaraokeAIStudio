# Karaoke AI Studio Plugin SDK 1.0

Plugins are installed Python distributions discovered from the `karaoke_ai_studio.plugins` entry-point group. The entry point must resolve to a zero-argument factory or object implementing `KaraokeStudioPlugin`. New plugins are disabled until explicitly enabled and require restart after state changes.

```toml
[project.entry-points."karaoke_ai_studio.plugins"]
my-plugin = "my_plugin:Plugin"
```

A plugin descriptor must use API version `1.0`, a lowercase namespaced ID, and only declared capabilities. SDK 1.0 supports `export_profiles` and `translation_labels`. The host provides a restricted context with only contribution registration methods; it exposes no window, model, subprocess, credential, or filesystem service.

Plugins execute in-process and are not a security sandbox. Users must install only trusted, signed, reviewed distributions. One plugin load failure is isolated and displayed without preventing other plugins or the host from starting.
