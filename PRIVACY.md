# Privacy

This is a static greeting page. It is plain HTML, CSS and JavaScript served by Cloudflare.

## What the page itself does

- No cookies, `localStorage` or `sessionStorage`.
- No analytics, advertising, tracking pixels, fonts or scripts from other sites, or remote embeds.
- No forms, logins or accounts. The page does not send data anywhere. Its only network request from script is to download its own song file (Content Security Policy `connect-src 'self'`).
- All images, styles and scripts load from the same site. The music file is served from this same site. Nothing plays until you click **Light the diya**, and the **Music** button stops it at any time.
- **Copy greeting** and **Share** run only when you press them. Copying puts text on your own clipboard. Sharing opens your device's share sheet or copies the link.
- The page sets `Referrer-Policy: no-referrer` (as a `<meta>` tag). When someone follows a link out of the page, the browser does not send this page's address.

## What Cloudflare may still process

Cloudflare hosts the page. Like any web host, it receives ordinary request data, such as IP address, user agent, requested URL and time, and may process it for security and operations under the [Cloudflare Privacy Policy](https://www.cloudflare.com/privacypolicy/). Request logging for this site is turned off in `wrangler.jsonc`. The source code is on GitHub.

## No names in links

The page no longer reads names from the link. A `?to=` parameter, or any other, is ignored, so every visitor sees "Dear friends and family,".

## Photos

Before you publish personal photos, remove their location (GPS) and camera metadata. See [ASSETS.md](ASSETS.md). Anyone with the link can see the published photos. `noindex` asks search engines not to list the page, but the page is still public.
