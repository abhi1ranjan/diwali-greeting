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
  const qs = (value) => '?to=' + encodeURIComponent(value);

  // ── sanitizeRecipient / readRecipient ──────────────────────────────────────
  test('plain name', () => equal(P.readRecipient('?to=Ananya'), 'Ananya'));
  test('name with surrounding whitespace is trimmed', () => equal(P.readRecipient(qs('   Ananya  ')), 'Ananya'));
  test('inner whitespace collapses to one space', () => equal(P.readRecipient(qs('Ravi \t\n  Kumar')), 'Ravi Kumar'));
  test('plus sign decodes to a space', () => equal(P.readRecipient('?to=Meera+Iyer'), 'Meera Iyer'));
  test('missing parameter returns empty', () => equal(P.readRecipient(''), ''));
  test('other parameters are ignored', () => equal(P.readRecipient('?from=Ananya'), ''));
  test('empty value returns empty', () => equal(P.readRecipient('?to='), ''));
  test('whitespace-only returns empty', () => equal(P.readRecipient(qs('   \t  ')), ''));
  test('HTML injection is rejected', () => equal(P.readRecipient(qs('<img src=x onerror=alert(1)>')), ''));
  test('script tag is rejected', () => equal(P.readRecipient(qs('<script>alert(1)</script>')), ''));
  test('javascript: scheme is rejected', () => equal(P.readRecipient(qs('javascript:alert(1)')), ''));
  test('quotes and angle brackets are rejected', () => equal(P.readRecipient(qs('"><svg onload=alert(1)>')), ''));
  test('URL is rejected', () => equal(P.readRecipient(qs('https://example.com')), ''));
  test('email address is rejected', () => equal(P.readRecipient(qs('ananya@example.com')), ''));
  test('control characters are rejected', () => equal(P.sanitizeRecipient('Ana\u0000nya'), ''));
  test('bidi override characters are rejected', () => equal(P.sanitizeRecipient('Ana\u202Enya'), ''));
  test('punctuation only is rejected', () => equal(P.sanitizeRecipient("..-'"), ''));
  test('non-string input returns empty', () => equal(P.sanitizeRecipient(null), ''));
  test('too long is truncated to 40 characters', () => {
    const name = P.readRecipient(qs('A'.repeat(60)));
    equal(name.length, 40);
    equal(name, 'A'.repeat(40));
  });
  test('truncation does not leave trailing space', () => {
    equal(P.sanitizeRecipient('A'.repeat(39) + ' Bcdef'), 'A'.repeat(39));
  });
  test('Devanagari name is preserved', () => equal(P.readRecipient(qs('अनन्या')), 'अनन्या'));
  test('Latin diacritics are preserved', () => equal(P.readRecipient(qs('Ananyā Shāh')), 'Ananyā Shāh'));
  test('Tamil name is preserved', () => equal(P.readRecipient(qs('அனன்யா')), 'அனன்யா'));
  test('apostrophe, hyphen and ampersand are allowed', () => {
    equal(P.readRecipient(qs("D'Souza-Rao & family")), "D'Souza-Rao & family");
  });
  test('long Devanagari truncates on grapheme boundaries', () => {
    const out = P.sanitizeRecipient('अनन्या'.repeat(20));
    const graphemes = typeof Intl.Segmenter === 'function'
      ? Array.from(new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(out)).length
      : Array.from(out).length;
    if (graphemes > 40) throw new Error('more than 40 graphemes: ' + graphemes);
    if (!/^[\u0900-\u097F]+$/.test(out)) throw new Error('unexpected characters: ' + out);
  });
  test('custom parameter name', () => equal(P.readRecipient('?name=Kabir', 'name'), 'Kabir'));
  test('malformed percent-encoding does not throw', () => equal(P.readRecipient('?to=%E0%A4'), ''));

  // ── buildSalutation ────────────────────────────────────────────────────────
  test('salutation with name', () => equal(P.buildSalutation('Ananya', {}), 'Dear Ananya,'));
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
