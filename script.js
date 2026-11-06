(function () {
  var root = document.documentElement;

  function currentTheme() {
    return root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
  }

  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = currentTheme() === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  // Mobile menu
  var menuBtn = document.getElementById('menu-toggle');
  var nav = document.getElementById('site-nav');
  function setMenu(open) {
    if (!menuBtn || !nav) return;
    nav.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () { setMenu(!nav.classList.contains('open')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); menuBtn.focus(); }
    });
    window.matchMedia('(min-width: 641px)').addEventListener('change', function (e) { if (e.matches) setMenu(false); });
  }

  function copyText(text, button, idle) {
    function done(msg) {
      button.textContent = msg;
      setTimeout(function () { button.textContent = idle; }, 1500);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done('Copied'); }, function () { done('Select and copy'); });
    } else {
      done('Select and copy');
    }
  }

  // Copy button on every code block
  document.querySelectorAll('.code-block').forEach(function (block) {
    var header = block.querySelector('.code-block-header');
    var pre = block.querySelector('pre');
    if (!header || !pre) return;
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = 'Copy';
    b.setAttribute('aria-label', 'Copy code');
    b.addEventListener('click', function () { copyText(pre.innerText, b, 'Copy'); });
    header.appendChild(b);
  });
})();
