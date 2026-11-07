"""Generate the festival artwork in site/assets/photos/.

Usage:  python3 tools/make_festival_art.py [name ...]
Needs:  pip install numpy scipy pillow

Everything is drawn from code with a fixed seed: no stock photos, no footage.
  art-rangoli-*.webp      rangoli designs on a transparent background
  fireworks-*.gif         seamless loops, each inspired by a festival's style
  fireworks-*-still.webp  a still frame, used for reduced motion and when paused

Each animation avoids full-frame flashes: bursts stay small against a dark sky
and the background barely changes, in line with WCAG 2.3.1.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

OUT = Path(__file__).resolve().parent.parent / "site" / "assets" / "photos"


def rgb(value: str) -> np.ndarray:
    value = value.lstrip("#")
    return np.array([int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)])


# ── Rangoli ──────────────────────────────────────────────────────────────────

class Rangoli:
    """A powder-textured rangoli painted layer by layer in polar coordinates."""

    def __init__(self, seed: int, size: int = 900, wobble: float = 0.0045):
        self.size = size
        rng = np.random.default_rng(seed)
        axis = np.linspace(-1.02, 1.02, size)
        self.x, self.y = np.meshgrid(axis, axis)
        coarse = gaussian_filter(rng.standard_normal((size, size)), 3)
        fine = gaussian_filter(rng.standard_normal((size, size)), 0.7)
        self.edge = coarse / coarse.std()
        self.grain = fine / fine.std()
        self.r = np.hypot(self.x, self.y) + wobble * self.edge
        self.th = np.arctan2(self.y, self.x)
        self.rgb = np.zeros((size, size, 3))
        self.alpha = np.zeros((size, size))
        self.soft = 2.4 / size

    def _mask(self, distance: np.ndarray) -> np.ndarray:
        """distance < 0 is inside; returns a soft-edged 0..1 mask."""
        return np.clip(0.5 - distance / self.soft / 2, 0, 1)

    def paint(self, mask: np.ndarray, colour: str, grain: float = 0.075) -> None:
        shade = 1 + grain * self.grain
        layer = rgb(colour)[None, None, :] * shade[..., None]
        self.rgb = self.rgb * (1 - mask[..., None]) + layer * mask[..., None]
        self.alpha = np.maximum(self.alpha, mask)

    def disc(self, radius: float, colour: str, inner: float = 0.0) -> None:
        mask = self._mask(self.r - radius)
        if inner:
            mask = mask * self._mask(inner - self.r)
        self.paint(mask, colour)

    def fold(self, n: int, offset: float = 0.0) -> np.ndarray:
        step = 2 * math.pi / n
        return np.mod(self.th - offset + step / 2, step) - step / 2

    def scallop(self, radius: float, depth: float, n: int, colour: str, offset: float = 0.0) -> None:
        phi = self.fold(n, offset)
        limit = radius - depth + depth * np.cos(phi * n / 2) ** 0.8
        self.paint(self._mask(self.r - limit), colour)

    def petals(self, r0: float, r1: float, width: float, n: int, colour: str,
               offset: float = 0.0, belly: float = 0.75) -> None:
        """A ring of pointed petals. width is the half-width at the widest point."""
        phi = self.fold(n, offset)
        u = np.clip((self.r - r0) / (r1 - r0), 1e-4, 1 - 1e-4)
        half = width * np.sin(np.pi * u ** belly) ** 0.85
        distance = np.abs(phi) * self.r - half
        distance = np.where((self.r > r0) & (self.r < r1), distance, 1.0)
        self.paint(self._mask(distance), colour)

    def dots(self, radius: float, size: float, n: int, colour: str, offset: float = 0.0) -> None:
        phi = self.fold(n, offset)
        px = self.r * np.cos(phi) - radius
        py = self.r * np.sin(phi)
        self.paint(self._mask(np.hypot(px, py) - size), colour)

    def star(self, radius: float, inner: float, n: int, colour: str, offset: float = 0.0) -> None:
        phi = np.abs(self.fold(n, offset)) / (math.pi / n)
        limit = radius + (inner - radius) * phi
        self.paint(self._mask(self.r - limit), colour)

    def glow(self, radius: float, spread: float, n: int, offset: float, colour: str, power: float) -> None:
        phi = self.fold(n, offset)
        px = self.r * np.cos(phi) - radius
        py = self.r * np.sin(phi)
        amount = np.exp(-(np.hypot(px, py) / spread) ** 2) * power
        self.rgb = self.rgb + rgb(colour)[None, None, :] * amount[..., None]

    def save(self, name: str) -> None:
        image = np.dstack([np.clip(self.rgb, 0, 1), self.alpha])
        pil = Image.fromarray((image * 255).astype("uint8"), "RGBA")
        pil.save(OUT / f"{name}.webp", "WEBP", quality=76, alpha_quality=80, method=6)
        print(f"{name}.webp  {(OUT / f'{name}.webp').stat().st_size // 1024} KB")


def lotus_mandala() -> None:
    r = Rangoli(11)
    r.scallop(0.99, 0.035, 48, "#FFF3DF")
    r.dots(0.945, 0.016, 48, "#C2185B")
    r.petals(0.50, 0.92, 0.205, 12, "#C2185B")
    r.petals(0.525, 0.885, 0.165, 12, "#EC407A")
    r.petals(0.565, 0.84, 0.105, 12, "#FFB300")
    r.petals(0.61, 0.79, 0.048, 12, "#FFF3DF")
    r.petals(0.56, 0.86, 0.075, 12, "#00897B", offset=math.pi / 12)
    r.petals(0.60, 0.82, 0.038, 12, "#80CBC4", offset=math.pi / 12)
    r.disc(0.55, "#FFF3DF")
    r.scallop(0.52, 0.03, 24, "#6A1B9A")
    r.petals(0.22, 0.50, 0.14, 12, "#FFB300")
    r.petals(0.25, 0.46, 0.085, 12, "#FF7043")
    r.petals(0.22, 0.42, 0.06, 12, "#AB47BC", offset=math.pi / 12)
    r.disc(0.235, "#FFF3DF")
    r.dots(0.205, 0.016, 16, "#C2185B")
    r.star(0.175, 0.095, 8, "#00897B")
    r.star(0.125, 0.07, 8, "#FFB300", offset=math.pi / 8)
    r.disc(0.055, "#C2185B")
    r.disc(0.024, "#FFF3DF")
    r.save("art-rangoli-lotus")


def peacock_wheel() -> None:
    r = Rangoli(23)
    r.disc(0.985, "#0D2B6B")
    r.disc(0.985, "#E8B23A", inner=0.955)
    r.dots(0.925, 0.014, 40, "#E8B23A")
    n = 14
    r.petals(0.26, 0.885, 0.135, n, "#1B7F6C", belly=1.15)
    r.petals(0.30, 0.86, 0.104, n, "#2FB98F", belly=1.15)
    r.dots(0.70, 0.112, n, "#E8B23A")
    r.dots(0.70, 0.091, n, "#0E9AA7")
    r.dots(0.70, 0.063, n, "#0D2B6B")
    r.dots(0.70, 0.033, n, "#6A1B9A")
    off = math.pi / n
    r.petals(0.28, 0.68, 0.052, n, "#FFD54F", offset=off)
    r.petals(0.31, 0.62, 0.024, n, "#FF7043", offset=off)
    r.disc(0.32, "#FFF3DF")
    r.scallop(0.29, 0.024, 28, "#0E9AA7")
    r.petals(0.08, 0.285, 0.085, 14, "#0D2B6B")
    r.petals(0.10, 0.255, 0.048, 14, "#FFD54F")
    r.disc(0.105, "#FF7043")
    r.dots(0.068, 0.012, 8, "#FFF3DF")
    r.disc(0.03, "#6A1B9A")
    r.save("art-rangoli-peacock")


def kolam() -> None:
    """White rice-flour line art on an earth floor, in the South Indian kolam style."""
    r = Rangoli(37)
    r.disc(0.985, "#5B2415")
    r.disc(0.985, "#D9A05B", inner=0.96)
    r.dots(0.925, 0.012, 36, "#FFF6E5")
    k = math.pi / 0.135
    u = (r.x + r.y) / math.sqrt(2) + 0.0015 * r.edge
    v = (r.y - r.x) / math.sqrt(2) + 0.0015 * r.edge
    field = np.cos(k * u) + np.cos(k * v)
    inside = np.clip((0.655 - r.r) / 0.006, 0, 1)
    line = np.exp(-((np.abs(field) - 0.34) / 0.1) ** 2) + np.exp(-((np.abs(field) - 1.42) / 0.11) ** 2)
    r.paint(np.clip(line * 1.5, 0, 1) * inside, "#FFF6E5", grain=0.03)
    # A dot at the centre of every loop, as a kolam is drawn around a dot grid.
    du = np.mod(u + 0.135, 0.27) - 0.135
    dv = np.mod(v + 0.135, 0.27) - 0.135
    dots = r._mask(np.hypot(du, dv) - 0.011) * inside
    r.paint(dots, "#FFC84A", grain=0.03)
    # A garland of open loops around the lattice.
    r.disc(0.692, "#FFF6E5", inner=0.678)
    r.petals(0.695, 0.905, 0.082, 16, "#FFF6E5")
    r.petals(0.715, 0.885, 0.062, 16, "#5B2415")
    r.petals(0.745, 0.85, 0.026, 16, "#FFC84A")
    r.dots(0.86, 0.012, 16, "#FFF6E5", offset=math.pi / 16)
    r.dots(0.745, 0.011, 16, "#FFC84A", offset=math.pi / 16)
    r.save("art-rangoli-kolam")


def flower_carpet() -> None:
    """Concentric rings of petals, like a flower carpet (pookalam)."""
    r = Rangoli(41, wobble=0.0065)
    rings = [(0.985, "#2E7D32", 44), (0.91, "#FFF3DF", 40), (0.86, "#FB8C00", 36),
             (0.76, "#FDD835", 32), (0.67, "#8E1B3A", 28), (0.58, "#FFF3DF", 24)]
    for radius, colour, n in rings:
        r.scallop(radius, 0.03, n, colour)
    # Wedges in the next band for a woven look.
    r.petals(0.30, 0.55, 0.11, 8, "#FF7043")
    r.petals(0.30, 0.55, 0.11, 8, "#FDD835", offset=math.pi / 8)
    r.petals(0.335, 0.5, 0.05, 16, "#8E1B3A")
    r.disc(0.335, "#7B1FA2")
    r.scallop(0.30, 0.02, 20, "#FFF3DF")
    r.scallop(0.265, 0.02, 16, "#FB8C00")
    r.star(0.215, 0.11, 6, "#FDD835")
    r.star(0.155, 0.08, 6, "#8E1B3A", offset=math.pi / 6)
    r.disc(0.06, "#FFF3DF")
    r.disc(0.03, "#2E7D32")
    # Fine radial strokes that read as individual petals.
    petal = 1 + 0.11 * np.cos(r.th * 180) * (r.r > 0.33)
    r.rgb = r.rgb * petal[..., None]
    r.save("art-rangoli-flowers")


def diya_star() -> None:
    r = Rangoli(53)
    r.scallop(0.985, 0.045, 16, "#FFF3DF")
    r.scallop(0.93, 0.045, 16, "#1E3A8A")
    r.star(0.905, 0.46, 8, "#F57C00")
    r.star(0.845, 0.44, 8, "#FFD54F")
    r.star(0.775, 0.41, 8, "#D32F2F")
    r.petals(0.40, 0.70, 0.075, 8, "#FFF3DF", offset=math.pi / 8)
    r.petals(0.43, 0.67, 0.04, 8, "#1E3A8A", offset=math.pi / 8)
    r.disc(0.42, "#FFF3DF")
    r.dots(0.395, 0.014, 24, "#D32F2F")
    r.star(0.36, 0.19, 8, "#00838F", offset=math.pi / 8)
    r.star(0.285, 0.15, 8, "#FFD54F")
    r.disc(0.125, "#D32F2F")
    r.disc(0.075, "#FFF3DF")
    r.disc(0.04, "#F57C00")
    # Eight small clay lamps, one at each star point, each with a lit flame.
    r.dots(0.665, 0.075, 8, "#7A3417")
    r.dots(0.665, 0.052, 8, "#C8602B")
    r.dots(0.665, 0.03, 8, "#FFE9A8")
    r.glow(0.665, 0.11, 8, 0.0, "#FFB14A", 0.42)
    r.save("art-rangoli-diya-star")


RANGOLI = {
    "art-rangoli-lotus": lotus_mandala,
    "art-rangoli-peacock": peacock_wheel,
    "art-rangoli-kolam": kolam,
    "art-rangoli-flowers": flower_carpet,
    "art-rangoli-diya-star": diya_star,
}


# ── Fireworks ────────────────────────────────────────────────────────────────

GOLD = ["#FFC24A", "#FF9A2E"]
PALETTES = {
    "gold": GOLD,
    "white": ["#FFF6E0", "#FFE7A8"],
    "red": ["#FF2A20", "#FF5230"],
    "green": ["#20F070", "#8CFF3A"],
    "blue": ["#2F8CFF", "#40C8FF"],
    "violet": ["#A84BFF", "#FF4FD8"],
    "pink": ["#FF3F90", "#FF8AC0"],
}


class Show:
    """A periodic particle show. Every particle's age wraps at T, so loops are seamless."""

    def __init__(self, width, height, background, seconds=4.8, fps=12.5, seed=1, water=None):
        self.w, self.h, self.bg, self.T, self.fps = width, height, background, seconds, fps
        self.rng = np.random.default_rng(seed)
        self.groups = []
        self.water = water

    def add(self, p0, v, t0, life, colours, drag=2.0, g=20.0, trail=3, trail_dt=0.03, fade=1.0,
            bright=1.0, flicker=False):
        n = len(p0)
        self.groups.append(dict(
            p0=np.asarray(p0, float), v=np.asarray(v, float), t0=np.broadcast_to(t0, (n,)).astype(float),
            life=np.broadcast_to(life, (n,)).astype(float), col=np.asarray(colours, float), drag=drag, g=g,
            trail=trail, dt=trail_dt, fade=fade, bright=bright,
            flicker=self.rng.random(n) * 1000 if flicker else None))

    def colours(self, names, n):
        options = [rgb(c) for name in names for c in PALETTES[name]]
        return np.array(options)[self.rng.integers(0, len(options), n)]

    def rise(self, t0, x, y, start_y, seconds=0.7, name="gold"):
        speed = (start_y - y) / seconds
        self.add([[x, start_y]], [[self.rng.normal(0, 3), -speed]], t0 - seconds, seconds,
                 self.colours([name], 1), drag=0.001, g=0, trail=7, trail_dt=0.018, fade=0.3, bright=0.85)

    def shell(self, t0, x, y, radius, names=("gold",), style="peony", rise_from=None):
        rng = self.rng
        n = {"peony": 170, "chrys": 150, "willow": 130, "ring": 70, "palm": 26, "crackle": 90}[style]
        n = int(n * min(1.5, 0.6 + radius / 110))
        if style == "ring":
            a = np.linspace(0, 2 * np.pi, n, endpoint=False)
            tilt = rng.uniform(0.35, 0.9)
            turn = rng.uniform(0, np.pi)
            dx, dy = np.cos(a), np.sin(a) * tilt
            directions = np.stack([dx * np.cos(turn) - dy * np.sin(turn), dx * np.sin(turn) + dy * np.cos(turn)], 1)
            spread = rng.normal(1, 0.02, n)
        elif style == "palm":
            a = rng.uniform(0, 2 * np.pi, n)
            directions = np.stack([np.cos(a), np.sin(a)], 1)
            spread = rng.normal(1, 0.05, n)
        else:
            sphere = rng.normal(size=(n, 3))
            sphere /= np.linalg.norm(sphere, axis=1, keepdims=True)
            directions = sphere[:, :2]
            spread = rng.normal(1, 0.06, n)
        drag = {"willow": 2.6, "palm": 2.2, "chrys": 2.4}.get(style, 2.8)
        velocity = directions * (radius * drag * spread)[:, None]
        life = rng.uniform(*{"peony": (1.0, 1.5), "chrys": (1.3, 1.8), "willow": (2.0, 2.8), "ring": (1.0, 1.3),
                             "palm": (1.6, 2.2), "crackle": (0.8, 1.3)}[style], n)
        gravity = {"willow": radius * 0.5, "palm": radius * 0.55}.get(style, radius * 0.28)
        trail, dt = {"chrys": (6, 0.035), "willow": (8, 0.05), "palm": (10, 0.05)}.get(style, (3, 0.03))
        self.add(np.tile([x, y], (n, 1)), velocity, t0, life, self.colours(names, n), drag=drag, g=gravity,
                 trail=trail, trail_dt=dt, flicker=style == "crackle", bright=1.15 if style == "ring" else 1.0)
        if style != "palm" and style != "willow" and radius > 40:
            core = int(n * 0.3)
            a = rng.uniform(0, 2 * np.pi, core)
            inner = np.stack([np.cos(a), np.sin(a)], 1) * (radius * 0.45 * drag * rng.random(core))[:, None]
            self.add(np.tile([x, y], (core, 1)), inner, t0 + 0.03, rng.uniform(0.5, 0.9, core),
                     np.tile(rgb("#FFF8E7"), (core, 1)), drag=drag, g=gravity, trail=1, bright=0.8)
        if rise_from is not None:
            self.rise(t0, x, y, rise_from, name=names[0])

    def fountain(self, x, y, n, speed, cone, life, names, g=120, angle=-math.pi / 2, drag=0.6, trail=3):
        rng = self.rng
        a = angle + rng.normal(0, cone, n)
        s = speed * rng.uniform(0.55, 1.05, n)
        self.add(np.tile([x, y], (n, 1)), np.stack([np.cos(a) * s, np.sin(a) * s], 1), rng.uniform(0, self.T, n),
                 rng.uniform(life * 0.6, life, n), self.colours(names, n), drag=drag, g=g, trail=trail,
                 trail_dt=0.022, fade=1.1)

    def wheel(self, x, y, radius, n, names, turns=8):
        """A spinning ground wheel (chakri): sparks leave a nozzle on a turning rim."""
        rng = self.rng
        t0 = rng.uniform(0, self.T, n)
        a = t0 / self.T * turns * 2 * np.pi
        ring = np.stack([np.cos(a) * radius, np.sin(a) * radius * 0.5], 1) + [x, y]
        speed = rng.uniform(40, 90, n)
        tangent = np.stack([-np.sin(a) * speed, np.cos(a) * speed * 0.5 - 8], 1)
        self.add(ring, tangent, t0, rng.uniform(0.35, 0.75, n), self.colours(names, n), drag=1.2, g=70,
                 trail=3, trail_dt=0.02, fade=1.0)

    def frame(self, t):
        acc = np.zeros((self.h, self.w, 3))
        for g in self.groups:
            base_age = np.mod(t - g["t0"], self.T)
            for j in range(g["trail"] + 1):
                age = base_age - j * g["dt"]
                live = (age >= 0) & (age < g["life"])
                if not live.any():
                    continue
                a = age[live]
                d = g["drag"]
                decay = (1 - np.exp(-d * a)) / d
                x = g["p0"][live, 0] + g["v"][live, 0] * decay
                y = g["p0"][live, 1] + g["v"][live, 1] * decay + g["g"] * (a / d - decay / d)
                strength = (1 - a / g["life"][live]) ** g["fade"] * g["bright"] * (0.74 ** j)
                if g["flicker"] is not None:
                    phase = np.floor(a * 18) + g["flicker"][live]
                    strength = strength * (0.25 + 1.5 * (np.sin(phase * 12.9898) * 43758.5453 % 1 > 0.5))
                ix, iy = x.astype(int), y.astype(int)
                keep = (ix >= 0) & (ix < self.w) & (iy >= 0) & (iy < self.h)
                np.add.at(acc, (iy[keep], ix[keep]), g["col"][live][keep] * strength[keep, None])
        light = acc * 1.9 + gaussian_filter(acc, (0.8, 0.8, 0)) * 2.6 + gaussian_filter(acc, (3.0, 3.0, 0)) * 2.2
        if self.water:
            top = self.water
            rows = self.h - top
            mirror = np.clip(top - 1 - np.arange(rows) * 1.25, 0, top - 1).astype(int)
            fade = np.linspace(0.55, 0.14, rows)[:, None, None]
            light[top:] += gaussian_filter(light[mirror], (1.4, 1.0, 0)) * fade
        light[light < 0.018] = 0
        return self.bg * 0 + (1 - (1 - self.bg) * np.exp(-light))

    def render(self, name):
        count = round(self.T * self.fps)
        frames = [self.frame(i / self.fps) for i in range(count)]
        bytes_frames = [(np.clip(f, 0, 1) * 255).astype("uint8") for f in frames]
        # Train the palette on every bright pixel plus a sample of the sky.
        bright = np.concatenate([f[f.max(axis=2) > 44] for f in bytes_frames])
        sky = bytes_frames[0].reshape(-1, 3)[::3]
        pixels = np.concatenate([bright[:: max(1, len(bright) // 220_000)], sky])
        side = int(math.ceil(math.sqrt(len(pixels))))
        sheet = np.zeros((side, side, 3), "uint8")
        sheet.reshape(-1, 3)[: len(pixels)] = pixels
        palette = Image.fromarray(sheet, "RGB").quantize(colors=96, method=Image.Quantize.MEDIANCUT)
        images = [Image.fromarray(f, "RGB").quantize(palette=palette, dither=Image.Dither.NONE) for f in bytes_frames]
        gif = OUT / f"{name}.gif"
        images[0].save(gif, save_all=True, append_images=images[1:], duration=round(1000 / self.fps), loop=0,
                       disposal=1, optimize=False)
        lively = max(range(count), key=lambda i: float(bytes_frames[i].astype("uint16").sum()))
        still = OUT / f"{name}-still.webp"
        Image.fromarray(bytes_frames[lively], "RGB").save(still, "WEBP", quality=74, method=6)
        print(f"{name}.gif  {gif.stat().st_size // 1024} KB, {count} frames; still {still.stat().st_size // 1024} KB")


def sky(width, height, top, bottom, scale=2, seed=3, stars=60):
    """A vertical gradient with a sprinkling of stars, drawn at 2x for clean silhouettes."""
    t = np.linspace(0, 1, height * scale)[:, None, None]
    base = rgb(top)[None, None, :] * (1 - t) + rgb(bottom)[None, None, :] * t
    array = np.tile(base, (1, width * scale, 1))
    rng = np.random.default_rng(seed)
    for _ in range(stars):
        x, y = rng.integers(0, width * scale), rng.integers(0, int(height * scale * 0.6))
        array[y:y + 2, x:x + 2] += rng.uniform(0.08, 0.3)
    return Image.fromarray((np.clip(array, 0, 1) * 255).astype("uint8"), "RGB")


def finish(image, width, height):
    return np.asarray(image.resize((width, height), Image.LANCZOS), float) / 255


def nagaoka():
    """A river valley with shells spanning the full width, in the spirit of Nagaoka's Shinano River display."""
    w, h, river = 540, 360, 292
    im = sky(w, h, "#050816", "#101A3C", seed=5)
    d = ImageDraw.Draw(im)
    hills = [(x * 2, (river - 18 - 10 * math.sin(x / 47) - 7 * math.sin(x / 19 + 1)) * 2) for x in range(0, w + 2)]
    d.polygon(hills + [(w * 2, river * 2), (0, river * 2)], fill="#070B18")
    d.rectangle([0, river * 2, w * 2, h * 2], fill="#080E22")
    show = Show(w, h, finish(im, w, h), seed=7, water=river)
    # A wave of shells sweeping along the bank from left to right.
    colours = (("red", "gold"), ("green", "white"), ("blue", "white"), ("violet", "gold"), ("gold",))
    for i in range(5):
        x = 62 + i * 104
        show.shell(0.15 + i * 0.32, x, 188 - 40 * math.sin(i / 4 * math.pi), 56, colours[i], "chrys", rise_from=river)
    # The giant centre shell that opens across the sky.
    show.shell(2.1, 270, 118, 104, ("gold",), "willow", rise_from=river)
    show.shell(2.15, 270, 118, 66, ("pink",), "ring")
    show.shell(3.3, 130, 138, 66, ("blue", "white"), "chrys", rise_from=river)
    show.shell(3.5, 410, 132, 66, ("green", "gold"), "chrys", rise_from=river)
    show.render("fireworks-nagaoka")


def spring_festival():
    """Red lanterns, a crackling firecracker string and red-gold shells for the Spring Festival."""
    w, h = 400, 500
    im = sky(w, h, "#10040A", "#2A0A0E", seed=9, stars=24)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 952, w * 2, h * 2], fill="#120506")
    # A pole with the hanging string of crackers.
    d.rectangle([0, 92, 800, 98], fill="#3A1A12")
    d.line([(150, 98), (150, 780)], fill="#7A2A1E", width=3)
    for y in range(120, 780, 22):
        side = -1 if (y // 22) % 2 else 1
        d.rounded_rectangle([150 + side * 3 - 9, y, 150 + side * 3 + 9, y + 18], 3, fill="#B81F1F", outline="#E8A83A")
    for x, y, s in ((470, 150, 58), (650, 200, 44), (330, 170, 34)):
        d.line([(x, 98), (x, y - s)], fill="#7A2A1E", width=3)
        d.ellipse([x - s, y - s * 0.86, x + s, y + s * 0.86], fill="#C81E1E")
        for k in (-0.55, 0, 0.55):
            d.arc([x - s * abs(k) - 2, y - s * 0.86, x + s * abs(k) + 2, y + s * 0.86], 90 if k < 0 else 270,
                  270 if k < 0 else 90, fill="#7E0F0F", width=2)
        d.rectangle([x - s * 0.34, y - s * 0.98, x + s * 0.34, y - s * 0.82], fill="#E8A83A")
        d.rectangle([x - s * 0.34, y + s * 0.82, x + s * 0.34, y + s * 0.98], fill="#E8A83A")
    show = Show(w, h, finish(im, w, h), seed=11)
    rng = show.rng
    # Cracker pops along the string, with red paper falling away.
    pops = 60
    y = rng.uniform(60, 395, pops)
    t0 = rng.uniform(0, show.T, pops)
    for py, pt in zip(y, t0):
        a = rng.uniform(0, 2 * np.pi, 34)
        speed = rng.uniform(90, 230, 34)
        show.add(np.tile([75, py], (34, 1)), np.stack([np.cos(a) * speed, np.sin(a) * speed], 1), pt,
                 rng.uniform(0.2, 0.42, 34), show.colours(["white", "gold", "red"], 34), drag=4, g=30, trail=1, bright=1.5)
        paper = 5
        b = rng.uniform(0, 2 * np.pi, paper)
        show.add(np.tile([75, py], (paper, 1)), np.stack([np.cos(b) * 50, np.sin(b) * 40], 1), pt,
                 rng.uniform(1.2, 2.0, paper), show.colours(["red"], paper), drag=3, g=95, trail=0, fade=0.5, bright=0.55)
    show.shell(0.3, 280, 240, 92, ("red", "gold"), "peony", rise_from=470)
    show.shell(1.6, 215, 300, 84, ("gold",), "chrys", rise_from=470)
    show.shell(2.8, 300, 190, 96, ("red", "white"), "chrys", rise_from=470)
    show.shell(3.9, 245, 320, 72, ("gold", "red"), "ring", rise_from=470)
    show.render("fireworks-spring-festival")


def city_tower():
    """A slender tower with sparks cascading from its levels, in the spirit of New Year's Eve in Dubai."""
    w, h = 400, 500
    im = sky(w, h, "#03040F", "#142040", seed=13, stars=32)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(13)
    x = 400
    for i in range(30):
        bx = i * 28
        top = 800 + rng.integers(0, 100)
        d.rectangle([bx, top, bx + 26, 1000], fill="#090E20")
        for _ in range(9):
            wx, wy = bx + rng.integers(3, 23), rng.integers(top + 6, 990)
            d.rectangle([wx, wy, wx + 2, wy + 3], fill="#7A6638")
    profile = [(84, 4), (200, 8), (320, 14), (440, 22), (580, 30), (720, 40), (860, 52), (1000, 60)]
    left = [(x - hw, y) for y, hw in profile]
    right = [(x + hw, y) for y, hw in reversed(profile)]
    d.polygon(left + right, fill="#0D1530", outline="#25335F")
    for y in range(100, 1000, 9):
        hw = np.interp(y, [p[0] for p in profile], [p[1] for p in profile]) * 0.82
        for wx in np.linspace(x - hw, x + hw, max(2, int(hw / 4))):
            if rng.random() < 0.55:
                d.rectangle([wx, y, wx + 1, y + 2], fill="#A98B4E")
    show = Show(w, h, finish(im, w, h), seed=17)
    rng = show.rng
    # Sparks shooting outward from each level of the tower, then falling.
    for level, (y, reach) in enumerate(((110, 110), (170, 135), (235, 150), (300, 160), (365, 170))):
        side_n = 230
        for side in (-1, 1):
            t = np.mod(level * 0.28 + rng.uniform(0, 0.9, side_n), show.T)
            speed = rng.uniform(0.6, 1.05, side_n) * reach * 2.2
            a = rng.normal(-0.15, 0.2, side_n)
            show.add(np.tile([200 + side * (6 + level * 3), y], (side_n, 1)),
                     np.stack([side * np.cos(a) * speed, np.sin(a) * speed], 1), t + 0.2,
                     rng.uniform(1.0, 1.7, side_n), show.colours(["gold", "white"], side_n), drag=2.2, g=70, trail=3,
                     trail_dt=0.03)
    show.shell(2.1, 200, 60, 92, ("gold", "white"), "chrys")
    show.shell(2.6, 80, 130, 60, ("violet",), "peony", rise_from=420)
    show.shell(2.9, 320, 130, 60, ("blue", "white"), "peony", rise_from=420)
    show.shell(3.6, 200, 42, 62, ("pink",), "ring")
    show.render("fireworks-city-tower")


def harbour():
    """An arch bridge with a spark waterfall over a harbour, in the spirit of Sydney's New Year's Eve."""
    w, h, sea = 540, 360, 278
    im = sky(w, h, "#040A1C", "#132B50", seed=19)
    d = ImageDraw.Draw(im)
    d.rectangle([0, sea * 2, w * 2, h * 2], fill="#06122A")
    deck = 212 * 2
    arch = [(x, deck - 150 * (1 - ((x - 400) / 340) ** 2)) for x in range(60, 741, 10)]
    lower = [(x, deck - 104 * (1 - ((x - 400) / 340) ** 2)) for x in range(60, 741, 10)]
    d.line(arch, fill="#1C2A4D", width=7)
    d.line(lower, fill="#1C2A4D", width=4)
    for a, b in zip(arch[::3], lower[::3]):
        d.line([a, b], fill="#1C2A4D", width=2)
    for x, y in arch[::3]:
        d.line([(x, y), (x, deck)], fill="#172442", width=2)
    d.rectangle([0, deck, 880, deck + 7], fill="#1C2A4D")
    for x in (56, 700):
        d.rectangle([x, deck - 40, x + 44, sea * 2], fill="#1A2747")
    # Original sail-like shells on the right shore.
    base = sea * 2
    for x, width, height in ((850, 62, 130), (900, 76, 170), (965, 72, 142), (1020, 52, 98)):
        d.polygon([(x, base), (x + width * 0.12, base - height), (x + width, base)], fill="#20325C")
    d.rectangle([800, base - 2, 1080, base + 4], fill="#141F3E")
    show = Show(w, h, finish(im, w, h), seed=23, water=sea)
    rng = show.rng
    # A curtain of sparks pouring from the deck.
    n = 2400
    x = rng.uniform(40, 375, n)
    t = rng.uniform(0.2, 2.7, n)
    show.add(np.stack([x, np.full(n, 215.0)], 1), np.stack([rng.normal(0, 3, n), rng.uniform(4, 26, n)], 1), t,
             rng.uniform(0.7, 1.1, n), show.colours(["white", "gold"], n), drag=1.0, g=120, trail=3, trail_dt=0.02, fade=0.8)
    for i, cx in enumerate((110, 200, 290)):
        show.shell(0.4 + i * 0.5, cx, 86 + 18 * ((i + 1) % 2), 68, (("red", "white"), ("gold",), ("blue", "white"))[i], "peony")
    show.shell(2.5, 200, 60, 78, ("gold",), "willow")
    show.shell(3.1, 80, 110, 58, ("green",), "chrys")
    show.shell(3.4, 330, 110, 58, ("violet",), "chrys")
    show.shell(2.8, 450, 90, 60, ("pink", "white"), "ring", rise_from=sea)
    show.render("fireworks-harbour")


def beehive():
    """Hundreds of rockets streaking from one rack, in the spirit of Yanshui's beehive festival."""
    w, h = 420, 420
    im = sky(w, h, "#07060C", "#1E1712", seed=29, stars=20)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(29)
    d.rectangle([0, 720, 840, 840], fill="#0A0806")
    # The rack: a boxy wall of rocket tubes on a frame.
    d.rectangle([340, 470, 500, 650], fill="#1A120C", outline="#4A3320", width=3)
    for x in range(350, 490, 18):
        for y in range(480, 640, 18):
            d.ellipse([x, y, x + 9, y + 9], fill="#080503", outline="#4A3320")
    d.line([(340, 660), (320, 730)], fill="#3A2818", width=7)
    d.line([(500, 660), (520, 730)], fill="#3A2818", width=7)
    # A crowd along the bottom edge, in helmets, watching.
    for x in range(-10, 860, 34):
        top = 738 + rng.integers(-10, 12)
        d.ellipse([x, top, x + 28, top + 28], fill="#040302")
        d.rectangle([x - 2, top + 22, x + 30, 840], fill="#040302")
    show = Show(w, h, finish(im, w, h), seed=31)
    rng = show.rng
    n = 1900
    a = rng.uniform(0, 2 * np.pi, n)
    # Bias a little upward and sideways, as rockets leave the rack in every direction.
    speed = rng.uniform(170, 460, n)
    vx = np.cos(a) * speed
    vy = np.sin(a) * speed * 0.72 - 55
    start = np.stack([rng.uniform(175, 245, n), rng.uniform(240, 320, n)], 1)
    # Three surges keep the swarm dense but rhythmic.
    t = np.mod(rng.choice([0.2, 1.8, 3.4], n) + rng.exponential(0.45, n), show.T)
    show.add(start, np.stack([vx, vy], 1), t, rng.uniform(0.5, 1.15, n), show.colours(["gold", "gold", "white", "red"], n),
             drag=0.9, g=26, trail=5, trail_dt=0.016, fade=0.55, bright=1.6)
    pops = 120
    show.add(np.stack([rng.uniform(25, 395, pops), rng.uniform(25, 310, pops)], 1), rng.normal(0, 25, (pops, 2)),
             rng.uniform(0, show.T, pops), rng.uniform(0.15, 0.35, pops), show.colours(["white", "red"], pops), drag=3, g=0,
             trail=1, bright=1.3)
    show.render("fireworks-beehive")


def diwali_ground():
    """Ground-level Diwali crackers: anar fountains and chakri wheels, under small sky bursts."""
    w, h = 540, 360
    im = sky(w, h, "#060716", "#1A1230", seed=37, stars=40)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 586, 1080, 720], fill="#1C1209")
    for y in range(600, 720, 26):
        d.line([(0, y), (1080, y)], fill="#241810", width=1)
    # A low wall with small lamps along it.
    d.rectangle([0, 548, 1080, 588], fill="#120D1C")
    for x in range(30, 1080, 86):
        d.ellipse([x - 14, 536, x + 14, 552], fill="#A9542A")
        d.ellipse([x - 3, 524, x + 3, 540], fill="#FFD27A")
    # Clay pots for the fountains.
    pots = [(112, 300), (270, 306), (428, 300)]
    for px, py in pots:
        d.polygon([(px * 2 - 16, py * 2 - 22), (px * 2 + 16, py * 2 - 22), (px * 2 + 28, py * 2 + 18), (px * 2 - 28, py * 2 + 18)],
                  fill="#8A4422")
        d.rectangle([px * 2 - 18, py * 2 - 26, px * 2 + 18, py * 2 - 20], fill="#C8742F")
    show = Show(w, h, finish(im, w, h), seed=41)
    for (px, py), names, tall in zip(pots, (("gold",), ("gold", "white"), ("gold", "red")), (260, 320, 250)):
        show.fountain(px, py - 11, 1500, tall * 1.25, 0.17, 1.15, names, g=240, drag=0.5)
    show.wheel(192, 322, 15, 1100, ("green", "gold"), turns=10)
    show.wheel(350, 326, 15, 1100, ("red", "gold"), turns=-10)
    show.wheel(55, 330, 12, 700, ("blue", "white"), turns=8)
    show.wheel(488, 330, 12, 700, ("violet", "gold"), turns=-8)
    show.shell(0.5, 150, 66, 46, ("violet",), "peony", rise_from=280)
    show.shell(2.1, 390, 62, 50, ("green", "gold"), "chrys", rise_from=280)
    show.shell(3.6, 270, 48, 44, ("pink",), "ring", rise_from=280)
    show.render("fireworks-diwali-ground")


FIREWORKS = {
    "fireworks-nagaoka": nagaoka,
    "fireworks-spring-festival": spring_festival,
    "fireworks-city-tower": city_tower,
    "fireworks-harbour": harbour,
    "fireworks-beehive": beehive,
    "fireworks-diwali-ground": diwali_ground,
}


def main(names):
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = {**RANGOLI, **FIREWORKS}
    for name in names or jobs:
        jobs[name]()


if __name__ == "__main__":
    main(sys.argv[1:])
