# Module 7 — Whisper Speech Recognition

Module 7 adds local multilingual speech recognition using Faster Whisper/CTranslate2. It supports automatic language detection, explicit language hints, original-language transcription, translation to English, VAD, beam search, initial prompts, CPU/CUDA selection, quantized compute, cancellable background processing, segment timestamps, confidence metadata, atomic JSON/TXT persistence, and Lyrics Editor integration.

## Install

```powershell
.\scripts\setup_windows.ps1
.\scripts\setup_asr.ps1
```

Models download on first use to the per-user application cache. CPU `int8` is the compatibility default. CUDA requires compatible CUDA 12 cuBLAS and cuDNN 9 libraries for current CTranslate2 releases.

## Use

Import and select a vocal stem or original song, then choose **AI > Transcribe Lyrics…** or press **Ctrl+Shift+T**. For best lyric accuracy, transcribe the Demucs `vocals` stem. Select model, device, compute type, language, task, beam size, VAD, context, and optional vocabulary prompt. Results are stored in `exports/transcripts` as canonical JSON and human-readable TXT, then displayed in Lyrics Editor.

Word-level alignment is deliberately reserved for Module 8. Module 7 persists accurate segment timing and all recognition metadata needed by that alignment stage.
