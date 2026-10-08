# /// script
# dependencies = ["Pillow>=11,<13"]
# ///
"""Make three still frames and save them as a looping GIF."""

from pathlib import Path

from PIL import Image, ImageDraw

POSITIONS = (8, 26, 44)
DURATION_MS = 200

out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)

frames = []
for x in POSITIONS:
    frame = Image.new("RGB", (64, 48), "white")
    draw = ImageDraw.Draw(frame)
    draw.ellipse((x, 18, x + 12, 30), fill=(232, 120, 53))
    frames.append(frame)

frames[0].save(
    out / "moving-dot.gif", save_all=True,
    append_images=frames[1:], duration=DURATION_MS, loop=0,
)
print("saved", len(frames), "frames to", out / "moving-dot.gif")
