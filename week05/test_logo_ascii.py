# /// script
# dependencies = ["ascii-magic==2.7.5", "Pillow>=11,<13"]
# ///
"""Run with: uv run test_logo_ascii.py"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from logo_ascii import mono_font

ROOT = Path(__file__).resolve().parent


class LogoAsciiTests(unittest.TestCase):
    def test_gif_uses_a_fixed_width_font(self):
        font = mono_font(24)
        advances = {round(font.getlength(char), 2) for char in 'Mi @.%'}
        self.assertEqual(len(advances), 1, 'ASCII spacing requires equal glyph advances')

    def test_local_outputs_are_valid_and_consistent(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            source = home / 'logo.png'
            image = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
            pen = ImageDraw.Draw(image)
            pen.ellipse((35, 25, 125, 115), fill='#182b33')
            pen.line((85, 108, 120, 150), fill='#182b33', width=8)
            image.save(source)
            out = home / 'out'
            subprocess.run([sys.executable, str(ROOT / 'logo_ascii.py'),
                            '--image', str(source), '--output-dir', str(out)],
                           check=True, capture_output=True, text=True)
            data = json.loads((out / 'frames.json').read_text())
            widths = [frame['columns'] for frame in data['frames']]
            self.assertEqual(widths, list(range(12, 67, 6)))
            for frame in data['frames']:
                self.assertAlmostEqual(len(frame['text'].splitlines()),
                                       frame['columns'] / 1.5, delta=2)
            self.assertTrue(all(frame['text'].strip() for frame in data['frames']))
            self.assertTrue(all('\x1b[' not in frame['text'] for frame in data['frames']))
            self.assertEqual(len(data['source_sha256']), 64)
            html = (out / 'logo-ascii.html').read_text()
            self.assertNotIn('clamp(5px', html)
            self.assertIn('white-space:pre', html)
            self.assertIn('type="range"', html)
            self.assertIn('textContent', html)
            self.assertNotIn('innerHTML', html)
            self.assertIn('prefers-reduced-motion', html)
            with Image.open(out / 'logo-resolution.gif') as animation:
                self.assertGreaterEqual(animation.n_frames, 10)
                self.assertEqual(animation.size, (640, 560))
            with Image.open(out / 'ascii-frame.png') as frame:
                self.assertEqual(frame.size, (640, 560))
            with Image.open(out / 'source-crop.png') as cropped:
                self.assertEqual(cropped.size[0], cropped.size[1])


if __name__ == '__main__':
    unittest.main()
