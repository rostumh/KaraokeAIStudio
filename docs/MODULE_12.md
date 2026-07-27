# Module 12 — Video Rendering

Module 12 renders a final karaoke video from a looping background, instrumental audio, and generated ASS subtitle file. The FFmpeg pipeline scales and letterboxes the background, renders ASS through libass, encodes H.264 or HEVC, encodes AAC audio, reports progress, supports cancellation, validates output, and atomically promotes a `.part` video.

Supported software encoders are libx264/libx265. When present in the active FFmpeg build, the UI exposes NVIDIA NVENC, Intel Quick Sync, and AMD AMF. Encoder availability is discovered with `ffmpeg -encoders`; unavailable hardware encoders are never offered. MP4 and MKV, 720p/1080p/4K, and 24/25/30/50/60 fps are supported.

Use **File > Render Karaoke Video…** or Ctrl+Alt+R. Select a background, cleaned instrumental, generated ASS, destination, codec, encoder, resolution, frame rate, quality, and audio bitrate.
