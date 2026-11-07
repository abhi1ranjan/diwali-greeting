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
  setText('moments-note', content.momentsNote);
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

  // ── Music: starts on the first click, loops until the tab closes ───────────
  // Browsers block audio before a user gesture, so nothing can play on load. The
  // Music button stays on screen in every scene, so the visitor can always stop it.
  const sound = (() => {
    const settings = content.sound || {};
    const src = P.safeAssetPath(settings.src || '', 'assets/audio/', ['mp3', 'm4a', 'ogg', 'opus', 'webm']);
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!features.sound || (!src && !AudioCtx)) return { start() {} };

    const level = Math.min(0.6, Math.max(0.05, Number(settings.volume) || 0.35));
    const FADE_IN = 1.5;
    let wanted = settings.startOnLight !== false;
    let lit = false;
    let started = false;
    let ctx = null;
    let master = null;
    let room = null;
    let audio = null;
    let fadeTimer = 0;
    let suspendTimer = 0;

    function reflect(on) {
      wanted = on;
      ui.soundToggle.setAttribute('aria-pressed', String(on));
      ui.soundState.textContent = on ? 'On' : 'Off';
    }

    // A file supplied by the owner: one element, looping, with a gentle fade.
    function fadeFile(target, seconds, done) {
      window.clearInterval(fadeTimer);
      const from = audio.volume;
      const begun = performance.now();
      fadeTimer = window.setInterval(() => {
        const progress = Math.min(1, (performance.now() - begun) / (seconds * 1000));
        audio.volume = from + (target - from) * progress;
        if (progress < 1) return;
        window.clearInterval(fadeTimer);
        if (done) done();
      }, 40);
    }

    // Fade the file through Web Audio where possible: iPhones ignore audio.volume.
    function fadeOut(seconds, done) {
      if (ctx) {
        fadeSynth(0, seconds);
        window.clearTimeout(fadeTimer);
        fadeTimer = window.setTimeout(done, seconds * 1000 + 30);
      } else {
        fadeFile(0, seconds, done);
      }
    }

    function playFile() {
      audio.play().then(() => {
        if (ctx) fadeSynth(level, FADE_IN);
        else fadeFile(level, FADE_IN);
      }).catch((error) => {
        // A missing or unreadable file is handled by the 'error' listener below.
        if (error && error.name === 'NotAllowedError') reflect(false);
      });
    }

    function beginFile() {
      audio = new Audio(src);
      audio.loop = settings.loop !== false;
      audio.preload = 'auto';
      if (ctx) ctx.createMediaElementSource(audio).connect(master);
      else audio.volume = 0;
      audio.addEventListener('error', () => {
        audio = null;
        if (ctx) beginSynth(); // fall back to the synthesised loop
        else reflect(false);
      }, { once: true });
      playFile();
    }

    // The synthesised loop: a tanpura-style drone and plucks in Sa and Pa, a soft
    // bansuri-like voice in the notes of Raag Bhupali, and an occasional temple bell.
    const BEAT = 0.72;
    const SA = 261.63;
    const PHRASES = [
      [[0, 2], [2, 1], [4, 2], [7, 3]],
      [[9, 1], [7, 1], [4, 2], [2, 1], [4, 3]],
      [[7, 2], [9, 1], [12, 3], [9, 1], [7, 2]],
      [[12, 1], [14, 1], [12, 1], [9, 1], [7, 3]],
      [[4, 1], [7, 1], [9, 2], [7, 1], [4, 1], [2, 1], [0, 4]]
    ];
    const PLUCKS = [196, 261.63, 261.63, 130.81];
    let nextPluck = 0;
    let pluckIndex = 0;
    let nextBell = 0;
    let nextPhrase = 0;

    function makeRoom() {
      const seconds = 2.6;
      const length = Math.floor(ctx.sampleRate * seconds);
      const impulse = ctx.createBuffer(2, length, ctx.sampleRate);
      for (let channel = 0; channel < 2; channel += 1) {
        const data = impulse.getChannelData(channel);
        for (let i = 0; i < length; i += 1) {
          data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, 3);
        }
      }
      const reverb = ctx.createConvolver();
      reverb.buffer = impulse;
      const wet = ctx.createGain();
      wet.gain.value = 0.32;
      reverb.connect(wet).connect(master);
      return reverb;
    }

    function output() {
      const bus = ctx.createGain();
      bus.connect(master);
      bus.connect(room);
      return bus;
    }

    function tone(bus, frequency, type, at, peak, length) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.value = frequency;
      gain.gain.setValueAtTime(0.0001, at);
      gain.gain.exponentialRampToValueAtTime(peak, at + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.0001, at + length);
      osc.connect(gain).connect(bus);
      osc.start(at);
      osc.stop(at + length + 0.05);
      return osc;
    }

    // Timers run while the music is paused, so clean up on audio time instead.
    function freeWhenEnded(source, bus) {
      source.onended = () => bus.disconnect();
    }

    function drone() {
      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 640;
      const gain = ctx.createGain();
      gain.gain.value = 0.11;
      const breath = ctx.createOscillator();
      const breathDepth = ctx.createGain();
      breath.frequency.value = 0.08;
      breathDepth.gain.value = 0.03;
      breath.connect(breathDepth).connect(gain.gain);
      breath.start();
      [[130.81, -4], [130.81, 4], [196, 2], [261.63, -3]].forEach(([frequency, detune]) => {
        const osc = ctx.createOscillator();
        osc.type = 'triangle';
        osc.frequency.value = frequency;
        osc.detune.value = detune;
        osc.connect(filter);
        osc.start();
      });
      filter.connect(gain).connect(output());
    }

    function pluck(at) {
      const base = PLUCKS[pluckIndex % PLUCKS.length];
      pluckIndex += 1;
      const bus = output();
      [[5, 0.012, 0.9], [3, 0.03, 1.4], [2, 0.05, 1.9]].forEach(([ratio, peak, length]) => {
        tone(bus, base * ratio, 'sine', at, peak, length);
      });
      freeWhenEnded(tone(bus, base, 'sine', at, 0.075, 2.4), bus);
    }

    function bell(at) {
      const bus = output();
      let last = null;
      [[0, 659.25], [0.45, 987.77]].forEach(([offset, base]) => {
        [[2.76, 0.014, 1.5], [5.4, 0.005, 0.8], [1, 0.055, 3.2]].forEach(([ratio, peak, length]) => {
          last = tone(bus, base * ratio, 'sine', at + offset, peak, length);
        });
      });
      freeWhenEnded(last, bus);
    }

    function flutePhrase(at) {
      const phrase = PHRASES[Math.floor(Math.random() * PHRASES.length)];
      const voice = ctx.createOscillator();
      const overtone = ctx.createOscillator();
      const overtoneGain = ctx.createGain();
      const vibrato = ctx.createOscillator();
      const vibratoDepth = ctx.createGain();
      const gain = ctx.createGain();
      const bus = output();
      overtone.frequency.value = 0;
      overtoneGain.gain.value = 0.1;
      vibrato.frequency.value = 4.6;
      vibratoDepth.gain.value = 7; // in cents
      vibrato.connect(vibratoDepth);
      vibratoDepth.connect(voice.detune);
      vibratoDepth.connect(overtone.detune);
      voice.connect(gain);
      overtone.connect(overtoneGain).connect(gain);
      gain.connect(bus);
      gain.gain.setValueAtTime(0.0001, at);
      let time = at;
      phrase.forEach(([semitone, beats], index) => {
        const frequency = SA * Math.pow(2, semitone / 12);
        const length = beats * BEAT;
        if (index === 0) {
          voice.frequency.setValueAtTime(frequency, time);
          overtone.frequency.setValueAtTime(frequency * 2, time);
        } else {
          voice.frequency.setTargetAtTime(frequency, time, 0.05);
          overtone.frequency.setTargetAtTime(frequency * 2, time, 0.05);
        }
        gain.gain.setTargetAtTime(0.085, time, 0.09);
        gain.gain.setTargetAtTime(0.052, time + length * 0.55, 0.22);
        time += length;
      });
      gain.gain.setTargetAtTime(0.0001, time, 0.5);
      const end = time + 3;
      [voice, overtone, vibrato].forEach((osc) => {
        osc.start(at);
        osc.stop(end);
      });
      freeWhenEnded(voice, bus);
      return time;
    }

    function schedule() {
      if (ctx.state !== 'running') return;
      const now = ctx.currentTime;
      const horizon = now + 2.5;
      if (nextPluck < now) nextPluck = now + 0.1;
      if (nextBell < now) nextBell = now + 0.2;
      if (nextPhrase < now) nextPhrase = now + 0.3;
      while (nextPluck < horizon) {
        pluck(nextPluck);
        nextPluck += BEAT * 2;
      }
      if (nextBell < horizon) {
        bell(nextBell);
        nextBell += 12 + Math.random() * 8;
      }
      if (nextPhrase < horizon) {
        nextPhrase = flutePhrase(nextPhrase) + BEAT * (3 + Math.floor(Math.random() * 3));
      }
    }

    function setUpOutput() {
      ctx = new AudioCtx(); // created inside the click, so Safari allows it
      ctx.resume();
      master = ctx.createGain();
      master.gain.value = 0.0001;
      const limiter = ctx.createDynamicsCompressor();
      master.connect(limiter).connect(ctx.destination);
    }

    function beginSynth() {
      room = makeRoom();
      drone();
      nextPluck = nextBell = ctx.currentTime + 0.1;
      nextPhrase = ctx.currentTime + BEAT * 2;
      if (settings.loop === false) {
        bell(ctx.currentTime + 0.1);
      } else {
        schedule();
        window.setInterval(schedule, 500);
      }
      fadeSynth(level, FADE_IN);
    }

    function fadeSynth(target, seconds) {
      const now = ctx.currentTime;
      master.gain.cancelScheduledValues(now);
      master.gain.setValueAtTime(Math.max(0.0001, master.gain.value), now);
      master.gain.linearRampToValueAtTime(Math.max(0.0001, target), now + seconds);
    }

    function begin() {
      started = true;
      try {
        if (AudioCtx) setUpOutput();
        if (src) beginFile();
        else beginSynth();
      } catch (error) {
        started = false;
        reflect(false);
      }
    }

    function resume() {
      if (!started) {
        begin();
        return;
      }
      window.clearTimeout(fadeTimer);
      window.clearTimeout(suspendTimer);
      if (audio) {
        playFile();
        return;
      }
      ctx.resume().catch(() => reflect(false));
      fadeSynth(level, 0.6);
    }

    function pause() {
      if (!started) return;
      if (audio) {
        fadeOut(0.25, () => { if (!wanted) audio.pause(); });
        return;
      }
      fadeSynth(0, 0.25);
      window.clearTimeout(suspendTimer);
      suspendTimer = window.setTimeout(() => ctx.suspend(), 280);
    }

    reflect(wanted);
    ui.soundToggle.hidden = false;
    ui.soundToggle.addEventListener('click', () => {
      reflect(!wanted);
      if (!lit) return; // before the diya is lit, this only sets the preference
      if (wanted) resume();
      else pause();
    });

    // Keep playing in the background. Phones may interrupt audio when the screen
    // locks; when the visitor comes back, pick up where it left off.
    document.addEventListener('visibilitychange', () => {
      if (document.hidden || !started || !wanted) return;
      if (ctx && ctx.state !== 'running') ctx.resume().catch(() => {});
      if (audio && audio.paused) playFile();
    });

    return {
      start() {
        lit = true;
        if (wanted && !started) begin();
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
    sound.start();
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

  // Animated images: only the ones on screen play. Everyone else sees a still.
  const animations = [];
  let animationsPlaying = !isCalm();

  function syncAnimation(item) {
    const next = animationsPlaying && item.onScreen ? item.gif : item.still;
    if (item.img.getAttribute('src') !== next) item.img.src = next;
  }

  function renderMoment(moment, index) {
    const shape = /^(round|arch|polaroid|wide|square|cutout)$/.test(moment.shape) ? moment.shape : 'wide';
    const slot = /^[a-z]$/.test(moment.slot) ? ' moment--slot-' + moment.slot : '';
    const width = Number(moment.width) || 1200;
    const height = Number(moment.height) || 1500;
    const item = make('li', 'moment moment--' + shape + slot);
    const figure = make('figure', 'moment__figure');
    const frame = make('div', 'moment__frame');
    frame.style.setProperty('aspect-ratio', shape === 'round' ? '1' : width + ' / ' + height);
    const src = P.safeAssetPath(moment.src || '', 'assets/photos/', ['avif', 'webp', 'jpg', 'jpeg', 'png', 'gif']);
    const still = P.safeAssetPath(moment.still || '', 'assets/photos/', ['avif', 'webp', 'jpg', 'jpeg', 'png']);

    if (src) {
      const img = document.createElement('img');
      img.alt = moment.alt || moment.caption || 'Memory photo ' + (index + 1);
      img.width = width;
      img.height = height;
      img.loading = 'lazy';
      img.decoding = 'async';
      img.addEventListener('error', () => {
        frame.replaceChildren(placeholder(index, height > width, 'This photo could not be loaded.'));
      }, { once: true });
      if (still && src !== still) {
        img.src = still;
        animations.push({ img, gif: src, still, onScreen: false, host: item });
      } else {
        img.src = src;
      }
      frame.appendChild(img);
    } else {
      frame.appendChild(placeholder(index, height > width));
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

  function setUpAnimations() {
    if (animations.length === 0) return;
    const toggle = byId('fireworks-toggle');
    const label = () => { toggle.textContent = animationsPlaying ? 'Pause fireworks' : 'Play fireworks'; };
    label();
    toggle.hidden = false;
    toggle.addEventListener('click', () => {
      animationsPlaying = !animationsPlaying;
      label();
      animations.forEach(syncAnimation);
    });
    if (!('IntersectionObserver' in window)) {
      animations.forEach((item) => {
        item.onScreen = true;
        syncAnimation(item);
      });
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const item = animations.find((candidate) => candidate.host === entry.target);
        if (!item) return;
        item.onScreen = entry.isIntersecting;
        syncAnimation(item);
      });
    }, { rootMargin: '200px 0px' });
    animations.forEach((item) => observer.observe(item.host));
  }

  function renderMoments() {
    const section = byId('moments');
    const moments = Array.isArray(content.moments) ? content.moments.slice(0, 26) : [];
    if (!features.moments || moments.length === 0) {
      section.remove();
      return;
    }
    const list = byId('moments-list');
    moments.forEach((moment, index) => list.appendChild(renderMoment(moment || {}, index)));
    setUpAnimations();

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
