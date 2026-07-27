# Auto Pipeline 0.21.2

The Windows build now installs and freezes Faster Whisper, CTranslate2, PyAV, tokenizers, Hugging Face Hub and ONNX Runtime. Build packaging fails if the frozen Whisper or CTranslate2 packages are absent. Runtime startup reports the specific missing or damaged component instead of a generic engine-unavailable message. Demucs, Whisper, automatic language detection, transcript persistence, word alignment and review chaining remain automatic.
