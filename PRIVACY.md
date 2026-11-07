# Privacy

This is a static greeting page. It is plain HTML, CSS and JavaScript served by GitHub Pages.

## What the page itself does

- No cookies, `localStorage` or `sessionStorage`.
- No analytics, advertising, tracking pixels, fonts or scripts from other sites, or remote embeds.
- No forms, logins or accounts. The page does not send data anywhere. Its Content Security Policy sets `connect-src 'none'`.
- All images, styles and scripts load from the same site. The music file is served from this same site. Nothing plays until you click **Light the diya**, and the **Music** button stops it at any time.
- **Copy greeting** and **Share** run only when you press them. Copying puts text on your own clipboard. Sharing opens your device's share sheet or copies the link.
- The page sets `Referrer-Policy: no-referrer` (as a `<meta>` tag). When someone follows a link out of the page, the browser does not send this page's address.

## What GitHub may still process

GitHub hosts the page. Like any web host, GitHub Pages receives ordinary request data, such as IP address, user agent, requested URL and time. It may log that data for security and operations under the [GitHub Privacy Statement](https://docs.github.com/site-policy/privacy-policies/github-privacy-statement). This page does not control that data.

## Names in links (`?to=Name`)

If you share a link such as `.../diwali-greeting/?to=Ananya`, the name is part of the URL. It can appear in:

- the browser history and synced devices of the sender and recipient,
- screenshots, chat messages and messaging-app link previews,
- server request logs, including GitHub's.

Use first names or nicknames only. Never put email addresses, phone numbers or private messages in the link. The **Share** and **Copy greeting** buttons use the plain page address, without `?to=`.

## Photos

Before you publish personal photos, remove their location (GPS) and camera metadata. See [ASSETS.md](ASSETS.md). Anyone with the link can see the published photos. `noindex` asks search engines not to list the page, but the page is still public.
