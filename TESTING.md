# Testing

Run everything with:

```powershell
python tools/check.py      # writes qa/report.txt and screenshots in qa/
```

`tools/check.py` drives the locally installed Chrome through Playwright. It serves `site/` under `/diwali-greeting/`, the same sub-path GitHub Pages uses. The project has no npm, lint or build step, so there are no format, lint, type-check or `npm audit` scripts to run.

## Latest automated run

Date: 2026-11-06 · Chrome 156 (Windows) · **26/26 checks passed**

| Area | What was checked | Result |
| --- | --- | --- |
| Unit tests (`tests/unit.html`) | 42 cases for `?to=` sanitizing (empty, whitespace-only, 60-char, Devanagari, Tamil, diacritics, HTML/JS payloads, URLs, emails, control and bidi characters, malformed encoding), salutation, copy text, asset-path allow-list, share URL | 42/42 pass |
| Injection | `?to=` set to `<img src=x onerror=alert(1)>`, `<script>…`, `"><svg onload=…>`, `javascript:…`, `Ananya<b>bold</b>` | Fallback salutation every time, no injected nodes, no dialogs |
| Names | empty, `Ananya`, whitespace-only, 60 × `A`, `अनन्या`, `  Meera  Iyer ` | Fallback / `Dear Ananya,` / fallback / 40 chars / `Dear अनन्या,` / `Dear Meera Iyer,` |
| Keyboard | Tab order, Enter to light, focus moves to the heading, Replay returns focus to the button, visible 3 px focus ring | Pass |
| Live region | "The diya is lit." announced; "Greeting copied." in a status region | Pass |
| Copy | Clipboard API (text checked, share URL has no `?to=`); legacy `execCommand` fallback with the Clipboard API removed | Pass |
| Reduced motion | Reveal happens in the same click, with no particles and no flame loop; text fully visible | Pass |
| Particles | 56 on 1440 px, 28 on 375 px; canvas ≤ 2.5 MP; loop stops on its own; no frames while the page is hidden | Pass |
| Sound | Toggle starts `aria-pressed="false"`; no `AudioContext` until the visitor opts in | Pass |
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
- [ ] **Chime volume and feel** on phone speakers.
- [ ] **After deployment**: open https://abhi1ranjan.github.io/diwali-greeting/ and `?to=YourName`, then paste the link into WhatsApp or another messenger to check the preview card.
- [ ] **Photos**: after you add them, rerun `python tools/check.py`. It fails if any image still has EXIF or GPS data.
