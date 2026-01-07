from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out = Path("resources")
out.mkdir(parents=True, exist_ok=True)
ico_path = out / "icon.ico"

# 이미지 생성
size = 256
img = Image.new("RGBA", (size, size), (52, 152, 219, 255))
draw = ImageDraw.Draw(img)

# 원형 배경
draw.ellipse((16, 16, size - 16, size - 16), fill=(255, 255, 255, 64))

# 텍스트 'CT'
try:
    # 시스템 폰트 사용 시도
    font = ImageFont.truetype("arial.ttf", 140)
except Exception:
    font = ImageFont.load_default()

text = "CT"
bbox = draw.textbbox((0, 0), text, font=font)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
draw.text(((size - w) / 2, (size - h) / 2), text, fill=(255, 255, 255, 255), font=font)

# Save as ICO (Pillow supports .ico)
img.save(ico_path, format="ICO")

print(f"아이콘을 생성했습니다: {ico_path}")