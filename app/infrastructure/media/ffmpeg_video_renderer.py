from __future__ import annotations

import logging, os, subprocess, time
from pathlib import Path
from threading import Event
from app.application.errors import MediaImportError
from app.application.ports.video_renderer import RenderProgress
from app.domain.models.video_render import RenderEncoder,VideoCodec,VideoRenderRequest,VideoRenderResult
from app.infrastructure.media.ffmpeg_audio_extractor import ExtractionCancelledError
from app.infrastructure.subtitles.videoke_composer import VideokeAssComposer
LOGGER=logging.getLogger(__name__)


class FFmpegVideoRenderer:
    """FFmpeg/libass renderer with encoder discovery, progress, cancellation, and atomic output."""
    def __init__(self,executable:Path)->None:self._executable=executable;self._encoders=self._discover_encoders()
    def available_encoders(self)->tuple[str,...]:return tuple(sorted(self._encoders))
    def render(self,request:VideoRenderRequest,progress:RenderProgress,cancel_event:Event)->VideoRenderResult:
        self._validate_inputs(request)
        encoder=self._select_encoder(request);temporary=request.output_path.with_name(request.output_path.stem+".part"+request.output_path.suffix);temporary.unlink(missing_ok=True);process=None;started=time.monotonic()
        try:
            if request.presentation is not None:
                composed=request.output_path.with_name(request.output_path.stem+"_presentation.ass")
                VideokeAssComposer().compose(request.subtitle_path,composed,request.presentation,request.duration_seconds)
                from dataclasses import replace
                request=replace(request,subtitle_path=composed,duration_seconds=request.duration_seconds+request.presentation.cta_delay+request.presentation.cta_duration)
            command=self._command(request,temporary,encoder);LOGGER.info("FFmpeg command prepared with %d arguments",len(command));LOGGER.debug("FFmpeg command: %r",command);LOGGER.info("Starting video render encoder=%s output=%s",encoder,request.output_path)
            process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace",creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0));assert process.stdout is not None
            while True:
                if cancel_event.is_set():
                    process.terminate()
                    try:process.wait(timeout=5)
                    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
                    raise ExtractionCancelledError("Video rendering was cancelled.")
                line=process.stdout.readline()
                if line:
                    key,sep,value=line.strip().partition("=")
                    if sep and key in {"out_time_us","out_time_ms"}:
                        try: numeric=int(value or 0)
                        except (TypeError,ValueError): numeric=0
                        ratio=min(.99,max(0,numeric/max(1,round(request.duration_seconds*1_000_000))));progress(ratio,f"Rendering {ratio*100:.0f}%")
                    elif key=="progress" and value=="end":progress(1,"Render complete")
                if process.poll() is not None:break
                if not line:time.sleep(.02)
            errors=process.stderr.read().splitlines() if process.stderr else []
            if process.returncode!=0:
                detail=" | ".join(line.strip() for line in errors[-6:] if line.strip()) or "Unknown FFmpeg error"
                raise MediaImportError(f"Video rendering failed: {detail}")
            if not temporary.is_file() or temporary.stat().st_size==0:raise MediaImportError("FFmpeg did not produce a valid video file.")
            if request.output_path.exists():
                if not request.overwrite:raise MediaImportError(f"The output file already exists: {request.output_path}")
                request.output_path.unlink()
            os.replace(temporary,request.output_path);elapsed=time.monotonic()-started;LOGGER.info("Video render completed in %.2fs",elapsed);return VideoRenderResult(request.output_path,request.output_path.stat().st_size,elapsed,encoder)
        except Exception:
            if process is not None and process.poll() is None:process.kill();process.wait(timeout=3)
            temporary.unlink(missing_ok=True);LOGGER.exception("Video render did not complete");raise
    def _discover_encoders(self)->set[str]:
        result=subprocess.run([str(self._executable),"-hide_banner","-encoders"],capture_output=True,text=True,encoding="utf-8",errors="replace",creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0),check=False)
        names={"libx264","libx265","h264_nvenc","hevc_nvenc","h264_qsv","hevc_qsv","h264_amf","hevc_amf"};return {name for name in names if name in result.stdout}
    def _select_encoder(self,request:VideoRenderRequest)->str:
        prefix="h264" if request.codec==VideoCodec.H264 else "hevc"
        candidates={RenderEncoder.SOFTWARE:"libx264" if prefix=="h264" else "libx265",RenderEncoder.NVIDIA:f"{prefix}_nvenc",RenderEncoder.INTEL:f"{prefix}_qsv",RenderEncoder.AMD:f"{prefix}_amf"}
        selected=candidates[request.encoder]
        if selected not in self._encoders:raise MediaImportError(f"Requested FFmpeg encoder '{selected}' is unavailable in this build or on this system.")
        return selected
    @staticmethod
    def _validate_inputs(request:VideoRenderRequest)->None:
        missing=[]
        if not request.audio_path.is_file():missing.append(f"Instrumental audio: {request.audio_path}")
        if not request.subtitle_path.is_file():missing.append(f"ASS subtitles: {request.subtitle_path}")
        if str(request.background_path) != "__generated_aurora__" and not request.background_path.is_file():missing.append(f"Background: {request.background_path}")
        if request.watermark_path is not None and not request.watermark_path.is_file():missing.append(f"Watermark: {request.watermark_path}")
        if request.frame_rate not in {24,25,30,50,60}:raise MediaImportError(f"Frame rate {request.frame_rate} is unsupported. Choose 30 fps (recommended).")
        if request.width<320 or request.height<240:raise MediaImportError('Resolution is invalid. Choose a named resolution preset.')
        if missing:raise MediaImportError("Render input file is missing. " + " | ".join(missing))
        request.output_path.parent.mkdir(parents=True,exist_ok=True)

    def _command(self,request:VideoRenderRequest,temporary:Path,encoder:str)->list[str]:
        subtitle=self._escape_filter_path(request.subtitle_path)
        filters=[f"scale={request.width}:{request.height}:force_original_aspect_ratio=decrease",f"pad={request.width}:{request.height}:(ow-iw)/2:(oh-ih)/2:black","setsar=1"]
        if request.presentation and request.presentation.ambient_motion:filters.append(f"zoompan=z='min(zoom+0.00015,1.08)':d=1:s={request.width}x{request.height}:fps={request.frame_rate}")
        filters.append(f"ass='{subtitle}'")
        if request.watermark_text:
            text=self._escape_drawtext(request.watermark_text);positions={'bottom-right':('w-tw-30','h-th-30'),'bottom-left':('30','h-th-30'),'top-right':('w-tw-30','30'),'top-left':('30','30'),'center':('(w-tw)/2','(h-th)/2')};x,y=positions.get(request.watermark_position,positions['bottom-right']);alpha=max(.1,min(1,request.watermark_opacity/100));filters.append(f"drawtext=text='{text}':fontcolor=white@{alpha:.2f}:fontsize=h/32:borderw=2:bordercolor=black@0.65:x={x}:y={y}")
        base_filter=','.join(part for part in filters if part.strip())
        if str(request.background_path) == "__generated_aurora__":
            # The gradients source is not included in every bundled Windows FFmpeg build
            # and its expression options differ across versions. A color source is part
            # of the core lavfi set and is therefore a reliable, portable input.
            source=f"color=c=0x061126:s={request.width}x{request.height}:r={request.frame_rate}:d={request.duration_seconds:.3f}"
            dynamic=r"drawbox=x=mod(t*95\,w+900)-900:y=h*0.05:w=900:h=h*0.9:color=0x6b3cff@0.32:t=fill,drawbox=x=w-mod(t*70\,w+760):y=h*0.18:w=760:h=h*0.7:color=0x00d9ff@0.28:t=fill,drawbox=x=mod(t*45\,w+620)-620:y=h*0.42:w=620:h=h*0.5:color=0xff3d9a@0.20:t=fill,gblur=sigma=95,hue=h=18*sin(t/4):s=1.25,eq=contrast=1.12:saturation=1.2"
            filters.insert(0,dynamic)
            command=[str(self._executable),"-hide_banner","-nostdin","-loglevel","error","-y","-f","lavfi","-i",source,"-i",str(request.audio_path)]
        else:
            command=[str(self._executable),"-hide_banner","-nostdin","-loglevel","error","-y","-stream_loop","-1","-i",str(request.background_path),"-i",str(request.audio_path)]
        if request.watermark_path is not None:
            command.extend(("-i",str(request.watermark_path)))
            positions={"bottom-right":"W-w-30:H-h-30","bottom-left":"30:H-h-30","top-right":"W-w-30:30","top-left":"30:30","center":"(W-w)/2:(H-h)/2"};xy=positions.get(request.watermark_position,positions["bottom-right"]);opacity=max(.1,min(1,request.watermark_opacity/100))
            command.extend(("-filter_complex",f"[0:v]{base_filter}[base];[2:v]format=rgba,colorchannelmixer=aa={opacity}[wm];[base][wm]overlay={xy}[v]","-map","[v]","-map","1:a:0"))
        else: command.extend(("-map","0:v:0","-map","1:a:0","-vf",base_filter))
        command.extend(("-r",str(request.frame_rate),"-c:v",encoder))
        if encoder in {"libx264","libx265"}:command.extend(("-preset","fast","-crf",str(request.quality)))
        elif encoder.endswith("_nvenc"):command.extend(("-preset","p5","-cq",str(request.quality),"-b:v","0"))
        elif encoder.endswith("_qsv"):command.extend(("-preset","medium","-global_quality",str(request.quality)))
        else:command.extend(("-quality","balanced","-rc","cqp","-qp_i",str(request.quality),"-qp_p",str(request.quality)))
        command.extend(("-pix_fmt","yuv420p","-af",f"highpass=f=28,equalizer=f=250:t=q:w=1:g=-1.2,acompressor=threshold=-16dB:ratio=2.2:attack=18:release=220,loudnorm=I=-14:LRA=9:TP=-1.0,alimiter=limit=0.95,apad=whole_dur={request.duration_seconds:.3f}","-t",f"{request.duration_seconds:.3f}","-c:a","aac","-b:a",f"{request.audio_bitrate_kbps}k","-ar","48000","-movflags","+faststart","-progress","pipe:1",str(temporary)))
        return command
    @staticmethod
    def _escape_drawtext(text:str)->str:return text.replace('\\','\\\\').replace("'","\\'").replace(':','\\:').replace('%','\\%').replace('\n',' ' )[:120]
    @staticmethod
    def _escape_filter_path(path:Path)->str:return str(path.resolve()).replace("\\","/").replace(":","\\:").replace("'","\\'")
