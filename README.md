# A Light From My Home to Yours: a Diwali greeting

This is a small interactive Diwali greeting that you can share as a link. The visitor sees a quiet arched doorway with an unlit diya. They press **Light the diya**, the flame catches, and warm light spreads. A rangoli draws itself in light, a short burst of marigold petals and gold dust rises, and small lamps travel out to form a constellation. Then the greeting appears, followed by optional memory photos and a closing blessing with **Replay**, **Copy greeting** and **Share**.

The site is plain HTML, CSS and JavaScript, with no framework, no build step and no runtime dependencies. It is hosted on GitHub Pages.

- Public URL: **https://abhi1ranjan.github.io/diwali-greeting/**
- Personalized link: `https://abhi1ranjan.github.io/diwali-greeting/?to=Ananya` (optional; see [PRIVACY.md](PRIVACY.md))

## Repository layout

```
site/                     ← the only folder that is published
  index.html              page structure + no-JavaScript fallback text + CSP/meta tags
  src/content.js          ★ all editable text, photos list and feature flags
  src/main.js             interaction, animation, copy/share, sound
  src/personalize.js      pure helpers: ?to= sanitising, text building (unit-tested)
  src/boot.js             tiny pre-paint script; falls back to static view if JS fails
  assets/css/styles.css   all styling, motion and reduced-motion rules
  assets/img/             favicon (SVG), touch icon, social preview
  assets/photos/          your memory photos go here (see ASSETS.md)
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
| `moments` | `true` | Shows the memory section. **Set it to `false`, or add photos, before sharing.** It currently shows labeled placeholders. |
| `sound` | `true` | Shows an off-by-default **Soft chime** toggle. Nothing ever autoplays. |
| `share` | `true` | Shows **Share** (Web Share API), or **Copy link** where sharing is unsupported. |
| `hindiLine` | `true` | Shows *दीपावली की हार्दिक शुभकामनाएँ*. |
| `urlPersonalization` | `true` | Reads `?to=Name` and shows "Dear Name,". |
| `animation` | `'full'` | `'gentle'` uses fewer particles. `'minimal'` gives a static reveal. Visitors with *reduced motion* turned on always get the static reveal. |

If you change the wording, also update the matching text inside `<main>` in `site/index.html`. Visitors without JavaScript see that copy, and link previews read it.

For photos and audio, see [ASSETS.md](ASSETS.md).

## Preview locally

You need Python 3.

```powershell
python tools/serve.py
```

Open http://127.0.0.1:8000/diwali-greeting/ (and try `?to=Ananya`). The server publishes `site/` under the same `/diwali-greeting/` sub-path that GitHub Pages uses, so path mistakes show up locally.

## Test

```powershell
python -m pip install --user playwright pillow   # one time; uses your installed Chrome
python tools/check.py
```

This runs the unit tests, static safety scans and browser checks, and writes `qa/report.txt` plus screenshots. You can also open `tests/unit.html` directly in any browser. See [TESTING.md](TESTING.md) for the latest results and the checks that still need a person.

## Deploy to GitHub Pages

1. On GitHub, create an **empty public repository** named `diwali-greeting` under `abhi1ranjan`. Do not add a README, license or .gitignore.
2. Push this folder:
   ```powershell
   git remote add origin https://github.com/abhi1ranjan/diwali-greeting.git
   git push -u origin main
   ```
3. In the repository, go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
4. Go to the **Actions** tab. If the first "Deploy to GitHub Pages" run failed because Pages was not enabled yet, open it and choose **Re-run all jobs**. Later pushes to `main` deploy automatically.
5. Visit **https://abhi1ranjan.github.io/diwali-greeting/**.

The workflow publishes only `site/`. Tests, tools and docs are never served. It uses read-only repository access and only the `pages`/`id-token` permissions that deployment needs.

**If you rename the repository** or use a different account, the page itself still works, because all asset paths are relative. Update the absolute URLs in `site/index.html` (`canonical`, `og:url`, `og:image`), plus `BASE` in `tools/serve.py` and this README.

## Indexing

`site/index.html` includes `<meta name="robots" content="noindex, nofollow">`, which asks search engines not to list a personal page. This is **not** privacy or access control. Anyone with the link can open it, and the repository is public. To allow indexing, remove that line. A `robots.txt` would not help on a project site, because crawlers only read it at the domain root.

## More

- [PRIVACY.md](PRIVACY.md): what the page does and does not collect
- [SECURITY.md](SECURITY.md): threat model, safe customization rules, how to report issues
- [ASSETS.md](ASSETS.md): photo and audio replacement guide, license notes
- [TESTING.md](TESTING.md): checks run and results
