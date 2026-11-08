# Testing

Run everything with:

```powershell
python tools/check.py      # writes qa/report.txt and screenshots in qa/
```

`tools/check.py` drives the locally installed Chrome through Playwright. It serves `site/` under `/diwali-greeting/`, the same sub-path GitHub Pages uses. The project has no npm, lint or build step, so there are no format, lint, type-check or `npm audit` scripts to run.

## Latest automated run

Date: 2026-11-08 · Chrome 154 (macOS) · **29/29 checks passed**

| Area | What was checked | Result |
| --- | --- | --- |
| Unit tests (`tests/unit.html`) | Salutation, copy text, asset-path allow-list, share URL | All pass |
| `?to=` ignored | `?to=` set to names and to `<img src=x onerror=alert(1)>`, `<script>…`, `"><svg onload=…>`, `javascript:…`, `Ananya<b>bold</b>` | "Dear friends and family," every time, no injected nodes, no dialogs |
| Keyboard | Tab order, Enter to light, focus moves to the heading, Replay returns focus to the button, visible 3 px focus ring | Pass |
| Live region | "The diya is lit." announced; "Greeting copied." in a status region | Pass |
| Copy | Clipboard API (text checked, share URL has no `?to=`); legacy `execCommand` fallback with the Clipboard API removed | Pass |
| Reduced motion | Reveal happens in the same click, with no particles and no flame loop; text fully visible | Pass |
| Particles | 56 on 1440 px, 28 on 375 px; canvas ≤ 2.5 MP; loop stops on its own; no frames while the page is hidden | Pass |
| Music | No `AudioContext` or media element before the first click. After **Light the diya** the 18-second clip is fetched once, decoded and looped in Web Audio; it stays audible for 28 s, past the loop point (RMS at least 0.002, peak below 0.99). The button stays visible and pauses it. Replay keeps one context and does not restart it; the button resumes it. If the clip returns 404, the synthesised loop plays instead | Pass |
| Photo wall | All 7 photos and the closing diya load, with alt text and no captions | Pass |
| No JavaScript | Full greeting, Hindi line and blessing visible; doorway, buttons and photo section hidden (no dead controls) | Pass |
| `main.js` blocked | Falls back to the static greeting | Pass |
| Missing photo | Placeholder "This photo could not be loaded."; caption and greeting kept | Pass |
| Layout | 320, 375, 768, 1440 px: no horizontal overflow; all buttons ≥ 44 × 44 px | Pass |
| 200% zoom | Approximated as 640 × 450 CSS px at 2× DPR: no overflow or clipped text | Pass |
| Sub-path | `/`, `index.html`, `?to=…`, CSS, JS, preview image all return 200 under `/diwali-greeting/`; reload works | Pass |
| Console / CSP | No console errors, no CSP violations, every request same-origin | Pass |
| Static scans | No inline handlers, inline scripts, `style=` attributes, `innerHTML`/`eval`; no remote resources apart from canonical/OG metadata; local references resolve; secret-pattern scan clean; no EXIF/XMP/GPS in images | Pass |
| Contrast | Body text 17.2:1, text at the brightest glow 8.4:1, headline 6.5:1, Hindi 5.6:1, button 8.7:1 | Pass (WCAG AA) |
| Size | Page assets ≈ 62 KB raw / ≈ 18 KB gzip (budget 500 KB), excluding the 93 KB social preview that only link scrapers fetch | Pass |

Screenshots of each layout are in `qa/`. That folder is git-ignored.

Note: the page's CSP blocks `eval`, which also blocks Playwright's `wait_for_function`. The script polls with `page.evaluate` instead, which confirms the CSP really is in force.

## Still needs a person

- [ ] **Real devices**: iPhone Safari and an Android phone, including the native Share sheet. Automation only covered desktop Chrome, where Share was shown but not pressed.
- [ ] **Firefox and Safari** rendering, especially SVG `pathLength` drawing and the Devanagari font fallback.
- [ ] **Screen reader**: NVDA or VoiceOver pass through the reveal, the announcements and the buttons.
- [ ] **Real 200% browser zoom** (Ctrl + +). It was only approximated above.
- [ ] **Lighthouse**: not run, because Node.js is not installed on this machine. In Chrome, open DevTools → Lighthouse against the deployed URL.
- [ ] **Music**: how it sounds, its volume and how it loops, on real phone speakers and headphones. Automation measures the signal but cannot judge it by ear. Also check iPhone behaviour with the silent switch on and after locking the screen.
- [ ] **Firework GIFs**: data use and smoothness on a real phone. They total about 7.7 MB, but only those near the screen are downloaded.
- [ ] **After deployment**: open https://diwali-greeting.diwali-greeting.workers.dev/ then paste the link into WhatsApp or another messenger to check the preview card.
- [ ] **Photos**: after you change them, rerun `python tools/check.py`. It fails if any image still has EXIF or GPS data.
