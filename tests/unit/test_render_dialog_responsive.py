from pathlib import Path
from app.domain.models.video_render import VideokePresentation

def test_dialog_scroll_and_fixed_buttons():
 s=Path('app/ui/dialogs/video_render_dialog.py').read_text();assert 'QScrollArea' in s and 'layout.addWidget(scroll,1)' in s and 'layout.addWidget(self.buttons)' in s
def test_clear_resolution_presets_and_1080p_default():
 s=Path('app/ui/dialogs/video_render_dialog.py').read_text()
 for label in ('4K UHD - Computer / TV','Vertical Full HD - TikTok / Reels / Shorts','Vertical HD - Social Media Lite','Vertical 4K - TikTok / Reels / Shorts'):assert label in s
 assert 'self.resolution.setCurrentIndex(1)' in s
def test_adjustable_countdown_fields():
 s=Path('app/ui/dialogs/video_render_dialog.py').read_text()
 assert 'Countdown animation' in s and 'Countdown duration' not in s and 'Countdown starts at' not in s
 p=VideokePresentation(countdown_start=3,countdown_duration=6,countdown_style='fade');assert (p.countdown_start,p.countdown_duration,p.countdown_style)==(3,6,'fade')

def test_composer_uses_selected_countdown_start(tmp_path):
 from app.infrastructure.subtitles.videoke_composer import VideokeAssComposer
 base='[Script Info]\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Karaoke,Arial,78,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,40,40,150,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
 src=tmp_path/'i.ass';out=tmp_path/'o.ass';src.write_text(base)
 VideokeAssComposer().compose(src,out,VideokePresentation(countdown_start=3,countdown_duration=6,countdown_style='fade'),20)
 text=out.read_text();assert text.count('Dialogue: 6')==3 and '}3' in text and '}1' in text
