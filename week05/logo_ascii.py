# /// script
# dependencies = ["ascii-magic==2.7.5", "Pillow>=11,<13"]
# ///
"""Turn a local mark into text, a frame-sequence GIF, and a browser slider."""

import argparse
import hashlib
import json
from pathlib import Path

from ascii_magic import AsciiArt
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
WIDTHS = tuple(range(12, 67, 6))
CHARACTERS = '@%#*+=-:. '
BACKGROUND = '#FAF8F4'
INK = '#000B1C'
SIZE = (640, 560)
MONO_FONT = HERE / 'assets/DejaVuSansMono.ttf'


def mono_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(MONO_FONT), size)


def prepare_source(source: Path, out: Path) -> Path:
    with Image.open(source) as original:
        original = original.convert('RGBA')
        white = Image.new('RGBA', original.size, 'white')
        white.alpha_composite(original)
        image = white.convert('RGB')
    # The package maps almost-white (254) to a visible dot; make paper truly white.
    paper = ImageOps.grayscale(image).point(lambda value: 255 if value >= 245 else 0)
    image.paste('white', mask=paper)
    # Ignore light paper/grid lines when locating the mark; retain a little margin.
    dark = ImageOps.grayscale(image).point(lambda value: 255 if value < 150 else 0)
    bounds = dark.getbbox()
    if bounds:
        left, top, right, bottom = bounds
        pad = max(10, int(max(right - left, bottom - top) * .12))
        image = image.crop((max(0, left - pad), max(0, top - pad),
                            min(image.width, right + pad), min(image.height, bottom + pad)))
    tile = ImageOps.contain(image, (600, 600), Image.Resampling.LANCZOS)
    square = Image.new('RGB', (600, 600), 'white')
    square.paste(tile, ((600 - tile.width) // 2, (600 - tile.height) // 2))
    dest = out / 'source-crop.png'
    square.save(dest)
    return dest


def render_frame(text: str, columns: int) -> Image.Image:
    rows = text.rstrip('\n').split('\n')
    occupied = [row for row in rows if row.strip()]
    left = min((len(row) - len(row.lstrip()) for row in occupied), default=0)
    right = max((len(row.rstrip()) for row in occupied), default=0)
    rows = [row[left:right] for row in rows]
    while rows and not rows[0].strip():
        rows.pop(0)
    while rows and not rows[-1].strip():
        rows.pop()
    longest = right - left
    image = Image.new('RGB', SIZE, BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.text((24, 16), f'{columns} columns / {len(rows)} rows', fill=INK,
              font=ImageFont.load_default(size=20))
    for size in range(54, 9, -1):
        font = mono_font(size)
        char_width = font.getlength('M')
        line_height = size * 1.25
        if longest * char_width <= SIZE[0] - 48 and len(rows) * line_height <= SIZE[1] - 125:
            break
    first_x = (SIZE[0] - longest * char_width) / 2
    first_y = 76 + (SIZE[1] - 170 - len(rows) * line_height) / 2
    for index, row in enumerate(rows):
        draw.text((first_x, first_y + index * line_height), row, fill=INK, font=font)
    draw.text((24, 530), 'Source: local ASCII / no model', fill=INK,
              font=ImageFont.load_default(size=16))
    return image


def make_html(frames: list[dict]) -> str:
    # JSON is data, not markup; prevent an unusual character sequence closing this script tag.
    encoded = json.dumps(frames, ensure_ascii=True).replace('<', '\\u003c')
    return '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>One mark, several text widths</title>
<style>
:root { --ink:#000b1c; --paper:#faf8f4; --accent:#ed6d24; }
* { box-sizing:border-box } body { margin:0; background:var(--paper); color:var(--ink);
  font:18px Georgia,serif; } main { max-width:1100px; margin:auto; padding:clamp(18px,4vw,60px) }
h1 { font-size:clamp(2rem,5vw,4rem); line-height:1; margin:.3em 0 }
small, label, button { font:14px 'Courier New',monospace; text-transform:uppercase; letter-spacing:.04em }
p { max-width:65ch; line-height:1.5 } .panels { display:grid; grid-template-columns:1fr 1.7fr;
  gap:22px; margin:28px 0 } .panel { min-width:0; border:1px solid #bdc0bf; padding:16px;
  background:white } .panel img { display:block; max-width:100%; max-height:470px; margin:auto }
pre { margin:0; min-height:470px; max-width:100%; overflow:auto; white-space:pre;
  font:15px/1.25 monospace; color:var(--ink) }
.controls { display:flex; flex-wrap:wrap; align-items:center; gap:14px; margin:20px 0 }
input[type=range] { width:min(380px,65vw); accent-color:var(--accent) }
button { padding:12px 18px; background:var(--ink); color:white; border:0; cursor:pointer }
button:focus-visible, input:focus-visible { outline:3px solid var(--accent); outline-offset:3px }
a { color:#99421e } @media(max-width:700px) { .panels { grid-template-columns:1fr }
  pre { min-height:250px; font-size:13px } }
</style>
<main><small>SD5913 / 8 October 2026 / local ASCII</small><h1>One mark. Several resolutions.</h1>
<p>The source on the left is a pixel image. The text on the right is computed locally by Python and
ascii-magic. Move the slider to inspect an exact text frame. Play runs those frames in sequence;
it does not invent new pixels or send your image to a service.</p>
<div class="panels"><div class="panel"><small>Original (cropped)</small><img src="source-crop.png" alt="Cropped source mark"></div>
<div class="panel"><small>Text frame · swipe sideways to inspect dense frames</small><pre id="frame" aria-label="ASCII rendering"></pre></div></div>
<div class="controls"><label for="width">Columns: <output id="count">36</output></label>
<input id="width" type="range" min="0" max="9" value="4" step="1" aria-label="Text columns">
<button id="play" type="button" aria-pressed="false">Play</button>
<a href="logo-resolution.gif">Open frame-sequence GIF</a><a href="avatar-square.png">Square icon</a></div>
<p>Try 12 columns, then 66. Which parts of the mark disappear? A larger character grid
cannot restore details the source never contained.</p></main>
<script>
const frames = ''' + encoded + ''';
const slider = document.getElementById('width');
const output = document.getElementById('count');
const picture = document.getElementById('frame');
const button = document.getElementById('play');
let playing = false, direction = 1;
function draw() {
  const frame = frames[Number(slider.value)];
  output.textContent = String(frame.columns);
  picture.textContent = frame.text;
  slider.setAttribute('aria-valuetext', frame.columns + ' columns');
}
function state(next) {
  playing = next;
  button.textContent = next ? 'Pause' : 'Play';
  button.setAttribute('aria-pressed', String(next));
}
slider.addEventListener('input', () => { state(false); draw(); });
button.addEventListener('click', () => state(!playing));
setInterval(() => {
  if (!playing) return;
  let next = Number(slider.value) + direction;
  if (next >= frames.length || next < 0) { direction *= -1; next = Number(slider.value) + direction; }
  slider.value = String(next); draw();
}, 650);
draw();
if (!matchMedia('(prefers-reduced-motion: reduce)').matches) state(true);
</script></html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, default=HERE / 'assets/mark-18.png')
    parser.add_argument('--output-dir', type=Path, default=HERE / 'out')
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f'Image not found: {args.image}')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cropped = prepare_source(args.image, args.output_dir)
    art = AsciiArt.from_image(str(cropped))
    frames = [{'columns': columns,
               'text': art.to_ascii(columns=columns, char=CHARACTERS, width_ratio=1.5)}
              for columns in WIDTHS]
    data = {'source_sha256': hashlib.sha256(args.image.read_bytes()).hexdigest(),
            'frames': frames}
    (args.output_dir / 'frames.json').write_text(json.dumps(data, indent=2) + '\n')
    (args.output_dir / 'logo-ascii.html').write_text(make_html(frames))
    (args.output_dir / 'logo-ascii.txt').write_text(frames[4]['text'])
    images = [render_frame(frame['text'], frame['columns']) for frame in frames]
    images[4].save(args.output_dir / 'ascii-frame.png')
    avatar = Image.new('RGB', (640, 640), BACKGROUND)
    avatar.paste(images[4].crop((0, 0, 640, 500)), (0, 70))
    avatar.save(args.output_dir / 'avatar-square.png')
    sequence = images + images[-2:0:-1]
    sequence[0].save(args.output_dir / 'logo-resolution.gif', save_all=True,
                     append_images=sequence[1:], duration=650, loop=0, disposal=2)
    print(f'Open {args.output_dir / "logo-ascii.html"} (slider), '
          f'{args.output_dir / "logo-resolution.gif"} (animation).')


if __name__ == '__main__':
    main()
