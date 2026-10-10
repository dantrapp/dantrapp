#!/usr/bin/env python3
"""Render the four README contribution diagrams with Pillow."""

import argparse
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, SCALE = 480, 240, 2
FPS, PERIOD = 20, 20
BACKGROUND = (32, 35, 33)
FOREGROUND = (245, 243, 237)
KINDS = ("vmaf", "ion", "pyrefly", "spicedb")
OFFSETS = dict(zip(KINDS, (0, 4, 8, 12)))
RECORD = '{ id: 42, name: "ion" }'
FONT_CANDIDATES = {
    "serif": (
        "/System/Library/Fonts/Supplemental/Iowan Old Style.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ),
    "sans": (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ),
    "mono": (
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ),
}


def shade(amount):
    return tuple(round(a + (b - a) * amount) for a, b in zip(BACKGROUND, FOREGROUND))


def smoothstep(value):
    value = max(0, min(value, 1))
    return value * value * (3 - 2 * value)


def state_at(kind, seconds):
    phase = round((seconds - OFFSETS[kind]) % PERIOD, 9) % PERIOD
    if phase < 0.8 or phase >= 3.8:
        return 2.4, 1.0
    if phase < 1.1:
        return 2.4, 1 - smoothstep((phase - 0.8) / 0.3)
    if phase < 1.4:
        return 0.0, smoothstep((phase - 1.1) / 0.3)
    return phase - 1.4, 1.0


@lru_cache(maxsize=None)
def load_font(path, size):
    return ImageFont.truetype(str(path), size * SCALE)


class Canvas:
    def __init__(self, fonts):
        self.fonts = fonts
        self.image = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), BACKGROUND)
        self.draw = ImageDraw.Draw(self.image)

    def font(self, role, size):
        return load_font(self.fonts[role], size)

    def text_width(self, content, size=20, role="sans"):
        return self.draw.textlength(content, font=self.font(role, size)) / SCALE

    def text(self, x, y, content, size=20, role="sans", ink=1.0):
        font = self.font(role, size)
        box = self.draw.textbbox((x * SCALE, y * SCALE), content, font=font, anchor="lt")
        assert box[0] >= 0 and box[1] >= 0 and box[2] <= WIDTH * SCALE and box[3] <= HEIGHT * SCALE, (content, box)
        self.draw.text((x * SCALE, y * SCALE), content, font=font, fill=shade(ink), anchor="lt")

    def right_text(self, x, y, content, **kwargs):
        width = self.text_width(content, kwargs.get("size", 20), kwargs.get("role", "sans"))
        self.text(x - width, y, content, **kwargs)

    def rectangle(self, box, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        assert 0 <= x0 <= x1 <= WIDTH and 0 <= y0 <= y1 <= HEIGHT, box
        self.draw.rectangle(
            tuple(round(point * SCALE) for point in box),
            fill=None if fill is None else shade(fill),
            outline=None if outline is None else shade(outline),
            width=width * SCALE,
        )

    def line(self, points, ink=0.25, width=1):
        assert all(0 <= x <= WIDTH and 0 <= y <= HEIGHT for x, y in points), points
        self.draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=shade(ink), width=width * SCALE)

    def heading(self, value, measure):
        self.text(24, 18, value, size=44, role="serif")
        self.text(25, 72, measure, size=20, ink=0.7)

    def footnote(self, content):
        self.text(25, 212, content, size=17, ink=0.6)


def video(canvas, elapsed, opacity):
    canvas.heading("2.10–2.73×", "full-model throughput")
    progress = min(1, elapsed / 2.4)
    for label, total, y, ink in (("Before", 10, 122, 0.45), ("After", 21, 167, 1.0)):
        canvas.text(25, y + 2, label, size=19, ink=0.7)
        for index in range(21):
            x = 106 + index * 14.5
            canvas.rectangle((x, y, x + 10.5, y + 25), outline=0.16)
            reveal = smoothstep((progress * total - index) * 2)
            if index < total and reveal > 0:
                color = ink * reveal * opacity
                canvas.rectangle((x, y, x + 10.5, y + 25), outline=color)
                canvas.line([(x + 2, y + 20), (x + 5, y + 12), (x + 8, y + 18)], ink=color * 0.7)
        canvas.right_text(456, y + 2, str(total), size=20, ink=ink)
    canvas.footnote("Equal elapsed time · 2.10× illustrated")


def parser(canvas, elapsed, opacity):
    canvas.heading("42%", "less time to read text records")
    for label, duration, y, ink in (("Before", 2.4, 124, 0.5), ("After", 2.4 * 0.58, 165, 1.0)):
        canvas.text(25, y + 1, label, size=19, ink=0.7)
        progress = min(1, elapsed / duration)
        unit = canvas.text_width("M", size=19, role="mono")
        for index, character in enumerate(RECORD):
            color = (ink if index < progress * len(RECORD) else 0.2) * opacity
            canvas.text(106 + index * unit, y, character, size=19, role="mono", ink=color)
        if 0 < progress < 1:
            cursor = 106 + progress * len(RECORD) * unit
            canvas.line([(cursor, y - 3), (cursor, y + 24)], ink=ink * opacity)
    canvas.footnote("Before = 100 · read 58 · scan 48")


def symbols(canvas, elapsed, opacity):
    canvas.heading("Symbol search", "instance attributes included")
    canvas.text(25, 111, "account.py · Account.__init__", size=17, ink=0.5)
    found = smoothstep((elapsed - 1.0) / 0.45) * opacity
    code = 'self.name = "Ada"'
    canvas.rectangle((23, 136, 152, 162), fill=found * 0.13)
    canvas.text(25, 139, code, size=22, role="mono", ink=0.8)
    canvas.line([(25, 162), (148, 162)], ink=0.55 * found)
    canvas.text(25, 179, "Before", size=17, ink=0.6)
    canvas.text(255, 179, "After", size=17, ink=0.6)
    canvas.text(25, 207, "No results", size=20, ink=0.45)
    if elapsed < 1.0:
        canvas.text(255, 207, "Searching…", size=20, ink=opacity * 0.5)
    else:
        canvas.text(255, 207, "Account.name", size=20, role="mono", ink=found)


def exclusions(canvas, elapsed, opacity):
    canvas.heading("87%", "lower p95 lookup latency")
    progress = smoothstep(elapsed / 1.6)
    for label, remaining, y in (("Latency", 13, 124), ("Allocation", 3, 167)):
        canvas.text(25, y + 1, label, size=18, ink=0.7)
        canvas.rectangle((126, y, 398, y + 5), fill=0.36)
        length = 272 * (1 - (1 - remaining / 100) * progress)
        canvas.rectangle((126, y + 14, 126 + length, y + 23), fill=opacity)
        canvas.right_text(456, y + 2, str(remaining), size=20)
    canvas.footnote("Before = 100 · after = 13 / 3")


DRAWERS = dict(zip(KINDS, (video, parser, symbols, exclusions)))


def render_at(kind, seconds, fonts):
    canvas = Canvas(fonts)
    DRAWERS[kind](canvas, *state_at(kind, seconds))
    return canvas.image


def palette_image():
    palette = Image.new("P", (1, 1))
    palette.putpalette([channel for level in range(256) for channel in shade(level / 255)])
    return palette


def render(kind, fonts, output):
    palette = palette_image()
    frames, durations = [], []
    previous_state = None
    for index in range(PERIOD * FPS):
        seconds = index / FPS
        state = state_at(kind, seconds)
        if state == previous_state:
            durations[-1] += 1000 // FPS
            continue
        frames.append(render_at(kind, seconds, fonts).quantize(palette=palette, dither=Image.Dither.NONE))
        durations.append(1000 // FPS)
        previous_state = state
    frames[0].save(
        output / f"{kind}.gif", save_all=True, append_images=frames[1:],
        duration=durations, loop=0, disposal=1, optimize=False,
    )
    render_at(kind, OFFSETS[kind] + 5, fonts).save(output / f"{kind}.png", optimize=True)


def verify(kind, fonts, output):
    for seconds in (0, 0.3, 1.0, 2.7, 3.8, 5, 19.95):
        assert render_at(kind, seconds, fonts).tobytes() == render_at(kind, seconds + PERIOD, fonts).tobytes(), (kind, "loop seam")
    image = Image.open(output / f"{kind}.gif")
    assert image.size == (WIDTH * SCALE, HEIGHT * SCALE)
    assert image.info.get("loop") == 0
    assert 1 < image.n_frames <= PERIOD * FPS
    elapsed = 0
    palette = palette_image()
    for index in range(image.n_frames):
        image.seek(index)
        duration = image.info["duration"]
        assert duration > 0 and duration % 10 == 0
        expected = render_at(kind, elapsed / 1000, fonts).quantize(palette=palette, dither=Image.Dither.NONE).convert("RGB")
        assert image.convert("RGB").tobytes() == expected.tobytes(), (kind, "encoded frame", index, elapsed)
        elapsed += duration
    assert elapsed == PERIOD * 1000, (kind, elapsed)
    poster = Image.open(output / f"{kind}.png")
    assert poster.size == image.size
    assert poster.tobytes() == render_at(kind, OFFSETS[kind] + 5, fonts).tobytes()
    print(f"{kind}: {image.width}×{image.height}, {image.n_frames} encoded frames, {elapsed} ms, {(output / f'{kind}.gif').stat().st_size:,} bytes; bounds, frames and seam passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify existing exports without changing them")
    parser.add_argument("--output", type=Path, default=ROOT / "assets" / "contributions")
    for role in FONT_CANDIDATES:
        parser.add_argument(f"--{role}", type=Path, help=f"Path to the {role} font")
    args = parser.parse_args()
    fonts = {}
    for role, candidates in FONT_CANDIDATES.items():
        fonts[role] = getattr(args, role) or next((Path(path) for path in candidates if Path(path).is_file()), None)
        if fonts[role] is None or not fonts[role].is_file():
            parser.error(f"Supply an installed font with --{role}")
    args.output.mkdir(parents=True, exist_ok=True)
    for kind in KINDS:
        if not args.check:
            render(kind, fonts, args.output)
        verify(kind, fonts, args.output)


if __name__ == "__main__":
    main()
