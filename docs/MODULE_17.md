# Module 17 — Export Profiles

Module 17 adds reusable rendering presets. Four immutable built-in profiles cover 720p preview, standard 1080p, 1080p60 high motion, and 4K HEVC master delivery. Users can create persistent profiles, and enabled Module 16 plugins can contribute validated profile metadata.

Profiles configure codec, container, preferred encoder, resolution, frame rate, quality, and AAC bitrate. Selecting a profile in the video-render dialog applies all values consistently while leaving media paths and overwrite choice untouched. User profiles are atomically stored under the application data directory in `export-profiles.json`.
