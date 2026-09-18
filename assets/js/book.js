/* Premier Barber & Beauty — booking concierge.
   A 4-step picker (pro -> service -> preferred time -> details) that hands the
   visitor off to the pro's real calendar (Booksy / StyleSeat / theCut) with a
   summary ready to go. Live availability, deposits and confirmation always
   happen on the pro's platform. Nothing here claims a slot is reserved. */
(() => {
  'use strict';
  const root = document.querySelector('[data-booking]');
  if (!root) return;
  const DATA = JSON.parse(document.getElementById('booking-data').textContent);
  const $ = (s, c = root) => c.querySelector(s);
  const $$ = (s, c = root) => [...c.querySelectorAll(s)];
  const money = n => '$' + (Number.isInteger(n) ? n : n.toFixed(2));
  const state = { pro: null, svc: null, date: null, time: null, name: '', phone: '', notes: '' };
  const steps = $$('.bk__step');
  const tabs = $$('.bk__steps li');
  let now = 0;

  const go = (n, quiet) => {
    now = n;
    steps.forEach((s, i) => s.classList.toggle('is-now', i === n));
    tabs.forEach((t, i) => {
      t.classList.toggle('is-now', i === n);
      t.classList.toggle('is-done', i < n);
      t.querySelector('button').disabled = i > maxStep();
      t.querySelector('button').setAttribute('aria-current', i === n ? 'step' : 'false');
    });
    if (!quiet) {
      const top = root.getBoundingClientRect().top + window.scrollY - 100;
      if (window.scrollY > top) window.scrollTo({ top, behavior: 'smooth' });
      const h = steps[n].querySelector('h2'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
    }
    summary();
  };
  const maxStep = () => (!state.pro ? 0 : !state.svc ? 1 : !(state.date && state.time) ? 2 : 3);
  tabs.forEach((t, i) => t.querySelector('button').addEventListener('click', () => { if (i <= maxStep()) go(i); }));

  /* ---------- step 1: pro */
  const proWrap = $('[data-pros]');
  DATA.team.forEach(p => {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'choice'; b.setAttribute('aria-pressed', 'false'); b.dataset.slug = p.slug;
    b.innerHTML = `<img src="${p.img}" alt="" loading="lazy" width="400" height="400"><span><b>${p.name}</b><small>${p.role}</small><small>★ ${p.rating.toFixed(1)} · ${p.reviews} reviews on ${p.platform}</small></span>`;
    b.addEventListener('click', () => pickPro(p.slug));
    proWrap.appendChild(b);
  });
  const pickPro = slug => {
    state.pro = DATA.team.find(p => p.slug === slug);
    if (state.svc && !state.pro.menu.some(g => g.items.some(s => s.name === state.svc.name))) state.svc = null;
    $$('[data-pros] .choice').forEach(c => c.setAttribute('aria-pressed', String(c.dataset.slug === slug)));
    renderServices(); renderDays(); go(1);
  };

  /* ---------- step 2: service */
  const svcWrap = $('[data-services]');
  const renderServices = () => {
    const p = state.pro; svcWrap.innerHTML = '';
    $('[data-svc-title]').textContent = `What are we doing with ${p.first}?`;
    p.menu.forEach(g => {
      const grp = document.createElement('div'); grp.className = 'svc-group';
      grp.innerHTML = `<h3>${g.title}</h3><div class="choices" role="radiogroup" aria-label="${g.title}"></div>`;
      g.items.forEach(s => {
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'choice'; b.setAttribute('role', 'radio');
        b.setAttribute('aria-checked', String(!!(state.svc && state.svc.name === s.name)));
        b.innerHTML = `<span><b>${s.name}</b><small>${s.dur}</small></span><span class="price">${s.plus ? 'from ' : ''}${money(s.price)}</span>`;
        b.addEventListener('click', () => { state.svc = s; $$('[data-services] .choice').forEach(c => c.setAttribute('aria-checked', 'false')); b.setAttribute('aria-checked', 'true'); go(2); });
        grp.querySelector('.choices').appendChild(b);
      });
      svcWrap.appendChild(grp);
    });
  };

  /* ---------- step 3: preferred day + time */
  const dayWrap = $('[data-days]'), timeWrap = $('[data-times]');
  const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const hoursFor = (p, d) => {
    const h = (p.hours || DATA.shopHours).find(x => x[0] === DAYS[d.getDay()]);
    return h && h[1] ? h : null;
  };
  const renderDays = () => {
    dayWrap.innerHTML = ''; timeWrap.innerHTML = '';
    const base = new Date(); base.setHours(0, 0, 0, 0);
    for (let i = 0; i < 21; i++) {
      const d = new Date(base); d.setDate(base.getDate() + i);
      const open = hoursFor(state.pro, d);
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'day'; b.disabled = !open;
      b.setAttribute('aria-pressed', String(!!(state.date && +state.date === +d)));
      b.setAttribute('aria-label', d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) + (open ? '' : ' (closed)'));
      b.innerHTML = `<small>${i === 0 ? 'Today' : d.toLocaleDateString('en-US', { weekday: 'short' })}</small><b>${d.getDate()}</b><small>${d.toLocaleDateString('en-US', { month: 'short' })}</small>`;
      b.addEventListener('click', () => { state.date = d; state.time = null; $$('.day', dayWrap).forEach(x => x.setAttribute('aria-pressed', 'false')); b.setAttribute('aria-pressed', 'true'); renderTimes(); summary(); });
      dayWrap.appendChild(b);
    }
  };
  const renderTimes = () => {
    timeWrap.innerHTML = '';
    const h = hoursFor(state.pro, state.date); if (!h) return;
    const [sh, sm] = h[1].split(':').map(Number), [eh, em] = h[2].split(':').map(Number);
    const nowT = new Date();
    for (let m = sh * 60 + sm; m <= eh * 60 + em - 30; m += 30) {
      const t = new Date(state.date); t.setHours(Math.floor(m / 60), m % 60);
      if (t < new Date(nowT.getTime() + 60 * 60 * 1000)) continue;
      const label = t.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'time'; b.textContent = label;
      b.setAttribute('aria-pressed', String(state.time === label));
      b.addEventListener('click', () => { state.time = label; $$('.time', timeWrap).forEach(x => x.setAttribute('aria-pressed', 'false')); b.setAttribute('aria-pressed', 'true'); summary(); go(3); });
      timeWrap.appendChild(b);
    }
    if (!timeWrap.children.length) timeWrap.innerHTML = '<p class="muted">No more times today. Pick another day.</p>';
  };

  /* ---------- step 4: details -> handoff */
  const form = $('[data-details]');
  form.addEventListener('submit', e => {
    e.preventDefault();
    if (!form.reportValidity()) return;
    const el = form.elements; state.name = el['name'].value.trim(); state.phone = el['phone'].value.trim(); state.notes = el['notes'].value.trim();
    renderDone(); go(4);
  });
  const dateLabel = () => state.date ? state.date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) : '';
  const text = () => `Hi ${state.pro.first}! I'd like to book ${state.svc.name} (${state.svc.plus ? 'from ' : ''}${money(state.svc.price)}, ${state.svc.dur}) on ${dateLabel()} around ${state.time}. Name: ${state.name}. Phone: ${state.phone}.${state.notes ? ' Notes: ' + state.notes : ''}`;
  const renderDone = () => {
    const p = state.pro;
    $('[data-done-title]').textContent = `You're almost in ${p.first}'s chair.`;
    $('[data-done-copy]').textContent = `${p.first} takes bookings on ${p.platform}. We've saved your choices below. Tap the button to open ${p.first}'s live calendar, choose ${state.svc.name} at ${state.time} on ${dateLabel()}, and confirm. It takes about a minute.`;
    const hand = $('[data-handoff]'); hand.href = p.book_url; hand.querySelector('span').textContent = `Confirm on ${p.platform}`;
    $('[data-sms]').href = `${DATA.sms}?&body=${encodeURIComponent(text())}`;
  };
  $('[data-copy]').addEventListener('click', async e => {
    try { await navigator.clipboard.writeText(text()); e.currentTarget.querySelector('span').textContent = 'Copied'; } catch { /* clipboard blocked */ }
  });
  $('[data-restart]').addEventListener('click', () => {
    Object.assign(state, { pro: null, svc: null, date: null, time: null });
    $$('[data-pros] .choice').forEach(c => c.setAttribute('aria-pressed', 'false')); form.reset(); go(0);
  });
  $$('[data-back]').forEach(b => b.addEventListener('click', () => go(Math.max(0, now - 1))));

  /* ---------- summary */
  const sum = document.querySelector('[data-summary]');
  const summary = () => {
    if (!sum) return;
    sum.querySelector('[data-s-pro]').textContent = state.pro ? state.pro.name : '—';
    sum.querySelector('[data-s-svc]').textContent = state.svc ? state.svc.name : '—';
    sum.querySelector('[data-s-when]').textContent = state.date ? `${dateLabel()}${state.time ? ' · ' + state.time : ''}` : '—';
    sum.querySelector('[data-s-dur]').textContent = state.svc ? state.svc.dur : '—';
    sum.querySelector('[data-s-total]').textContent = state.svc ? (state.svc.plus ? 'from ' : '') + money(state.svc.price) : '$0';
    sum.querySelector('[data-s-where]').textContent = state.pro ? `Booked on ${state.pro.platform}` : 'Pick a pro to begin';
  };

  // deep link: /book.html?pro=maal
  const q = new URLSearchParams(location.search).get('pro');
  if (q && DATA.team.some(p => p.slug === q)) pickPro(q); else go(0, true);
})();
