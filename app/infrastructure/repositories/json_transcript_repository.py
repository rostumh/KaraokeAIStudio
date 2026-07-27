from __future__ import annotations

import json,os
from dataclasses import asdict
from pathlib import Path
from app.domain.models.transcription import Transcript


class JsonTranscriptRepository:
    """Atomic UTF-8 persistence for canonical JSON and readable text transcripts."""
    def save(self,transcript:Transcript,destination:Path)->tuple[Path,Path]:
        stem=transcript.source_path.stem
        json_path=destination/f"{stem}.transcript.json";text_path=destination/f"{stem}.transcript.txt"
        payload=asdict(transcript);payload["source_path"]=str(transcript.source_path);payload["options"]["device"]=transcript.options.device.value;payload["options"]["task"]=transcript.options.task.value
        self._atomic_write(json_path,json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
        lines=[f"[{self._time(s.start_seconds)} --> {self._time(s.end_seconds)}] {s.text}" for s in transcript.segments]
        self._atomic_write(text_path,"\n".join(lines)+"\n")
        return json_path,text_path
    @staticmethod
    def _atomic_write(path:Path,content:str)->None:
        temporary=path.with_name(path.name+".part");temporary.write_text(content,encoding="utf-8",newline="\n");os.replace(temporary,path)
    @staticmethod
    def _time(seconds:float)->str:
        millis=round(max(0,seconds)*1000);hours,rem=divmod(millis,3600000);minutes,rem=divmod(rem,60000);secs,ms=divmod(rem,1000);return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"
