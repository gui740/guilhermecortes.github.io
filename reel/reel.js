/* Motor de timeline determinístico: window.seek(t) desenha o quadro do instante t (s).
   Tempos vêm de timeline.js (timestamps por palavra da narração). */
const FPS = 30, W = 1080, H = 1920;
const TLW = {}; TL.frases.forEach(f => TLW[f.id] = f);

/* "c2a" início da frase · "c2a:3" palavra 3 · "c2a:3e" fim da palavra · "c2a$" fim da frase · "end" · +/- offset */
function T(ref) {
  ref = String(ref).trim();
  if (/^-?[\d.]+$/.test(ref)) return +ref;
  const m = ref.match(/^([a-z0-9]+?)(?::(\d+)(e)?|(\$))?([+-][\d.]+)?$/i);
  if (!m) throw new Error('ref inválida: ' + ref);
  let base;
  if (m[1] === 'end') base = TL.duracao;
  else {
    const f = TLW[m[1]]; if (!f) throw new Error('frase desconhecida: ' + ref);
    if (m[2] != null) { const w = f.palavras[+m[2]]; if (!w) throw new Error('palavra inexistente: ' + ref); base = m[3] ? w.e : w.t; }
    else base = m[4] ? f.t1 : f.palavras[0].t;
  }
  return base + (m[5] ? +m[5] : 0);
}
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const eOut = p => 1 - Math.pow(1 - p, 3), eIn = p => p * p * p, eIO = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eBack = p => { const c = 1.9; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const DUR = { word: .15, pop: .28, stamp: .13, up: .38, down: .38, left: .34, right: .34, draw: .24, wipe: .32, fade: .2, drop: .26, flash: .3, cut: .001 };
const LEAD = 0.03;          // a palavra entra 1 quadro antes do som
const items = [], shots = [], SFX = [];

/* ---------- construção das palavras ----------
   tokens separados por espaço; "|" quebra linha. Prefixos: * ExtraBold · ~ conectivo pequeno · _ sublinhado
   / itálico · # tarja de sigilo · + não consome palavra da narração (entra junto com a anterior) · "·" = espaço */
function buildSay(el) {
  const [sid, st] = el.dataset.say.split(':'); let idx = +(st || 0), last = T(sid);
  const keep = [...el.children];                                   // filhos (ex.: risco) são preservados
  const toks = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').trim().split(/\s+/); el.textContent = '';
  let ln = document.createElement('div'); ln.className = 'ln'; el.appendChild(ln);
  for (let tok of toks) {
    if (tok === '|') { ln = document.createElement('div'); ln.className = 'ln'; el.appendChild(ln); continue; }
    const f = {}; while (/^[*~_\/#+]/.test(tok)) { f[tok[0]] = 1; tok = tok.slice(1); }
    const s = document.createElement('span');
    s.className = 'w' + (f['+'] ? ' glue' : '') + (f['*'] ? ' b' : '') + (f['~'] ? ' l' : '') + (f['/'] ? ' it' : '');
    tok = tok.replace(/·/g, ' ');
    if (tok.endsWith('!')) { s.append(tok.slice(0, -1)); const i = document.createElement('i'); i.textContent = '!'; s.appendChild(i); } else s.textContent = tok;
    let t; if (f['+']) t = last + 0.1; else { t = T(sid + ':' + idx) - LEAD; idx++; } last = t;
    ln.appendChild(s); items.push({ el: s, t0: t, fx: 'word', dur: DUR.word });
    if (f['_']) { const u = document.createElement('s'); u.className = 'ul'; s.appendChild(u); items.push({ el: u, t0: t + .12, fx: 'draw', dur: DUR.draw }); }
    if (f['#']) { const u = document.createElement('s'); u.className = 'tarja'; s.appendChild(u); items.push({ el: u, t0: t, fx: 'cut', dur: .001, out: t + .55, outDur: .3 }); SFX.push({ t: t + .55, n: 'whoosh_s' }); }
  }
  keep.forEach(k => el.appendChild(k));
  if (idx > TLW[sid].palavras.length) throw new Error('tokens demais em ' + el.dataset.say);
}
const SELO = `<svg viewBox="0 0 240 240"><defs><path id="sa" d="M 34 120 A 86 86 0 0 1 206 120"/><path id="sb" d="M 22 120 A 98 98 0 0 0 218 120"/></defs>
<circle cx="120" cy="120" r="113" fill="none" stroke="currentColor" stroke-width="3.2"/>
<text font-family="Space Mono" font-weight="700" font-size="30" fill="currentColor" letter-spacing="2"><textPath href="#sa" startOffset="50%" text-anchor="middle">MPT + TRT</textPath></text>
<text font-family="Space Mono" font-weight="700" font-size="30" fill="currentColor" letter-spacing="2"><textPath href="#sb" startOffset="50%" text-anchor="middle">MATO GROSSO</textPath></text>
<circle cx="22" cy="132" r="4" fill="currentColor"/><circle cx="218" cy="132" r="4" fill="currentColor"/></svg>`;
const CHECK = `<svg viewBox="0 0 100 100"><polyline points="27,52 44,68 75,34" fill="none" stroke="#EAE7DC" stroke-width="11" stroke-linejoin="miter"/></svg>`;

function init() {
  document.querySelectorAll('.selo').forEach(e => e.innerHTML = SELO);
  document.querySelectorAll('.ck').forEach(e => e.innerHTML = CHECK);
  document.querySelectorAll('.bars').forEach(e => { for (let i = 0; i < 30; i++) e.appendChild(document.createElement('b')); });
  document.querySelectorAll('[data-say]').forEach(buildSay);
  document.querySelectorAll('[data-fit]').forEach(el => {          // encolhe a fonte até a linha mais larga caber
    const max = +el.dataset.fit; let w = 0; el.querySelectorAll('.ln').forEach(l => w = Math.max(w, l.scrollWidth)); if (!w) w = el.scrollWidth;
    if (w > max) el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) * max / w) + 'px';
  });
  document.querySelectorAll('[data-at]').forEach(el => {
    const fx = el.dataset.fx || 'word', t0 = T(el.dataset.at);
    const it = { el, t0, fx, dur: +(el.dataset.dur || DUR[fx]), base: el.dataset.base || '', dist: +(el.dataset.dist || 1500) };
    if (el.dataset.out) { it.out = T(el.dataset.out); it.outDur = +(el.dataset.outdur || .3); }
    items.push(it);
    if (el.dataset.sfx) el.dataset.sfx.split(',').forEach(n => SFX.push({ t: t0 + (fx === 'stamp' ? DUR.stamp : 0), n }));
  });
  document.querySelectorAll('[data-poses]').forEach(el => {
    const poses = el.dataset.poses.split(';').map(s => { const a = s.trim().split(/\s+/); return { t: T(a[0]), x: +a[1], y: +a[2], s: +a[3], tw: +(a[4] || 0) }; });
    let it = items.find(i => i.el === el); if (!it) { it = { el, t0: -1, fx: 'cut', dur: .001, base: '' }; items.push(it); }
    it.poses = poses; it.w = el.offsetWidth; it.h = el.offsetHeight;
  });
  document.querySelectorAll('.shot').forEach((el, i) => {
    const s = { el, from: T(el.dataset.from), to: T(el.dataset.to), enter: el.dataset.enter, exit: el.dataset.exit, bg: el.classList.contains('black') ? 'black' : el.classList.contains('yellow') ? 'yellow' : 'cream', ht: el.dataset.ht || 'A', lab: el.dataset.lab || '' };
    el.style.zIndex = 100 - i; shots.push(s);
    if (el.dataset.sfx) el.dataset.sfx.split(',').forEach(n => SFX.push({ t: s.from, n }));
  });
  items.forEach(it => { it.shot = shots.find(s => s.el.contains(it.el)); });
  document.querySelectorAll('[data-sfxat]').forEach(el => el.dataset.sfxat.split(',').forEach(p => { const [n, r] = p.split('@'); SFX.push({ t: T(r), n }); }));
  SFX.sort((a, b) => a.t - b.t); window.SFX = SFX; window.SHOTS = shots.map(s => ({ from: s.from, to: s.to, bg: s.bg }));
  window.DURACAO = TL.duracao;
}

function applyItem(it, t) {
  const el = it.el; let p = (t - it.t0) / it.dur;
  if (p < 0) { el.style.visibility = 'hidden'; return; }
  el.style.visibility = 'visible'; p = Math.min(1, p);
  let tr = '', op = 1, fl = '', clip = '';
  switch (it.fx) {
    case 'word': { const e = eOut(p); op = .4 + .6 * e; if (p < 1) { fl = `blur(${(12 * (1 - e)).toFixed(2)}px)`; tr = `scale(${(.9 + .1 * e).toFixed(4)})`; } break; }
    case 'pop': tr = `scale(${eBack(p).toFixed(4)})`; break;
    case 'stamp': { const s = 2.6 - 1.6 * eIn(p); op = clamp(p * 2.5); const k = (t - it.t0 - it.dur) * FPS; const j = k >= 0 && k < 3 ? [1.06, .98, 1.01][Math.floor(k)] : 1; tr = `scale(${(p < 1 ? s : j).toFixed(4)})`; break; }
    case 'up': tr = `translateY(${((1 - eOut(p)) * it.dist).toFixed(1)}px)`; break;
    case 'down': tr = `translateY(${(-(1 - eOut(p)) * it.dist).toFixed(1)}px)`; break;
    case 'left': tr = `translateX(${(-(1 - eOut(p)) * it.dist).toFixed(1)}px)`; break;
    case 'right': tr = `translateX(${((1 - eOut(p)) * it.dist).toFixed(1)}px)`; break;
    case 'drop': { const e = eBack(p); tr = `translateY(${(-(1 - e) * 260).toFixed(1)}px) rotate(${((1 - e) * -6).toFixed(2)}deg)`; op = clamp(p * 3); break; }
    case 'draw': tr = `scaleX(${eOut(p).toFixed(4)})`; break;
    case 'wipe': clip = `inset(-20% ${((1 - eIO(p)) * 100).toFixed(2)}% -20% -5%)`; break;
    case 'fade': op = p; break;
    case 'flash': op = 1 - p; break;
  }
  if (it.out != null && t >= it.out) {
    const q = clamp((t - it.out) / it.outDur);
    if (q >= 1) { el.style.visibility = 'hidden'; return; }
    tr += ` scaleX(${(1 - eIO(q)).toFixed(4)})`;
  }
  let pose = '';
  if (it.poses) {
    let k = 0; for (let i = 0; i < it.poses.length; i++) if (t >= it.poses[i].t) k = i;
    const P = it.poses[k], nx = it.poses[k + 1], end = nx ? nx.t : (it.shot ? it.shot.to : P.t + 3);
    let x = P.x, y = P.y, s = P.s;
    if (P.tw && k > 0 && t < P.t + P.tw) {        // zoom contínuo entre duas poses, com ponto focal fixo
      const A = it.poses[k - 1], u = eOut((t - P.t) / P.tw); s = A.s * Math.pow(P.s / A.s, u);
      const f = (s - A.s) / (P.s - A.s); x = A.x + (P.x - A.x) * f; y = A.y + (P.y - A.y) * f;
    } else {                                       // deriva lenta: a foto nunca fica parada
      const q = clamp((t - P.t - (P.tw || 0)) / Math.max(.5, end - P.t)), d = .045 * q * Math.min(1, (end - P.t) / 2.5);
      x -= it.w * s * d * .5; y -= it.h * s * d * .35; s *= 1 + d;
    }
    pose = `translate(${x.toFixed(2)}px,${y.toFixed(2)}px) scale(${s.toFixed(5)})`;
  }
  el.style.transform = `${tr} ${pose} ${it.base || ''}`.trim() || 'none';
  el.style.opacity = op; el.style.filter = fl || 'none'; if (it.fx === 'wipe') el.style.clipPath = clip;
}

const hooks = [];
function seek(t) {
  const frame = Math.round(t * FPS); let top = null;
  for (const s of shots) {
    const vis = t >= s.from && t < s.to; s.el.style.display = vis ? 'block' : 'none'; if (!vis) continue;
    if (!top) top = s;
    let tr = '', fl = 'none';
    if (s.exit) {
      const d = s.exit === 'push' ? .3 : s.exit === 'burst' ? .2 : .17, p = clamp((t - (s.to - d)) / d);
      if (p > 0) {
        if (s.exit === 'burst') { tr = `scale(${(1 + eIn(p) * 7).toFixed(4)})`; fl = `blur(${(p * 14).toFixed(1)}px)`; }
        if (s.exit === 'whipL') { tr = `translateX(${(-eIn(p) * 1250).toFixed(1)}px)`; fl = 'url(#hblur)'; }
        if (s.exit === 'push') tr = `translateX(${(eIO(p) * 1080).toFixed(1)}px)`;
      }
    }
    if (s.enter === 'whipR') { const p = clamp((t - s.from) / .2); if (p < 1) { tr = `translateX(${((1 - eOut(p)) * 1250).toFixed(1)}px)`; fl = 'url(#hblur)'; } }
    s.el.style.transform = tr || 'none'; s.el.style.filter = fl;
  }
  for (const it of items) if (!it.shot || it.shot.el.style.display !== 'none') applyItem(it, t);
  // texturas por cima de tudo, com "boil" a cada 4 quadros
  const st = document.getElementById('stage'), k = Math.floor(frame / 4) % 6, bg = top ? top.bg : 'cream';
  st.dataset.bg = bg;
  document.getElementById('gr').style.backgroundImage = document.getElementById('gr2').style.backgroundImage = `url(tex/grain${k}.png)`;
  const sp = document.getElementById('sp'); sp.style.webkitMaskImage = `url(tex/specks${k}.png)`;
  const ht = document.getElementById('ht'), hv = top ? top.ht : 'A';
  ht.style.display = hv === 'none' ? 'none' : 'block'; ht.style.webkitMaskImage = `url(tex/halftone${hv[0]}.png)`;
  const hp = clamp((t - .15) / .9);   // retícula surge nos cantos na abertura
  ht.style.webkitMaskSize = '100% 100%'; ht.style.clipPath = hp < 1 ? `circle(${(60 + 115 * (1 - eOut(hp))).toFixed(1)}% at 50% 50%)` : 'none';
  ht.style.opacity = hp < 1 ? eOut(hp) : 1; ht.style.transform = `translate(${[0, 1, -1, 0, 1, -1][k]}px,${[0, -1, 0, 1, 1, 0][k]}px)`;
  document.getElementById('lab-il').style.display = top && top.lab.includes('il') ? 'block' : 'none';
  document.getElementById('lab-secom').style.display = top && top.lab.includes('secom') ? 'block' : 'none';
  for (const h of hooks) h(t, frame);
}
// onda de áudio pulsando
hooks.push((t) => document.querySelectorAll('.bars b').forEach((b, i) => {
  const a = .25 + .75 * Math.abs(Math.sin(i * 1.7 + Math.floor(t * 15) * 0.9) * Math.sin(i * .35 + 1)); b.style.transform = `scaleY(${a.toFixed(3)})`;
}));
// mão que entra pela lateral e empurra a cena 6 para fora
hooks.push((t) => {
  const el = document.getElementById('pushhand'), t0 = T('c7a-0.36'), p = (t - t0) / .3;
  if (p < -.2 || p > 1.9) { el.style.display = 'none'; return; }
  el.style.display = 'block'; const edge = p <= 1 ? eIO(clamp(p)) * 1080 - (p < 0 ? (-p) * 900 : 0) : 1080 + (p - 1) * 1500;
  el.style.transform = `translate(${(edge - 560).toFixed(1)}px,830px)`;
});
window.seek = seek; window.T = T;
window.ready = document.fonts.ready.then(() => { init(); seek(0); return true; });
