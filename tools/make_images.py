"""Render the social preview (1200x630 JPEG) and apple-touch-icon (180x180 PNG).

Usage:  python tools/make_images.py
Needs:  pip install playwright pillow   (uses the locally installed Chrome)
Output files are re-encoded with Pillow so they carry no EXIF/text metadata.
"""
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "site" / "assets" / "img"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.goto((ROOT / "tools" / "social-card.html").as_uri())
        page.wait_for_timeout(300)
        shot = Image.open(BytesIO(page.screenshot(type="png"))).convert("RGB")
        shot.save(IMG / "social-preview.jpg", "JPEG", quality=84, optimize=True, progressive=True)

        icon = browser.new_page(viewport={"width": 180, "height": 180})
        icon.goto((IMG / "diya.svg").as_uri())
        icon.wait_for_timeout(200)
        # iOS applies its own rounded mask, so fill the transparent corners.
        glyph = Image.open(BytesIO(icon.screenshot(type="png", omit_background=True))).convert("RGBA")
        tile = Image.new("RGBA", glyph.size, "#0B1026")
        tile.alpha_composite(glyph)
        tile.convert("RGB").save(IMG / "apple-touch-icon.png", "PNG", optimize=True)
        browser.close()

    for name in ("social-preview.jpg", "apple-touch-icon.png"):
        path = IMG / name
        with Image.open(path) as im:
            print(f"{name}: {im.size[0]}x{im.size[1]}, {path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
