# /// script
# dependencies = ["numpy>=2,<3", "Pillow>=11,<13"]
# ///
"""Compare NumPy's row/column/channel shape with Pillow's size and modes."""

from pathlib import Path

import numpy as np
from PIL import Image

out = Path(__file__).resolve().parent / "out"
out.mkdir(exist_ok=True)

pixels = np.zeros((100, 100, 3), dtype=np.uint8)
pixels[:50, :50] = [255, 0, 0]
image = Image.fromarray(pixels)
gray = image.convert("L")
print(pixels.shape, pixels.dtype)
print(image.size, image.mode, gray.mode)
image.save(out / "array-image.png")
gray.save(out / "array-gray.png")
print("saved", out / "array-image.png", "and", out / "array-gray.png")
