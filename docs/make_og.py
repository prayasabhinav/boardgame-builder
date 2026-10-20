"""Draw static/og.png (1200 × 630), the link-preview card, from docs/screenshot.jpg. Run from the repo root: python docs/make_og.py"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from site_config import TOOL_URL  # noqa: E402

W, H = 1200, 630
SURFACE, INK, BAR, ACCENT, BORDER = "#F7F3ED", "#2D3436", "#2D3436", "#4A8C5C", "#E5E2DF"
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEORGIA_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"

card = Image.new("RGB", (W, H), SURFACE)
d = ImageDraw.Draw(card)

# header bar, as on the page
d.rectangle([0, 0, W, 64], fill=BAR)
d.text((48, 23), "A PRAYAS ABHINAV TOOL", font=ImageFont.truetype(MONO, 16), fill="#FFFFFF")
site = "prayasabhinav.net"
mono16 = ImageFont.truetype(MONO, 16)
d.text((W - 48 - d.textlength(site, font=mono16), 23), site, font=mono16, fill="#B9C2C4")

# left: what it is
d.text((48, 120), "boardgameBuilder", font=ImageFont.truetype(GEORGIA_BOLD, 54), fill=INK)
body = ImageFont.truetype(GEORGIA, 28)
for i, line in enumerate(["Design a board game from blocks.", "Read what the combination", "tends to produce."]):
    d.text((48, 210 + i * 40), line, font=body, fill=INK)
d.rectangle([48, 352, 112, 356], fill=ACCENT)
small = ImageFont.truetype(MONO, 17)
for i, line in enumerate(["Includes blocks for serious games", "No AI at runtime · free · no login"]):
    d.text((48, 380 + i * 30), line, font=small, fill=ACCENT)
d.text((48, 540), TOOL_URL.split("//")[1], font=ImageFont.truetype(MONO, 22), fill=INK)

# right: the real screen, canvas and feedback
shot = Image.open("docs/screenshot.jpg").convert("RGB")
crop = shot.crop((440, 60, shot.width, shot.height))
fw = 560
crop = crop.resize((fw, round(crop.height * fw / crop.width)), Image.LANCZOS)
x, y = W - fw - 40, 104
d.rounded_rectangle([x - 6, y - 6, x + fw + 6, y + crop.height + 6], radius=10, fill="#FFFFFF", outline=BORDER, width=2)
card.paste(crop, (x, y))

card.save("static/og.png", optimize=True)
print("static/og.png", card.size)
