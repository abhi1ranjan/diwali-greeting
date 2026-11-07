# Assets: photos, festival art, music and license notes

## The festival wall

The "Little moments that light up the year" section mixes three kinds of image, all listed in the `moments` array in `site/src/content.js`:

- **Your photos**: `moment-1.webp` to `moment-5.webp`.
- **Rangoli art**: `art-rangoli-*.webp`, transparent cut-outs drawn by `tools/make_festival_art.py`.
- **Fireworks**: `fireworks-*.gif` with matching `fireworks-*-still.webp` frames, drawn by the same script. They are inspired by the style of each festival, not footage of it, and the page says so.

To regenerate the art, run `pip install numpy scipy pillow`, then `python tools/make_festival_art.py`. To move a picture, change its `shape` and `slot`; the slots are placed in `styles.css` under `.moment--slot-*`.

A GIF must have a `still` image. The page shows the still until the picture is on screen, when the visitor presses **Pause fireworks**, and for anyone who prefers reduced motion. Keep each GIF under about 2 MB and avoid full-frame flashes.

### 1. Prepare each photo

Any aspect ratio works. Keep the real proportions, with the long side no more than about 1600 px. Use `shape: 'round'` for images that still read well when cropped to a circle.

- Format: **WebP**. All current browsers support it. AVIF, JPEG and PNG also work.
- Size: aim for **150 to 300 KB** per photo.
- **Remove metadata, especially GPS location and camera details.**
- Keep original, unprocessed photos outside `site/`. The `originals/` folder is git-ignored.

One way to resize, crop and strip metadata with Pillow, which is already used by the tools:

```powershell
python -c "from PIL import Image, ImageOps; im = ImageOps.exif_transpose(Image.open('originals/diya-night.jpg')).convert('RGB'); im.thumbnail((1600, 1600)); im.save('site/assets/photos/moment-1.webp', 'WEBP', quality=80, method=6)"
```

Pillow writes a new file without EXIF, so this also removes GPS and camera data. Adjust `quality` (70 to 85) to stay within the size target. `python tools/check.py` fails if a published image still has EXIF, XMP or GPS data.

### 2. Point the content file at it

In `site/src/content.js`:

```js
{
  src: 'assets/photos/moment-1.webp',
  orientation: 'portrait',
  width: 1200,
  height: 1500,
  alt: 'Describe what is in the photo for someone who cannot see it',
  caption: 'A short caption',
  when: 'Diwali 2025',   // optional
  where: 'Pune'          // optional; omit if you prefer not to share places
}
```

- `src` must be a plain filename directly inside `assets/photos/`. Remote URLs, sub-folders, `..` and query strings are ignored for safety.
- `width` and `height` should match the real file. This reserves space and prevents layout shift.
- Images load lazily. If a file is missing or fails to load, a quiet placeholder appears and the caption stays.

## Music

By default, the page plays an original loop that JavaScript generates with the Web Audio API: a tanpura-style drone and plucks, a soft flute-like voice in the notes of Raag Bhupali, and an occasional temple bell. There is no file to download or license. It starts on the **Light the diya** click, fades in, and loops until the tab closes. Replay never starts a second copy. On phones, the system may stop it when the screen locks or the browser goes to the background, and the iPhone silent switch can mute it.

To use your own audio instead:

1. **Check the rights first.** This site is public, so publishing a file redistributes it. Use only audio you recorded yourself or have a license for, and record which here. Commercially released songs are not covered by owning a copy of them.
2. Trim a loop of 30 to 90 seconds, at 64 to 96 kbps and **under about 1 MB**, with low, normalised loudness. Prefer AAC in `.m4a` or Opus in `.webm`/`.ogg`, because MP3 leaves a small gap at the loop point.
3. Add it to `site/assets/audio/`, for example `diwali-loop.m4a`, and set `sound.src` to `'assets/audio/diwali-loop.m4a'` in `content.js`.

`sound.volume` sets the level (0.05 to 0.6). `sound.startOnLight: false` keeps music off until the visitor presses **Music**. `features.sound: false` removes music and the button entirely.

## Social preview and icons

| File | Size | Source |
| --- | --- | --- |
| `site/assets/img/social-preview.jpg` | 1200 × 630 | Rendered from `tools/social-card.html` by `python tools/make_images.py` |
| `site/assets/img/apple-touch-icon.png` | 180 × 180 | Rendered from `site/assets/img/diya.svg` by the same script |
| `site/assets/img/diya.svg` | vector | Hand-written for this project |

The preview has no recipient name. If you change the wording, edit `tools/social-card.html` and rerun the script. Messaging apps cache previews, so changes may take time to appear.

## License notes

All bundled artwork is original to this repository: diya and rangoli SVG artwork, CSS textures, the generated social preview and icon, and the rangoli art and firework animations drawn by `tools/make_festival_art.py`. The music is generated in the browser. There are no stock photos, icon packs, web fonts or audio files.

- **Fonts**: none are bundled. The page uses fonts already installed on the visitor's device. The social preview image was rendered on Windows with installed system fonts (Palatino Linotype, Nirmala UI). If you need to be strict about font licensing for that image, regenerate it on a machine with open-licensed fonts such as Noto Serif and Noto Sans Devanagari.
- **Photos and audio you add** belong to you. Only publish media you own or have permission to share, and ask the people in your photos before you publish them.
