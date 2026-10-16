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

  // ---- copy buttons on code / terminal blocks ----------------------------
  document.querySelectorAll('.copy').forEach(b => b.addEventListener('click', async () => {
    const box = b.closest('.term, .codebox');
    const text = b.dataset.copy !== undefined ? b.dataset.copy : box.querySelector('pre').innerText;
    try { await navigator.clipboard.writeText(text); }
    catch (e) { const t = document.createElement('textarea'); t.value = text; document.body.appendChild(t); t.select(); document.execCommand('copy'); t.remove(); }
    const old = b.textContent; b.textContent = 'Copied ✓'; b.classList.add('done-copy');
    setTimeout(() => { b.textContent = old; b.classList.remove('done-copy'); }, 1400);
  }));

  // ---- chapter quizzes ---------------------------------------------------
  const quizKey = ch => 'ccna-quiz-' + ch;
  function quizStats(ch, total) {
    const st = store.get(quizKey(ch), {});
    const vals = Object.values(st);
    return { answered: vals.length, right: vals.filter(v => v.ok).length, total };
  }
  function paintQuizMeta() {
    document.querySelectorAll('.qmeta[data-ch]').forEach(a => {
      const s = quizStats(a.dataset.ch, +a.dataset.total);
      a.textContent = s.answered ? `📝 Self-check: ${s.right} / ${s.total}` : `📝 Self-check: ${s.total} questions`;
      a.classList.toggle('has-score', s.answered > 0);
    });
  }
  document.querySelectorAll('.quiz').forEach(quiz => {
    const ch = quiz.dataset.ch, total = +quiz.dataset.total;
    const save = (q, rec) => { const st = store.get(quizKey(ch), {}); st[q] = rec; store.set(quizKey(ch), st); };
    function paintScore() {
      const s = quizStats(ch, total);
      quiz.querySelector('.qs-num').textContent = `${s.right} / ${total}`;
      quiz.querySelector('.qs-sub').textContent = s.answered ? `${s.answered} of ${total} answered` : 'not started';
      quiz.querySelector('.quiz-score .bar i').style.width = (s.right / total * 100) + '%';
      const done = quiz.querySelector('.quiz-done');
      if (s.answered === total) {
        const pct = Math.round(s.right / total * 100);
        const msg = pct >= 85 ? ['🏆', 'Exam-ready on this chapter!', 'Mark it as done and keep going.']
                  : pct >= 60 ? ['💪', 'Solid — nearly there.', 'Re-read the sections behind the questions you missed, then reset and try again.']
                  : ['📚', 'Worth another pass.', 'Revisit the chapter (start with the exam tips and memory tricks), then reset the quiz.'];
        done.innerHTML = `<span class="big">${msg[0]}</span><div><b>${s.right} / ${total} (${pct} %) — ${msg[1]}</b><p>${msg[2]}</p></div>`;
        done.hidden = false;
      } else done.hidden = true;
      paintQuizMeta();
    }
    function show(q, ok, picks) {
      const correct = (q.dataset.correct || '').split('');
      q.classList.add('answered'); q.classList.toggle('right', ok); q.classList.toggle('wrong', !ok);
      q.querySelectorAll('.opt').forEach(o => {
        o.disabled = true; const l = o.dataset.l;
        o.classList.toggle('is-correct', correct.includes(l));
        o.classList.toggle('is-wrong', picks.includes(l) && !correct.includes(l));
        o.classList.toggle('picked', picks.includes(l));
      });
      const ck = q.querySelector('.qcheck'); if (ck) ck.disabled = true;
      const rv = q.querySelector('.qreveal'); if (rv) rv.closest('.qact').hidden = true;
      const a = q.querySelector('.qans'); a.hidden = false;
      const v = q.querySelector('.qverdict');
      if (q.classList.contains('open')) {
        v.innerHTML = ok === null ? '' : ok ? '<span class="ok">✓ You got it</span>' : '<span class="no">✗ Not yet — worth another look</span>';
        q.querySelector('.selfmark').hidden = ok !== null;
      } else {
        v.innerHTML = ok ? '<span class="ok">✓ Correct</span>' : `<span class="no">✗ Not quite — the answer is ${correct.join(' and ')}</span>`;
      }
    }
    quiz.querySelectorAll('.q:not(.open)').forEach(q => {
      const need = (q.dataset.correct || '').length;
      const check = q.querySelector('.qcheck');
      const grade = picks => {
        const correct = q.dataset.correct.split('');
        const ok = picks.length === correct.length && picks.every(p => correct.includes(p));
        save(q.dataset.q, { ok, pick: picks.join('') }); show(q, ok, picks); paintScore();
      };
      q.querySelectorAll('.opt').forEach(o => o.addEventListener('click', () => {
        if (need === 1) return grade([o.dataset.l]);
        o.classList.toggle('picked');
        const picks = [...q.querySelectorAll('.opt.picked')].map(x => x.dataset.l);
        check.disabled = picks.length !== need;
      }));
      check && check.addEventListener('click', () => grade([...q.querySelectorAll('.opt.picked')].map(x => x.dataset.l)));
    });
    quiz.querySelectorAll('.q.open').forEach(q => {
      q.querySelector('.qreveal').addEventListener('click', () => show(q, null, []));
      q.querySelectorAll('.selfmark button').forEach(b => b.addEventListener('click', () => {
        const ok = b.dataset.m === '1'; save(q.dataset.q, { ok }); show(q, ok, []); paintScore();
      }));
    });
    quiz.querySelector('.qreset').addEventListener('click', () => {
      store.set(quizKey(ch), {});
      quiz.querySelectorAll('.q').forEach(q => {
        q.classList.remove('answered', 'right', 'wrong');
        q.querySelectorAll('.opt').forEach(o => { o.disabled = false; o.classList.remove('is-correct', 'is-wrong', 'picked'); });
        const ck = q.querySelector('.qcheck'); if (ck) ck.disabled = true;
        const rv = q.querySelector('.qreveal'); if (rv) rv.closest('.qact').hidden = false;
        q.querySelector('.qans').hidden = true;
        const sm = q.querySelector('.selfmark'); if (sm) sm.hidden = false;
      });
      paintScore();
    });
    // restore saved answers
    const st = store.get(quizKey(ch), {});
    quiz.querySelectorAll('.q').forEach(q => {
      const rec = st[q.dataset.q]; if (!rec) return;
      show(q, rec.ok, (rec.pick || '').split('').filter(Boolean));
    });
    paintScore();
  });
  paintQuizMeta();

  // ---- subnetting practice -----------------------------------------------
  const sn = document.getElementById('sn');
  if (sn) {
    const LEVELS = { easy: [24, 30], medium: [16, 30], hard: [8, 30] };
    const toInt = a => a.split('.').reduce((n, o) => n * 256 + +o, 0) >>> 0;
    const toIp = n => [24, 16, 8, 0].map(s => (n >>> s) & 255).join('.');
    const maskOf = p => p === 0 ? 0 : (0xFFFFFFFF << (32 - p)) >>> 0;
    const valid = s => /^\s*\d{1,3}(\.\d{1,3}){3}\s*$/.test(s) && s.trim().split('.').every(o => +o <= 255);
    const rnd = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
    let level = store.get('sn-level', 'easy'), cur = null, solved = false;
    const stats = () => store.get('sn-stats', { streak: 0, best: 0, total: 0 });
    function paintStats() {
      const s = stats();
      sn.querySelector('.st-streak').textContent = s.streak; sn.querySelector('.st-best').textContent = s.best; sn.querySelector('.st-total').textContent = s.total;
      sn.querySelectorAll('.sn-levels button').forEach(b => b.classList.toggle('on', b.dataset.level === level));
    }
    function firstOctet() {
      const pool = [[10, 10], [172, 172], [192, 192], [rnd(1, 223), 0]];
      const pick = pool[rnd(0, 3)][0];
      return pick === 127 ? 10 : pick;
    }
    function next() {
      const [lo, hi] = LEVELS[level];
      const p = rnd(lo, hi);
      const o1 = firstOctet();
      const o2 = o1 === 172 ? rnd(16, 31) : o1 === 192 ? 168 : rnd(0, 255);
      let ip = toInt(`${o1}.${o2}.${rnd(0, 255)}.${rnd(0, 255)}`);
      const m = maskOf(p), net = (ip & m) >>> 0, bc = (net | (~m >>> 0)) >>> 0;
      if (ip === net || ip === bc) ip = net + 1 + rnd(0, Math.max(0, bc - net - 2));
      cur = { p, ip, m, net, bc };
      solved = false;
      sn.querySelector('.sn-addr').textContent = `${toIp(ip)} /${p}`;
      sn.querySelector('.sn-mask').textContent = `mask ${toIp(m)}`;
      sn.querySelectorAll('.sn-form input').forEach(i => { i.value = ''; i.classList.remove('good', 'bad'); });
      sn.querySelector('.sn-result').hidden = true;
      sn.querySelector('.sn-form input').focus({ preventScroll: true });
    }
    function answers() {
      const c = cur;
      return { net: toIp(c.net), bc: toIp(c.bc), first: toIp(c.net + 1), last: toIp(c.bc - 1), hosts: String(2 ** (32 - c.p) - 2) };
    }
    function explain() {
      const c = cur, maskOct = toIp(c.m).split('.').map(Number);
      const k = maskOct.findIndex(o => o !== 255);
      const magic = 256 - maskOct[k];
      const ipOct = toIp(c.ip).split('.').map(Number), netOct = toIp(c.net).split('.').map(Number);
      const names = ['1st', '2nd', '3rd', '4th'];
      const a = answers();
      if (maskOct[k] === 0) {
        return `<ol>
        <li>/${c.p} → mask <b>${toIp(c.m)}</b>. The mask ends exactly on an octet boundary — no magic number needed.</li>
        <li>Keep the first ${k} octet${k > 1 ? 's' : ''} (the network part); set the rest to 0 for the network and 255 for the broadcast.</li>
        <li>Network <b>${a.net}</b> · broadcast <b>${a.bc}</b>.</li>
        <li>Usable range <b>${a.first} – ${a.last}</b> · hosts = 2<sup>${32 - c.p}</sup> − 2 = <b>${Number(a.hosts).toLocaleString()}</b>.</li></ol>`;
      }
      return `<ol>
        <li>/${c.p} → mask <b>${toIp(c.m)}</b>. The interesting octet is the <b>${names[k]}</b> (${maskOct[k]}).</li>
        <li>Magic number = 256 − ${maskOct[k]} = <b>${magic}</b>. Subnets in the ${names[k]} octet start at 0, ${magic}, ${magic * 2}, ${magic * 3} …</li>
        <li>The host's ${names[k]} octet is ${ipOct[k]}, which falls in the block <b>${netOct[k]} – ${netOct[k] + magic - 1}</b>.</li>
        <li>Network <b>${a.net}</b> · broadcast <b>${a.bc}</b> (next subnet − 1).</li>
        <li>Usable range <b>${a.first} – ${a.last}</b> · hosts = 2<sup>${32 - c.p}</sup> − 2 = <b>${Number(a.hosts).toLocaleString()}</b>.</li></ol>`;
    }
    function check(e) {
      e && e.preventDefault();
      if (solved) return next();
      const a = answers(); let good = 0;
      sn.querySelectorAll('.sn-form input').forEach(i => {
        const v = i.value.trim().replace(/,/g, '');
        const ok = i.name === 'hosts' ? v === a.hosts : valid(v) && toIp(toInt(v.trim())) === a[i.name];
        i.classList.toggle('good', ok); i.classList.toggle('bad', !ok); if (ok) good++;
      });
      const s = stats(), res = sn.querySelector('.sn-result');
      if (good === 5) {
        s.streak++; s.total++; s.best = Math.max(s.best, s.streak); solved = true;
        res.className = 'sn-result right';
        res.innerHTML = `<b>✓ All five correct!</b> ${s.streak > 1 ? `Streak: ${s.streak} 🔥` : ''} Press <kbd>Enter</kbd> for the next address.`;
      } else {
        s.streak = 0;
        res.className = 'sn-result wrong';
        res.innerHTML = `<b>${good} of 5 correct.</b> Fix the red boxes, or <button type="button" class="linkish sn-show2">show the solution</button>.`;
        res.querySelector('.sn-show2').addEventListener('click', reveal);
      }
      store.set('sn-stats', s); res.hidden = false; paintStats();
    }
    function reveal() {
      const a = answers();
      sn.querySelectorAll('.sn-form input').forEach(i => { i.value = a[i.name]; i.classList.remove('bad'); i.classList.add('good'); });
      const s = stats(); s.streak = 0; store.set('sn-stats', s); paintStats();
      solved = true;
      const res = sn.querySelector('.sn-result');
      res.className = 'sn-result solution'; res.innerHTML = `<b>How to solve it</b>${explain()}<p>Press <kbd>Enter</kbd> for the next address.</p>`;
      res.hidden = false;
    }
    sn.querySelector('.sn-form').addEventListener('submit', check);
    sn.querySelector('.sn-show').addEventListener('click', reveal);
    sn.querySelector('.sn-next').addEventListener('click', next);
    sn.querySelectorAll('.sn-levels button').forEach(b => b.addEventListener('click', () => { level = b.dataset.level; store.set('sn-level', level); paintStats(); next(); }));
    paintStats(); next();
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
