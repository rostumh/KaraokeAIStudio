from __future__ import annotations
import re
from pathlib import Path
from app.domain.models.video_render import VideokePresentation
class VideokeAssComposer:
    """Adds a collision-free title card, lyric-timed countdown and CTA."""
    @staticmethod
    def _t(seconds:float)->str:
        cs=round(max(0,seconds)*100);h,r=divmod(cs,360000);m,r=divmod(r,6000);s,c=divmod(r,100);return f'{h}:{m:02d}:{s:02d}.{c:02d}'
    @staticmethod
    def _seconds(value:str)->float:
        h,m,s=value.split(':');return int(h)*3600+int(m)*60+float(s)
    @staticmethod
    def _esc(text:str)->str:return text.replace('\\','\\\\').replace('{','\\{').replace('}','\\}').replace('\n',' ')
    def compose(self,source:Path,destination:Path,p:VideokePresentation,song_duration:float)->Path:
        lines=source.read_text(encoding='utf-8-sig').splitlines();event_index=lines.index('[Events]');format_index=event_index+1
        while format_index<len(lines) and not lines[format_index].startswith('Format:'):format_index+=1
        header=lines[:format_index+1];events=lines[format_index+1:];styles_at=header.index('[Events]')
        title_size=max(150,p.title_font_size);credit_size=max(64,round(title_size*.46))
        header[styles_at:styles_at]=[
          f'Style: Title,{p.font_name},{title_size},&H00FFFFFF,&H0000FFFF,&H00101010,&H70000000,-1,0,0,0,100,100,0,0,1,8,3,5,100,100,0,1',
          f'Style: Credit,{p.font_name},{credit_size},&H00FFFFFF,&H0000FFFF,&H00101010,&H70000000,0,0,0,0,100,100,0,0,1,5,2,5,100,100,0,1',
          f'Style: Countdown,{p.font_name},190,&H0000D5FF,&H0000FFFF,&H00101010,&H40000000,-1,0,0,0,100,100,0,0,1,7,3,5,50,50,0,1',
          f'Style: CTA,{p.font_name},76,&H00FFFFFF,&H0000FFFF,&H00101010,&H50000000,-1,0,0,0,100,100,0,0,1,5,2,5,50,50,0,1']
        meta=[]
        lyric_events=[e for e in events if e.startswith('Dialogue:')]
        first_lyric=self._seconds(lyric_events[0].split(',',3)[1]) if lyric_events else 7.0
        count=max(1,p.countdown_start) if p.countdown_enabled else 0
        countdown_start=max(0.8,first_lyric-count) if count else first_lyric
        td=max(0.8,countdown_start-.20)
        # Explicit 4K-safe positions prevent title/artist/songwriter collisions.
        if p.title:meta.append(f'Dialogue: 5,{self._t(0)},{self._t(td)},Title,,0,0,0,,{{\\an5\\pos(960,425)\\fad(450,450)}}{self._esc(p.title)}')
        if p.artist:meta.append(f'Dialogue: 5,{self._t(.5)},{self._t(td)},Credit,,0,0,0,,{{\\an5\\pos(960,540)\\fad(450,450)}}{self._esc(p.artist)}')
        if p.songwriter:meta.append(f'Dialogue: 5,{self._t(.8)},{self._t(td)},Credit,,0,0,0,,{{\\an5\\pos(960,610)\\fs58\\fad(450,450)}}Songwriter: {self._esc(p.songwriter)}')
        if p.release_year:meta.append(f'Dialogue: 5,{self._t(.4)},{self._t(td)},Credit,,0,0,0,,{{\\an9\\pos(1780,75)\\fs64\\fad(350,350)}}{self._esc(p.release_year)}')
        # Legacy fixed schedule: count=3;step=1.0 and start=td+1.0+i*step. Runtime below intelligently targets first lyric.
        if p.countdown_enabled:
            count=max(1,p.countdown_start);available=max(0.0,first_lyric-td-.10);count=(min(count,int(available)) if lyric_events else count)
            if count:
                step=min(1.0,available/count);start=first_lyric-count*step
                for i,n in enumerate(range(count,0,-1)):
                    a=start+i*step;tag='\\fad(100,150)\\t(0,650,\\fscx130\\fscy130)'
                    meta.append(f'Dialogue: 6,{self._t(a)},{self._t(min(first_lyric,a+step))},Countdown,,0,0,0,,{{{tag}}}{n}')
        # No secondary Preview events: one authoritative karaoke subtitle layer only.
        cta_start=song_duration+p.cta_delay;cta_end=cta_start+p.cta_duration
        if p.cta_text:meta.append(f'Dialogue: 7,{self._t(cta_start)},{self._t(cta_end)},CTA,,0,0,0,,{{\\fad(600,800)}}{self._esc(p.cta_text)}')
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text('\n'.join(header+events+meta)+'\n',encoding='utf-8');return destination
