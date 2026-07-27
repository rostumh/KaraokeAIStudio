from pathlib import Path
from app.domain.models.instrumental_cleanup import CleanupOutputFormat,CleanupPreset,CleanupSettings,InstrumentalCleanupRequest
from app.infrastructure.media.ffmpeg_instrumental_cleaner import FFmpegInstrumentalCleaner
def request(tmp_path):return InstrumentalCleanupRequest(tmp_path/"in.wav",tmp_path/"out.wav",0,60,CleanupSettings(CleanupPreset.BALANCED,10,-50,30,19000,-16,-1.5,9,True,CleanupOutputFormat.WAV_24),False)
def test_filter_chain_contains_denoise_loudness_and_limiter(tmp_path):
 cleaner=FFmpegInstrumentalCleaner(Path("ffmpeg"));chain=cleaner._filter_chain(request(tmp_path));assert "afftdn=" in chain and "loudnorm=" in chain and "alimiter=" in chain
def test_command_maps_stream_and_writes_pcm24(tmp_path):
 cleaner=FFmpegInstrumentalCleaner(Path("ffmpeg"));command=cleaner._command(request(tmp_path),tmp_path/"out.part");assert command[command.index("-map")+1]=="0:0" and "pcm_s24le" in command and "pipe:1" in command
