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

  // Scroll reveal
  var items = document.querySelectorAll('.reveal');
  if (items.length) {
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -6% 0px' });
      items.forEach(function (el) { io.observe(el); });
    } else {
      items.forEach(function (el) { el.classList.add('in'); });
    }
  }

  // Highlight the nav link for the section in view (home page)
  var spyLinks = {};
  document.querySelectorAll('#site-nav a[data-section]').forEach(function (a) { spyLinks[a.getAttribute('data-section')] = a; });
  var spySections = ['about', 'learning', 'projects', 'logs', 'contact']
    .map(function (id) { return document.getElementById(id); })
    .filter(function (el) { return el && spyLinks[el.id]; });
  if (spySections.length > 1 && 'IntersectionObserver' in window) {
    var visible = {};
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
      var current = null;
      spySections.forEach(function (s) { if (visible[s.id] && !current) current = s.id; });
      Object.keys(spyLinks).forEach(function (k) { spyLinks[k].classList.toggle('active', k === current); });
    }, { rootMargin: '-35% 0px -55% 0px' });
    spySections.forEach(function (s) { spy.observe(s); });
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
