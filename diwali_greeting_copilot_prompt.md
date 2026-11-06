# Copilot Agent Prompt: Build a Unique Interactive Diwali Greeting Experience

## Role
Act as a senior creative technologist, interaction designer, frontend engineer, accessibility specialist, and web-security reviewer. Build a polished, personal Diwali greeting experience that I can host as a static site on GitHub Pages and safely share as a link with friends and family.

Do not produce only a concept, wireframe, or tutorial. Inspect the repository, make the implementation decisions, create the files, run the available checks, fix defects, and leave the repository ready to deploy.

## Product intent
Create an intimate digital keepsake, not a generic festival landing page. The emotional progression should be:

1. **Anticipation:** a quiet, elegant closed greeting or doorway.
2. **Participation:** the visitor lights a diya through one simple interaction.
3. **Reveal:** warm light spreads, the greeting appears, and restrained celebratory particles animate.
4. **Personal connection:** the visitor sees a short message and optional memory moments.
5. **Keepsake:** the experience ends with a shareable blessing and a way to replay it.

The experience should feel unmistakably Indian and Diwali-inspired without becoming visually crowded, culturally careless, or similar to a template marketplace card.

## First action: inspect before changing
Before editing anything:

1. Inspect the repository structure, existing files, package manager, framework, scripts, and Git status.
2. Read `README`, contribution instructions, and existing design or lint configurations.
3. Reuse a healthy existing stack. If the repository is empty, prefer a dependency-light static implementation using semantic HTML, modern CSS, and vanilla JavaScript. Use Vite only if a build tool provides a clear benefit.
4. Do not overwrite unrelated user work.
5. Summarize the implementation plan in the agent log, then proceed without waiting for confirmation unless a destructive action or unavailable secret is involved.

## Creative direction
Use the concept **“A Light From My Home to Yours.”**

The central visual metaphor is one diya whose light travels outward and becomes a constellation of small lamps, stars, or rangoli points. The visitor should feel that they personally completed the greeting by lighting it.

### Suggested visual language
- Background: deep midnight indigo or near-black blue, not pure black.
- Primary light: warm diya amber and soft gold.
- Accent: restrained marigold orange, magenta, peacock teal, or ruby.
- Surface treatment: subtle paper grain or textile-inspired texture created locally with CSS, a tiny inline SVG, or an optimized local asset.
- Motifs: diya, rangoli geometry, marigold petals, tiny stars, jali-inspired light, and soft bokeh.
- Avoid generic fireworks wallpaper, casino-like gold, excessive neon, clip-art deities, religious iconography used only as decoration, or an overloaded red-and-gold wedding aesthetic.

### Suggested palette
Use these as starting points, then tune contrast:
- Night: `#0B1026`
- Indigo: `#171A3A`
- Diya flame: `#FFD27A`
- Gold: `#E8A83A`
- Marigold: `#F28C28`
- Rose: `#B83B67`
- Teal: `#1F7A78`
- Warm text: `#FFF4D6`

### Typography
- Prefer a refined local/system font stack so the page works without third-party tracking or fragile font requests.
- Use a high-character display face only if it is committed as a properly licensed, subsetted local asset.
- Body text must remain highly readable on mobile.
- Do not imitate Devanagari letterforms with a Latin novelty font.

## Core visitor journey

### Scene 1: sealed greeting
Show a centered, elegant card or doorway with the line:

> A little light is waiting for you.

Primary control:

> Light the diya

The control must be a real `<button>`, keyboard accessible, clearly focused, and usable with touch. A subtle flame silhouette can respond to pointer movement, but the action must never depend on hover.

### Scene 2: lighting ritual
After activation:

1. Animate the wick catching light.
2. Expand a warm radial glow across the scene.
3. Reveal a rangoli gradually, as if drawn by light.
4. Release a short burst of marigold-like petals, gold dust, or tiny lamps.
5. Play no audio automatically.

Optional audio may be offered behind a clearly labeled, off-by-default control. Keep it short, local, compressed, and non-startling. The full experience must remain meaningful without audio.

### Scene 3: the greeting
Use this default copy, stored in one obvious configuration object or data file so I can edit it easily:

**Headline**

> Happy Diwali

**Primary message**

> May every light you kindle bring warmth to your home, courage to your heart, and joy to the paths we share. Wishing you and your loved ones a Diwali filled with peace, laughter, good health, and bright new beginnings.

**Personal sign-off**

> With warmth,  
> Abhishek

Add a restrained optional Hindi line:

> दीपावली की हार्दिक शुभकामनाएँ

Ensure the Hindi text is correctly encoded, rendered, and marked with an appropriate `lang` attribute. Do not use machine-translated text beyond the approved line above.

### Scene 4: memory moments
Create an optional “Little moments that light up the year” section. It should support three to five locally stored photos, each with:
- a short caption,
- meaningful alt text,
- responsive dimensions,
- lazy loading,
- and an optional date or place.

If no personal photos exist in the repository, do **not** download stock images or fabricate memories. Instead:
- create tasteful image placeholders that are clearly labeled for replacement,
- document the exact target filename, aspect ratio, recommended pixel dimensions, and compression target,
- and make the section easy to hide through configuration.

Recommended image preparation:
- portrait moments: `4:5`, approximately `1200 x 1500` pixels;
- landscape moments: `3:2`, approximately `1600 x 1067` pixels;
- prefer AVIF or WebP with a JPEG fallback only if the implementation supports it cleanly;
- target roughly `150 to 300 KB` per photo where quality permits;
- strip metadata, especially GPS and camera details, before publishing.

### Scene 5: closing blessing
End on a calm final panel:

> From my home to yours, may the light stay with you long after the lamps grow quiet.

Provide:
- **Replay** button;
- **Copy greeting** button using the Clipboard API with a graceful fallback;
- optional **Share** button using the Web Share API where supported, with a copy-link fallback;
- no forced social platform buttons;
- no visitor tracking.

## Personalization model
Create one easy-to-edit configuration module, such as `src/content.js`, `content.json`, or an equivalent appropriate to the stack. It should contain:

- sender name;
- recipient name or generic salutation;
- headline;
- English message;
- approved Hindi line;
- closing blessing;
- memory moments array;
- feature flags for photos, sound, sharing, and animation intensity;
- optional URL personalization parameter.

If URL personalization is implemented, support only a simple form such as `?to=Ananya`. Treat it as untrusted input:
- read it with `URLSearchParams`;
- trim it;
- limit it to 40 characters;
- render it with `textContent`, never `innerHTML`;
- do not interpret markup;
- fall back to “Dear friends and family” when absent or invalid;
- do not put private messages, email addresses, phone numbers, or secrets in URL parameters.

Document that personalized names in URLs can appear in browser history, screenshots, referrer logs, and link previews. Keep personalization optional and non-sensitive.

## Animation craft
Use animation to support the emotional arc, not to demonstrate technical excess.

- Favor CSS transforms and opacity.
- Use `requestAnimationFrame` only when justified.
- Cap or adapt particle count for small or low-powered devices. A practical starting range is 30 to 70 visible particles on desktop and 15 to 35 on mobile.
- Stop particle loops when the page is hidden.
- Do not allocate particles indefinitely.
- Avoid layout thrashing and large canvas buffers.
- Provide a complete static or near-static experience under `prefers-reduced-motion: reduce`.
- Disable parallax and nonessential movement for reduced motion.
- Avoid rapid flashing, high-frequency flicker, and strobing.
- Verify that text remains readable during and after every transition.

## Accessibility requirements
Target WCAG 2.2 AA where applicable.

- Semantic landmark structure: header, main, sections, footer as appropriate.
- Logical heading order.
- All functionality works with keyboard only.
- Highly visible focus states.
- Minimum practical touch target around `44 x 44 CSS px`.
- Sufficient color contrast, including text over glowing backgrounds.
- Decorative visuals hidden from assistive technology.
- Useful alt text for personal photos, not filenames.
- Announce meaningful state changes, such as the greeting reveal or copied status, with a restrained `aria-live` region.
- No audio autoplay.
- Test at `320 px` CSS width and at `200%` zoom.
- Preserve operation when JavaScript is unavailable by showing the essential greeting in a `<noscript>` or progressively enhanced base view.

## Security and privacy requirements
The deployed result must be a static site suitable for GitHub Pages.

1. Do not add backend code, databases, logins, forms that collect personal data, analytics, advertising, third-party trackers, remote embeds, or unnecessary network requests.
2. Do not include secrets, tokens, credentials, private photo metadata, private repository paths, or environment files in the published output.
3. Avoid inline event-handler attributes and dynamic HTML injection.
4. Never pass URL content into `innerHTML`, `insertAdjacentHTML`, `eval`, `new Function`, or unsafe template interpolation.
5. Minimize dependencies. Run the package manager's audit command if a package manager is used, assess the actual production exposure, and do not blindly apply breaking “force” fixes.
6. Pin important dependency versions through the lockfile.
7. Add a restrictive Content Security Policy where practical for the chosen architecture. Prefer an external JavaScript file so the policy can avoid `unsafe-inline` for scripts. If GitHub Pages limits response headers, use a documented `<meta http-equiv="Content-Security-Policy">` policy while acknowledging its limitations.
8. Add a conservative referrer policy through markup, such as `strict-origin-when-cross-origin` or stricter when compatible.
9. Keep all visual and audio assets local unless a remote asset is essential and explicitly documented.
10. Do not claim the site is “fully secure.” Document the threat model and residual limitations of a static public page.

## GitHub Pages deployment
Implement deployment appropriate to the detected repository.

- If this is a plain static site, ensure `index.html` is at the correct publish root or document the selected `/docs` setup.
- If a build tool is used, configure its base path correctly for a project site hosted at `https://<user>.github.io/<repository>/`.
- Prefer an official GitHub Actions Pages workflow when a build step is required.
- Grant the workflow the minimum necessary permissions.
- Do not require a custom domain.
- Use relative or base-aware asset paths so refreshes and project-site hosting work.
- Add a harmless `404.html` fallback only if it improves navigation for the selected architecture.
- Document repository Settings steps clearly: Pages source, branch or Actions workflow, and the final expected URL pattern.

## Performance budget
Aim for a fast experience on a mid-range mobile device and ordinary Indian mobile networks.

- Initial transfer target, excluding optional personal photos: preferably under `500 KB` compressed.
- Avoid shipping a heavy framework solely for a single greeting.
- Avoid uncompressed video backgrounds.
- Reserve image space to reduce layout shift.
- Use responsive images where useful.
- Lazy-load memory photos below the fold.
- Keep the first meaningful greeting usable even if optional assets fail.
- Run Lighthouse if Chrome tooling is available. Treat scores as diagnostics, not as the product goal. Address material accessibility, performance, best-practice, and SEO findings.

## Social preview and metadata
Add tasteful, non-sensitive sharing metadata:

- concise page title and description;
- theme color;
- favicon or small diya mark created locally;
- Open Graph metadata;
- Twitter card metadata if it adds no external dependency;
- canonical URL only when the final URL is known through configuration.

Create a dedicated social preview image if the available tooling supports it. It must not contain a recipient’s private name by default. If a preview asset cannot be generated reliably, provide precise instructions and dimensions, typically `1200 x 630` pixels, with a placeholder that does not break the page.

## SEO and robots
This is a greeting, not a discovery product. Add a simple configuration choice for indexing. Default to avoiding accidental broad discovery if the greeting contains personal photos. Explain that `noindex` reduces indexing but does not make a public GitHub Pages URL private or access-controlled.

## Quality assurance
Create and execute an appropriate validation checklist. At minimum:

1. Run formatting, lint, type checks, unit tests, and production build when those scripts exist.
2. Add small tests for any parsing or personalization logic.
3. Verify no DOM injection from `?to=` values such as `<img src=x onerror=alert(1)>`.
4. Verify an empty, whitespace-only, too-long, and Unicode recipient name.
5. Verify keyboard operation and focus order.
6. Verify reduced-motion behavior.
7. Verify mobile layouts at approximately `320`, `375`, `768`, and `1440` CSS pixels.
8. Verify refresh and asset loading under the GitHub Pages repository subpath.
9. Check for broken links and missing assets.
10. Check the browser console for errors.
11. Confirm essential content is visible when optional images or audio fail.
12. Confirm no secrets or accidental sensitive metadata are included in tracked files.

If browser automation is already available, use it. Do not add a large testing dependency only for superficial coverage.

## Required repository outputs
Produce the implementation and the following supporting files or equivalent sections:

- `README.md` with local preview and GitHub Pages deployment steps;
- a clearly documented content configuration file;
- `PRIVACY.md` explaining that the static page collects no data, while GitHub infrastructure may still process ordinary request metadata;
- `SECURITY.md` with the scope, safe customization rules, and how to report issues;
- an asset replacement guide for photos and optional audio;
- a short `TESTING.md` or README checklist recording checks completed and any checks that require manual verification;
- appropriate `.gitignore`;
- license notes for every non-original bundled asset.

Do not add placeholder legal claims that have not been verified. Keep documentation proportional to a small personal static site.

## Deliverable standard
The finished experience must:

- feel personal, calm, celebratory, and crafted;
- work as a shareable GitHub Pages link;
- remain complete without audio, third-party services, or personal photos;
- avoid exposing sensitive information;
- be responsive, keyboard usable, and reduced-motion friendly;
- be easy for me to customize by editing one content file;
- contain no dead controls or fake features;
- build and run from the documented commands.

## Final agent response
When implementation is complete, report:

1. the concept and interaction implemented;
2. files created or materially changed;
3. exact local run commands;
4. exact GitHub Pages deployment steps;
5. tests and checks run, with results;
6. performance or accessibility findings;
7. security and privacy decisions;
8. every remaining manual step, especially replacing photos, setting the repository name/base path, or enabling Pages;
9. the expected public URL pattern;
10. any known limitations.

Do not say something was tested, secured, deployed, or verified unless it actually was.
