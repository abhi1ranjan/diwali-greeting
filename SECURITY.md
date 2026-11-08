# Security

## Scope

This repository contains a public, static greeting page: HTML, CSS and vanilla JavaScript on GitHub Pages. It has no backend, database, login, form, API key or third-party service, and it has no runtime dependencies. The page is not "fully secure," but it has very little attack surface.

## Threat model

| Concern | Mitigation | Residual risk |
| --- | --- | --- |
| URL parameters | The page reads nothing from the URL. `?to=` and other parameters are ignored, and browser tests confirm HTML/JS payloads have no effect. | None known. |
| Injection through content config | No `innerHTML`, `insertAdjacentHTML`, `eval`, `new Function` or `document.write`. Photo and audio paths must be plain filenames under `assets/photos/` or `assets/audio/`. | Whoever can commit to the repo controls the page. Protect your GitHub account with 2FA. |
| Third-party script or tracker compromise | Every asset is local. The CSP is `default-src 'none'` and allows only `'self'` for scripts, styles, images and media. It has no `unsafe-inline`, and `connect-src 'self'` only lets the page download its own song file. | The CSP is a `<meta>` tag, because the static host sets no custom headers. A meta CSP cannot set `frame-ancestors`, so another site could frame the page. The page has no actions that clickjacking could abuse. |
| Leaking personal data | No secrets in the repo. `.gitignore` excludes `.env`, keys and raw photo formats. `tools/check.py` scans for common token patterns and checks published images for EXIF/XMP/GPS data. `Referrer-Policy: no-referrer`. | Anyone with the URL can see everything published. `noindex` is a request to search engines, not access control. |
| Supply chain (CI) | The workflow uses only official `actions/*` steps, pinned to commit SHAs. Default token is `contents: read`. The deploy job adds only `pages: write` and `id-token: write`. `persist-credentials: false`. | Pinned actions need occasional manual updates. |
| Supply chain (site) | No npm packages, so there is nothing to audit. | None for the published site. Playwright and Pillow are local QA tools only and are never deployed. |

## Safe customization rules

1. Edit text only in `site/src/content.js` and the matching fallback text in `site/index.html`. Use plain text, never HTML.
2. Keep photos and audio local under `site/assets/photos/` and `site/assets/audio/`. Remove metadata first (see [ASSETS.md](ASSETS.md)).
3. Do not add `<script>` tags that point to other sites, `on...=` attributes, inline `<script>` or `style="..."` attributes. The CSP blocks them by design.
4. Do not add analytics, embeds, web fonts from CDNs or forms. If you must, update the CSP, [PRIVACY.md](PRIVACY.md) and this file.
5. Never commit tokens, `.env` files or private photos you do not want public.
6. Run `python tools/check.py` before you push.

## Reporting a problem

If you find a security or privacy issue with this page, please contact the owner privately. Do not open a public issue.

- Use GitHub's **Report a vulnerability** button on the repository's Security tab, if private vulnerability reporting is enabled.
- Otherwise, contact [@abhi1ranjan](https://github.com/abhi1ranjan) through GitHub.
