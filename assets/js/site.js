/* Premier Barber & Beauty — site.js
   Smooth scroll (Lenis) + GSAP ScrollTrigger choreography, nav, menus,
   open/closed badge, gallery filters + lightbox, services tabs. */
(() => {
  'use strict';
  const doc = document.documentElement;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const hasGSAP = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';
  if (hasGSAP && !reduce) doc.classList.add('js');

  /* ------------------------------------------------ smooth scroll */
  let lenis = null;
  if (!reduce && typeof window.Lenis !== 'undefined') {
    lenis = new window.Lenis({ duration: 1.1, easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)), smoothWheel: true });
    if (hasGSAP) {
      lenis.on('scroll', window.ScrollTrigger.update);
      gsap.ticker.add(t => lenis.raf(t * 1000));
      gsap.ticker.lagSmoothing(0);
    } else {
      const raf = t => { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
    $$('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
      const id = a.getAttribute('href');
      if (id.length > 1 && $(id)) { e.preventDefault(); lenis.scrollTo(id, { offset: -80 }); }
    }));
  }

  /* ------------------------------------------------ nav + progress pole */
  const nav = $('.nav');
  const pole = $('.pole');
  const mbar = $('.mbar');
  let lastY = 0;
  const onScroll = () => {
    const y = window.scrollY;
    const max = document.body.scrollHeight - window.innerHeight;
    if (nav) {
      nav.classList.toggle('is-scrolled', y > 24);
      nav.classList.toggle('is-hidden', y > 400 && y > lastY && !document.body.classList.contains('menu-open'));
    }
    if (pole) pole.style.setProperty('--p', max > 0 ? (y / max).toFixed(4) : 0);
    if (mbar) mbar.classList.toggle('is-on', y > window.innerHeight * 0.55);
    lastY = y;
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ------------------------------------------------ mobile menu */
  const burger = $('.burger');
  if (burger) {
    const toggle = open => {
      document.body.classList.toggle('menu-open', open);
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      if (lenis) open ? lenis.stop() : lenis.start();
    };
    burger.addEventListener('click', () => toggle(!document.body.classList.contains('menu-open')));
    $$('.mmenu a').forEach(a => a.addEventListener('click', () => toggle(false)));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') toggle(false); });
  }

  /* ------------------------------------------------ open / closed badge (America/New_York) */
  const hoursEl = $('#shop-hours-data');
  if (hoursEl) {
    const hours = JSON.parse(hoursEl.textContent);
    const parts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', weekday: 'long', hour: '2-digit', minute: '2-digit', hour12: false })
      .formatToParts(new Date()).reduce((o, p) => (o[p.type] = p.value, o), {});
    const day = parts.weekday; const mins = (+parts.hour % 24) * 60 + (+parts.minute);
    const today = hours.find(h => h[0] === day);
    const toM = s => { const [h, m] = s.split(':'); return +h * 60 + +m; };
    const fmt = s => { let [h, m] = s.split(':').map(Number); const ap = h >= 12 ? 'PM' : 'AM'; h = h % 12 || 12; return h + (m ? ':' + String(m).padStart(2, '0') : '') + ' ' + ap; };
    let open = false, label = '';
    if (today && today[1]) {
      open = mins >= toM(today[1]) && mins < toM(today[2]);
      label = open ? `Open now · until ${fmt(today[2])}` : (mins < toM(today[1]) ? `Opens today at ${fmt(today[1])}` : '');
    }
    if (!label) {
      const idx = hours.findIndex(h => h[0] === day);
      for (let i = 1; i <= 7; i++) {
        const n = hours[(idx + i) % 7];
        if (n[1]) { label = `Closed now · opens ${i === 1 ? 'tomorrow' : n[0]} ${fmt(n[1])}`; break; }
      }
    }
    $$('[data-open-status]').forEach(el => {
      el.querySelector('.txt').textContent = label;
      el.querySelector('.dot').classList.toggle('is-closed', !open);
    });
    $$('.hours tr').forEach(tr => tr.classList.toggle('is-today', tr.dataset.day === day));
  }

  /* ------------------------------------------------ year */
  $$('[data-year]').forEach(el => (el.textContent = new Date().getFullYear()));

  /* ------------------------------------------------ gallery filters + lightbox */
  const masonry = $('.masonry');
  if (masonry) {
    const tiles = $$('.tile', masonry);
    $$('.filter').forEach(btn => btn.addEventListener('click', () => {
      const f = btn.dataset.filter;
      $$('.filter').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
      tiles.forEach(t => { t.hidden = !(f === 'all' || t.dataset.pro === f || t.dataset.cat === f); });
      if (hasGSAP) ScrollTrigger.refresh();
    }));
  }
  const lb = $('.lb');
  if (lb) {
    const img = $('.lb__stage img', lb), cap = $('.lb__cap', lb), count = $('.lb__count', lb), book = $('.lb__book', lb);
    let list = [], i = 0, lastFocus = null;
    const show = n => {
      i = (n + list.length) % list.length;
      const t = list[i];
      img.src = t.dataset.full; img.alt = t.querySelector('img').alt;
      cap.textContent = t.querySelector('img').alt;
      count.textContent = `${i + 1} / ${list.length}`;
      book.href = t.dataset.book; book.querySelector('span').textContent = `Book with ${t.dataset.proname}`;
    };
    const open = t => {
      list = $$('.tile').filter(x => !x.hidden); lastFocus = t;
      show(list.indexOf(t)); lb.classList.add('is-open'); lb.setAttribute('aria-hidden', 'false');
      if (lenis) lenis.stop(); $('.lb__close', lb).focus();
    };
    const close = () => { lb.classList.remove('is-open'); lb.setAttribute('aria-hidden', 'true'); if (lenis) lenis.start(); if (lastFocus) lastFocus.focus(); };
    $$('.tile').forEach(t => t.addEventListener('click', () => open(t)));
    $('.lb__close', lb).addEventListener('click', close);
    $('.lb__prev', lb).addEventListener('click', () => show(i - 1));
    $('.lb__next', lb).addEventListener('click', () => show(i + 1));
    lb.addEventListener('click', e => { if (e.target === lb || e.target.classList.contains('lb__stage')) close(); });
    document.addEventListener('keydown', e => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(i - 1); if (e.key === 'ArrowRight') show(i + 1);
    });
    let sx = 0;
    lb.addEventListener('touchstart', e => (sx = e.touches[0].clientX), { passive: true });
    lb.addEventListener('touchend', e => { const dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1)); });
  }

  /* ------------------------------------------------ services tab highlight */
  const tabs = $$('.svc-tabs a');
  if (tabs.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) tabs.forEach(t => t.classList.toggle('is-active', t.getAttribute('href') === '#' + e.target.id));
    }), { rootMargin: '-40% 0px -55% 0px' });
    $$('.cat').forEach(c => io.observe(c));
  }

  /* ================================================ MOTION ================================================ */
  if (!hasGSAP || reduce) return;
  gsap.registerPlugin(ScrollTrigger);
  const mm = gsap.matchMedia();

  // word-split headlines
  $$('[data-split]').forEach(el => {
    const walk = node => {
      [...node.childNodes].forEach(n => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(w => {
            if (!w) return;
            if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(w)); return; }
            const o = document.createElement('span'); o.className = 'w';
            const i = document.createElement('span'); i.textContent = w; o.appendChild(i); frag.appendChild(o);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1 && !n.classList.contains('w')) walk(n);
      });
    };
    walk(el); el.classList.add('is-split');
    const words = $$('.w>span', el);
    const inHero = !!el.closest('.hero');
    gsap.fromTo(words, { y: 0, yPercent: 105 }, {
      y: 0, yPercent: 0, duration: 1.1, ease: 'expo.out', stagger: 0.06, delay: inHero ? 0.25 : 0,
      scrollTrigger: inHero ? null : { trigger: el, start: 'top 85%' },
    });
  });

  // generic reveals (batched)
  ScrollTrigger.batch('[data-reveal]', {
    start: 'top 88%',
    onEnter: batch => gsap.to(batch, { opacity: 1, y: 0, scale: 1, duration: 1, ease: 'expo.out', stagger: 0.08, overwrite: true }),
  });

  // clip reveals on images
  $$('.clip-reveal').forEach(el => gsap.to(el, {
    clipPath: 'inset(0% 0% 0% 0% round 28px)', ease: 'none',
    scrollTrigger: { trigger: el, start: 'top 92%', end: 'top 35%', scrub: 0.6 },
  }));

  // parallax
  $$('[data-speed]').forEach(el => gsap.to(el, {
    yPercent: () => parseFloat(el.dataset.speed) * 100, ease: 'none',
    scrollTrigger: { trigger: el.parentElement, start: 'top bottom', end: 'bottom top', scrub: true },
  }));

  // count-ups
  $$('[data-count]').forEach(el => {
    const end = parseFloat(el.dataset.count), dec = (el.dataset.count.split('.')[1] || '').length, suf = el.dataset.suffix || '';
    const o = { v: 0 };
    gsap.to(o, { v: end, duration: 2, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 90%', once: true },
      onUpdate: () => (el.textContent = o.v.toFixed(dec) + suf) });
  });

  /* hero: image drift + razors swing open like a straight razor on scroll */
  const hero = $('.hero');
  if (hero) {
    const himg = $('.hero__media img', hero);
    gsap.fromTo(himg, { scale: 1.18 }, { scale: 1, duration: 2.2, ease: 'expo.out' });
    gsap.to(himg, { yPercent: 12, scale: 1.08, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
    gsap.from('.hero [data-hero-in]', { opacity: 0, y: 26, duration: 1.1, ease: 'expo.out', stagger: 0.1, delay: 0.55 });
    const rA = $('#razorA'), rB = $('#razorB');
    if (rA && rB) {
      gsap.from([rA, rB], { rotate: (i) => (i ? 40 : -40), opacity: 0, duration: 1.8, ease: 'expo.out', delay: 0.3, transformOrigin: '50% 50%' });
      gsap.to(rA, { rotate: -26, ease: 'none', transformOrigin: '50% 50%', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: 0.8 } });
      gsap.to(rB, { rotate: 26, ease: 'none', transformOrigin: '50% 50%', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: 0.8 } });
    }
  }

  /* marquees: constant drift, velocity-boosted, direction follows scroll */
  $$('.marquee').forEach(mq => {
    const right = mq.dataset.dir === 'right';
    const dur = parseFloat(mq.dataset.mqSpeed || 28);
    const tween = right
      ? gsap.fromTo(mq, { xPercent: -50 }, { xPercent: 0, repeat: -1, duration: dur, ease: 'none' })
      : gsap.to(mq, { xPercent: -50, repeat: -1, duration: dur, ease: 'none' });
    ScrollTrigger.create({
      trigger: mq, start: 'top bottom', end: 'bottom top',
      onUpdate: self => {
        const v = Math.min(Math.abs(self.getVelocity()) / 300, 5);
        gsap.to(tween, { timeScale: (self.direction === 1 ? 1 : -1) * (1 + v), duration: 0.3, overwrite: true });
        gsap.to(tween, { timeScale: self.direction === 1 ? 1 : -1, duration: 1.2, delay: 0.3 });
      },
    });
  });

  /* photo strips drift against each other */
  $$('.strip').forEach((s, k) => gsap.fromTo(s, { xPercent: k % 2 ? -22 : 0 }, {
    xPercent: k % 2 ? 0 : -22, ease: 'none',
    scrollTrigger: { trigger: s.closest('.strips'), start: 'top bottom', end: 'bottom top', scrub: 0.5 },
  }));

  /* team: pinned horizontal scroll on desktop.
     The min-height guard keeps short windows (landscape phones, small laptops)
     on the native swipe rail, where the whole card always fits on screen.
     Keep this query in sync with the matching block in site.css. */
  mm.add('(min-width: 901px) and (min-height: 640px)', () => {
    const rail = $('.team-rail[data-pin]');
    if (!rail) return;
    const track = $('.team-track', rail);
    const dist = () => track.scrollWidth - rail.clientWidth;
    const t = gsap.to(track, {
      x: () => -dist(), ease: 'none',
      scrollTrigger: { trigger: rail.closest('section'), start: 'top top', end: () => '+=' + dist(), pin: true, scrub: 0.8, invalidateOnRefresh: true, anticipatePin: 1 },
    });
    $$('.pro__img img', track).forEach(im => gsap.fromTo(im, { scale: 1.2 }, {
      scale: 1, ease: 'none', scrollTrigger: { trigger: im.closest('.pro'), containerAnimation: t, start: 'left right', end: 'center center', scrub: true },
    }));
    return () => t.kill();
  });

  /* pillars subtle stagger tilt */
  mm.add('(min-width: 901px)', () => {
    $$('.pillar').forEach((p, i) => gsap.fromTo(p, { y: 60 + i * 30 }, { y: 0, ease: 'none', scrollTrigger: { trigger: p.parentElement, start: 'top bottom', end: 'center center', scrub: 0.6 } }));
  });

  // footer mega word slides in
  const mega = $('.foot__mega');
  if (mega) gsap.fromTo(mega, { xPercent: 8 }, { xPercent: -4, ease: 'none', scrollTrigger: { trigger: mega, start: 'top bottom', end: 'bottom bottom', scrub: true } });

  window.addEventListener('load', () => ScrollTrigger.refresh());
})();
