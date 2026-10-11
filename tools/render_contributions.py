#!/usr/bin/env python3
"""Render compact, transparent contribution animations for the profile README."""

import argparse
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, SCALE = 480, 120, 2
FPS, PERIOD = 20, 12
KINDS = ("vmaf", "ion", "pyrefly", "spicedb")
OFFSETS = dict(zip(KINDS, (0, 3, 6, 9)))
RECORD = '{id:42, name:"ion"}'
THEMES = {
    "light": {"background": (255, 255, 255), "foreground": (36, 41, 47), "accent": (36, 116, 87)},
    "dark": {"background": (13, 17, 23), "foreground": (230, 237, 243), "accent": (153, 216, 191)},
}
FONT_CANDIDATES = {
    "display": (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
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


def clamp(value):
    return max(0, min(value, 1))


def smoothstep(value):
    value = clamp(value)
    return value * value * (3 - 2 * value)


def mix(start, end, amount):
    return tuple(round(a + (b - a) * clamp(amount)) for a, b in zip(start, end))


def elapsed_at(kind, seconds):
    phase = round((seconds - OFFSETS[kind]) % PERIOD, 9) % PERIOD
    if phase < 0.5 or phase >= 3.4:
        return 2.4
    if phase < 0.8:
        return 2.4 * (1 - smoothstep((phase - 0.5) / 0.3))
    if phase < 1:
        return 0
    return round(phase - 1, 9)


@lru_cache(maxsize=None)
def load_font(path, size):
    return ImageFont.truetype(str(path), round(size * SCALE))


class Canvas:
    def __init__(self, fonts, theme):
        self.fonts = fonts
        self.theme = THEMES[theme]
        self.image = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), self.theme["background"])
        self.draw = ImageDraw.Draw(self.image)

    def color(self, ink=1, accent=False):
        return mix(self.theme["background"], self.theme["accent" if accent else "foreground"], ink)

    def font(self, role, size):
        return load_font(self.fonts[role], size)

    def text_width(self, content, size=16, role="sans"):
        return self.draw.textlength(content, font=self.font(role, size)) / SCALE

    def text(self, x, y, content, size=16, role="sans", ink=1, accent=False):
        font = self.font(role, size)
        box = self.draw.textbbox((x * SCALE, y * SCALE), content, font=font, anchor="lt")
        assert 0 <= box[0] <= box[2] <= WIDTH * SCALE and 0 <= box[1] <= box[3] <= HEIGHT * SCALE, (content, box)
        self.draw.text((x * SCALE, y * SCALE), content, font=font, fill=self.color(ink, accent), anchor="lt")

    def right_text(self, x, y, content, **kwargs):
        width = self.text_width(content, kwargs.get("size", 16), kwargs.get("role", "sans"))
        self.text(x - width, y, content, **kwargs)

    def rectangle(self, box, fill=None, outline=None, width=1, accent=False):
        x0, y0, x1, y1 = box
        assert 0 <= x0 <= x1 <= WIDTH and 0 <= y0 <= y1 <= HEIGHT, box
        self.draw.rectangle(
            tuple(round(point * SCALE) for point in box),
            fill=None if fill is None else self.color(fill, accent),
            outline=None if outline is None else self.color(outline, accent),
            width=round(width * SCALE),
        )

    def line(self, points, ink=0.25, width=1, accent=False):
        assert all(0 <= x <= WIDTH and 0 <= y <= HEIGHT for x, y in points), points
        self.draw.line(
            [(round(x * SCALE), round(y * SCALE)) for x, y in points],
            fill=self.color(ink, accent), width=round(width * SCALE),
        )

    def check(self, x, y, accent=False):
        self.line([(x, y + 5), (x + 4, y + 9), (x + 13, y)], ink=1, width=1.5, accent=accent)

    def metric(self, value, label, note=None):
        assert self.text_width(value, size=35, role="display") <= 115, value
        self.text(12, 31, value, size=35, role="display")
        self.text(14, 76, label, size=16, ink=0.72)
        if note:
            self.text(14, 100, note, size=12, ink=0.63)
        self.line([(134, 12), (134, 108)], ink=0.15)


def video(canvas, elapsed):
    canvas.metric("2.10×", "throughput", "equal elapsed time")
    progress = clamp(elapsed / 2.4)
    for label, total, x, accent in (("Before", 10, 152, False), ("After", 21, 320, True)):
        complete = min(total, int(progress * total + 1e-8))
        canvas.text(x, 14, label, size=16, ink=0.7)
        canvas.right_text(x + 134, 11, str(complete), size=21, role="mono", accent=accent)
        for index in range(21):
            left, top = x + index % 7 * 19, 43 + index // 7 * 22
            box = (left, top, left + 14, top + 16)
            canvas.rectangle(box, outline=0.15)
            if index < total:
                reveal = smoothstep(progress * total - index)
                if reveal:
                    canvas.rectangle(box, fill=0.12 * reveal, outline=0.85 * reveal, accent=accent)
                    canvas.line([(left + 3, top + 12), (left + 6, top + 7), (left + 10, top + 11)], ink=0.75 * reveal, accent=accent)


def parser(canvas, elapsed):
    canvas.metric("−42%", "read time", "scan time −52%")
    unit = canvas.text_width("M", size=22, role="mono")
    assert 156 + unit * len(RECORD) < 432
    for label, duration, y, accent in (("Before", 2.4, 13, False), ("After", 2.4 * 0.58, 66, True)):
        canvas.text(156, y, label, size=14, ink=0.7)
        progress = clamp(elapsed / duration)
        for index, character in enumerate(RECORD):
            parsed = index < int(progress * len(RECORD) + 1e-8)
            canvas.text(156 + index * unit, y + 22, character, size=22, role="mono", ink=0.9 if parsed else 0.3, accent=accent and parsed)
        if 0 < progress < 1:
            cursor = 156 + progress * len(RECORD) * unit
            canvas.line([(cursor, y + 19), (cursor, y + 43)], ink=1, width=1.5, accent=accent)
        if progress == 1:
            canvas.check(449, y + 27, accent=accent)


def symbols(canvas, elapsed):
    canvas.text(14, 16, "Account.__init__", size=14, role="mono", ink=0.7)
    canvas.line([(244, 12), (244, 108)], ink=0.15)
    query = "name"[:min(4, int(elapsed / 0.6 * 4))]
    found = elapsed >= 1.2
    highlight = smoothstep((elapsed - 1.2) / 0.35)
    attribute_width = canvas.text_width("self.name", size=21, role="mono")
    assert 14 + canvas.text_width('self.name = "Ada"', size=21, role="mono") < 236
    if highlight:
        canvas.rectangle((12, 50, 16 + attribute_width, 80), fill=0.12 * highlight, accent=True)
        canvas.line([(14, 80), (14 + attribute_width, 80)], ink=highlight, accent=True)
    canvas.text(14, 54, "self.name", size=21, role="mono", ink=0.88, accent=found)
    canvas.text(14 + attribute_width, 54, ' = "Ada"', size=21, role="mono", ink=0.75)
    canvas.text(14, 96, "instance attribute", size=13, ink=0.65)
    canvas.rectangle((263, 12, 466, 44), outline=0.23)
    canvas.draw.ellipse((273 * SCALE, 21 * SCALE, 283 * SCALE, 31 * SCALE), outline=canvas.color(0.65), width=SCALE)
    canvas.line([(282, 30), (287, 35)], ink=0.65)
    canvas.text(298, 19, query, size=18, role="mono", ink=0.9)
    if elapsed < 0.7:
        cursor = 298 + canvas.text_width(query, size=18, role="mono")
        canvas.line([(cursor, 19), (cursor, 37)], ink=0.7)
    if found:
        canvas.check(267, 67, accent=True)
        canvas.text(290, 61, "Account.name", size=18, role="mono", accent=True)
        canvas.text(290, 89, "1 result · line 3", size=13, ink=0.65)
    else:
        canvas.text(267, 61, "No results", size=18, ink=0.65)
        canvas.text(267, 89, "0 results", size=13, ink=0.65)


def exclusions(canvas, elapsed):
    canvas.metric("−87%", "p95 latency", "before = 100")
    progress = smoothstep(elapsed / 1.8)
    for label, remaining, y in (("Latency", 13, 12), ("Allocation", 3, 67)):
        current = round(100 - (100 - remaining) * progress)
        canvas.text(156, y, label, size=15, ink=0.72)
        canvas.right_text(466, y - 1, f"100 → {current}", size=17, role="mono", accent=True)
        canvas.rectangle((156, y + 26, 466, y + 29), fill=0.3)
        canvas.rectangle((156, y + 36, 156 + 310 * current / 100, y + 43), fill=1, accent=True)


DRAWERS = dict(zip(KINDS, (video, parser, symbols, exclusions)))


def render_at(kind, seconds, fonts, theme):
    canvas = Canvas(fonts, theme)
    DRAWERS[kind](canvas, elapsed_at(kind, seconds))
    return canvas.image


@lru_cache(maxsize=None)
def palette_image(theme):
    colors = THEMES[theme]
    palette = Image.new("P", (1, 1))
    shades = [colors["background"]]
    shades += [mix(colors["background"], colors["foreground"], level / 127) for level in range(1, 128)]
    shades += [mix(colors["background"], colors["accent"], level / 128) for level in range(1, 129)]
    palette.putpalette([channel for color in shades for channel in color])
    return palette


def indexed(image, theme):
    result = image.quantize(palette=palette_image(theme), dither=Image.Dither.NONE)
    # Index zero clears the canvas without painting a rectangle into the README.
    difference = ImageChops.difference(image, Image.new("RGB", image.size, THEMES[theme]["background"]))
    red, green, blue = difference.split()
    background = ImageChops.lighter(ImageChops.lighter(red, green), blue).point(lambda value: 255 if value == 0 else 0)
    result.paste(0, mask=background)
    result.info["transparency"] = 0
    return result


def render(kind, fonts, theme, output):
    frames, durations = [], []
    previous_state = None
    for index in range(PERIOD * FPS):
        seconds = index / FPS
        state = elapsed_at(kind, seconds)
        if state == previous_state:
            durations[-1] += 1000 // FPS
            continue
        frames.append(indexed(render_at(kind, seconds, fonts, theme), theme).convert("RGBA"))
        durations.append(1000 // FPS)
        previous_state = state
    frames[0].save(
        output / f"{kind}-{theme}.webp", save_all=True, append_images=frames[1:],
        duration=durations, loop=0, lossless=True, quality=80, method=4,
    )
    indexed(render_at(kind, OFFSETS[kind] + 5, fonts, theme), theme).save(output / f"{kind}-{theme}.png", optimize=True)


def verify(kind, fonts, theme, output):
    for seconds in (0, 0.5, 0.7, 1, 2.4, 3.4, 5, 11.95):
        assert render_at(kind, seconds, fonts, theme).tobytes() == render_at(kind, seconds + PERIOD, fonts, theme).tobytes(), (kind, theme, "loop seam")
    image = Image.open(output / f"{kind}-{theme}.webp")
    assert image.size == (WIDTH * SCALE, HEIGHT * SCALE)
    assert image.info.get("loop") == 0
    assert 1 < image.n_frames <= PERIOD * FPS
    elapsed = 0
    for index in range(image.n_frames):
        image.seek(index)
        actual = image.convert("RGBA")
        duration = image.info["duration"]
        assert duration > 0 and duration % 10 == 0
        expected = indexed(render_at(kind, elapsed / 1000, fonts, theme), theme).convert("RGBA")
        clear = Image.new("RGBA", image.size)
        assert Image.alpha_composite(clear, actual).tobytes() == Image.alpha_composite(clear, expected).tobytes(), (kind, theme, "encoded frame", index, elapsed)
        assert actual.getpixel((0, 0))[3] == 0 and actual.getpixel((image.width - 1, image.height - 1))[3] == 0
        elapsed += duration
    assert elapsed == PERIOD * 1000, (kind, theme, elapsed)
    poster = Image.open(output / f"{kind}-{theme}.png").convert("RGBA")
    expected = indexed(render_at(kind, OFFSETS[kind] + 5, fonts, theme), theme).convert("RGBA")
    assert poster.tobytes() == expected.tobytes()
    assert poster.getchannel("A").histogram()[0] > image.width * image.height / 2
    print(f"{kind}-{theme}: {image.width}×{image.height}, {image.n_frames} frames, {elapsed} ms, {(output / f'{kind}-{theme}.webp').stat().st_size:,} bytes; bounds, transparency, frames and seam passed")


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
        for theme in THEMES:
            if not args.check:
                render(kind, fonts, theme, args.output)
            verify(kind, fonts, theme, args.output)


if __name__ == "__main__":
    main()
