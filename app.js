/* ==========================================================================
   app.js — interactions + live GitHub projects
   No build step, no dependencies. Safe to edit.
   ========================================================================== */
(function () {
  'use strict';

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- theme ------------------------------------------------------ */
  var root = document.documentElement;
  var themeBtn = $('#themeToggle');
  function syncThemeLabel() {
    var dark = root.getAttribute('data-theme') === 'dark';
    if (themeBtn) {
      themeBtn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    }
    var meta = $('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', dark ? '#16130F' : '#F5F0E6');
  }
  syncThemeLabel();
  if (themeBtn) themeBtn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('jss-theme', next); } catch (e) {}
    syncThemeLabel();
  });

  /* ---------- year ------------------------------------------------------- */
  var y = $('#year');
  if (y) y.textContent = new Date().getFullYear();

  /* ---------- mobile menu ------------------------------------------------ */
  var menuBtn = $('#menuToggle'), nav = $('#primaryNav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    $$('a', nav).forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('is-open');
        menuBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- scroll progress + active nav ------------------------------ */
  var bar = $('#scrollProgress');
  function onScroll() {
    if (bar) {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if ('IntersectionObserver' in window && nav) {
    var links = $$('a[href^="#"]', nav);
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) {
          a.classList.toggle('is-active', a.getAttribute('href') === '#' + en.target.id);
        });
      });
    }, { rootMargin: '-25% 0px -65% 0px', threshold: 0 });
    $$('main section[id]').forEach(function (s) { obs.observe(s); });
  }

  /* ---------- reveal on scroll ------------------------------------------ */
  var reveals = $$('.reveal');
  if ('IntersectionObserver' in window && !reduced) {
    var ro = new IntersectionObserver(function (entries, observer) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-visible'); observer.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    reveals.forEach(function (el) { ro.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- ticker: duplicate the set for a seamless loop -------------- */
  var track = $('#tickerTrack');
  if (track) {
    var set = $('.ticker-set', track);
    if (set) track.appendChild(set.cloneNode(true));
  }

  /* ---------- soft spotlight following the cursor in the hero ----------- */
  var hero = $('.hero');
  if (hero && !reduced && window.matchMedia('(pointer:fine)').matches) {
    hero.addEventListener('pointermove', function (e) {
      var r = hero.getBoundingClientRect();
      hero.style.setProperty('--mx', ((e.clientX - r.left) / r.width) * 100 + '%');
      hero.style.setProperty('--my', ((e.clientY - r.top) / r.height) * 100 + '%');
    });
  }

  /* ---------- copy email ------------------------------------------------- */
  var copyBtn = $('#copyEmail');
  if (copyBtn) copyBtn.addEventListener('click', function () {
    var email = copyBtn.getAttribute('data-email');
    var done = function () {
      copyBtn.classList.add('is-copied');
      copyBtn.innerHTML = 'Copied! <span aria-hidden="true">✓</span>';
      setTimeout(function () {
        copyBtn.classList.remove('is-copied');
        copyBtn.innerHTML = 'Copy address <span aria-hidden="true">⧉</span>';
      }, 2000);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(email).then(done, function () { fallback(); });
    } else { fallback(); }
    function fallback() {
      var t = document.createElement('textarea');
      t.value = email; t.style.position = 'fixed'; t.style.opacity = '0';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); done(); } catch (e) { window.location.href = 'mailto:' + email; }
      document.body.removeChild(t);
    }
  });

  /* ======================================================================
     PROJECTS  — live from GitHub, with curated copy from data.js
     ====================================================================== */
  var D = window.SITE_DATA || {};
  var FEATURED = (D.FEATURED || []).map(function (f) { return typeof f === 'string' ? { repo: f } : f; });
  var OVERRIDES = D.OVERRIDES || {};
  var HIDDEN = new Set(D.HIDDEN || []);
  var grid = $('#projectsGrid');
  var status = $('#syncStatus');

  var LANG_COLORS = {
    Python: '#3572A5', TypeScript: '#3178C6', JavaScript: '#E5B94E', Java: '#B07219',
    Scala: '#C22D40', Jupyter: '#DA5B0B', Rust: '#DEA584', Go: '#00ADD8',
    Ruby: '#701516', Shell: '#89E051', HTML: '#E34C26', CSS: '#563D7C', 'C++': '#F34B7D'
  };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /** Merge curated ordering/overrides with live repo objects. */
  function assemble(repos) {
    var byName = {};
    repos.forEach(function (r) { if (!HIDDEN.has(r.name)) byName[r.name] = r; });
    var out = [];
    FEATURED.forEach(function (f) {
      if (byName[f.repo]) { out.push(byName[f.repo]); delete byName[f.repo]; return; }
      if (f.url) {                       // a project that doesn't live on GitHub
        out.push({ name: f.repo, html_url: f.url, language: f.language || null,
                   description: f.blurb || '', topics: f.tags || [], fork: false, stargazers_count: 0 });
      }
    });
    Object.keys(byName).forEach(function (k) { out.push(byName[k]); });
    return out;
  }

  function cardHTML(r, i) {
    var o = OVERRIDES[r.name] || {};
    var blurb = o.blurb || r.description || 'A small experiment — notes and write-up coming soon.';
    var tags = (o.tags || r.topics || []).slice(0, 5);
    var url = o.url || r.html_url;
    var lang = r.language;
    var badges = '';
    if (i === 0) badges += '<span class="mini-badge badge-featured">✳ Featured</span>';
    if (o.badge) badges += '<span class="mini-badge">' + esc(o.badge) + '</span>';
    if (r.fork) badges += '<span class="mini-badge badge-fork">Fork</span>';

    var langHTML = lang
      ? '<span class="lang-chip"><span class="lang-dot" style="background:' + (LANG_COLORS[lang] || 'var(--ink-3)') + '"></span>' + esc(lang) + '</span>'
      : '';

    return '' +
      '<a class="project-card' + (i === 0 ? ' project-card--featured' : '') + '" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">' +
        '<div class="pc-top">' +
          '<span class="pc-index">/' + String(i + 1).padStart(2, '0') + '</span>' +
          '<div class="pc-badges">' + badges + langHTML + '</div>' +
        '</div>' +
        '<h3 class="project-title">' + esc(r.name) + '</h3>' +
        '<p class="project-blurb">' + esc(blurb) + '</p>' +
        (tags.length ? '<div class="project-tags">' + tags.map(function (t) {
          return '<span class="topic-tag">' + esc(t) + '</span>';
        }).join('') + '</div>' : '') +
        '<div class="pc-foot">' +
          '<span>★ ' + (r.stargazers_count || 0) + (r.fork ? ' · forked' : '') + '</span>' +
          '<span class="pc-link">View repository <span aria-hidden="true">↗</span></span>' +
        '</div>' +
      '</a>';
  }

  function setStatus(text, offline) {
    if (!status) return;
    status.classList.toggle('is-offline', !!offline);
    status.innerHTML = '<span class="live-dot" aria-hidden="true"></span>' + text;
  }

  function render(repos, offline, pending) {
    if (!grid) return;
    var list = assemble(repos);
    grid.innerHTML = list.map(cardHTML).join('');
    setStatus(pending ? 'Syncing with GitHub…'
      : (offline ? 'Showing saved list · GitHub unreachable'
                 : 'Live from GitHub · ' + list.length + ' repos'), offline && !pending);
    // newly-added cards should also reveal
    $$('.project-card', grid).forEach(function (c, i) {
      c.classList.add('reveal');
      c.style.setProperty('--d', Math.min(i * 0.05, 0.3) + 's');
      if (reduced || !('IntersectionObserver' in window)) {
        c.classList.add('is-visible');
      } else {
        var io = new IntersectionObserver(function (es, ob) {
          es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-visible'); ob.unobserve(en.target); } });
        }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
        io.observe(c);
      }
    });
  }

  var fallback = (D.OFFLINE_PROJECTS || []).slice();
  render(fallback, true, true); // instant paint, never an empty grid

  if (D.githubUser && window.fetch) {
    fetch('https://api.github.com/users/' + encodeURIComponent(D.githubUser) + '/repos?per_page=100&sort=updated', {
      headers: { 'Accept': 'application/vnd.github+json' }
    })
      .then(function (res) { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
      .then(function (data) { if (Array.isArray(data) && data.length) render(data, false); })
      .catch(function () { setStatus('Showing saved list · GitHub unreachable', true); });
  } else {
    setStatus('Showing saved list · GitHub unreachable', true);
  }
})();
