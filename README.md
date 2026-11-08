# A Light From My Home to Yours: a Diwali greeting

This is a small interactive Diwali greeting that you can share as a link. The visitor sees a quiet arched doorway with an unlit diya. They press **Light the diya**, the flame catches, warm light spreads, and a short clip of "Jai Raghuvanshi" begins and loops until the tab closes (the **Music** button stops it at any time). A rangoli draws itself in light, a short burst of marigold petals and gold dust rises, and small lamps travel out to form a constellation. Then the greeting appears, followed by a wall of Diwali photos (diyas, rangoli and festive lights), and a closing blessing with **Replay**, **Copy greeting** and **Share**.

The site is plain HTML, CSS and JavaScript, with no framework, no build step and no runtime dependencies. It is hosted on Cloudflare (Workers static assets, free plan). GitHub holds the source code.

- Public URL: **https://diwali-greeting.diwali-greeting.workers.dev/**

## Repository layout

```
site/                     ← the only folder that is published
  index.html              page structure + no-JavaScript fallback text + CSP/meta tags
  src/content.js          ★ all editable text, photos list and feature flags
  src/main.js             interaction, animation, copy/share, sound
  src/personalize.js      pure helpers: text building, safe asset paths (unit-tested)
  src/boot.js             tiny pre-paint script; falls back to static view if JS fails
  assets/css/styles.css   all styling, motion and reduced-motion rules
  assets/img/             favicon (SVG), touch icon, social preview
  assets/photos/          the Diwali photos on the wall (see ASSETS.md)
tests/                    unit tests (open tests/unit.html in a browser)
tools/serve.py            local server that mimics the GitHub Pages sub-path
tools/check.py            automated QA (unit, static scans, browser checks)
tools/make_images.py      regenerates social preview + touch icon
tools/social-card.html    source for the social preview image
.github/workflows/pages.yml  deploys site/ to GitHub Pages
```

## Customize

Edit **`site/src/content.js`**. It holds the sender, salutation, headline, message, Hindi line, sign-off, blessing, memory moments, share text, sound source and feature flags:

| Flag | Default | Effect |
| --- | --- | --- |
| `moments` | `true` | Shows the wall of Diwali photos. |
| `sound` | `true` | Plays the song in `sound.src` (see ASSETS.md → Changing the song), looping, from the **Light the diya** click, with a **Music** on/off button that is always on screen. Nothing can play before that first click. Set `sound.startOnLight: false` to keep it off until the visitor turns it on. |
| `share` | `true` | Shows **Share** (Web Share API), or **Copy link** where sharing is unsupported. |
| `hindiLine` | `true` | Shows *दीपावली की हार्दिक शुभकामनाएँ*. |
| `animation` | `'full'` | `'gentle'` uses fewer particles. `'minimal'` gives a static reveal. Visitors with *reduced motion* turned on always get the static reveal. |

If you change the wording, also update the matching text inside `<main>` in `site/index.html`. Visitors without JavaScript see that copy, and link previews read it.

For photos and audio, see [ASSETS.md](ASSETS.md).

## Preview locally

You need Python 3.

```powershell
python tools/serve.py
```

Open http://127.0.0.1:8000/diwali-greeting/. The server publishes `site/` under the same `/diwali-greeting/` sub-path that GitHub Pages uses, so path mistakes show up locally.

## Test

```powershell
python -m pip install --user playwright pillow   # one time; uses your installed Chrome
python tools/check.py
```

This runs the unit tests, static safety scans and browser checks, and writes `qa/report.txt` plus screenshots. You can also open `tests/unit.html` directly in any browser. See [TESTING.md](TESTING.md) for the latest results and the checks that still need a person.

## Deploy (Cloudflare)

The live site is served by Cloudflare from the `site/` folder, using the settings in `wrangler.jsonc`. GitHub Actions is not needed.

1. One-time setup: `npm install -g wrangler`, then `wrangler login` and click **Allow** in the browser (Cloudflare account: the owner's).
2. After any change, from this folder:
   ```bash
   wrangler deploy          # publishes site/ in a few seconds
   git add -A && git commit -m "Describe the change" && git push   # keeps GitHub in sync
   ```
3. Visit **https://diwali-greeting.diwali-greeting.workers.dev/**.

Only `site/` is uploaded. Tests, tools and docs are never served. Request logging (`observability`) is turned off in `wrangler.jsonc`, in line with [PRIVACY.md](PRIVACY.md).

`.github/workflows/pages.yml` still deploys to GitHub Pages on every push, but GitHub has stopped running it because of a billing lock on the account. If that lock is cleared, both addresses will work.

**If the address changes**, the page itself still works, because all asset paths are relative. Update the absolute URLs in `site/index.html` (`canonical`, `og:url`, `og:image`), plus `BASE` in `tools/serve.py` and this README.

## Indexing

`site/index.html` includes `<meta name="robots" content="noindex, nofollow">`, which asks search engines not to list a personal page. This is **not** privacy or access control. Anyone with the link can open it, and the repository is public. To allow indexing, remove that line. A `robots.txt` would not help on a project site, because crawlers only read it at the domain root.

## More

- [PRIVACY.md](PRIVACY.md): what the page does and does not collect
- [SECURITY.md](SECURITY.md): threat model, safe customization rules, how to report issues
- [ASSETS.md](ASSETS.md): photo and audio replacement guide, license notes
- [TESTING.md](TESTING.md): checks run and results
