/* CCNA 200-301 v2.0 Study Guide — site behaviour (no dependencies) */
(function () {
  const root = document.documentElement;
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } },
  };

  // ---- theme ------------------------------------------------------------
  const themeBtn = document.querySelector('.theme');
  themeBtn && themeBtn.addEventListener('click', () => {
    const dark = root.dataset.theme ? root.dataset.theme === 'dark'
      : window.matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('theme', root.dataset.theme); } catch (e) {}
  });

  // ---- mobile menu -------------------------------------------------------
  const menu = document.querySelector('.menu');
  menu && menu.addEventListener('click', () => document.body.classList.toggle('nav-open'));
  document.querySelector('.content').addEventListener('click', () => document.body.classList.remove('nav-open'));

  // ---- progress ----------------------------------------------------------
  const TOTAL = 28;
  function paint() {
    const done = store.get('ccna-done', []);
    document.querySelectorAll('[data-ch]').forEach(el => {
      const on = done.includes(+el.dataset.ch);
      if (el.matches('input')) el.checked = on; else el.classList.toggle('is-done', on);
    });
    const pct = Math.round(done.length / TOTAL * 100);
    document.querySelectorAll('.bar i').forEach(b => { b.style.width = pct + '%'; });
    document.querySelectorAll('.progress span, .ptext').forEach(s => { s.textContent = `${done.length} of ${TOTAL} chapters done · ${pct}%`; });
  }
  document.querySelectorAll('input[data-ch]').forEach(cb => cb.addEventListener('change', () => {
    const n = +cb.dataset.ch; let done = store.get('ccna-done', []);
    done = cb.checked ? [...new Set([...done, n])] : done.filter(x => x !== n);
    store.set('ccna-done', done); paint();
  }));
  paint();

  // keep the active chapter visible in the sidebar
  const active = document.querySelector('.sidebar a.active');
  active && active.scrollIntoView({ block: 'center' });

  // ---- figure lightbox ---------------------------------------------------
  const lb = document.querySelector('.lightbox'), lbImg = lb && lb.querySelector('img');
  document.querySelectorAll('.zoom').forEach(b => b.addEventListener('click', () => {
    const img = b.querySelector('img'); lbImg.src = img.src; lbImg.alt = img.alt; lb.hidden = false;
  }));
  lb && lb.addEventListener('click', () => { lb.hidden = true; lbImg.src = ''; });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && lb && !lb.hidden) { lb.hidden = true; } });

  // ---- "on this page" highlight -----------------------------------------
  const tocLinks = [...document.querySelectorAll('.toc a')];
  if (tocLinks.length && 'IntersectionObserver' in window) {
    const map = new Map(tocLinks.map(a => [decodeURIComponent(a.hash.slice(1)), a]));
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) { tocLinks.forEach(a => a.classList.remove('on')); const a = map.get(en.target.id); a && a.classList.add('on'); }
      });
    }, { rootMargin: '-70px 0px -70% 0px' });
    document.querySelectorAll('.prose h3[id]').forEach(h => io.observe(h));
  }

  // ---- search ------------------------------------------------------------
  const q = document.getElementById('q'), out = document.getElementById('results');
  let index = null, sel = -1;
  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  async function load() {
    if (index) return index;
    const r = await fetch('assets/site/search.json'); index = await r.json(); return index;
  }
  function snippet(text, terms) {
    const low = text.toLowerCase(); let i = -1;
    for (const t of terms) { i = low.indexOf(t); if (i >= 0) break; }
    const start = Math.max(0, i - 60), s = (start ? '…' : '') + text.slice(start, start + 180) + '…';
    let h = esc(s);
    terms.forEach(t => { if (t.length > 1) h = h.replace(new RegExp(t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), m => `<mark>${m}</mark>`); });
    return h;
  }
  async function run() {
    const v = q.value.trim().toLowerCase();
    if (v.length < 2) { out.classList.remove('open'); return; }
    const terms = v.split(/\s+/).filter(Boolean);
    const data = await load();
    const hits = [];
    for (const s of data) {
      const t = s.t.toLowerCase(), x = s.x.toLowerCase();
      if (!terms.every(w => t.includes(w) || x.includes(w))) continue;
      let score = 0; terms.forEach(w => { if (t.includes(w)) score += 10; score += Math.min(5, x.split(w).length - 1); });
      hits.push([score, s]);
    }
    hits.sort((a, b) => b[0] - a[0]);
    sel = -1;
    out.innerHTML = hits.slice(0, 12).map(([, s]) =>
      `<a href="${s.p}"><small>${esc(s.c)}</small><b>${esc(s.t)}</b><p>${snippet(s.x, terms)}</p></a>`).join('')
      || '<div class="none">No matches — try fewer or different words.</div>';
    out.classList.add('open');
  }
  let timer;
  q && q.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(run, 120); });
  q && q.addEventListener('focus', () => { load(); if (q.value.trim().length > 1) run(); });
  q && q.addEventListener('keydown', e => {
    const items = [...out.querySelectorAll('a')];
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
      items.forEach((a, i) => a.classList.toggle('sel', i === sel)); items[sel] && items[sel].scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter' && items.length) { location.href = (items[sel] || items[0]).href; }
    else if (e.key === 'Escape') { out.classList.remove('open'); q.blur(); }
  });
  document.addEventListener('click', e => { if (!e.target.closest('.search')) out.classList.remove('open'); });
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement !== q && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); q.focus(); }
  });
})();
