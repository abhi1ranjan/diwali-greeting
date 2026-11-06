// Runs before first paint. If main.js never finishes (blocked, failed, old browser),
// the load handler restores the complete no-JS greeting instead of a dead button.
(function () {
  var root = document.documentElement;
  root.classList.remove('no-js');
  root.classList.add('js');
  window.addEventListener('load', function () {
    if (!root.classList.contains('is-ready')) {
      root.classList.remove('js');
      root.classList.add('no-js');
    }
  });
})();
