// Die Line Maker: shared page behaviour (mobile menu, section highlight, smooth links, guides filter and search,
// theme toggle, copy buttons, back to top, reading progress)
(function(){
  'use strict';
  const reduce = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // mobile menu
  const btn = document.querySelector('.menubtn'), menu = document.getElementById('mobileMenu');
  if (btn && menu){
    const set = (open) => { menu.hidden = !open; btn.setAttribute('aria-expanded', String(open)); };
    btn.addEventListener('click', () => set(menu.hidden));
    menu.addEventListener('click', (e) => { if (e.target.closest('a')) set(false); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !menu.hidden){ set(false); btn.focus(); } });
    document.addEventListener('click', (e) => { if (!menu.hidden && !e.target.closest('.nav')) set(false); });
  }

  // smooth scrolling for links to sections on the same page
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href*="#"]'); if (!a) return;
    const url = new URL(a.href, location.href);
    if (url.pathname !== location.pathname || !url.hash) return;
    const t = document.getElementById(decodeURIComponent(url.hash.slice(1))); if (!t) return;
    e.preventDefault();
    t.scrollIntoView({ block:'start', behavior: reduce() ? 'auto' : 'smooth' });
    history.replaceState(null, '', url.hash);
  });

  // guides page: filter posts by type and app (a link like guides#photoshop pre-selects a filter)
  const list = document.getElementById('postList');
  if (list){
    const sel = { cat:'', app:'' };
    const q = document.getElementById('postSearch');
    const norm = (s) => s.toLowerCase().replace(/\s+/g, ' ').trim();
    const apply = () => {
      let shown = 0;
      const words = q ? norm(q.value).split(' ').filter(Boolean) : [];
      list.querySelectorAll('li').forEach(li => {
        const text = li.dataset.text || (li.dataset.text = norm(li.textContent));
        const ok = (!sel.cat || li.dataset.cat === sel.cat) && (!sel.app || li.dataset.app === sel.app) && words.every(w => text.includes(w));
        li.hidden = !ok; if (ok) shown++;
      });
      const none = document.getElementById('noPosts'); if (none) none.hidden = shown > 0;
    };
    const choose = (f, v) => {
      sel[f] = v;
      document.querySelectorAll(`.filters button[data-f="${f}"]`).forEach(b => b.setAttribute('aria-pressed', String(b.dataset.v === v)));
      apply();
    };
    document.querySelectorAll('.filters button').forEach(b => b.addEventListener('click', () => choose(b.dataset.f, b.dataset.v)));
    if (q){
      q.addEventListener('input', apply);
      const fromQuery = new URLSearchParams(location.search).get('q'); if (fromQuery){ q.value = fromQuery; apply(); }
    }
    const fromHash = () => {
      const pre = { coreldraw:['app','CorelDraw'], photoshop:['app','Photoshop'], tutorials:['cat','Tutorial'], guides:['cat','Guide'], tips:['cat','Tips'], blog:['cat','Blog'] }[location.hash.slice(1).toLowerCase()];
      if (pre) choose(pre[0], pre[1]);
    };
    fromHash();
    window.addEventListener('hashchange', fromHash);
  }

  // highlight the section currently in view (pages whose nav links point at #sections)
  const links = [...document.querySelectorAll('.nav nav a[href^="#"]')];
  const targets = links.map(a => document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
  if (targets.length && 'IntersectionObserver' in window){
    const io = new IntersectionObserver((entries) => {
      for (const en of entries){
        if (!en.isIntersecting) continue;
        links.forEach(a => a.getAttribute('href') === '#' + en.target.id ? a.setAttribute('aria-current', 'true') : a.removeAttribute('aria-current'));
      }
    }, { rootMargin:'-40% 0px -55% 0px' });
    targets.forEach(t => io.observe(t));
  }

  // light / dark toggle (the choice is remembered on this device; the head script applies it before paint)
  const root = document.documentElement, darkMQ = window.matchMedia('(prefers-color-scheme: dark)');
  // pages with the product skin (body.skin) are dark until the visitor picks light
  const current = () => root.dataset.theme || (darkMQ.matches || document.body.classList.contains('skin') ? 'dark' : 'light');
  const label = () => document.querySelectorAll('.themebtn').forEach(b => {
    const d = current() === 'dark';
    b.setAttribute('aria-label', d ? 'Switch to light mode' : 'Switch to dark mode'); b.title = d ? 'Light mode' : 'Dark mode';
  });
  document.querySelectorAll('.themebtn').forEach(b => b.addEventListener('click', () => {
    const next = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('dlm-theme', next); } catch {}
    const meta = document.querySelector('meta[name="theme-color"]'); if (meta) meta.content = next === 'dark' ? '#0b0f17' : '#f4f5f8';
    label(); window.dispatchEvent(new Event('themechange'));
  }));
  darkMQ.addEventListener?.('change', label);
  label();

  // copy buttons for spot colour names in articles
  const COPY = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="13" height="13" x="9" y="9" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
  const DONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';
  const SPOTS = new Set(['CutContour', 'PerfCutContour', 'ThroughCut', 'RDG_WHITE', 'DieLine', 'Thru-cut', 'KissCut']);
  document.querySelectorAll('.prose code').forEach(c => {
    const v = c.textContent.trim(); if (!SPOTS.has(v) || c.closest('pre, a')) return;
    const b = document.createElement('button'); b.type = 'button'; b.className = 'copychip';
    b.title = 'Copy ' + v; b.setAttribute('aria-label', 'Copy ' + v); b.innerHTML = '<span></span>' + COPY; b.firstChild.textContent = v;
    b.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(v); }
      catch { const r = document.createRange(); r.selectNodeContents(b.firstChild); const s = getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand('copy'); s.removeAllRanges(); }
      b.classList.add('done'); b.lastChild.outerHTML = DONE; b.title = 'Copied';
      setTimeout(() => { b.classList.remove('done'); b.lastChild.outerHTML = COPY; b.title = 'Copy ' + v; }, 1600);
    });
    c.replaceWith(b);
  });

  // pages with a site header: back-to-top button; articles: reading progress bar
  if (document.querySelector('.nav')){
    const top = document.createElement('button'); top.type = 'button'; top.className = 'totop'; top.setAttribute('aria-label', 'Back to top'); top.title = 'Back to top';
    top.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m18 15-6-6-6 6"/></svg>';
    top.tabIndex = -1; document.body.appendChild(top);
    top.addEventListener('click', () => { window.scrollTo({ top:0, behavior: reduce() ? 'auto' : 'smooth' }); (document.querySelector('.skip') || document.body).focus?.(); });
    const bar = document.querySelector('.article') ? document.body.appendChild(Object.assign(document.createElement('div'), { className:'progress' })) : null;
    if (bar) bar.setAttribute('aria-hidden', 'true');
    let ticking = false;
    const onScroll = () => {
      ticking = false;
      const y = window.scrollY, show = y > window.innerHeight * 1.2;
      top.classList.toggle('show', show); top.tabIndex = show ? 0 : -1;
      if (bar){ const max = document.documentElement.scrollHeight - window.innerHeight; bar.style.transform = `scaleX(${max > 0 ? Math.min(1, y / max) : 0})`; }
    };
    window.addEventListener('scroll', () => { if (!ticking){ ticking = true; requestAnimationFrame(onScroll); } }, { passive:true });
    onScroll();
  }
  if (document.querySelector('.contactfab')) document.body.classList.add('has-fab');
})();
