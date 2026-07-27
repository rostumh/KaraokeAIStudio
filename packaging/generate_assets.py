from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)


def render(size: tuple[int, int], name: str) -> None:
    image = Image.new("RGBA", size, (18, 23, 38, 255))
    draw = ImageDraw.Draw(image)
    scale = min(size)
    cx, cy = size[0] // 2, size[1] // 2
    radius = max(4, int(scale * 0.25))
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(0, 215, 255, 255))
    bar = max(2, int(scale * 0.07))
    draw.rounded_rectangle((cx-bar, cy-radius, cx+bar, cy+radius), radius=bar, fill=(255,255,255,255))
    draw.arc((cx-radius*2, cy-radius, cx+radius*2, cy+radius*2), 15, 165, fill=(255,255,255,255), width=max(2,bar//2))
    image.save(ASSETS / name)


for size, name in [((44,44),"Square44x44Logo.png"),((150,150),"Square150x150Logo.png"),((310,310),"Square310x310Logo.png"),((310,150),"Wide310x150Logo.png"),((50,50),"StoreLogo.png")]:
    render(size, name)
render((256,256), "AppIcon.png")
Image.open(ASSETS / "AppIcon.png").save(ASSETS / "KaraokeAIStudio.ico", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
