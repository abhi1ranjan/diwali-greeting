(function () {
  'use strict';
  const P = window.DiwaliPersonalize;
  const results = [];

  function test(name, fn) {
    try {
      fn();
      results.push({ name, ok: true });
    } catch (error) {
      results.push({ name, ok: false, error: String(error && error.message ? error.message : error) });
    }
  }
  function equal(actual, expected) {
    if (actual !== expected) {
      throw new Error('expected ' + JSON.stringify(expected) + ' but got ' + JSON.stringify(actual));
    }
  }

  // ── buildSalutation ────────────────────────────────────────────────────────
  test('salutation fallback', () => equal(P.buildSalutation('', {}), 'Dear friends and family,'));
  test('salutation honours options', () => {
    equal(P.buildSalutation('', { greetingWord: 'Hello', fallback: 'everyone' }), 'Hello everyone,');
  });

  // ── buildGreetingText ──────────────────────────────────────────────────────
  test('greeting text joins sections and skips empty ones', () => {
    const text = P.buildGreetingText({
      salutation: 'Dear Ananya,', headline: 'Happy Diwali', hindiLine: '', message: 'Message.',
      signoff: 'With warmth,', sender: 'Abhishek', blessing: 'Blessing.', url: ''
    });
    equal(text, 'Dear Ananya,\n\nHappy Diwali\n\nMessage.\n\nWith warmth,\nAbhishek\n\nBlessing.');
  });

  // ── safeAssetPath ──────────────────────────────────────────────────────────
  const photo = (p) => P.safeAssetPath(p, 'assets/photos/', ['webp', 'jpg', 'avif']);
  test('valid photo path', () => equal(photo('assets/photos/moment-1.webp'), 'assets/photos/moment-1.webp'));
  test('upper-case extension allowed', () => equal(photo('assets/photos/IMG_01.JPG'), 'assets/photos/IMG_01.JPG'));
  test('remote URL rejected', () => equal(photo('https://example.com/a.webp'), ''));
  test('protocol-relative URL rejected', () => equal(photo('//example.com/a.webp'), ''));
  test('path traversal rejected', () => equal(photo('assets/photos/../../secret.webp'), ''));
  test('subfolder rejected', () => equal(photo('assets/photos/a/b.webp'), ''));
  test('query string rejected', () => equal(photo('assets/photos/a.webp?x=1'), ''));
  test('wrong extension rejected', () => equal(photo('assets/photos/a.svg'), ''));
  test('javascript URL rejected', () => equal(photo('javascript:alert(1)'), ''));
  test('empty path rejected', () => equal(photo(''), ''));

  // ── pageUrl ────────────────────────────────────────────────────────────────
  test('page URL drops query and fragment', () => {
    const loc = new URL('https://abhi1ranjan.github.io/diwali-greeting/?to=Ananya#x');
    equal(P.pageUrl(loc), 'https://abhi1ranjan.github.io/diwali-greeting/');
  });

  const failed = results.filter((r) => !r.ok);
  document.getElementById('results').textContent = results
    .map((r) => (r.ok ? 'ok   ' : 'FAIL ') + r.name + (r.ok ? '' : '  -> ' + r.error))
    .join('\n') + '\n\n' + (results.length - failed.length) + '/' + results.length + ' passed';
  document.title = failed.length ? 'FAIL' : 'PASS';
})();
