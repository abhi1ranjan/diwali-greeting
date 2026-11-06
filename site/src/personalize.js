// Pure helpers for untrusted input and text building. No DOM access, so they
// can be unit-tested in isolation (see tests/unit.html).
(function (global) {
  'use strict';

  var MAX_RECIPIENT_LENGTH = 40;
  // Letters and combining marks from any script (so Devanagari names work),
  // digits, spaces, ZWNJ/ZWJ, and a few name punctuation marks.
  var ALLOWED_NAME = /^[\p{L}\p{M}\p{N}\u200C\u200D .,'\u2019&-]+$/u;
  var HAS_LETTER_OR_DIGIT = /[\p{L}\p{N}]/u;

  function truncateGraphemes(text, max) {
    if (typeof Intl !== 'undefined' && typeof Intl.Segmenter === 'function') {
      var out = '';
      var count = 0;
      var segments = new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(text);
      for (var it = segments[Symbol.iterator](), step = it.next(); !step.done; step = it.next()) {
        if (count === max) break;
        out += step.value.segment;
        count += 1;
      }
      return out;
    }
    return Array.from(text).slice(0, max).join('');
  }

  function sanitizeRecipient(raw, max) {
    var limit = typeof max === 'number' ? max : MAX_RECIPIENT_LENGTH;
    if (typeof raw !== 'string') return '';
    var cleaned = raw.slice(0, 400).normalize('NFC').replace(/\s+/gu, ' ').trim();
    if (!cleaned || !ALLOWED_NAME.test(cleaned) || !HAS_LETTER_OR_DIGIT.test(cleaned)) return '';
    return truncateGraphemes(cleaned, limit).trim();
  }

  function readRecipient(search, param) {
    try {
      var value = new URLSearchParams(search || '').get(param || 'to');
      return sanitizeRecipient(value === null ? '' : value);
    } catch (e) {
      return '';
    }
  }

  function buildSalutation(name, options) {
    var opts = options || {};
    var word = opts.greetingWord || 'Dear';
    var fallback = opts.fallback || 'friends and family';
    return word + ' ' + (name || fallback) + ',';
  }

  function buildGreetingText(parts) {
    var blocks = [
      parts.salutation,
      [parts.headline, parts.hindiLine].filter(Boolean).join('\n'),
      parts.message,
      [parts.signoff, parts.sender].filter(Boolean).join('\n'),
      parts.blessing,
      parts.url
    ];
    return blocks.filter(Boolean).join('\n\n');
  }

  // Only plain filenames inside a known local folder; blocks remote URLs,
  // "javascript:", traversal and query strings even if config is mistyped.
  function safeAssetPath(path, folder, extensions) {
    if (typeof path !== 'string' || typeof folder !== 'string') return '';
    var p = path.trim();
    if (p.indexOf(folder) !== 0) return '';
    var file = p.slice(folder.length);
    var match = /^[A-Za-z0-9][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)*\.([A-Za-z0-9]+)$/.exec(file);
    if (!match) return '';
    return extensions.indexOf(match[1].toLowerCase()) === -1 ? '' : p;
  }

  // The page address without ?to= or #fragment, so shares never carry a name.
  function pageUrl(loc) {
    return loc.origin + loc.pathname;
  }

  global.DiwaliPersonalize = Object.freeze({
    MAX_RECIPIENT_LENGTH: MAX_RECIPIENT_LENGTH,
    sanitizeRecipient: sanitizeRecipient,
    readRecipient: readRecipient,
    buildSalutation: buildSalutation,
    buildGreetingText: buildGreetingText,
    safeAssetPath: safeAssetPath,
    pageUrl: pageUrl
  });
})(window);
