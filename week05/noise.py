# /// script
# dependencies = ["Pillow>=11,<13"]
# ///
"""Generate repeatable RGB noise with Python's random module."""

import random
from pathlib import Path

from PIL import Image

WIDTH = 256
HEIGHT = 256
SEED = 7

out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)

rng = random.Random(SEED)
pixels = [(rng.randrange(256), rng.randrange(256), rng.randrange(256))
          for _ in range(WIDTH * HEIGHT)]
image = Image.new("RGB", (WIDTH, HEIGHT))
image.putdata(pixels)
image.save(out / "noise.png")
print(image.size, image.mode, "saved", out / "noise.png")
