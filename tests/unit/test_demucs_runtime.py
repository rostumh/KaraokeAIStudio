from pathlib import Path
from app.domain.models.separation import ComputeDevice,SeparationMode,SeparationRequest,StemFormat
from app.infrastructure.ai.demucs_runtime import DemucsSourceSeparator
def test_command_uses_two_stem_quality_and_resource_options(tmp_path):
 runtime=object.__new__(DemucsSourceSeparator); runtime._python=Path("python"); runtime._runner=None
 request=SeparationRequest(tmp_path/"song.wav",tmp_path/"out","htdemucs",SeparationMode.VOCALS,ComputeDevice.CPU,StemFormat.WAV_24,2,.25,10)
 command=runtime._command(request,"cpu")
 assert command[0:3]==["python","-m","demucs"]
 assert "--two-stems" in command and "vocals" in command and "--int24" in command and "--segment" in command
