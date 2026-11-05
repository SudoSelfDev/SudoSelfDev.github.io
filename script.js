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

  // Copy button for the email address
  var copyMail = document.getElementById('copy-email');
  if (copyMail) {
    copyMail.addEventListener('click', function () {
      copyText(document.getElementById('addr').textContent, copyMail, 'Copy');
    });
  }
})();
