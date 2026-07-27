from app.domain.models.transcription import WhisperDevice
from app.infrastructure.ai.faster_whisper_recognizer import FasterWhisperRecognizer
def test_cpu_coerces_unsupported_float16_to_int8():assert FasterWhisperRecognizer._resolve_compute("cpu","float16")=="int8"
def test_clock_formats_minutes():assert FasterWhisperRecognizer._clock(125)=="02:05"
