from app.infrastructure.ai.faster_whisper_word_aligner import FasterWhisperWordAligner
def test_cpu_compute_fallback():assert FasterWhisperWordAligner._resolve_compute("cpu","float16")=="int8"
def test_clock():assert FasterWhisperWordAligner._clock(185)=="03:05"
