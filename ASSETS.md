# Assets: photos, festival art, music and license notes

## The festival wall

The "Little moments that light up the year" section mixes three kinds of image, all listed in the `moments` array in `site/src/content.js`:

- **Your photos**: `moment-1.webp` to `moment-5.webp`.
- **Rangoli art**: `art-rangoli-*.webp`, transparent cut-outs drawn by `tools/make_festival_art.py`.
- **Diya pictures**: `diya-bokeh.webp`, `diya-marigold.webp` and `rangoli-crescent.webp`, drawn by `tools/make_diya_art.py`. The same script draws `site/assets/img/diya-row.webp` (under the greeting) and `diya-sparkle.webp` (above the closing blessing).
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

The page plays **"Shaam Rangoli Si Raatein Taaron Wali"** by Vishal Mishra from `site/assets/audio/diwali-song.m4a`, used under the owner's licence. It starts on the **Light the diya** click (browsers block sound before a click), fades in to a gentle level and loops until the tab closes. The **Music** button stays on screen and stops it at any time, and Replay never starts a second copy. On phones, the system may stop it when the screen locks, and the iPhone silent switch can mute it.

The file was prepared from the 320 kbps MP3 with a 1-second fade-in and a 4-second fade-out, so the loop restarts smoothly. It was encoded as AAC at 96 kbps, which is about 3.5 MB, and it streams, so playback starts before the whole file arrives.

If the file is missing or cannot be played, the page falls back to an original loop generated in the browser: a tanpura-style drone, a soft flute line in Raag Bhupali and an occasional temple bell.

### Changing the song

1. **Check the rights.** The site is public, so publishing a song redistributes it. Use only audio you recorded yourself or have a licence for.
2. **Convert it** to AAC (`.m4a`) at 96 kbps, which keeps the file small. On a Mac, you can use the built-in `afconvert`:
   ```bash
   afconvert -f m4af -d aac -b 96000 "My Song.mp3" site/assets/audio/my-song.m4a
   ```
   Or, with ffmpeg: `ffmpeg -i "My Song.mp3" -vn -map_metadata -1 -c:a aac -b:a 96k site/assets/audio/my-song.m4a`. File names must use only letters, numbers, `-` and `_`, with no spaces.
3. **Point the page at it.** In `site/src/content.js`, set `sound.src` to `'assets/audio/my-song.m4a'`. `.mp3`, `.ogg`, `.opus` and `.webm` also work.
4. **Remove the old file** from `site/assets/audio/` if you no longer use it.
5. **Publish:** run `wrangler deploy` (the site updates within seconds), then `git add -A site && git commit -m "Change the music" && git push` to keep GitHub in sync.

To use the generated loop instead of a song, set `sound.src` to `''`. `sound.volume` sets the level (0.05 to 0.6). `sound.startOnLight: false` keeps music off until the visitor presses **Music**. `features.sound: false` removes music and the button entirely.

## Social preview and icons

| File | Size | Source |
| --- | --- | --- |
| `site/assets/img/social-preview.jpg` | 1200 × 630 | Rendered from `tools/social-card.html` by `python tools/make_images.py` |
| `site/assets/img/apple-touch-icon.png` | 180 × 180 | Rendered from `site/assets/img/diya.svg` by the same script |
| `site/assets/img/diya.svg` | vector | Hand-written for this project |

The preview has no recipient name. If you change the wording, edit `tools/social-card.html` and rerun the script. Messaging apps cache previews, so changes may take time to appear.

## License notes

All bundled artwork is original to this repository: diya and rangoli SVG artwork, CSS textures, the generated social preview and icon, and the rangoli art and firework animations drawn by `tools/make_festival_art.py`. The diya and flower-rangoli pictures (`diya-*.webp`, `rangoli-crescent.webp`) are original illustrations drawn by `tools/make_diya_art.py`. There are no stock photos, icon packs or web fonts. The song in `site/assets/audio/` is used under the owner's licence.

- **Fonts**: none are bundled. The page uses fonts already installed on the visitor's device. The social preview image was rendered on Windows with installed system fonts (Palatino Linotype, Nirmala UI). If you need to be strict about font licensing for that image, regenerate it on a machine with open-licensed fonts such as Noto Serif and Noto Sans Devanagari.
- **Photos and audio you add** belong to you. Only publish media you own or have permission to share, and ask the people in your photos before you publish them.
