"""Generate the diya and flower-rangoli pictures in site/assets/photos/.

Usage:  python3 tools/make_diya_art.py [name ...]
Needs:  pip install numpy scipy pillow

Original artwork drawn from code with fixed seeds: no stock photos.
  diya-bokeh.webp         painted clay diyas on a table, warm bokeh behind
  diya-sparkle.webp       one clay diya with sparks, reflected on a dark floor
  rangoli-crescent.webp   a crescent flower rangoli ringed with brass diyas
  diya-marigold.webp      embroidered diyas around a cluster of marigolds
  diya-row.webp           a row of lit diyas on a transparent background
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

OUT = Path(__file__).resolve().parent.parent / "site" / "assets" / "photos"
SS = 3  # supersampling for crisp shapes


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def frgb(value: str) -> np.ndarray:
    return np.array(rgb(value), float) / 255


def shade(colour: str, k: float) -> tuple[int, int, int]:
    return tuple(int(max(0, min(255, c * k))) for c in rgb(colour))


class Scene:
    """Shapes are drawn with PIL at SS x size; light is added in float afterwards."""

    def __init__(self, w: int, h: int, seed: int, transparent: bool = False):
        self.w, self.h = w, h
        self.rng = np.random.default_rng(seed)
        mode = "RGBA"
        self.img = Image.new(mode, (w * SS, h * SS), (0, 0, 0, 0 if transparent else 255))
        self.d = ImageDraw.Draw(self.img)
        self.flames: list[tuple[float, float, float]] = []  # x, y (base), height in output px
        self.transparent = transparent

    # Coordinates are in output pixels; these helpers scale them.
    def S(self, *v):
        return [x * SS for x in v]

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=None, width=1):
        self.d.ellipse(self.S(cx - rx, cy - ry, cx + rx, cy + ry), fill=fill, outline=outline, width=int(width * SS))

    def poly(self, pts, fill):
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)

    def background(self, top, bottom, split=1.0, floor_top=None, floor_bottom=None):
        t = np.linspace(0, 1, self.h * SS)[:, None]
        y_split = split
        a, b = np.array(rgb(top), float), np.array(rgb(bottom), float)
        col = a * (1 - np.clip(t / y_split, 0, 1)) + b * np.clip(t / y_split, 0, 1)
        if floor_top is not None:
            ft, fb = np.array(rgb(floor_top), float), np.array(rgb(floor_bottom), float)
            u = np.clip((t - y_split) / (1 - y_split), 0, 1)
            floor = ft * (1 - u) + fb * u
            col = np.where(t > y_split, floor, col)
        arr = np.repeat(col[:, None, :], self.w * SS, axis=1)
        alpha = np.full((self.h * SS, self.w * SS, 1), 255.0)
        self.img = Image.fromarray(np.concatenate([arr, alpha], 2).astype("uint8"), "RGBA")
        self.d = ImageDraw.Draw(self.img)

    def flame(self, x, y, height):
        self.flames.append((x, y, height))

    # ── Objects ─────────────────────────────────────────────────────────────
    def clay_diya(self, cx, cy, w, body="#8A3A1C", inner="#2E4FA0", paint=("#F2C14E", "#E8E3D3", "#2FA36B"), tilt=0.3):
        """A painted clay diya seen from the side. Returns the flame base."""
        rx, ry = w / 2, w / 2 * tilt
        depth = w * 0.34
        spout = (cx + rx * 1.18, cy - ry * 0.15)
        # Body: the lower half of a deep ellipse, joined to the rim.
        self.poly([(cx + rx * 0.62, cy - ry * 0.75), spout, (cx + rx * 0.62, cy + ry * 0.75)], shade(body, 0.95))
        self.d.chord(self.S(cx - rx, cy - depth, cx + rx, cy + depth), 0, 180, fill=rgb(body))
        self.ellipse(cx, cy + depth * 0.92, rx * 0.36, ry * 0.4, fill=shade(body, 0.55))
        # Painted bands with dots, following the curve of the body.
        for k, (scale, colour) in enumerate(((0.8, paint[0]), (0.55, paint[1]), (0.3, paint[2]))):
            n = 22 - k * 5
            for i in range(n):
                a = math.pi * (0.06 + 0.88 * i / (n - 1))
                x = cx + rx * 0.97 * math.cos(a)
                y = cy + depth * scale * math.sin(a)
                r = w * (0.022 - k * 0.003)
                self.ellipse(x, y, r, r * 0.9, fill=rgb(colour))
        self.d.arc(self.S(cx - rx * 0.96, cy - depth * 0.7, cx + rx * 0.96, cy + depth * 0.7), 10, 170,
                   fill=rgb(paint[0]), width=int(w * 0.018 * SS))
        # Rim and the oil well.
        self.ellipse(cx, cy, rx, ry, fill=rgb(paint[0]))
        self.ellipse(cx, cy, rx * 0.9, ry * 0.8, fill=shade(body, 1.15))
        self.ellipse(cx + rx * 0.03, cy + ry * 0.05, rx * 0.78, ry * 0.62, fill=rgb(inner))
        self.ellipse(cx + rx * 0.08, cy + ry * 0.12, rx * 0.5, ry * 0.32, fill=shade(inner, 0.6))
        for i in range(18):
            a = 2 * math.pi * i / 18
            self.ellipse(cx + rx * 0.95 * math.cos(a), cy + ry * 0.9 * math.sin(a), w * 0.012, w * 0.009,
                         fill=rgb(paint[1]))
        # Wick lying in the spout.
        base = (cx + rx * 0.95, cy - ry * 0.25)
        self.d.line(self.S(cx + rx * 0.45, cy - ry * 0.05, *base), fill=(240, 228, 200), width=int(w * 0.03 * SS))
        self.flame(base[0], base[1], w * 0.42)
        return base

    def bowl_diya(self, cx, cy, w, metal="#C8913A", wax="#C24A1E"):
        """A small brass diya with a scalloped edge, seen from above at an angle."""
        rx, ry = w / 2, w / 2 * 0.62
        self.ellipse(cx, cy + ry * 0.55, rx * 1.02, ry * 0.85, fill=shade(metal, 0.45))
        for i in range(16):
            a = 2 * math.pi * i / 16
            self.ellipse(cx + rx * math.cos(a), cy + ry * math.sin(a), w * 0.11, w * 0.08, fill=shade(metal, 0.9))
        self.ellipse(cx, cy, rx, ry, fill=rgb(metal))
        self.ellipse(cx, cy, rx * 0.74, ry * 0.72, fill=shade(metal, 0.6))
        self.ellipse(cx, cy + ry * 0.04, rx * 0.66, ry * 0.62, fill=rgb(wax))
        self.ellipse(cx - rx * 0.1, cy - ry * 0.1, rx * 0.3, ry * 0.22, fill=shade(wax, 1.35))
        self.d.line(self.S(cx, cy, cx, cy - w * 0.08), fill=(40, 26, 18), width=max(1, int(w * 0.03 * SS)))
        self.flame(cx, cy - w * 0.06, w * 0.5)

    def round_diya(self, cx, cy, r, rings, flame=True):
        """A decorated diya seen from above: concentric rings with gold bead borders."""
        k = 0.78  # slight perspective
        self.ellipse(cx, cy + r * 0.12, r * 1.04, r * k * 1.06, fill=(20, 8, 6))
        radius = r
        for colour, beads in rings:
            self.ellipse(cx, cy, radius, radius * k, fill=rgb(colour))
            if beads:
                n = max(10, int(radius / 2.4))
                for i in range(n):
                    a = 2 * math.pi * i / n
                    bx, by = cx + radius * 0.9 * math.cos(a), cy + radius * 0.9 * k * math.sin(a)
                    self.ellipse(bx, by, r * 0.045, r * 0.04, fill=rgb(beads))
                    self.ellipse(bx - r * 0.012, by - r * 0.012, r * 0.016, r * 0.014, fill=(255, 240, 190))
            radius *= 0.8
        self.ellipse(cx, cy, r * 0.3, r * 0.3 * k, fill=(36, 30, 32))
        self.ellipse(cx, cy, r * 0.22, r * 0.22 * k, fill=(70, 62, 64))
        self.d.line(self.S(cx, cy, cx, cy - r * 0.1), fill=(20, 12, 10), width=max(1, int(r * 0.04 * SS)))
        if flame:
            self.flame(cx, cy - r * 0.08, r * 0.62)

    def marigold(self, cx, cy, r, hue="orange"):
        rng = self.rng
        base = {"orange": ("#E8650F", "#F68B1F", "#FFA733"), "yellow": ("#E9A00B", "#F7C21A", "#FFD84D")}[hue]
        self.ellipse(cx, cy + r * 0.12, r * 1.02, r * 0.95, fill=shade(base[0], 0.45))
        for i in range(int(90 + r * 3)):
            a = rng.uniform(0, 2 * np.pi)
            d = r * math.sqrt(rng.uniform(0, 1)) * 0.92
            x, y = cx + d * math.cos(a), cy + d * math.sin(a) * 0.95
            light = 0.65 + 0.55 * (1 - (x - cx + y - cy) / (2.2 * r) - 0.5)
            pr = r * rng.uniform(0.12, 0.2)
            col = shade(base[rng.integers(0, 3)], light * rng.uniform(0.85, 1.1))
            ang = math.atan2(y - cy, x - cx)
            dx, dy = math.cos(ang) * pr * 0.35, math.sin(ang) * pr * 0.35
            self.ellipse(x + dx, y + dy, pr, pr * 0.75, fill=col)

    def leaf(self, x, y, angle, length, colour="#1F5A2A"):
        pts = []
        for t in np.linspace(0, 1, 14):
            pts.append((t, 0.28 * math.sin(math.pi * t) ** 0.9))
        outline = pts + [(t, -wd) for t, wd in reversed(pts)]
        ca, sa = math.cos(angle), math.sin(angle)
        poly = [(x + (t * ca - wd * sa) * length, y + (t * sa + wd * ca) * length) for t, wd in outline]
        self.poly(poly, rgb(colour))
        self.d.line(self.S(x, y, x + ca * length * 0.9, y + sa * length * 0.9), fill=shade(colour, 1.5), width=SS)

    def petal(self, x, y, angle, length, width, colour, outline=None):
        pts = []
        for t in np.linspace(0, 1, 16):
            pts.append((t, width * math.sin(math.pi * t ** 0.8) ** 0.85))
        shape = pts + [(t, -wd) for t, wd in reversed(pts)]
        ca, sa = math.cos(angle), math.sin(angle)
        poly = [(x + (t * ca * length - wd * sa), y + (t * sa * length + wd * ca)) for t, wd in shape]
        if outline:
            grow = [(x + (t * ca * length * 1.06 - wd * 1.25 * sa), y + (t * sa * length * 1.06 + wd * 1.25 * ca))
                    for t, wd in shape]
            self.poly(grow, rgb(outline))
        self.poly(poly, rgb(colour))

    # ── Light ───────────────────────────────────────────────────────────────
    def render(self, bokeh=None, sparks=None, reflection=None, warmth=1.0, vignette=0.35):
        img = self.img.resize((self.w, self.h), Image.LANCZOS)
        arr = np.asarray(img, float) / 255
        colour, alpha = arr[..., :3], arr[..., 3]
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(float)
        light = np.zeros((self.h, self.w))
        add = np.zeros((self.h, self.w, 3))
        for x, y, hgt in self.flames:
            d2 = ((xx - x) ** 2 + ((yy - y + hgt * 0.4) * 1.15) ** 2)
            light += np.exp(-d2 / (hgt * 2.4) ** 2) * 0.8 + np.exp(-d2 / (hgt * 7) ** 2) * 0.28
            add += self._flame_layer(xx, yy, x, y, hgt)
        light = 1 - np.exp(-light)
        lit = colour * (0.4 + warmth * light[..., None] * frgb("#FFC27A") * 0.95)
        if bokeh is not None:
            lit = 1 - (1 - lit) * (1 - bokeh)
        if sparks is not None:
            add += sparks
        if vignette and not self.transparent:
            v = 1 - vignette * (((xx / self.w - 0.5) * 1.6) ** 2 + ((yy / self.h - 0.5) * 1.3) ** 2)
            lit = lit * np.clip(v, 0.3, 1)[..., None]
        out = 1 - (1 - np.clip(lit, 0, 1)) * np.exp(-add)
        if reflection is not None:
            top = reflection
            rows = self.h - top
            src = np.clip(top - 1 - np.arange(rows), 0, top - 1)
            mirror = gaussian_filter(out[src], (2.5, 1.5, 0))
            fade = np.linspace(0.45, 0.05, rows)[:, None, None]
            out[top:] = 1 - (1 - out[top:]) * (1 - mirror * fade)
        if self.transparent:
            glow = np.clip(add.max(axis=2), 0, 1)
            alpha = np.maximum(alpha, gaussian_filter(glow, 2) * 0.9)
            return np.dstack([np.clip(out, 0, 1), alpha])
        return np.clip(out, 0, 1)

    @staticmethod
    def _flame_layer(xx, yy, x, y, hgt):
        t = (y - yy) / hgt  # 0 at base, 1 at tip
        inside = (t > -0.12) & (t < 1.05)
        half = hgt * 0.17 * np.clip(np.sin(np.pi * np.clip((t + 0.12) / 1.17, 0, 1) ** 0.62), 0, 1) ** 1.2
        dx = np.abs(xx - x) / np.maximum(half, 1e-3)
        body = np.where(inside, np.clip(1.15 - dx, 0, 1), 0) ** 0.8
        core = body * np.clip(1 - t * 1.2, 0, 1) * np.clip(1.3 - dx * 1.4, 0, 1)
        layer = body[..., None] * frgb("#FFB43C") * 2.6 + core[..., None] * frgb("#FFF6DA") * 3.5
        blue = np.exp(-(((xx - x) / (hgt * 0.07)) ** 2 + ((yy - y) / (hgt * 0.05)) ** 2)) * 0.6
        layer += blue[..., None] * frgb("#5A7BFF")
        d2 = (xx - x) ** 2 + ((yy - (y - hgt * 0.45)) * 0.8) ** 2
        layer += np.exp(-d2 / (hgt * 0.55) ** 2)[..., None] * frgb("#FF9A2E") * 0.9
        return layer

    def bokeh(self, n, area, sizes, colours, strength=0.5, seed=5):
        rng = np.random.default_rng(seed)
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(float)
        out = np.zeros((self.h, self.w, 3))
        x0, y0, x1, y1 = area
        for _ in range(n):
            x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
            r = rng.uniform(*sizes)
            d = np.hypot(xx - x, yy - y) / r
            disc = np.clip((1.0 - d) * r * 0.12, 0, 1) * (0.7 + 0.4 * np.clip(d, 0, 1) ** 4)
            out += disc[..., None] * frgb(colours[rng.integers(0, len(colours))]) * rng.uniform(0.25, 1) * strength
        return np.clip(1 - np.exp(-out), 0, 1)

    def sparks(self, x, y, n, spread, height, seed=9):
        rng = np.random.default_rng(seed)
        out = np.zeros((self.h, self.w, 3))
        for _ in range(n):
            a = rng.normal(-math.pi / 2, spread)
            dist = height * rng.uniform(0.05, 1) ** 0.7
            px, py = x + math.cos(a) * dist, y + math.sin(a) * dist + dist * dist / height * 0.25
            length = rng.uniform(1, 5)
            for s in np.linspace(0, 1, 5):
                qx, qy = int(px - math.cos(a) * length * s), int(py - math.sin(a) * length * s)
                if 0 <= qx < self.w and 0 <= qy < self.h:
                    out[qy, qx] += frgb("#FFD98A") * rng.uniform(0.6, 2.2) * (1 - s * 0.7)
        return gaussian_filter(out, (0.6, 0.6, 0)) * 2.2 + gaussian_filter(out, (2.5, 2.5, 0)) * 1.2


def save(array, name, quality=82):
    mode = "RGBA" if array.shape[2] == 4 else "RGB"
    img = Image.fromarray((np.clip(array, 0, 1) * 255).astype("uint8"), mode)
    path = OUT / f"{name}.webp"
    img.save(path, "WEBP", quality=quality, method=6, **({"alpha_quality": 85} if mode == "RGBA" else {}))
    print(f"{name}.webp  {img.size}  {path.stat().st_size // 1024} KB")


# ── Scenes ───────────────────────────────────────────────────────────────────

def diya_bokeh():
    s = Scene(1200, 800, 3)
    s.background("#0A0C26", "#24102A", split=0.5, floor_top="#4A1A2A", floor_bottom="#1A0812")
    bokeh = s.bokeh(46, (0, -40, 1200, 380), (28, 70), ("#FF8A2A", "#FFA040", "#E86A1A", "#FFC060"), 0.3)
    s.clay_diya(250, 470, 190, body="#7A2814", inner="#B0306A", paint=("#E8B23A", "#F4E6C8", "#2AA0A0"))
    s.clay_diya(600, 440, 170, body="#5E2412", inner="#2E58B8", paint=("#E8B23A", "#F4E6C8", "#D2453A"))
    s.clay_diya(940, 470, 190, body="#6A2A12", inner="#2E9A4C", paint=("#E8B23A", "#F4E6C8", "#7A4FC0"))
    s.clay_diya(380, 640, 300, body="#6A1E22", inner="#1D3C8C", paint=("#E8B23A", "#F2E2BE", "#2FA36B"))
    s.clay_diya(820, 650, 300, body="#5A1E30", inner="#1E6B6A", paint=("#E8B23A", "#F2E2BE", "#E0648F"))
    save(s.render(bokeh=bokeh, vignette=0.25), "diya-bokeh")


def diya_sparkle():
    s = Scene(800, 1100, 7)
    s.background("#0A0806", "#1C120A", split=0.74, floor_top="#2A1408", floor_bottom="#0E0604")
    bokeh = s.bokeh(70, (-40, -40, 840, 760), (30, 62), ("#D89A4A", "#E8B070", "#B8742E", "#F2C98A"), 0.26, seed=11)
    # A ring of red rangoli powder around the diya on the floor.
    for i in range(240):
        a = s.rng.uniform(0, 2 * math.pi)
        r = s.rng.uniform(150, 330)
        s.ellipse(400 + r * math.cos(a), 868 + r * 0.16 * math.sin(a), s.rng.uniform(2, 7), s.rng.uniform(1, 3),
                  fill=shade("#B8401C", s.rng.uniform(0.5, 1.1)))
    s.clay_diya(400, 790, 360, body="#8A3416", inner="#5A1A0A", paint=("#D9822E", "#B8501E", "#7A2A10"), tilt=0.22)
    s.flames[-1] = (400, 760, 150)
    sparks = s.sparks(400, 700, 900, 0.75, 300)
    save(s.render(bokeh=bokeh, sparks=sparks, reflection=890, vignette=0.4), "diya-sparkle")


def rangoli_crescent():
    s = Scene(1000, 1000, 13)
    s.background("#5A4632", "#2E2218")
    cx, cy, R = 470, 520, 330
    # The crescent: a large circle with an offset circle taken out of it.
    ox, r2 = cx + 105, R * 0.8
    yy, xx = np.mgrid[0:s.h * SS, 0:s.w * SS].astype(float) / SS
    crescent = (np.hypot(xx - cx, yy - cy) < R) & (np.hypot(xx - ox, yy - cy) > r2)
    petals = np.zeros((s.h * SS, s.w * SS, 3))
    base = np.array(rgb("#8E1240"), float)
    noise = gaussian_filter(s.rng.standard_normal((s.h * SS, s.w * SS)), 2.5)
    petals[:] = base * (1 + 0.9 * noise[..., None])
    arr = np.asarray(s.img, float)
    arr[..., :3] = np.where(crescent[..., None], np.clip(petals, 0, 255), arr[..., :3])
    s.img = Image.fromarray(arr.astype("uint8"), "RGBA")
    s.d = ImageDraw.Draw(s.img)
    # White borders of jasmine buds along both edges.
    for a in np.linspace(0, 2 * math.pi, 120, endpoint=False):
        x, y = cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a)
        if math.hypot(x - ox, y - cy) > r2:
            s.ellipse(x, y, 6, 5, fill=(246, 240, 226))
    for a in np.linspace(0, 2 * math.pi, 100, endpoint=False):
        x, y = ox + (r2 + 6) * math.cos(a), cy + (r2 + 6) * math.sin(a)
        if math.hypot(x - cx, y - cy) < R - 4:
            s.ellipse(x, y, 6, 5, fill=(246, 240, 226))
    # Marigolds and leaves around the outer edge.
    for i, a in enumerate(np.linspace(math.radians(-55), math.radians(235), 25)):
        a = -a
        lx, ly = cx + (R + 36) * math.cos(a), cy + (R + 36) * math.sin(a)
        s.leaf(lx, ly, a, 44)
    for i, a in enumerate(np.linspace(math.radians(-58), math.radians(238), 26)):
        a = -a
        s.marigold(cx + (R + 18) * math.cos(a), cy + (R + 18) * math.sin(a), 22, "orange" if i % 2 else "yellow")
    # Inside the crescent's opening: a fan of petals around a brass bowl.
    fx, fy = ox + 20, cy
    for i, a in enumerate(np.linspace(-1.25, 1.25, 7)):
        s.petal(fx + 60 * math.cos(a), fy + 60 * math.sin(a), a, 150, 34,
                ("#F28C28", "#F7B733")[i % 2], outline="#2E6B2A")
        s.petal(fx + 85 * math.cos(a), fy + 85 * math.sin(a), a, 95, 16, "#C2185B")
    for a in np.linspace(0, 2 * math.pi, 28, endpoint=False):
        s.petal(fx + 58 * math.cos(a), fy + 58 * math.sin(a), a, 42, 9, "#F4EEDC")
    s.ellipse(fx, fy, 56, 56, fill=rgb("#B07A2A"))
    s.ellipse(fx, fy, 48, 48, fill=rgb("#8E1240"))
    for i in range(30):
        a, r = s.rng.uniform(0, 2 * math.pi), s.rng.uniform(5, 42)
        s.ellipse(fx + r * math.cos(a), fy + r * math.sin(a), 5, 4, fill=(250, 244, 228) if i % 3 else rgb("#F7B733"))
    s.bowl_diya(fx, fy, 46)
    # Brass diyas standing round the whole design.
    for a in np.linspace(0, 2 * math.pi, 9, endpoint=False):
        s.bowl_diya(cx + 60 + (R + 120) * math.cos(a + 0.35), cy + (R + 120) * math.sin(a + 0.35) * 0.92, 54)
    save(s.render(warmth=1.15, vignette=0.55), "rangoli-crescent")


def diya_marigold():
    s = Scene(900, 1100, 17)
    s.background("#0B2418", "#06120C")
    d = s.d
    # Velvet lobes edged with gold beads, top and bottom.
    for cy_, colour in ((90, "#9E1638"), (1010, "#9E1638")):
        s.ellipse(450, cy_, 360, 230, fill=rgb(colour))
        for a in np.linspace(0, 2 * math.pi, 64, endpoint=False):
            s.ellipse(450 + 345 * math.cos(a), cy_ + 218 * math.sin(a), 9, 8, fill=rgb("#C9A04A"))
    for side in (-1, 1):
        s.ellipse(450 + side * 470, 560, 260, 300, fill=rgb("#13604F"))
        for a in np.linspace(0, 2 * math.pi, 60, endpoint=False):
            s.ellipse(450 + side * 470 + 248 * math.cos(a), 560 + 288 * math.sin(a), 8, 7, fill=rgb("#C9A04A"))
    for x, y in ((90, 1080), (810, 1080), (60, 40), (840, 40), (230, 1095), (670, 1095)):
        s.marigold(x, y, 52, "yellow")
    rings = {
        "rose": [("#C21E4E", "#D9B25A"), ("#E06AA0", None), ("#2E8B3A", "#D9B25A"), ("#B8D84A", None)],
        "blue": [("#1E8C8A", "#D9B25A"), ("#2244A8", None), ("#1B3C8C", "#D9B25A"), ("#3050B8", None)],
        "red": [("#B0163A", "#D9B25A"), ("#E8508A", None), ("#2840A0", "#D9B25A"), ("#1A2C7A", None)],
    }
    spots = [(450, 170, 125, "red"), (450, 390, 120, "rose"), (210, 520, 125, "rose"), (690, 520, 125, "rose"),
             (200, 790, 135, "blue"), (700, 790, 135, "blue"), (450, 1000, 150, "red")]
    for x, y, r, kind in spots:
        s.round_diya(x, y, r, rings[kind])
    for x, y in ((450, 560), (390, 650), (515, 650), (450, 760)):
        s.marigold(x, y, 66, "yellow")
    save(s.render(warmth=1.0, vignette=0.45), "diya-marigold")


def diya_row():
    s = Scene(1400, 230, 19, transparent=True)
    paints = [("#7A2814", "#B0306A", "#2AA0A0"), ("#5E2412", "#2E58B8", "#D2453A"), ("#6A2A12", "#2E9A4C", "#7A4FC0"),
              ("#6A1E22", "#1D3C8C", "#2FA36B"), ("#5A1E30", "#1E6B6A", "#E0648F")]
    for i in range(7):
        body, inner, accent = paints[i % len(paints)]
        s.clay_diya(110 + i * 195, 175, 130, body=body, inner=inner, paint=("#E8B23A", "#F2E2BE", accent))
    save(s.render(warmth=0.6), "diya-row", quality=86)


JOBS = {
    "diya-bokeh": diya_bokeh,
    "diya-sparkle": diya_sparkle,
    "rangoli-crescent": rangoli_crescent,
    "diya-marigold": diya_marigold,
    "diya-row": diya_row,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or JOBS:
        JOBS[name]()
