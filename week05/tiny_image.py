# /// script
# dependencies = ["Pillow>=11,<13"]
# ///
"""Enlarge four RGB pixels without blending their colours."""

from pathlib import Path

from PIL import Image

out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)

pixels = [
    [(255, 0, 0), (0, 255, 0)],
    [(0, 0, 255), (255, 255, 0)],
]
# Try: pixels[0][1] = (255, 255, 255) before putting the values into the image.
image = Image.new("RGB", (2, 2))
image.putdata([pixel for row in pixels for pixel in row])
image.resize((120, 120), Image.Resampling.NEAREST).save(out / "tiny-image.png")
print("saved", out / "tiny-image.png")
