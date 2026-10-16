/* CCNA 200-301 v2.0 Study Guide — review schedule, mistakes notebook and exam mode (no dependencies) */
(function () {
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) {} },
  };
  const DAY = 864e5, RK = 'ccna-review', MK = 'ccna-mistakes', EK = 'ccna-exams', AK = 'ccna-exam-active';
  const INTERVAL = [1, 1, 7, 30];               // days until the next review, by stage (0 = last attempt below 85 %)
  const DOMAINS = { 1: 'Network Infrastructure & Connectivity', 2: 'Switching & Network Access', 3: 'IP Routing',
    4: 'Network Services & Security', 5: 'AI, Operations & Management', R: 'Final review (mixed)' };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const fmtDate = t => new Date(t).toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
  const chTitle = n => { const e = $(`.sidebar a.ch[data-ch="${n}"] .cht`); return e ? e.textContent : `Chapter ${n}`; };
  const page = n => `chapter-${String(n).padStart(2, '0')}.html`;

  // ---- shared API used by the chapter quizzes (app.js) -------------------
  const CCNA = window.CCNA = {
    addMistake(id) {
      const m = store.get(MK, {});
      const e = m[id] || { added: Date.now(), note: '', misses: 0 };
      e.misses++; e.last = Date.now(); m[id] = e; store.set(MK, m); paintCounts();
    },
    quizDone(ch, pct) {
      const r = store.get(RK, {});
      const e = r[ch] || { stage: 0, history: [] };
      e.stage = pct >= 85 ? Math.min(e.stage + 1, 3) : 0;
      e.last = Date.now(); e.pct = pct; e.history = (e.history || []).concat([[Date.now(), pct]]).slice(-10);
      r[ch] = e; store.set(RK, r); paintDue();
      const days = INTERVAL[e.stage];
      toast(pct >= 85
        ? `🔁 Quiz complete (${pct} %). It comes back for review in ${days} day${days > 1 ? 's' : ''} — ${fmtDate(Date.now() + days * DAY)}.`
        : `🔁 Quiz complete (${pct} %). Below 85 %, so it comes back tomorrow. Missed questions are in your mistakes notebook.`);
    },
  };
  const dueAt = e => e.last + INTERVAL[e.stage] * DAY;

  function toast(msg) {
    const t = document.createElement('div'); t.className = 'toast'; t.textContent = msg;
    document.body.appendChild(t); setTimeout(() => t.classList.add('show'), 20);
    setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 400); }, 6000);
  }

  function paintCounts() {
    const n = Object.keys(store.get(MK, {})).length;
    $$('.mcount').forEach(e => { e.textContent = n || ''; e.hidden = !n; });
    $$('.mk-num').forEach(e => { e.textContent = n; });
  }

  function paintDue() {
    const r = store.get(RK, {}), now = Date.now();
    $$('[data-ch]').forEach(el => {
      if (!el.matches('a')) return;
      const e = r[el.dataset.ch];
      el.classList.toggle('due', !!e && dueAt(e) <= now);
    });
    const body = $('.rv-body'); if (!body) return;
    const rows = Object.entries(r).map(([ch, e]) => ({ ch: +ch, e, due: dueAt(e) })).sort((a, b) => a.due - b.due);
    if (!rows.length) {
      body.innerHTML = '<p class="dash-empty">Nothing scheduled yet. Finish any chapter\'s self-check quiz and it will come back here after 1 day, 1 week and 1 month.</p>';
      return;
    }
    const due = rows.filter(x => x.due <= now), soon = rows.filter(x => x.due > now).slice(0, 3);
    const mastered = rows.filter(x => x.e.stage >= 3).length;
    const row = (x, isDue) => `<a class="rv-row${isDue ? ' is-due' : ''}" href="${page(x.ch)}?retake=1#quiz"><span class="cn-mini">${x.ch}</span>
      <span class="rv-t">${esc(chTitle(x.ch))}<small>last ${x.e.pct} % · ${isDue ? 'due now' : 'due ' + fmtDate(x.due)}</small></span>
      <span class="rv-go">${isDue ? 'Retake →' : ''}</span></a>`;
    body.innerHTML = (due.length ? due.map(x => row(x, true)).join('') : '<p class="dash-empty">✓ Nothing due today. Nice work.</p>')
      + (soon.length ? `<div class="rv-soon">Coming up</div>${soon.map(x => row(x, false)).join('')}` : '')
      + `<div class="rv-foot">${rows.length} chapter${rows.length > 1 ? 's' : ''} on the schedule · ${mastered} at the 1-month stage</div>`;
  }

  function paintExamCard() {
    const h = store.get(EK, []); const n = $('.ex-num'); if (!n) return;
    if (h.length) { const last = h[h.length - 1]; n.textContent = last.pct + ' %'; $('.ex-sub').textContent = `last exam · ${last.total} questions · ${fmtDate(last.date)}`; }
  }

  // ---- question bank -----------------------------------------------------
  let bankP = null;
  const loadBank = () => bankP || (bankP = fetch('assets/site/questions.json').then(r => r.json()));

  const head = (q, extra = '') => `<div class="qhead"><span class="qn">${q.n}</span><span class="qkind">Ch ${q.ch} · ${esc(q.k)}</span>${extra}</div>`;
  const ctx = q => q.x ? `<details class="qctx"><summary>Show the output this question refers to</summary>${q.x}</details>` : '';

  // interactive card with instant feedback (used by the mistakes notebook)
  function practiceCard(q, onResult) {
    const el = document.createElement('div');
    const need = q.c ? q.c.length : 0;
    el.className = 'q' + (q.o ? '' : ' open');
    el.innerHTML = head(q) + ctx(q) + `<div class="qstem">${q.s}</div>` + (q.o
      ? `<div class="opts">${q.o.map(([l, t]) => `<button class="opt" type="button" data-l="${l}"><span class="ol">${l}</span><span class="ot">${t}</span></button>`).join('')}</div>`
        + (need > 1 ? `<div class="qact"><span class="qhint">Choose ${need}</span><button class="btn small qcheck" type="button" disabled>Check answer</button></div>` : '')
      : `<div class="qact"><button class="btn small qreveal" type="button">Show answer</button><span class="qhint">Answer it in your head first.</span></div>`)
      + `<div class="qans" hidden><div class="qverdict"></div>${q.a}${q.o ? '' : '<div class="selfmark"><span>Did you get it?</span><button class="btn small ok" type="button" data-m="1">✓ Got it</button><button class="btn small no" type="button" data-m="0">✗ Not yet</button></div>'}</div>`;
    const finish = (ok, picks) => {
      el.classList.add('answered'); el.classList.toggle('right', ok); el.classList.toggle('wrong', !ok);
      if (q.o) {
        $$('.opt', el).forEach(o => { o.disabled = true; const l = o.dataset.l;
          o.classList.toggle('is-correct', q.c.includes(l)); o.classList.toggle('is-wrong', picks.includes(l) && !q.c.includes(l)); });
        const ck = $('.qcheck', el); if (ck) ck.disabled = true;
        $('.qverdict', el).innerHTML = ok ? '<span class="ok">✓ Correct</span>' : `<span class="no">✗ Not quite — the answer is ${q.c.split('').join(' and ')}</span>`;
      } else {
        $('.selfmark', el).hidden = true;
        $('.qverdict', el).innerHTML = ok ? '<span class="ok">✓ You got it</span>' : '<span class="no">✗ Not yet</span>';
      }
      $('.qans', el).hidden = false; onResult(ok);
    };
    if (q.o) {
      const grade = picks => finish(picks.length === need && picks.every(p => q.c.includes(p)), picks);
      $$('.opt', el).forEach(o => o.addEventListener('click', () => {
        if (need === 1) return grade([o.dataset.l]);
        o.classList.toggle('picked'); $('.qcheck', el).disabled = $$('.opt.picked', el).length !== need;
      }));
      const ck = $('.qcheck', el); ck && ck.addEventListener('click', () => grade($$('.opt.picked', el).map(o => o.dataset.l)));
    } else {
      $('.qreveal', el).addEventListener('click', () => { $('.qans', el).hidden = false; $('.qreveal', el).closest('.qact').hidden = true; });
      $$('.selfmark button', el).forEach(b => b.addEventListener('click', () => finish(b.dataset.m === '1', [])));
    }
    return el;
  }

  // ---- mistakes notebook page -------------------------------------------
  const mkRoot = document.getElementById('mistakes');
  if (mkRoot) loadBank().then(bank => {
    const byId = Object.fromEntries(bank.map(q => [q.id, q]));
    const list = $('.mk-list', mkRoot), filter = $('.mk-filter', mkRoot);
    $('.mk-print', mkRoot).addEventListener('click', () => window.print());
    function render() {
      const m = store.get(MK, {});
      const ids = Object.keys(m).filter(id => byId[id]).sort((a, b) => m[b].last - m[a].last);
      const chs = [...new Set(ids.map(id => byId[id].ch))].sort((a, b) => a - b);
      const cur = filter.value;
      filter.innerHTML = '<option value="all">All chapters</option>' + chs.map(c => `<option value="${c}">Chapter ${c} · ${esc(chTitle(c))}</option>`).join('');
      filter.value = chs.includes(+cur) ? cur : 'all';
      const shown = ids.filter(id => filter.value === 'all' || byId[id].ch === +filter.value);
      $('.mk-summary', mkRoot).textContent = ids.length ? `${ids.length} question${ids.length > 1 ? 's' : ''} from ${chs.length} chapter${chs.length > 1 ? 's' : ''}` : '';
      list.innerHTML = ids.length ? '' : `<div class="mk-empty"><span>🎉</span><b>Your notebook is empty.</b><p>Questions you miss in a chapter quiz or in exam mode are added here automatically, so you can come back to exactly what you got wrong.</p><a class="btn primary" href="exam.html">Try exam mode →</a></div>`;
      shown.forEach(id => {
        const q = byId[id], e = m[id];
        const wrap = document.createElement('article'); wrap.className = 'mk-item';
        wrap.innerHTML = `<div class="mk-meta"><span>Missed ${e.misses}× · first on ${fmtDate(e.added)}</span><a href="${page(q.ch)}#quiz">Open in Chapter ${q.ch} →</a></div>`;
        wrap.appendChild(practiceCard(q, ok => {
          if (!ok) CCNA.addMistake(id);
          wrap.querySelector('.mk-hint').hidden = !ok;
        }));
        const foot = document.createElement('div'); foot.className = 'mk-foot';
        foot.innerHTML = `<label>My note<textarea rows="2" placeholder="What I thought → what is true → why I mixed it up">${esc(e.note || '')}</textarea></label>
          <div class="mk-btns"><span class="mk-hint" hidden>Got it right — if you can explain why, you can remove it.</span><button class="btn small mk-remove" type="button">✓ Remove — I've got it</button></div>`;
        $('textarea', foot).addEventListener('input', ev => { const mm = store.get(MK, {}); if (mm[id]) { mm[id].note = ev.target.value; store.set(MK, mm); } });
        $('.mk-remove', foot).addEventListener('click', () => {
          const mm = store.get(MK, {}); delete mm[id]; store.set(MK, mm);
          wrap.classList.add('gone'); setTimeout(() => { render(); paintCounts(); }, 250);
        });
        wrap.appendChild(foot); list.appendChild(wrap);
      });
    }
    filter.addEventListener('change', render);
    render();
  });

  // ---- exam mode page ----------------------------------------------------
  const exRoot = document.getElementById('exam');
  if (exRoot) loadBank().then(bank => {
    const byId = Object.fromEntries(bank.map(q => [q.id, q]));
    const setup = $('.ex-setup', exRoot), run = $('.ex-run', exRoot), res = $('.ex-results', exRoot), form = $('.ex-form', exRoot);
    let S = null, tick = null;
    const save = () => store.set(AK, S);
    const show = which => { setup.hidden = which !== 'setup'; run.hidden = which !== 'run'; res.hidden = which !== 'res'; window.scrollTo({ top: 0, behavior: 'instant' }); };

    function pool() {
      const f = new FormData(form), scope = f.get('scope'), done = store.get('ccna-done', []);
      return bank.filter(q => (f.get('types') === 'mixed' || q.o)
        && (scope === 'all' || (scope === 'done' ? done.includes(q.ch) : String(q.d) === scope)));
    }
    function paintNote() {
      const p = pool().length, want = +new FormData(form).get('count');
      $('.ex-note', exRoot).textContent = p === 0 ? 'No questions match — mark some chapters as done, or pick "All chapters".'
        : p < want ? `Only ${p} questions match, so the exam will have ${p}.` : `${p} questions match.`;
      $('.ex-go button', exRoot).disabled = p === 0;
    }
    form.addEventListener('change', paintNote);

    function history() {
      const h = store.get(EK, []).slice(-8).reverse();
      $('.ex-history', exRoot).innerHTML = h.length ? `<h3>Your recent exams</h3><div class="table-wrap"><table><thead><tr><th>Date</th><th>Score</th><th>Questions</th><th>Time</th><th>Weakest domain</th></tr></thead><tbody>${
        h.map(x => `<tr><td>${fmtDate(x.date)}</td><td><b class="${x.pct >= 85 ? 'good' : x.pct >= 60 ? 'mid' : 'low'}">${x.pct} %</b></td><td>${x.total}</td><td>${Math.round(x.secs / 60)} min</td><td>${esc(x.weak || '—')}</td></tr>`).join('')}</tbody></table></div>` : '';
    }
    function resumeBox() {
      const a = store.get(AK, null), box = $('.ex-resume', exRoot);
      if (a && a.finished && a.saved) { store.del(AK); box.hidden = true; return; }
      if (!a) { box.hidden = true; return; }
      if (a.finished) { S = a; results(); return; }
      const answered = Object.keys(a.picks).filter(k => a.picks[k]).length;
      box.innerHTML = `<b>⏸️ You have an exam in progress</b><span>${answered} of ${a.ids.length} answered${a.limit ? ' · ' + clock(left(a)) + ' left' : ''}</span><button class="btn small primary" type="button" data-act="resume">Resume</button><button class="btn small" type="button" data-act="discard">Discard</button>`;
      box.hidden = false;
      box.querySelector('[data-act=resume]').onclick = () => { S = a; if (S.limit && left(S) <= 0) return submit(); start(); };
      box.querySelector('[data-act=discard]').onclick = () => { store.del(AK); box.hidden = true; };
    }

    const left = s => Math.max(0, Math.round(s.limit - (Date.now() - s.start) / 1000));
    const clock = sec => `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`;

    form.addEventListener('submit', ev => {
      ev.preventDefault();
      const f = new FormData(form), p = pool();
      for (let i = p.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [p[i], p[j]] = [p[j], p[i]]; }
      const ids = p.slice(0, +f.get('count')).map(q => q.id);
      S = { ids, i: 0, picks: {}, flags: [], self: {}, start: Date.now(), limit: ids.length * +f.get('timer'), finished: false };
      save(); start();
    });

    function start() {
      show('run'); paintRun();
      clearInterval(tick);
      if (S.limit) tick = setInterval(() => {
        const t = $('.ex-timer', run); if (!t) return;
        const l = left(S); t.textContent = '⏱️ ' + clock(l); t.classList.toggle('warn', l <= 300);
        if (l <= 0) { clearInterval(tick); toast('⏰ Time is up — your exam has been submitted.'); submit(); }
      }, 1000);
    }

    function paintRun() {
      const q = byId[S.ids[S.i]], N = S.ids.length, pick = S.picks[q.id] || '';
      const need = q.c ? q.c.length : 0;
      const answered = S.ids.filter(id => S.picks[id]).length;
      run.innerHTML = `<div class="ex-bar"><b>Question ${S.i + 1} of ${N}</b><div class="bar"><i style="width:${answered / N * 100}%"></i></div>
        <span class="ex-count">${answered} answered</span>${S.limit ? `<span class="ex-timer">⏱️ ${clock(left(S))}</span>` : ''}
        <button class="btn small ex-flag${S.flags.includes(q.id) ? ' on' : ''}" type="button">⚑ ${S.flags.includes(q.id) ? 'Flagged' : 'Flag'}</button></div>
        <div class="q ex-q">${head({ ...q, n: S.i + 1 }, `<span class="qtag">${q.o ? (need > 1 ? 'choose ' + need : 'choose 1') : 'written'}</span>`)}${ctx(q)}<div class="qstem">${q.s}</div>
        ${q.o ? `<div class="opts">${q.o.map(([l, t]) => `<button class="opt${pick.includes(l) ? ' picked' : ''}" type="button" data-l="${l}"><span class="ol">${l}</span><span class="ot">${t}</span></button>`).join('')}</div>`
              : `<textarea class="ex-text" rows="4" placeholder="Type your answer (optional) — after submitting you will compare it with the model answer and mark it yourself.">${esc(pick)}</textarea>`}</div>
        <div class="ex-nav"><button class="btn ex-prev" type="button"${S.i ? '' : ' disabled'}>← Previous</button>
        ${S.i < N - 1 ? '<button class="btn primary ex-next" type="button">Next →</button>' : '<button class="btn primary ex-submit" type="button">Review &amp; submit</button>'}</div>
        <div class="ex-grid">${S.ids.map((id, k) => `<button type="button" data-k="${k}" class="${k === S.i ? 'cur ' : ''}${S.picks[id] ? 'ans ' : ''}${S.flags.includes(id) ? 'flag' : ''}">${k + 1}</button>`).join('')}</div>
        <div class="ex-end"><button class="btn small ex-submit2" type="button">Submit exam now</button></div>`;
      const go = k => { S.i = k; save(); paintRun(); };
      $$('.opt', run).forEach(o => o.addEventListener('click', () => {
        let p = S.picks[q.id] || '';
        if (need === 1) p = o.dataset.l;
        else p = p.includes(o.dataset.l) ? p.replace(o.dataset.l, '') : (p.length < need ? p + o.dataset.l : p);
        S.picks[q.id] = p.split('').sort().join(''); save(); paintRun();
      }));
      const ta = $('.ex-text', run); ta && ta.addEventListener('input', () => { S.picks[q.id] = ta.value.trim() ? ta.value : ''; save(); });
      $('.ex-flag', run).onclick = () => { S.flags = S.flags.includes(q.id) ? S.flags.filter(x => x !== q.id) : S.flags.concat(q.id); save(); paintRun(); };
      $('.ex-prev', run).onclick = () => go(S.i - 1);
      const nx = $('.ex-next', run); nx && (nx.onclick = () => go(S.i + 1));
      $$('.ex-grid button', run).forEach(b => b.onclick = () => go(+b.dataset.k));
      const confirmSubmit = () => {
        const open = S.ids.filter(id => !S.picks[id] && byId[id].o).length, flagged = S.flags.length;
        const msg = [open && `${open} multiple-choice question${open > 1 ? 's are' : ' is'} unanswered`, flagged && `${flagged} flagged`].filter(Boolean).join(' and ');
        if (!msg || confirm(`${msg}. Submit anyway?`)) submit();
      };
      const sb = $('.ex-submit', run); sb && (sb.onclick = confirmSubmit);
      $('.ex-submit2', run).onclick = confirmSubmit;
    }

    function submit() {
      clearInterval(tick);
      S.finished = true; S.secs = Math.round(Math.min((Date.now() - S.start) / 1000, S.limit || Infinity));
      S.ids.forEach(id => { const q = byId[id]; if (q.o && S.picks[id] !== q.c) CCNA.addMistake(id); });
      save(); results();
    }

    function score() {
      let right = 0, marked = 0; const dom = {};
      S.ids.forEach(id => {
        const q = byId[id], d = q.d;
        dom[d] = dom[d] || { r: 0, t: 0 };
        const ok = q.o ? S.picks[id] === q.c : S.self[id];
        if (q.o || ok !== undefined) { marked++; dom[d].t++; if (ok) { right++; dom[d].r++; } }
      });
      return { right, marked, dom, pending: S.ids.length - marked };
    }

    function results() {
      show('res');
      const sc = score(), N = S.ids.length;
      const pct = sc.marked ? Math.round(sc.right / N * 100) : 0;
      const domRows = Object.entries(sc.dom).sort().map(([d, v]) => {
        const p = v.t ? Math.round(v.r / v.t * 100) : 0;
        return `<div class="ex-dom"><span>${d === 'R' ? '' : 'Domain ' + d + ' · '}${esc(DOMAINS[d])}</span><div class="bar"><i class="${p >= 85 ? 'good' : p >= 60 ? 'mid' : 'low'}" style="width:${p}%"></i></div><b>${v.r} / ${v.t}</b></div>`;
      }).join('');
      res.innerHTML = `<div class="ex-score ${sc.pending ? '' : pct >= 85 ? 'good' : pct >= 60 ? 'mid' : 'low'}">
          <div><small>Your score</small><b>${sc.right} / ${N}</b><span>${sc.pending ? `${sc.pending} written answer${sc.pending > 1 ? 's' : ''} still to mark below` : pct + ' %' + (pct >= 85 ? ' — exam-ready pace 🏆' : pct >= 60 ? ' — getting there 💪' : ' — review the weak domains 📚')}</span></div>
          <div class="ex-meta">⏱️ ${Math.floor(S.secs / 60)} min ${S.secs % 60} s<br>📒 Wrong answers were added to your <a href="mistakes.html">mistakes notebook</a></div></div>
        <h3>By exam domain</h3><div class="ex-doms">${domRows}</div>
        <div class="ex-again"><button class="btn primary ex-new" type="button">New exam</button><a class="btn" href="mistakes.html">Open mistakes notebook</a></div>
        <h3>Question review</h3><div class="ex-review"></div>`;
      const rv = $('.ex-review', res);
      S.ids.forEach((id, k) => {
        const q = byId[id], pick = S.picks[id] || '';
        const el = document.createElement('div');
        if (q.o) {
          const ok = pick === q.c;
          el.className = 'q answered ' + (ok ? 'right' : 'wrong');
          el.innerHTML = head({ ...q, n: k + 1 }) + ctx(q) + `<div class="qstem">${q.s}</div><div class="opts">${q.o.map(([l, t]) =>
            `<button class="opt${q.c.includes(l) ? ' is-correct' : ''}${pick.includes(l) && !q.c.includes(l) ? ' is-wrong' : ''}" type="button" disabled><span class="ol">${l}</span><span class="ot">${t}</span></button>`).join('')}</div>
            <div class="qans"><div class="qverdict">${ok ? '<span class="ok">✓ Correct</span>' : `<span class="no">✗ ${pick ? 'You chose ' + pick.split('').join(' and ') : 'Not answered'} — the answer is ${q.c.split('').join(' and ')}</span>`}</div>${q.a}</div>`;
        } else {
          const m = S.self[id];
          el.className = 'q open answered' + (m === true ? ' right' : m === false ? ' wrong' : '');
          el.innerHTML = head({ ...q, n: k + 1 }) + ctx(q) + `<div class="qstem">${q.s}</div>
            <div class="ex-yours"><small>Your answer</small>${pick ? esc(pick).replace(/\n/g, '<br>') : '<i>(answered in your head)</i>'}</div>
            <div class="qans"><div class="qverdict">${m === true ? '<span class="ok">✓ You got it</span>' : m === false ? '<span class="no">✗ Not yet</span>' : '<b>Model answer</b>'}</div>${q.a}
            ${m === undefined ? '<div class="selfmark"><span>Did you get it?</span><button class="btn small ok" type="button" data-m="1">✓ Got it</button><button class="btn small no" type="button" data-m="0">✗ Not yet</button></div>' : ''}</div>`;
          $$('.selfmark button', el).forEach(b => b.onclick = () => {
            S.self[id] = b.dataset.m === '1'; if (!S.self[id]) CCNA.addMistake(id);
            save(); const y = window.scrollY; results(); window.scrollTo({ top: y, behavior: 'instant' }); finalize();
          });
        }
        rv.appendChild(el);
      });
      $('.ex-new', res).onclick = () => { store.del(AK); S = null; show('setup'); history(); resumeBox(); paintNote(); };
      finalize();
    }

    function finalize() {
      const sc = score();
      if (sc.pending || S.saved) return;
      const weakest = Object.entries(sc.dom).filter(([, v]) => v.t).sort((a, b) => a[1].r / a[1].t - b[1].r / b[1].t)[0];
      const h = store.get(EK, []);
      h.push({ date: Date.now(), total: S.ids.length, right: sc.right, pct: Math.round(sc.right / S.ids.length * 100), secs: S.secs,
        weak: weakest ? (weakest[0] === 'R' ? DOMAINS.R : `Domain ${weakest[0]} · ${DOMAINS[weakest[0]]}`) : '' });
      store.set(EK, h.slice(-30)); S.saved = true; save();
    }

    paintNote(); history(); resumeBox();
  });

  paintCounts(); paintDue(); paintExamCard();
})();
