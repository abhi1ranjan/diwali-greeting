// Pure helpers for untrusted input and text building. No DOM access, so they
// can be unit-tested in isolation (see tests/unit.html).
(function (global) {
  'use strict';

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

  // The page address without any query or #fragment.
  function pageUrl(loc) {
    return loc.origin + loc.pathname;
  }

  global.DiwaliPersonalize = Object.freeze({
    buildSalutation: buildSalutation,
    buildGreetingText: buildGreetingText,
    safeAssetPath: safeAssetPath,
    pageUrl: pageUrl
  });
})(window);
