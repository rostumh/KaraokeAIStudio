from pathlib import Path
from app.domain.models.video_render import VideokePresentation
from app.infrastructure.subtitles.videoke_composer import VideokeAssComposer
BASE='''[Script Info]\nScriptType: v4.00+\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Karaoke,Arial,78,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,40,40,150,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\nDialogue: 0,0:00:10.00,0:00:13.00,Karaoke,,0,0,0,,First line\nDialogue: 0,0:00:13.00,0:00:16.00,Karaoke,,0,0,0,,Next line\n'''
def test_composer_adds_title_countdown_preview_and_cta(tmp_path):
 src=tmp_path/'in.ass';src.write_text(BASE);out=tmp_path/'out.ass'
 VideokeAssComposer().compose(src,out,VideokePresentation(title='Sample',artist='Artist',songwriter='Writer',release_year='2026'),20)
 s=out.read_text();assert 'Sample' in s and 'Songwriter: Writer' in s and 'Dialogue: 6' in s and ',Preview,' not in s and 'Please Subscribe' in s
def test_render_dialog_exposes_configurable_videoke_fields():
 s=Path('app/ui/dialogs/video_render_dialog.py').read_text();
 for x in ('Song title','Songwriter credit','Release year','Title card','Countdown','End call-to-action','Background motion'):assert x in s
