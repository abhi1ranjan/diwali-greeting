// The interactive greeting. Loaded with `defer` after content.js and personalize.js.
// All visitor-facing text is written with textContent; nothing is parsed as HTML.
(function () {
  'use strict';

  const content = window.DIWALI_CONTENT;
  const P = window.DiwaliPersonalize;
  if (!content || !P) return; // boot.js falls back to the static greeting

  const root = document.documentElement;
  const body = document.body;
  const features = Object.assign(
    { moments: true, sound: false, share: true, hindiLine: true, urlPersonalization: true, animation: 'full' },
    content.features
  );
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const isCalm = () => motionQuery.matches || features.animation === 'minimal';
  if (features.animation === 'minimal') root.classList.add('calm');

  const byId = (id) => document.getElementById(id);
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  };
  const setText = (id, value) => {
    const node = byId(id);
    if (node && typeof value === 'string' && value) node.textContent = value;
  };

  const ui = {
    lightButton: byId('light-button'),
    soundToggle: byId('sound-toggle'),
    soundState: byId('sound-state'),
    waitingDiya: byId('waiting-diya'),
    litDiya: byId('lit-diya'),
    title: byId('greeting-title'),
    hindi: byId('hindi-line'),
    replay: byId('replay-button'),
    copy: byId('copy-button'),
    share: byId('share-button'),
    announcer: byId('announcer'),
    status: byId('action-status'),
    canvas: byId('particles'),
    constellation: byId('constellation'),
    art: document.querySelector('.greeting__art'),
    words: document.querySelector('.greeting__words')
  };

  // ── Content ────────────────────────────────────────────────────────────────
  const recipientOptions = content.recipient || {};
  const recipient = features.urlPersonalization
    ? P.readRecipient(window.location.search, recipientOptions.param)
    : '';
  const salutation = P.buildSalutation(recipient, recipientOptions);
  const threshold = content.threshold || {};
  const hindiLine = features.hindiLine ? content.hindiLine || '' : '';
  const pageUrl = P.pageUrl(window.location);

  setText('salutation', salutation);
  setText('eyebrow', content.eyebrow);
  setText('threshold-line', threshold.line);
  setText('light-button', threshold.button);
  setText('greeting-title', content.headline);
  setText('message', content.message);
  setText('signoff', content.signoff);
  setText('sender', content.sender);
  setText('blessing', content.blessing);
  setText('moments-title', content.momentsTitle);
  if (hindiLine) ui.hindi.textContent = hindiLine;
  else ui.hindi.hidden = true;

  // ── Announcements ──────────────────────────────────────────────────────────
  let statusTimer = 0;
  function announce(message) {
    ui.announcer.textContent = '';
    window.setTimeout(() => { ui.announcer.textContent = message; }, 60);
  }
  function showStatus(message) {
    window.clearTimeout(statusTimer);
    ui.status.textContent = message;
    if (message) statusTimer = window.setTimeout(() => { ui.status.textContent = ''; }, 6000);
  }

  // ── Particles: one short burst of petals and gold dust, then the loop stops ─
  const particles = (() => {
    const canvas = ui.canvas;
    const ctx = canvas.getContext('2d');
    const PETALS = ['#F28C28', '#E8A83A', '#F28C28', '#E0648F', '#FFB347'];
    let pool = [];
    let frame = 0;
    let last = 0;
    let active = false;

    function budget() {
      const small = Math.min(window.innerWidth, window.innerHeight) < 600;
      let count = small ? 28 : 56;
      if (features.animation === 'gentle') count *= 0.6;
      if ((navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 4) count *= 0.7;
      return Math.round(Math.max(12, Math.min(small ? 35 : 70, count)));
    }

    function resize() {
      const w = window.innerWidth;
      const h = window.innerHeight;
      // Cap the backing store at ~2.5 megapixels regardless of screen density.
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5, Math.sqrt(2.5e6 / (w * h)));
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function clear() {
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.restore();
    }

    function burst(x, y) {
      stop();
      resize();
      const count = budget();
      pool = new Array(count);
      for (let i = 0; i < count; i += 1) {
        const petal = i % 3 !== 0;
        const angle = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI * 1.5;
        const speed = (petal ? 150 : 210) * (0.45 + Math.random() * 0.75);
        pool[i] = {
          x, y,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          life: 0,
          ttl: 2.6 + Math.random() * 1.6,
          size: petal ? 4.5 + Math.random() * 4 : 1.1 + Math.random() * 1.5,
          rot: Math.random() * Math.PI * 2,
          spin: (Math.random() - 0.5) * 4,
          phase: Math.random() * Math.PI * 2,
          petal,
          color: petal ? PETALS[i % PETALS.length] : '#FFE9B0'
        };
      }
      active = true;
      body.dataset.particles = String(count);
      last = performance.now();
      if (!document.hidden) frame = window.requestAnimationFrame(tick);
    }

    function tick(now) {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      clear();
      let alive = 0;
      for (const p of pool) {
        p.life += dt;
        if (p.life >= p.ttl) continue;
        alive += 1;
        const drag = 1 - 1.5 * dt;
        p.vx *= drag;
        p.vy = p.vy * drag + (p.petal ? 55 : 28) * dt;
        p.phase += dt * 2;
        p.x += (p.vx + Math.sin(p.phase) * (p.petal ? 18 : 6)) * dt;
        p.y += p.vy * dt;
        p.rot += p.spin * dt;
        const t = p.life / p.ttl;
        ctx.globalAlpha = t < 0.1 ? t / 0.1 : Math.max(0, 1 - Math.pow((t - 0.1) / 0.9, 2));
        ctx.fillStyle = p.color;
        ctx.beginPath();
        if (p.petal) ctx.ellipse(p.x, p.y, p.size, p.size * 0.45, p.rot, 0, Math.PI * 2);
        else ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      if (alive) frame = window.requestAnimationFrame(tick);
      else stop();
    }

    function stop() {
      window.cancelAnimationFrame(frame);
      frame = 0;
      active = false;
      pool = [];
      clear();
      delete body.dataset.particles;
    }

    function pause() {
      window.cancelAnimationFrame(frame);
      frame = 0;
    }

    function resume() {
      if (!active || frame) return;
      last = performance.now();
      frame = window.requestAnimationFrame(tick);
    }

    return { burst, stop, pause, resume };
  })();

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) particles.pause();
    else particles.resume();
  });
  motionQuery.addEventListener('change', () => {
    if (isCalm()) particles.stop();
  });

  // ── Constellation: the single flame becomes many small lamps ──────────────
  // Lamps travel out from the diya and settle only where they won't sit behind text.
  const constellation = {
    show(instant) {
      this.hide();
      const host = ui.constellation;
      const box = host.getBoundingClientRect();
      const art = ui.art.getBoundingClientRect();
      const words = ui.words.getBoundingClientRect();
      const ox = art.left + art.width / 2 - box.left;
      const oy = art.top + art.height / 2 - box.top;
      host.style.setProperty('--ox', ox.toFixed(1) + 'px');
      host.style.setProperty('--oy', oy.toFixed(1) + 'px');

      const margin = 20;
      const avoid = {
        left: words.left - box.left - margin,
        right: words.right - box.left + margin,
        top: words.top - box.top - margin,
        bottom: words.bottom - box.top + margin
      };
      const minReach = art.width * 0.56;
      const maxReach = Math.max(box.width, Math.min(box.height, window.innerHeight)) * 0.6;
      const target = Math.round((window.innerWidth < 600 ? 9 : 14) * (features.animation === 'gentle' ? 0.7 : 1));
      const fragment = document.createDocumentFragment();
      let placed = 0;
      for (let i = 0; i < target; i += 1) {
        for (let attempt = 0; attempt < 16; attempt += 1) {
          const angle = ((i + Math.random() * 0.8) / target) * Math.PI * 2;
          const reach = minReach + Math.random() * (maxReach - minReach);
          const x = ox + Math.cos(angle) * reach;
          const y = oy + Math.sin(angle) * reach;
          if (x < 14 || x > box.width - 14 || y < 14 || y > box.height - 14) continue;
          if (x > avoid.left && x < avoid.right && y > avoid.top && y < avoid.bottom) continue;
          const lamp = make('span', 'lamp');
          lamp.style.setProperty('--tx', (x - ox).toFixed(1) + 'px');
          lamp.style.setProperty('--ty', (y - oy).toFixed(1) + 'px');
          lamp.style.setProperty('--delay', instant ? '0s' : (0.3 + placed * 0.11).toFixed(2) + 's');
          fragment.appendChild(lamp);
          placed += 1;
          break;
        }
      }
      host.appendChild(fragment);
    },
    hide() {
      ui.constellation.replaceChildren();
    }
  };

  let resizeTimer = 0;
  window.addEventListener('resize', () => {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => {
      if (body.dataset.scene === 'revealed') constellation.show(true);
    }, 250);
  });

  // ── Optional sound: off by default, only after an explicit toggle ─────────
  const sound = (() => {
    const src = P.safeAssetPath((content.sound && content.sound.src) || '', 'assets/audio/',
      ['mp3', 'm4a', 'ogg', 'opus', 'webm']);
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!features.sound || (!src && !AudioCtx)) return { play() {} };

    let enabled = false;
    let ctx = null;
    let audio = null;

    ui.soundToggle.hidden = false;
    ui.soundToggle.addEventListener('click', () => {
      enabled = !enabled;
      ui.soundToggle.setAttribute('aria-pressed', String(enabled));
      ui.soundState.textContent = enabled ? 'On' : 'Off';
      if (enabled && !src && !ctx) ctx = new AudioCtx(); // created inside a user gesture
    });

    // A small temple-bell chime: two soft strikes with gently decaying partials.
    function chime() {
      if (!ctx) ctx = new AudioCtx();
      if (ctx.state === 'suspended') ctx.resume();
      const start = ctx.currentTime + 0.05;
      const master = ctx.createGain();
      master.gain.value = 0.16;
      master.connect(ctx.destination);
      [[0, 659.25], [0.45, 987.77]].forEach(([offset, base]) => {
        [[1, 0.5, 2.8], [2.76, 0.12, 1.4], [5.4, 0.04, 0.7]].forEach(([ratio, peak, length]) => {
          const t = start + offset;
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.value = base * ratio;
          gain.gain.setValueAtTime(0.0001, t);
          gain.gain.exponentialRampToValueAtTime(peak, t + 0.015);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + length);
          osc.connect(gain).connect(master);
          osc.start(t);
          osc.stop(t + length + 0.05);
        });
      });
    }

    return {
      play() {
        if (!enabled) return;
        if (src) {
          audio = audio || new Audio(src);
          audio.volume = 0.6;
          audio.currentTime = 0;
          audio.play().catch(() => {});
        } else {
          chime();
        }
      }
    };
  })();

  // ── Pointer: the unlit flame outline leans gently toward the cursor ───────
  if (!isCalm() && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    let pointerX = null;
    let queued = false;
    window.addEventListener('pointermove', (event) => {
      if (body.dataset.scene !== 'sealed') return;
      pointerX = event.clientX;
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(() => {
        queued = false;
        const rect = ui.waitingDiya.getBoundingClientRect();
        const lean = (pointerX - (rect.left + rect.width / 2)) / (window.innerWidth / 2);
        ui.waitingDiya.style.setProperty('--lean', Math.max(-1, Math.min(1, lean)).toFixed(3));
      });
    }, { passive: true });
  }

  // ── Scenes ─────────────────────────────────────────────────────────────────
  let timers = [];
  const later = (fn, ms) => timers.push(window.setTimeout(fn, ms));
  const setScene = (scene) => { body.dataset.scene = scene; };

  function light() {
    if (body.dataset.scene !== 'sealed') return;
    setScene('lighting');
    ui.lightButton.setAttribute('aria-disabled', 'true');
    sound.play();
    if (isCalm()) reveal();
    else later(reveal, 1400);
  }

  function reveal() {
    setScene('revealed');
    ui.lightButton.removeAttribute('aria-disabled');
    window.scrollTo(0, 0);
    ui.title.focus({ preventScroll: true });
    announce('The diya is lit.');
    const calm = isCalm();
    constellation.show(calm);
    if (!calm) {
      later(() => {
        const rect = ui.litDiya.getBoundingClientRect();
        particles.burst(rect.left + rect.width / 2, rect.top + rect.height * 0.3);
      }, 250);
    }
  }

  function replay() {
    timers.forEach(window.clearTimeout);
    timers = [];
    particles.stop();
    constellation.hide();
    showStatus('');
    setScene('sealed');
    ui.lightButton.removeAttribute('aria-disabled');
    window.scrollTo(0, 0);
    ui.lightButton.focus();
    announce('The greeting is closed again. Light the diya to open it.');
  }

  // ── Copy and share ────────────────────────────────────────────────────────
  async function copyText(text, returnFocusTo) {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (error) {
        // Permission denied or unsupported; fall through to the legacy path.
      }
    }
    const buffer = make('textarea', 'clipboard-buffer');
    buffer.value = text;
    buffer.setAttribute('readonly', '');
    buffer.setAttribute('aria-hidden', 'true');
    buffer.tabIndex = -1;
    body.appendChild(buffer);
    buffer.select();
    let copied = false;
    try {
      copied = document.execCommand('copy');
    } catch (error) {
      copied = false;
    }
    buffer.remove();
    if (returnFocusTo) returnFocusTo.focus();
    return copied;
  }

  function selectForManualCopy(node) {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(node);
    selection.removeAllRanges();
    selection.addRange(range);
  }

  ui.copy.addEventListener('click', async () => {
    const text = P.buildGreetingText({
      salutation,
      headline: content.headline,
      hindiLine,
      message: content.message,
      signoff: content.signoff,
      sender: content.sender,
      blessing: content.blessing,
      url: /^https?:$/.test(window.location.protocol) ? pageUrl : ''
    });
    if (await copyText(text, ui.copy)) {
      showStatus('Greeting copied.');
    } else {
      selectForManualCopy(byId('message'));
      showStatus('Copying is blocked here. The message is selected so you can copy it yourself.');
    }
  });

  if (features.share && /^https?:$/.test(window.location.protocol)) {
    const shareData = {
      title: (content.share && content.share.title) || content.headline,
      text: (content.share && content.share.text) || '',
      url: pageUrl
    };
    const canShare = typeof navigator.share === 'function' &&
      (typeof navigator.canShare !== 'function' || navigator.canShare(shareData));
    ui.share.textContent = canShare ? 'Share' : 'Copy link';
    ui.share.hidden = false;
    ui.share.addEventListener('click', async () => {
      if (canShare) {
        try {
          await navigator.share(shareData);
          return;
        } catch (error) {
          if (error && error.name === 'AbortError') return;
        }
      }
      const copied = await copyText(pageUrl, ui.share);
      showStatus(copied ? 'Link copied.' : 'Copy this link: ' + pageUrl);
    });
  }

  // ── Memory moments ────────────────────────────────────────────────────────
  function placeholder(index, portrait, note) {
    const box = make('div', 'moment__placeholder');
    if (note) {
      box.appendChild(make('p', 'moment__placeholder-title', note));
      return box;
    }
    box.appendChild(make('p', 'moment__placeholder-title', 'Photo placeholder ' + (index + 1)));
    box.appendChild(make('p', '', 'Replace with'));
    box.appendChild(make('p', 'moment__placeholder-file', 'assets/photos/moment-' + (index + 1) + '.webp'));
    box.appendChild(make('p', '', portrait ? '4:5, about 1200 × 1500 px' : '3:2, about 1600 × 1067 px'));
    return box;
  }

  function renderMoment(moment, index) {
    const portrait = moment.orientation !== 'landscape';
    const item = make('li', 'moment');
    const figure = make('figure', 'moment__figure');
    const frame = make('div', 'moment__frame ' + (portrait ? 'moment__frame--portrait' : 'moment__frame--landscape'));
    const src = P.safeAssetPath(moment.src || '', 'assets/photos/', ['avif', 'webp', 'jpg', 'jpeg', 'png']);

    if (src) {
      const img = document.createElement('img');
      img.alt = moment.alt || moment.caption || 'Memory photo ' + (index + 1);
      img.width = Number(moment.width) || (portrait ? 1200 : 1600);
      img.height = Number(moment.height) || (portrait ? 1500 : 1067);
      img.loading = 'lazy';
      img.decoding = 'async';
      img.addEventListener('error', () => {
        frame.replaceChildren(placeholder(index, portrait, 'This photo could not be loaded.'));
      }, { once: true });
      img.src = src;
      frame.appendChild(img);
    } else {
      frame.appendChild(placeholder(index, portrait));
    }
    figure.appendChild(frame);

    const meta = [moment.when, moment.where].filter(Boolean).join(' · ');
    if (moment.caption || meta) {
      const caption = make('figcaption', 'moment__caption');
      if (moment.caption) caption.appendChild(make('p', 'moment__caption-text', moment.caption));
      if (meta) caption.appendChild(make('p', 'moment__meta', meta));
      figure.appendChild(caption);
    }
    item.appendChild(figure);
    return item;
  }

  function renderMoments() {
    const section = byId('moments');
    const moments = Array.isArray(content.moments) ? content.moments.slice(0, 5) : [];
    if (!features.moments || moments.length === 0) {
      section.remove();
      return;
    }
    const list = byId('moments-list');
    moments.forEach((moment, index) => list.appendChild(renderMoment(moment || {}, index)));

    const items = Array.from(list.children);
    if (isCalm() || !('IntersectionObserver' in window)) {
      items.forEach((item) => item.classList.add('is-visible'));
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach((item) => observer.observe(item));
  }

  renderMoments();
  ui.lightButton.addEventListener('click', light);
  ui.replay.addEventListener('click', replay);
  root.classList.add('is-ready');
})();
