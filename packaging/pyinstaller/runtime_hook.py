import os,sys
from pathlib import Path
if getattr(sys,"frozen",False):
    root=Path(sys.executable).resolve().parent
    os.environ.setdefault("KAS_FFMPEG_PATH",str(root/"runtime"/"ffmpeg"/"bin"/"ffmpeg.exe"))
    os.environ.setdefault("KAS_FFPROBE_PATH",str(root/"runtime"/"ffmpeg"/"bin"/"ffprobe.exe"))
