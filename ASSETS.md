# Assets: replacing photos and audio, and license notes

## Memory photos

The "Little moments that light up the year" section shows 3 to 5 photos. It has **three labeled placeholders** right now. Before you share the link, either add real photos or hide the section by setting `features.moments: false` in `site/src/content.js`.

### 1. Prepare each photo

| Orientation | Aspect ratio | Recommended size | `orientation` value |
| --- | --- | --- | --- |
| Portrait | 4:5 | 1200 × 1500 px | `'portrait'` |
| Landscape | 3:2 | 1600 × 1067 px | `'landscape'` |

- Format: **WebP**. All current browsers support it. AVIF, JPEG and PNG also work.
- Size: aim for **150 to 300 KB** per photo.
- **Remove metadata, especially GPS location and camera details.**
- Keep original, unprocessed photos outside `site/`. The `originals/` folder is git-ignored.

One way to resize, crop and strip metadata with Pillow, which is already used by the tools:

```powershell
python -c "from PIL import Image, ImageOps; im = ImageOps.exif_transpose(Image.open('originals/diya-night.jpg')).convert('RGB'); ImageOps.fit(im, (1200, 1500)).save('site/assets/photos/moment-1.webp', 'WEBP', quality=80, method=6)"
```

Pillow writes a new file without EXIF, so this also removes GPS and camera data. For landscape photos, use `(1600, 1067)`. Adjust `quality` (70 to 85) to stay within the size target. `python tools/check.py` fails if a published image still has EXIF, XMP or GPS data.

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

## Optional audio

By default, the **Soft chime** toggle plays a short bell sound. JavaScript generates it with the Web Audio API, so there is no file to download or license. It never plays unless the visitor turns the toggle on.

To use your own recording instead:

1. Add a short, quiet clip (under 3 seconds, under 60 KB, MP3/M4A/OGG/Opus) to `site/assets/audio/`, for example `chime.mp3`. Use only audio you recorded yourself or have a license for.
2. Set `sound: { src: 'assets/audio/chime.mp3' }` in `content.js`.
3. To remove the sound control entirely, set `features.sound: false`.

## Social preview and icons

| File | Size | Source |
| --- | --- | --- |
| `site/assets/img/social-preview.jpg` | 1200 × 630 | Rendered from `tools/social-card.html` by `python tools/make_images.py` |
| `site/assets/img/apple-touch-icon.png` | 180 × 180 | Rendered from `site/assets/img/diya.svg` by the same script |
| `site/assets/img/diya.svg` | vector | Hand-written for this project |

The preview has no recipient name. If you change the wording, edit `tools/social-card.html` and rerun the script. Messaging apps cache previews, so changes may take time to appear.

## License notes

All bundled visual assets are original to this repository: diya and rangoli SVG artwork, CSS textures and the generated social preview and icon. There are no stock photos, icon packs, web fonts or audio files.

- **Fonts**: none are bundled. The page uses fonts already installed on the visitor's device. The social preview image was rendered on Windows with installed system fonts (Palatino Linotype, Nirmala UI). If you need to be strict about font licensing for that image, regenerate it on a machine with open-licensed fonts such as Noto Serif and Noto Sans Devanagari.
- **Photos and audio you add** belong to you. Only publish media you own or have permission to share, and ask the people in your photos before you publish them.
