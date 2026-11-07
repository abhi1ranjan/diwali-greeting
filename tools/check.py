"""Automated QA for the Diwali greeting.

Usage:  python tools/check.py            (writes qa/report.txt and qa/*.png)
Needs:  pip install playwright pillow    (drives the locally installed Chrome)

Covers unit tests, static safety scans, and browser checks served under the
same /diwali-greeting/ sub-path that GitHub Pages uses.
"""
from __future__ import annotations

import gzip
import json
import re
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote

from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from serve import BASE, make_server  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
QA = ROOT / "qa"
QA.mkdir(exist_ok=True)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

results: list[tuple[bool, str, str]] = []


def record(ok: bool, name: str, detail: str = "") -> None:
    results.append((bool(ok), name, detail))


def check(name: str):
    def wrap(fn):
        try:
            fn()
        except Exception as exc:  # report and keep going
            record(False, name, f"{type(exc).__name__}: {exc}")
        return fn
    return wrap


# ── Static checks ────────────────────────────────────────────────────────────

def text_files(base: Path):
    for path in base.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".html", ".js", ".css", ".svg", ".md", ".py", ".yml", ".txt", ".json"}:
            if ".git" in path.parts or ".venv" in path.parts or "qa" in path.relative_to(ROOT).parts[:1]:
                continue
            yield path


@check("static: local references resolve")
def _refs():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    refs = re.findall(r'(?:src|href)="([^"#]+)"', html)
    missing = [r for r in refs if not re.match(r"^[a-z]+:", r) and not (SITE / r).exists()]
    record(not missing, "static: local references resolve", f"{len(refs)} refs; missing={missing}")


@check("static: no inline handlers / unsafe DOM APIs in site")
def _unsafe():
    hits = []
    for path in SITE.rglob("*"):
        if path.suffix not in {".html", ".js"}:
            continue
        src = path.read_text(encoding="utf-8")
        if path.suffix == ".html":
            hits += [f"{path.name}: {m}" for m in re.findall(r"<[^>]*\son[a-z]+\s*=", src)]
            hits += [f"{path.name}: inline <script>" for m in re.findall(r"<script(?![^>]*\bsrc=)[^>]*>", src)]
            hits += [f"{path.name}: style attr" for m in re.findall(r"<[^>]*\sstyle\s*=", src)]
        else:
            hits += [f"{path.name}: {m}" for m in re.findall(r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|\beval\(|new Function", src)]
    record(not hits, "static: no inline handlers / unsafe DOM APIs in site", "; ".join(hits) or "none found")


@check("static: no remote resources in site")
def _remote():
    hits = []
    for path in SITE.rglob("*"):
        if path.suffix not in {".html", ".js", ".css"}:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            for url in re.findall(r"https?://[^\s\"')]+", line):
                # Absolute URLs are only allowed in canonical / Open Graph metadata.
                if 'rel="canonical"' in line or 'property="og:' in line:
                    continue
                hits.append(f"{path.name}: {url}")
    record(not hits, "static: no remote resources in site", "; ".join(hits) or "only canonical/og metadata URLs")


@check("static: secret scan")
def _secrets():
    pattern = re.compile(
        r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
        r"xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|(?i:(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"][^'\"]{6,}['\"]))"
    )
    hits = []
    for path in text_files(ROOT):
        if path.name == "check.py":
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{n}")
    env_files = [str(p.relative_to(ROOT)) for p in ROOT.rglob(".env*") if ".git" not in p.parts]
    record(not hits and not env_files, "static: secret scan", f"matches={hits} env_files={env_files}")


@check("static: image metadata stripped")
def _exif():
    bad = []
    for path in SITE.rglob("*"):
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}:
            with Image.open(path) as im:
                exif = im.getexif()
                extra = {k for k in im.info if k.lower() in {"exif", "xmp", "comment", "icc_profile", "gps"}}
                if len(exif) or extra:
                    bad.append(f"{path.name}: exif={len(exif)} {sorted(extra)}")
    record(not bad, "static: image metadata stripped", "; ".join(bad) or "no EXIF/XMP/GPS in site images")


@check("static: transfer size budget")
def _budget():
    total_raw = total_gz = 0
    for path in SITE.rglob("*"):
        if path.is_file() and "photos" not in path.parts and path.name != "social-preview.jpg" and path.name != "apple-touch-icon.png":
            data = path.read_bytes()
            total_raw += len(data)
            total_gz += len(gzip.compress(data)) if path.suffix in {".html", ".css", ".js", ".svg"} else len(data)
    record(total_gz < 500 * 1024, "static: transfer size budget",
           f"initial page assets {total_raw / 1024:.1f} KB raw, ~{total_gz / 1024:.1f} KB gzip (budget 500 KB)")


def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    chans = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in chans]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _blend(fg: str, bg: str, alpha: float) -> str:
    f = [int(fg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(bg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(fc * alpha + bc * (1 - alpha)):02x}" for fc, bc in zip(f, b))


@check("static: colour contrast")
def _contrast():
    glow_peak = _blend("#FFD27A", "#0B1026", 0.28)  # brightest point of the reveal glow
    pairs = {
        "text on night": ("#FFF4D6", "#0B1026", 4.5),
        "text on glow peak": ("#FFF4D6", glow_peak, 4.5),
        "flame headline on glow peak": ("#FFD27A", glow_peak, 3.0),
        "hindi on glow peak": ("#F5C26B", glow_peak, 4.5),
        "soft text (82%) on night": (_blend("#FFF4D6", "#0B1026", 0.82), "#0B1026", 4.5),
        "soft text (82%) on glow peak": (_blend("#FFF4D6", glow_peak, 0.82), glow_peak, 4.5),
        "button text on gold": ("#22130A", "#E8A83A", 4.5),
        "status flame on night": ("#FFD27A", "#0B1026", 4.5),
        "focus ring on night": ("#FFF4D6", "#0B1026", 3.0),
    }
    lines, ok = [], True
    for name, (fg, bg, need) in pairs.items():
        l1, l2 = sorted((_lum(fg), _lum(bg)), reverse=True)
        ratio = (l1 + 0.05) / (l2 + 0.05)
        ok &= ratio >= need
        lines.append(f"{name} {ratio:.1f}:1 (need {need})")
    record(ok, "static: colour contrast", "; ".join(lines))


# ── Browser checks ───────────────────────────────────────────────────────────

server = make_server(0)
PORT = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{PORT}{BASE}/"

AUDIO_PROBE = """
window.__audioContexts = 0;
const Real = window.AudioContext;
if (Real) window.AudioContext = class extends Real { constructor(...a) { super(...a); window.__audioContexts++; window.__audioContext = this; } };
const realConnect = AudioNode.prototype.connect;
AudioNode.prototype.connect = function (target, ...rest) {
  if (target instanceof AudioDestinationNode && !window.__meter) {
    window.__meter = this.context.createAnalyser();
    window.__meter.fftSize = 2048;
    realConnect.call(this, window.__meter);
  }
  return realConnect.call(this, target, ...rest);
};
window.__level = () => {
  const d = new Float32Array(2048);
  window.__meter.getFloatTimeDomainData(d);
  let sum = 0, peak = 0;
  for (const v of d) { sum += v * v; peak = Math.max(peak, Math.abs(v)); }
  return { rms: Math.sqrt(sum / d.length), peak };
};
window.__csp = [];
document.addEventListener('securitypolicyviolation', e => window.__csp.push(e.violatedDirective + ' ' + e.blockedURI));
"""


def open_page(browser, *, width=1440, height=900, query="", reduced=False, js=True, scale=1, route=None):
    ctx = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=scale,
                              reduced_motion="reduce" if reduced else "no-preference", java_script_enabled=js)
    page = ctx.new_page()
    page.__errors = []
    page.__requests = []
    page.__dialogs = []
    page.on("console", lambda m: m.type == "error" and page.__errors.append(m.text))
    page.on("pageerror", lambda e: page.__errors.append(str(e)))
    page.on("requestfinished", lambda r: page.__requests.append((r.url, r.response().status if r.response() else 0)))
    page.on("requestfailed", lambda r: page.__requests.append((r.url, -1)))
    page.on("dialog", lambda d: (page.__dialogs.append(d.message), d.dismiss()))
    if js:
        page.add_init_script(AUDIO_PROBE)
    if route:
        route(page)
    page.goto(URL + query, wait_until="load")
    return ctx, page


def wait_until(page, expression: str, timeout: int = 5000) -> None:
    # page.wait_for_function relies on eval(), which the page's CSP (correctly) blocks.
    deadline = time.perf_counter() + timeout / 1000
    while time.perf_counter() < deadline:
        if page.evaluate(expression):
            return
        page.wait_for_timeout(25)
    raise TimeoutError(f"timed out waiting for: {expression}")


def light(page):
    page.click("#light-button")
    wait_until(page, "document.body.dataset.scene === 'revealed'")


with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome")
    record(True, "browser", f"Chrome {browser.version}")

    @check("unit tests")
    def _unit():
        page = browser.new_page()
        page.goto((ROOT / "tests" / "unit.html").as_uri())
        page.wait_for_function("document.title !== 'RUNNING'", timeout=5000)
        out = page.inner_text("#results")
        record(page.title() == "PASS", "unit tests", out.strip().splitlines()[-1])
        (QA / "unit-results.txt").write_text(out, encoding="utf-8")
        page.close()

    @check("load: sealed scene, no errors, same-origin sub-path requests")
    def _load():
        ctx, page = open_page(browser)
        ok = page.is_visible("#light-button") and not page.is_visible("#greeting")
        ready = page.evaluate("document.documentElement.className")
        bad = [(u, s) for u, s in page.__requests if not u.startswith(URL) or s >= 400 or s < 0]
        csp = page.evaluate("window.__csp")
        audio = page.evaluate("window.__audioContexts")
        record(ok and "is-ready" in ready and not bad and not page.__errors and not csp and audio == 0,
               "load: sealed scene, no errors, same-origin sub-path requests",
               f"classes='{ready}' requests={len(page.__requests)} bad={bad} console_errors={page.__errors} csp={csp} audioContexts={audio}")
        ctx.close()

    @check("page reload / direct URLs under sub-path")
    def _reload():
        ctx, page = open_page(browser)
        statuses = []
        for path in ("", "index.html", "?to=Ananya", "assets/css/styles.css", "src/main.js", "assets/img/social-preview.jpg"):
            statuses.append((path or "/", page.goto(URL + path).status))
        page.reload()
        record(all(s == 200 for _, s in statuses), "page reload / direct URLs under sub-path", str(statuses))
        ctx.close()

    @check("structure: landmarks, headings, Hindi lang")
    def _structure():
        ctx, page = open_page(browser)
        light(page)
        info = page.evaluate("""() => ({
            landmarks: ['header','main','footer'].map(t => !!document.querySelector(t)),
            headings: [...document.querySelectorAll('h1,h2,h3')].map(h => h.tagName + ':' + h.textContent.trim()),
            hindiLang: document.getElementById('hindi-line').lang,
            hindiText: document.getElementById('hindi-line').textContent,
            decorativeHidden: [...document.querySelectorAll('svg')].every(s => s.closest('[aria-hidden="true"]') || s.getAttribute('aria-hidden') === 'true'),
        })""")
        ok = (all(info["landmarks"]) and info["headings"][0].startswith("H1:") and info["hindiLang"] == "hi"
              and info["hindiText"] == "दीपावली की हार्दिक शुभकामनाएँ" and info["decorativeHidden"])
        record(ok, "structure: landmarks, headings, Hindi lang", json.dumps(info, ensure_ascii=False))
        ctx.close()

    @check("keyboard: focus order, reveal, replay")
    def _keyboard():
        ctx, page = open_page(browser)
        active = lambda: page.evaluate("document.activeElement && document.activeElement.id")
        page.keyboard.press("Tab")
        first = active()
        outline = page.evaluate("getComputedStyle(document.activeElement).outlineStyle + ' ' + getComputedStyle(document.activeElement).outlineWidth")
        page.keyboard.press("Tab")
        second = active()
        page.keyboard.press("Shift+Tab")
        page.keyboard.press("Enter")
        wait_until(page, "document.body.dataset.scene === 'revealed'")
        after_reveal = active()
        page.wait_for_timeout(300)
        announced = page.inner_text("#announcer")
        order = []
        for _ in range(4):
            page.keyboard.press("Tab")
            order.append(active())
        page.focus("#replay-button")
        page.keyboard.press("Enter")
        scene = page.evaluate("document.body.dataset.scene")
        after_replay = active()
        ok = (first == "light-button" and second == "sound-toggle" and after_reveal == "greeting-title"
              and order[:4] == ["fireworks-toggle", "replay-button", "copy-button", "share-button"] and scene == "sealed"
              and after_replay == "light-button" and "none" not in outline and announced == "The diya is lit.")
        record(ok, "keyboard: focus order, reveal, replay",
               f"tab1={first} ({outline}) tab2={second} afterReveal={after_reveal} announced='{announced}' "
               f"next={order} afterReplay={after_replay} scene={scene}")
        ctx.close()

    @check("copy greeting via Clipboard API")
    def _copy():
        ctx, page = open_page(browser)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=f"http://127.0.0.1:{PORT}")
        page.goto(URL + "?to=Ananya")
        light(page)
        page.click("#copy-button")
        wait_until(page, "document.getElementById('action-status').textContent.length > 0")
        status = page.inner_text("#action-status")
        clip = page.evaluate("navigator.clipboard.readText()")
        share_label = page.inner_text("#share-button")
        ok = (status == "Greeting copied." and clip.startswith("Dear Ananya,") and "Happy Diwali" in clip
              and "दीपावली" in clip and clip.rstrip().endswith(URL) and "?to=" not in clip)
        record(ok, "copy greeting via Clipboard API",
               f"status='{status}' share_label='{share_label}' clipboard={clip!r}")
        ctx.close()

    @check("copy fallback when Clipboard API is unavailable")
    def _copy_fallback():
        ctx, page = open_page(browser, route=lambda p: p.add_init_script(
            "Object.defineProperty(navigator, 'clipboard', { get: () => undefined });"))
        light(page)
        page.click("#copy-button")
        wait_until(page, "document.getElementById('action-status').textContent.length > 0")
        status = page.inner_text("#action-status")
        focus = page.evaluate("document.activeElement.id")
        record(status in ("Greeting copied.", "Copying is blocked here. The message is selected so you can copy it yourself.")
               and focus == "copy-button" and not page.__errors,
               "copy fallback when Clipboard API is unavailable", f"status='{status}' focus={focus} errors={page.__errors}")
        ctx.close()

    @check("URL personalisation: injection payloads are inert")
    def _xss():
        payloads = ["<img src=x onerror=alert(1)>", "<script>alert(1)</script>", '"><svg onload=alert(1)>',
                    "javascript:alert(1)", "Ananya<b>bold</b>"]
        detail, ok = [], True
        for value in payloads:
            ctx, page = open_page(browser, query="?to=" + quote(value))
            light(page)
            page.wait_for_timeout(200)
            sal = page.inner_text("#salutation")
            injected = page.evaluate("document.querySelectorAll('[onerror],[onload],script:not([src]),img[src=\"x\"],b').length")
            good = sal == "Dear friends and family," and injected == 0 and not page.__dialogs and not page.__errors
            ok &= good
            detail.append(f"{value!r} -> {sal!r} injected={injected} dialogs={page.__dialogs}")
            ctx.close()
        record(ok, "URL personalisation: injection payloads are inert", " | ".join(detail))

    @check("URL personalisation: names")
    def _names():
        cases = [("", "Dear friends and family,"), ("Ananya", "Dear Ananya,"), ("   ", "Dear friends and family,"),
                 ("A" * 60, "Dear " + "A" * 40 + ","), ("अनन्या", "Dear अनन्या,"), ("  Meera  Iyer ", "Dear Meera Iyer,")]
        detail, ok = [], True
        for value, expected in cases:
            ctx, page = open_page(browser, query=("?to=" + quote(value)) if value else "")
            light(page)
            sal = page.inner_text("#salutation")
            ok &= sal == expected
            detail.append(f"{value!r} -> {sal!r}")
            ctx.close()
        record(ok, "URL personalisation: names", " | ".join(detail))

    @check("reduced motion: immediate, static reveal")
    def _reduced():
        ctx, page = open_page(browser, reduced=True)
        scene_after_click = page.evaluate("""() => {
            document.getElementById('light-button').click();
            return document.body.dataset.scene;
        }""")
        page.wait_for_timeout(300)
        info = page.evaluate("""() => ({
            particles: document.body.dataset.particles || null,
            riseDuration: getComputedStyle(document.querySelector('.rise')).animationDuration,
            flameDuration: getComputedStyle(document.querySelector('.diya--lit .diya__flame')).animationIterationCount,
            lamps: document.querySelectorAll('.lamp').length,
            messageOpacity: getComputedStyle(document.getElementById('message')).opacity,
        })""")
        page.wait_for_timeout(100)
        page.screenshot(path=str(QA / "reduced-motion-1440.png"))
        ok = scene_after_click == "revealed" and info["particles"] is None and info["riseDuration"] in ("1e-06s", "0.000001s", "0s") \
            and info["flameDuration"] == "1" and info["messageOpacity"] == "1"
        record(ok, "reduced motion: immediate, static reveal", f"scene right after click='{scene_after_click}' {info}")
        ctx.close()

    @check("particles: bounded count and loop stops")
    def _particles():
        detail, ok = [], True
        for width, height, lo, hi in ((1440, 900, 30, 70), (375, 812, 15, 35)):
            ctx, page = open_page(browser, width=width, height=height)
            light(page)
            wait_until(page, "document.body.dataset.particles !== undefined", 3000)
            count = int(page.evaluate("document.body.dataset.particles"))
            canvas = page.evaluate("[document.getElementById('particles').width, document.getElementById('particles').height]")
            wait_until(page, "document.body.dataset.particles === undefined", 8000)
            ok &= lo <= count <= hi and canvas[0] * canvas[1] <= 2.6e6
            detail.append(f"{width}px: {count} particles, canvas {canvas[0]}x{canvas[1]}, loop stopped")
            ctx.close()
        record(ok, "particles: bounded count and loop stops", "; ".join(detail))

    @check("particles pause while the page is hidden")
    def _hidden():
        ctx, page = open_page(browser)
        page.evaluate("""() => {
            window.__frames = 0;
            const raf = window.requestAnimationFrame.bind(window);
            window.requestAnimationFrame = (cb) => { window.__frames++; return raf(cb); };
        }""")
        light(page)
        wait_until(page, "document.body.dataset.particles !== undefined", 3000)
        page.evaluate("""() => {
            Object.defineProperty(document, 'hidden', { configurable: true, get: () => true });
            document.dispatchEvent(new Event('visibilitychange'));
            window.__framesAtHide = window.__frames;
        }""")
        page.wait_for_timeout(600)
        frames_hidden = page.evaluate("window.__frames - window.__framesAtHide")
        page.evaluate("""() => {
            Object.defineProperty(document, 'hidden', { configurable: true, get: () => false });
            document.dispatchEvent(new Event('visibilitychange'));
        }""")
        page.wait_for_timeout(300)
        resumed = page.evaluate("window.__frames - window.__framesAtHide")
        record(frames_hidden == 0 and resumed > 0, "particles pause while the page is hidden",
               f"frames while hidden={frames_hidden}, after visible={resumed}")
        ctx.close()

    @check("music: no audio before the first user gesture")
    def _music_gesture():
        ctx, page = open_page(browser)
        page.wait_for_timeout(500)
        contexts = page.evaluate("window.__audioContexts")
        media = page.evaluate("document.querySelectorAll('audio, video').length")
        record(contexts == 0 and media == 0 and not page.__errors, "music: no audio before the first user gesture",
               f"contexts on load={contexts} media elements={media} errors={page.__errors}")
        ctx.close()

    @check("music: starts on light, loops, button pauses, Replay adds no second copy")
    def _music_play():
        ctx, page = open_page(browser)
        pressed_before = page.get_attribute("#sound-toggle", "aria-pressed")
        light(page)
        started = page.evaluate("window.__audioContext.state")
        page.wait_for_timeout(2500)
        samples = []
        for _ in range(26):  # past several plucks, phrases and one scheduler refill cycle
            samples.append(page.evaluate("window.__level()"))
            page.wait_for_timeout(1000)
        rms = [s["rms"] for s in samples]
        peak = max(s["peak"] for s in samples)
        quiet = min(rms)
        visible = page.is_visible("#sound-toggle")
        page.click("#sound-toggle")
        page.wait_for_timeout(500)
        paused = page.evaluate("window.__audioContext.state")
        state_off = page.inner_text("#sound-state")
        page.focus("#replay-button")
        page.keyboard.press("Enter")
        page.wait_for_timeout(100)
        page.click("#light-button")
        wait_until(page, "document.body.dataset.scene === 'revealed'")
        still_paused = page.evaluate("window.__audioContext.state")
        page.click("#sound-toggle")
        page.wait_for_timeout(1200)
        resumed = page.evaluate("window.__audioContext.state")
        audible = page.evaluate("window.__level().rms")
        contexts = page.evaluate("window.__audioContexts")
        ok = (pressed_before == "true" and started == "running" and quiet > 0.002 and peak < 0.9 and visible
              and paused == "suspended" and state_off == "Off" and still_paused == "suspended"
              and resumed == "running" and audible > 0.001 and contexts == 1 and not page.__errors)
        record(ok, "music: starts on light, loops, button pauses, Replay adds no second copy",
               f"state={started} rms min={quiet:.4f} max={max(rms):.4f} peak={peak:.3f} over 26s; toggle visible={visible}; "
               f"paused={paused}/{state_off}; after replay={still_paused}; resumed={resumed} rms={audible:.4f}; contexts={contexts}; errors={page.__errors}")
        ctx.close()

    @check("gallery: all images load, GIFs play on screen, Pause and reduced motion use stills")
    def _gallery():
        def all_loaded(page):
            for item in page.locator(".moment").all():
                item.scroll_into_view_if_needed()
                page.wait_for_timeout(120)
            wait_until(page, "[...document.querySelectorAll('.moment img')].every(i => i.complete && i.naturalWidth > 0)", 15000)
        ctx, page = open_page(browser, width=1440, height=900)
        light(page)
        count = page.locator(".moment img").count()
        alts = page.evaluate("[...document.querySelectorAll('.moment img')].every(i => i.alt.length > 10)")
        all_loaded(page)
        last = page.locator(".moment--slot-p")
        last.scroll_into_view_if_needed()
        wait_until(page, "document.querySelector('.moment--slot-p img').currentSrc.endsWith('.gif')", 8000)
        page.click("#fireworks-toggle")
        stills = page.evaluate("[...document.querySelectorAll('.moment img')].filter(i => /fireworks-/.test(i.src)).every(i => i.getAttribute('src').endsWith('-still.webp'))")
        label = page.inner_text("#fireworks-toggle")
        errors = list(page.__errors)
        ctx.close()
        ctx = browser.new_context(reduced_motion="reduce", viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(URL)
        page.click("#light-button")
        page.locator(".moment--slot-p").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        reduced = page.evaluate("[...document.querySelectorAll('.moment img')].filter(i => /fireworks-/.test(i.src)).every(i => i.getAttribute('src').endsWith('-still.webp'))")
        ctx.close()
        record(count == 16 and alts and stills and label == "Play fireworks" and reduced and not errors,
               "gallery: all images load, GIFs play on screen, Pause and reduced motion use stills",
               f"images={count} alts ok={alts} stills after pause={stills} label='{label}' reduced motion stills={reduced} errors={errors}")

    @check("no-JS: full greeting, no dead controls")
    def _nojs():
        ctx, page = open_page(browser, js=False)
        info = {
            "greeting": page.is_visible("#greeting"),
            "headline": page.inner_text("#greeting-title"),
            "hindi": page.is_visible("#hindi-line"),
            "blessing": page.is_visible("#blessing"),
            "threshold": page.is_visible("#threshold"),
            "actions": page.is_visible("#actions"),
            "moments": page.is_visible("#moments"),
        }
        page.screenshot(path=str(QA / "no-js-1440.png"), full_page=True)
        ok = info["greeting"] and info["hindi"] and info["blessing"] and not info["threshold"] and not info["actions"] and not info["moments"]
        record(ok, "no-JS: full greeting, no dead controls", json.dumps(info, ensure_ascii=False))
        ctx.close()

    @check("main.js blocked: falls back to static greeting")
    def _blocked():
        ctx, page = open_page(browser, route=lambda p: p.route("**/src/main.js", lambda r: r.abort()))
        page.wait_for_timeout(200)
        cls = page.evaluate("document.documentElement.className")
        ok = "no-js" in cls and page.is_visible("#greeting") and not page.is_visible("#light-button")
        record(ok, "main.js blocked: falls back to static greeting", f"classes='{cls}'")
        ctx.close()

    @check("missing photo: placeholder, greeting intact")
    def _photo():
        def route(p):
            def fulfil(r):
                body = (SITE / "src" / "content.js").read_text(encoding="utf-8")
                head, tail = body.split("assets/photos/moment-1.webp", 1)
                tail = tail.replace("caption: ''", "caption: 'Test caption'", 1)
                body = head + "assets/photos/does-not-exist.webp" + tail
                r.fulfill(status=200, content_type="application/javascript", body=body)
            p.route("**/src/content.js", fulfil)
        ctx, page = open_page(browser, route=route)
        light(page)
        page.locator("#moments").scroll_into_view_if_needed()
        wait_until(page, "document.querySelector('.moment .moment__placeholder-title') && "
                         "document.querySelector('.moment .moment__placeholder-title').textContent.includes('could not')")
        caption = page.inner_text(".moment--slot-b .moment__caption-text")
        record(page.is_visible("#greeting-title") and caption == "Test caption", "missing photo: placeholder, greeting intact",
               f"first moment shows 'This photo could not be loaded.', caption kept='{caption}'")
        ctx.close()

    @check("responsive layouts")
    def _responsive():
        detail, ok = [], True
        for width, height in ((320, 640), (375, 812), (768, 1024), (1440, 900)):
            ctx, page = open_page(browser, width=width, height=height)
            page.wait_for_timeout(200)
            page.screenshot(path=str(QA / f"sealed-{width}.png"))
            btn = page.locator("#light-button").bounding_box()
            light(page)
            page.wait_for_timeout(3600)
            page.screenshot(path=str(QA / f"revealed-{width}.png"))
            for item in page.locator(".moment").all():
                item.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            page.screenshot(path=str(QA / f"revealed-{width}-full.png"), full_page=True)
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            small = page.evaluate("""() => [...document.querySelectorAll('button')].filter(b => b.offsetParent)
                .map(b => b.getBoundingClientRect()).filter(r => r.width < 44 || r.height < 44).length""")
            good = overflow <= 0 and small == 0 and btn["height"] >= 44 and not page.__errors
            ok &= good
            detail.append(f"{width}px overflowX={overflow} smallTargets={small} lightBtn={btn['width']:.0f}x{btn['height']:.0f}")
            ctx.close()
        record(ok, "responsive layouts", "; ".join(detail))

    @check("200% zoom (1280x900 window = 640x450 CSS px at 2x)")
    def _zoom():
        ctx, page = open_page(browser, width=640, height=450, scale=2)
        page.screenshot(path=str(QA / "zoom200-sealed.png"))
        light(page)
        page.wait_for_timeout(3600)
        page.screenshot(path=str(QA / "zoom200-revealed-full.png"), full_page=True)
        overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        clipped = page.evaluate("""() => [...document.querySelectorAll('p,h1,h2,button')].filter(e => e.offsetParent &&
            !e.classList.contains('visually-hidden') && (e.scrollWidth > e.clientWidth + 1)).map(e => e.id || e.className)""")
        record(overflow <= 0 and not clipped, "200% zoom (1280x900 window = 640x450 CSS px at 2x)",
               f"overflowX={overflow} clipped={clipped}")
        ctx.close()

    browser.close()

server.shutdown()

lines = [f"{'PASS' if ok else 'FAIL'}  {name}\n      {detail}" for ok, name, detail in results]
summary = f"\n{sum(ok for ok, _, _ in results)}/{len(results)} checks passed"
report = "\n".join(lines) + summary
(QA / "report.txt").write_text(report, encoding="utf-8")
print(report)
sys.exit(0 if all(ok for ok, _, _ in results) else 1)
