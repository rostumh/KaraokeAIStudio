from __future__ import annotations
import re
from app.domain.models.lyrics_document import EditableWord,LyricsDocument
from .models import LyricsResult
_TIME=re.compile(r'^\[(\d{1,3}):(\d{2})(?:[.:](\d{1,3}))?\]\s*(.*)$')
_TAG=re.compile(r'^\[[a-z]+:.*\]$',re.I)
class LyricsReviewDocumentBuilder:
    """Makes online lyrics immediately editable/continuable without invoking Whisper."""
    def build(self,result:LyricsResult)->LyricsDocument:
        duration=max(1.0,result.song.duration_seconds);lines=[]
        for raw in result.lyrics.splitlines():
            m=_TIME.match(raw.strip())
            if m:
                fraction=float('0.'+(m.group(3) or '0'));lines.append((int(m.group(1))*60+int(m.group(2))+fraction,m.group(4).strip()))
            elif raw.strip() and not _TAG.match(raw.strip()):lines.append((None,raw.strip()))
        words=[]
        if result.synchronized and any(t is not None for t,_ in lines):
            timed=[(t,text) for t,text in lines if t is not None and text]
            for segment,(start,text) in enumerate(timed):
                end=timed[segment+1][0] if segment+1<len(timed) else duration
                self._append(words,segment,text,start,max(start+.2,end))
        else:
            text_lines=[text for _,text in lines if text];span=duration/max(1,len(text_lines))
            for segment,text in enumerate(text_lines):self._append(words,segment,text,segment*span,(segment+1)*span)
        return LyricsDocument(result.song.media_path or result.source_path,result.song.language or 'und',duration,tuple(words),0)
    @staticmethod
    def _append(out,segment,text,start,end):
        tokens=text.split();step=max(.05,(end-start)/max(1,len(tokens)))
        for token in tokens:
            i=len(out);a=start+(i-sum(1 for w in out if w.segment_id<segment))*step
            out.append(EditableWord(i,segment,token,a,min(end,a+step),1.0))
