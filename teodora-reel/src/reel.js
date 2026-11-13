/* Teodora · Reel de terror em colagem vintage animada.
 * Tudo é função do tempo t (segundos): renderFrame(t) desenha um quadro determinístico.
 * Tempos das falas/cenas: timings.json. Imagens: assets.json (gerado por tools/process_assets.py).
 */
"use strict";
const W = 1080, H = 1920;
const SAFE = { x0: 80, x1: 900, yMax: 1440 };          // texto fica dentro disto (25% inferiores e coluna direita livres)
const PAL = {
  paper: "#e9dfc8", ink: "#1b1712", gold: "#d8b25a", white: "#f7f2e6",
  night: "#1d2a44", sepia: "#7a5a36",
  confetti: ["#b8473b", "#d9b148", "#5d8a58", "#c9643f", "#e8dcc0", "#4f7896"],
  petal: ["#5a3a2e", "#6e4a36", "#3f2a22", "#7a5b45"], ash: ["#8d8a85", "#b3b0aa", "#5f5c58"],
};

let T = null;            // timings
const IMG = {};          // imagens carregadas
let SCN = null;          // mapa de cenas
const c = document.getElementById("c");
const ctx = c.getContext("2d");

/* ---------- utilidades ---------- */
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (t, t0, d) => clamp((t - t0) / d);
const DEG = Math.PI / 180;
const E = {
  lin: k => k,
  outCubic: k => 1 - Math.pow(1 - k, 3),
  inCubic: k => k * k * k,
  inOutCubic: k => (k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
  inOutSine: k => -(Math.cos(Math.PI * k) - 1) / 2,
  outBack: k => { const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); },
  outQuint: k => 1 - Math.pow(1 - k, 5),
};
function hash(n) { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
function noise1(x, seed = 0) { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i + seed * 57.3), hash(i + 1 + seed * 57.3), u); }
function mkCanvas(w, h) { const k = document.createElement("canvas"); k.width = w; k.height = h; return k; }

/* ---------- carregamento ---------- */
async function loadAll() {
  T = await (await fetch("timings.json?" + Date.now())).json();
  let manifest = {};
  try { manifest = await (await fetch("assets.json?" + Date.now())).json(); } catch (e) { console.warn("sem assets.json"); }
  const jobs = Object.entries(manifest).filter(([k]) => !k.startsWith("_")).map(([k, src]) => new Promise(res => {
    const im = new Image(); im.onload = () => { IMG[k] = im; res(); }; im.onerror = () => { console.warn("faltou", k); res(); };
    im.src = "../" + src;
  }));
  await Promise.all(jobs);
  await document.fonts.load('64px "Playfair"'); await document.fonts.load('italic 64px "Playfair"');
  await document.fonts.load('900 64px "Playfair"'); await document.fonts.load('italic 40px "Garamond"'); await document.fonts.load('40px "Garamond"');
  buildCaches();
}

/* ---------- caches procedurais ---------- */
const CACHE = {};
function buildCaches() {
  // grão de filme
  CACHE.grain = [];
  for (let g = 0; g < 6; g++) {
    const k = mkCanvas(540, 960), x = k.getContext("2d"), d = x.createImageData(540, 960);
    for (let i = 0; i < d.data.length; i += 4) { const v = 128 + (Math.random() - .5) * 200; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
    x.putImageData(d, 0, 0); CACHE.grain.push(k);
  }
  // vinheta
  const v = mkCanvas(W, H), vx = v.getContext("2d");
  const rg = vx.createRadialGradient(W / 2, H * .45, H * .25, W / 2, H * .5, H * .78);
  rg.addColorStop(0, "rgba(0,0,0,0)"); rg.addColorStop(1, "rgba(10,6,2,.78)");
  vx.fillStyle = rg; vx.fillRect(0, 0, W, H); CACHE.vignette = v;
  // névoa
  const f = mkCanvas(512, 256), fx = f.getContext("2d");
  const fg = fx.createRadialGradient(256, 128, 10, 256, 128, 250);
  fg.addColorStop(0, "rgba(235,235,240,.55)"); fg.addColorStop(1, "rgba(235,235,240,0)");
  fx.setTransform(1, 0, 0, .5, 0, 64); fx.fillStyle = fg; fx.fillRect(0, 0, 512, 512); CACHE.fog = f;
  // papel de fundo (textura procedural se não houver foto)
  CACHE.paper = IMG.paper || proceduralPaper();
  // buffers de composição
  CACHE.bufA = mkCanvas(W, H); CACHE.bufB = mkCanvas(W, H); CACHE.bufC = mkCanvas(W, H);
  CACHE.snap = {};
}
function proceduralPaper() {
  const k = mkCanvas(540, 960), x = k.getContext("2d");
  x.fillStyle = "#d9cfb8"; x.fillRect(0, 0, 540, 960);
  const d = x.getImageData(0, 0, 540, 960);
  for (let i = 0; i < d.data.length; i += 4) { const p = i / 4, xx = p % 540, yy = (p / 540) | 0; const n = (noise1(xx * .02, yy * .013) - .5) * 30 + (Math.random() - .5) * 18; d.data[i] += n; d.data[i + 1] += n; d.data[i + 2] += n * .9; }
  x.putImageData(d, 0, 0); return k;
}

/* ---------- primitivas de colagem ---------- */
function placeholder(g, w, h, label) {
  g.fillStyle = "rgba(90,80,70,.85)"; g.fillRect(-w / 2, -h / 2, w, h);
  g.strokeStyle = "#e9dfc8"; g.lineWidth = 4; g.strokeRect(-w / 2 + 6, -h / 2 + 6, w - 12, h - 12);
  g.fillStyle = "#e9dfc8"; g.font = '28px "Garamond"'; g.textAlign = "center"; g.fillText(label, 0, 10);
}
/** Desenha um recorte com entrada "colada": mode grow | left | right | top | bottom | none.
 *  o = {x,y,w|h,rot,t0,d,mode,sway,swayF,phase,flip,alpha,shadow,scale,out} ; lt = tempo local da cena */
function piece(g, key, lt, o) {
  const t0 = o.t0 || 0, d = o.d || .5;
  if (lt < t0) return;
  const im = IMG[key];
  const ar = im ? im.width / im.height : (o.ar || 1);
  const w = o.w || o.h * ar, h = o.h || o.w / ar;
  const k = prog(lt, t0, d);
  let s = (o.scale || 1), dx = 0, dy = 0, rot = (o.rot || 0), a = o.alpha == null ? 1 : o.alpha;
  const mode = o.mode || "grow";
  if (mode === "grow") { const e = E.outBack(k); s *= lerp(.35, 1, e); rot += (1 - e) * -10; a *= clamp(k * 3); }
  else if (mode !== "none") {
    const e = E.outCubic(k), dist = o.dist || 1300;
    const v = { left: [-1, 0], right: [1, 0], top: [0, -1], bottom: [0, 1] }[mode];
    dx = v[0] * dist * (1 - e); dy = v[1] * dist * (1 - e); rot += (1 - e) * (v[0] || v[1]) * 7;
    s *= 1 + .04 * Math.sin(k * Math.PI);          // leve "pressionar" ao colar
  }
  if (o.out) { const ko = E.inCubic(prog(lt, o.out.t0, o.out.d || .4)); a *= 1 - ko; s *= 1 - .3 * ko; }
  if (a <= 0.003) return;
  const sw = o.sway ? Math.sin((lt + (o.phase || 0)) * (o.swayF || 1.3) * Math.PI * 2) * o.sway : 0;
  g.save();
  g.translate(o.x + dx, o.y + dy);
  g.rotate((rot + sw) * DEG);
  g.scale(s * (o.flip || 1), s);
  if (o.pivotY) g.translate(0, -h * o.pivotY);
  g.globalAlpha *= a;
  if (o.shadow !== false) { g.shadowColor = "rgba(8,5,2,.55)"; g.shadowBlur = o.shadowBlur || 22; g.shadowOffsetX = 6; g.shadowOffsetY = 12; }
  if (im) g.drawImage(im, -w / 2, -h / 2, w, h); else placeholder(g, w, h, key);
  g.restore();
}
/** recorte retangular de foto com borda de papel rasgada (deckle) */
function photoCard(g, key, lt, o) {
  const t0 = o.t0 || 0; if (lt < t0) return;
  const im = IMG[key]; const ar = im ? im.width / im.height : (o.ar || 1.4);
  const w = o.w, h = o.h || o.w / ar;
  const k = E.outBack(prog(lt, t0, o.d || .55));
  const mode = o.mode || "grow";
  g.save();
  let dx = 0, dy = 0, s = o.scale || 1;
  if (mode === "grow") s *= lerp(.4, 1, k); else if (mode !== "none") {
    const v = { left: [-1, 0], right: [1, 0], top: [0, -1], bottom: [0, 1] }[mode]; const e = E.outCubic(prog(lt, t0, o.d || .55));
    dx = v[0] * 1300 * (1 - e); dy = v[1] * 1300 * (1 - e);
  }
  const sw = o.sway ? Math.sin((lt + (o.phase || 0)) * (o.swayF || .8) * Math.PI * 2) * o.sway : 0;
  g.translate(o.x + dx, o.y + dy); g.rotate(((o.rot || 0) + sw + (1 - k) * -6) * DEG); g.scale(s, s);
  g.globalAlpha *= clamp(prog(lt, t0, .15)) * (o.alpha == null ? 1 : o.alpha);
  const seed = o.seed || 3, b = o.border == null ? 18 : o.border;
  // papel
  g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 24; g.shadowOffsetY = 12;
  deckle(g, w + b * 2, h + b * 2, seed); g.fillStyle = o.paper || "#efe7d4"; g.fill();
  g.shadowColor = "transparent";
  // foto
  g.save(); deckle(g, w, h, seed + 9, 5); g.clip();
  const zoom = o.zoom || 1, pan = o.pan || [0, 0];
  if (im) {
    // cover-fit
    const ir = im.width / im.height; let dw = w, dh = h; if (ir > w / h) dw = h * ir; else dh = w / ir;
    dw *= zoom; dh *= zoom;
    g.filter = o.filter || "none";
    g.drawImage(im, -dw / 2 + pan[0], -dh / 2 + pan[1], dw, dh); g.filter = "none";
  } else placeholder(g, w, h, key);
  if (o.tint) { g.globalCompositeOperation = "multiply"; g.fillStyle = o.tint; g.fillRect(-w / 2, -h / 2, w, h); g.globalCompositeOperation = "source-over"; }
  g.restore();
  g.restore();
}
function deckle(g, w, h, seed, amp = 9) {
  g.beginPath();
  const step = 14, pts = [];
  for (let x = -w / 2; x <= w / 2; x += step) pts.push([x, -h / 2 + (hash(seed + x) - .5) * amp]);
  for (let y = -h / 2; y <= h / 2; y += step) pts.push([w / 2 + (hash(seed * 2 + y) - .5) * amp, y]);
  for (let x = w / 2; x >= -w / 2; x -= step) pts.push([x, h / 2 + (hash(seed * 3 + x) - .5) * amp]);
  for (let y = h / 2; y >= -h / 2; y -= step) pts.push([-w / 2 + (hash(seed * 4 + y) - .5) * amp, y]);
  pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath();
}

/* ---------- fundos ---------- */
function bg(g, tone, lt, opt = {}) {
  g.save();
  const p = CACHE.paper; const z = 1.04 + .02 * Math.sin(lt * .4);
  g.drawImage(p, -W * (z - 1) / 2, -H * (z - 1) / 2, W * z, H * z);
  const tones = {
    sepia: ["#b4875a", .62], warm: ["#c08a52", .55], night: ["#22345a", .86], deepnight: ["#121b33", .9],
    gray: ["#6f6f6f", .55], day: ["#9a9a96", .45], board: ["#cdbf9f", .35],
  };
  const [col, al] = tones[tone] || tones.sepia;
  g.globalCompositeOperation = "multiply"; g.globalAlpha = al; g.fillStyle = col; g.fillRect(0, 0, W, H);
  g.globalCompositeOperation = "source-over"; g.globalAlpha = 1;
  if (opt.glow) { // halo
    const rg = g.createRadialGradient(opt.glow[0], opt.glow[1], 20, opt.glow[0], opt.glow[1], opt.glow[2] || 700);
    rg.addColorStop(0, opt.glowCol || "rgba(255,230,180,.45)"); rg.addColorStop(1, "rgba(0,0,0,0)");
    g.globalCompositeOperation = "screen"; g.fillStyle = rg; g.fillRect(0, 0, W, H); g.globalCompositeOperation = "source-over";
  }
  g.restore();
}
function fog(g, lt, y, alpha = .5, n = 6, seed = 1) {
  g.save(); g.globalAlpha = alpha;
  for (let i = 0; i < n; i++) {
    const sp = 18 + hash(seed + i) * 30, x = ((hash(seed * 3 + i) * (W + 900) + lt * sp * (i % 2 ? 1 : -1)) % (W + 900) + (W + 900)) % (W + 900) - 450;
    const s = 1.4 + hash(i + seed * 7) * 1.4;
    g.drawImage(CACHE.fog, x - 256 * s, y - 128 * s + Math.sin(lt * .5 + i) * 14 + (hash(i * 9 + seed) - .5) * 140, 512 * s, 256 * s);
  }
  g.restore();
}
function rain(g, t, intensity = 1, angle = 12) {
  g.save(); g.strokeStyle = "rgba(220,228,240,.42)"; g.lineWidth = 2;
  const n = Math.floor(170 * intensity), ta = Math.tan(angle * DEG);
  g.beginPath();
  for (let i = 0; i < n; i++) {
    const sp = 1900 + hash(i) * 900, len = 40 + hash(i + 3) * 50;
    const y = ((hash(i * 7) * (H + 200) + t * sp) % (H + 200)) - 100;
    const x = ((hash(i * 13) * (W + 300) - y * ta) % (W + 300) + (W + 300)) % (W + 300) - 150;
    g.moveTo(x, y); g.lineTo(x - len * ta, y - len);
  }
  g.stroke(); g.restore();
}
function stars(g, lt, n = 40, seed = 5) {
  g.save();
  for (let i = 0; i < n; i++) {
    const x = hash(seed + i) * W, y = hash(seed * 2 + i) * 760, r = 2 + hash(i + 11) * 4;
    const tw = .45 + .55 * Math.abs(Math.sin(lt * (1 + hash(i) * 3) + i));
    g.globalAlpha = tw; g.fillStyle = "#f3ead2"; starShape(g, x, y, r * 2.2, r * .6, 4); g.fill();
  }
  g.restore();
}
function starShape(g, x, y, R, r, n) { g.beginPath(); for (let i = 0; i < n * 2; i++) { const a = i * Math.PI / n - Math.PI / 2, rr = i % 2 ? r : R; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); }

/* ---------- objetos procedurais ---------- */
function mirrorBall(g, x, y, r, lt, swing = 1, alpha = 1) {
  g.save(); g.globalAlpha *= alpha;
  const ang = Math.sin(lt * 1.3) * 5 * swing * DEG;
  g.translate(x, y); g.rotate(ang);
  // fio
  g.strokeStyle = "#1b1712"; g.lineWidth = 4; g.beginPath(); g.moveTo(0, -r); g.lineTo(0, -y - 40); g.stroke();
  g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 30; g.shadowOffsetY = 14;
  g.beginPath(); g.arc(0, 0, r, 0, Math.PI * 2); g.fillStyle = "#6c6a66"; g.fill(); g.shadowColor = "transparent";
  g.save(); g.clip();
  const rows = 14, rot = lt * .9;
  for (let i = 0; i < rows; i++) {
    const la0 = -Math.PI / 2 + i * Math.PI / rows, la1 = la0 + Math.PI / rows;
    const y0 = Math.sin(la0) * r, y1 = Math.sin(la1) * r, rr = Math.cos((la0 + la1) / 2) * r;
    const cols = Math.max(4, Math.round(26 * Math.cos((la0 + la1) / 2)));
    for (let j = 0; j < cols; j++) {
      const lo0 = rot + j * 2 * Math.PI / cols, lo1 = lo0 + 2 * Math.PI / cols * .9;
      if (Math.cos((lo0 + lo1) / 2) < 0) continue;
      const x0 = Math.sin(lo0) * rr, x1 = Math.sin(lo1) * rr;
      const b = 90 + 120 * hash(i * 40 + j) * (.5 + .5 * Math.sin(lt * 3 + i + j)) + 40 * Math.cos((lo0 + lo1) / 2);
      g.fillStyle = `rgb(${b},${b},${b * .97})`; g.fillRect(Math.min(x0, x1), y0 + 1, Math.abs(x1 - x0) - 1.5, y1 - y0 - 2);
    }
  }
  const sh = g.createRadialGradient(-r * .4, -r * .4, r * .1, 0, 0, r * 1.05);
  sh.addColorStop(0, "rgba(255,255,255,.25)"); sh.addColorStop(1, "rgba(0,0,0,.55)");
  g.fillStyle = sh; g.fillRect(-r, -r, 2 * r, 2 * r);
  g.restore();
  // brilhos
  for (let i = 0; i < 6; i++) {
    const a = hash(i * 3) * Math.PI * 2, rr = r * (.3 + .6 * hash(i * 5));
    const tw = Math.max(0, Math.sin(lt * 4 + i * 2.1)); if (tw < .2) continue;
    g.fillStyle = `rgba(255,250,235,${tw})`; starShape(g, Math.cos(a) * rr, Math.sin(a) * rr, 26 * tw, 3, 4); g.fill();
  }
  g.restore();
}
function lightSpots(g, cx, cy, lt, n = 10, alpha = .16) {
  g.save(); g.globalCompositeOperation = "screen";
  for (let i = 0; i < n; i++) {
    const a = lt * .6 + i * 2 * Math.PI / n, d = 300 + 260 * hash(i);
    const x = cx + Math.cos(a) * d, y = cy + Math.sin(a) * d * .9 + 300;
    const rg = g.createRadialGradient(x, y, 0, x, y, 46);
    rg.addColorStop(0, `rgba(255,245,215,${alpha * 3})`); rg.addColorStop(1, "rgba(255,245,215,0)");
    g.fillStyle = rg; g.fillRect(x - 50, y - 50, 100, 100);
  }
  g.restore();
}
function serpentine(g, x0, y0, len, lt, col, seed, amp = 40, width = 11) {
  g.save(); g.strokeStyle = col; g.lineWidth = width; g.lineCap = "round"; g.globalAlpha *= .92;
  g.beginPath();
  for (let s = 0; s <= len; s += 8) {
    const k = s / len;
    const x = x0 + Math.sin(s * .045 + lt * 2.2 + seed) * amp * k + Math.sin(lt * .9 + seed) * 30 * k;
    const y = y0 + s;
    s ? g.lineTo(x, y) : g.moveTo(x, y);
  }
  g.stroke();
  g.strokeStyle = "rgba(0,0,0,.25)"; g.lineWidth = 2; g.stroke();
  g.restore();
}
function garland(g, x0, y0, x1, y1, sag, lt, seed = 1, flags = 14) {
  g.save();
  const pt = k => { const x = lerp(x0, x1, k), y = lerp(y0, y1, k) + Math.sin(k * Math.PI) * (sag + Math.sin(lt * 1.6 + seed) * 10); return [x, y]; };
  g.strokeStyle = "#2a221a"; g.lineWidth = 3; g.beginPath();
  for (let i = 0; i <= 40; i++) { const [x, y] = pt(i / 40); i ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
  for (let i = 1; i < flags; i++) {
    const [x, y] = pt(i / flags); const sw = Math.sin(lt * 3 + i + seed) * 12 * DEG;
    g.save(); g.translate(x, y); g.rotate(sw);
    g.fillStyle = PAL.confetti[(i + seed) % 4]; g.beginPath(); g.moveTo(-20, 0); g.lineTo(20, 0); g.lineTo(0, 44); g.closePath();
    g.shadowColor = "rgba(0,0,0,.35)"; g.shadowBlur = 6; g.shadowOffsetY = 3; g.fill(); g.restore();
  }
  g.restore();
}
function candle(g, x, y, s, lt, seed = 0) {
  g.save(); g.translate(x, y); g.scale(s, s);
  // halo
  const fl = .85 + .15 * noise1(lt * 9, seed) + .08 * Math.sin(lt * 23 + seed);
  const rg = g.createRadialGradient(0, -120, 5, 0, -120, 220 * fl);
  rg.addColorStop(0, "rgba(255,210,130,.55)"); rg.addColorStop(1, "rgba(255,200,120,0)");
  g.globalCompositeOperation = "screen"; g.fillStyle = rg; g.fillRect(-240, -360, 480, 480); g.globalCompositeOperation = "source-over";
  // corpo
  g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 14; g.shadowOffsetY = 8;
  const bg_ = g.createLinearGradient(-26, 0, 26, 0); bg_.addColorStop(0, "#cbbd9d"); bg_.addColorStop(.5, "#f2e9d4"); bg_.addColorStop(1, "#b5a684");
  g.fillStyle = bg_; g.beginPath(); g.moveTo(-26, -90); g.lineTo(26, -90); g.lineTo(26, 60); g.lineTo(-26, 60); g.closePath(); g.fill();
  g.shadowColor = "transparent";
  g.fillStyle = "#efe5cd"; g.beginPath(); g.ellipse(-12, -90, 9, 26, 0, 0, Math.PI); g.fill();
  g.strokeStyle = "#222"; g.lineWidth = 3; g.beginPath(); g.moveTo(0, -90); g.lineTo(0, -104); g.stroke();
  // chama
  const sx = 1 + .12 * Math.sin(lt * 17 + seed), lean = (noise1(lt * 4, seed + 3) - .5) * 10;
  g.save(); g.translate(0, -104); g.scale(sx, fl);
  const fg = g.createRadialGradient(0, -18, 2, 0, -18, 34); fg.addColorStop(0, "#fffbe8"); fg.addColorStop(.45, "#ffd27a"); fg.addColorStop(1, "rgba(255,120,30,0)");
  g.fillStyle = fg; g.beginPath(); g.moveTo(0, 6); g.bezierCurveTo(-16, -6, -12, -30, lean, -58); g.bezierCurveTo(12, -30, 16, -6, 0, 6); g.fill();
  g.restore(); g.restore();
}
function clockFace(g, x, y, r, lt, speed = 1) {
  g.save(); g.translate(x, y);
  g.shadowColor = "rgba(0,0,0,.45)"; g.shadowBlur = 18; g.shadowOffsetY = 8;
  g.fillStyle = "#efe6cf"; g.beginPath(); g.arc(0, 0, r, 0, Math.PI * 2); g.fill(); g.shadowColor = "transparent";
  g.strokeStyle = "#2b2219"; g.lineWidth = 6; g.stroke(); g.lineWidth = 2; g.beginPath(); g.arc(0, 0, r - 12, 0, Math.PI * 2); g.stroke();
  g.fillStyle = "#2b2219"; g.font = `${r * .22}px "Playfair"`; g.textAlign = "center"; g.textBaseline = "middle";
  const rom = ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"];
  rom.forEach((s, i) => { const a = i * Math.PI / 6 - Math.PI / 2; g.fillText(s, Math.cos(a) * r * .72, Math.sin(a) * r * .72); });
  const hA = (lt * speed * .5) * Math.PI * 2 + 9 * Math.PI / 6, mA = lt * speed * 6 * Math.PI * 2;
  g.lineCap = "round"; g.lineWidth = 9; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(hA - Math.PI / 2) * r * .45, Math.sin(hA - Math.PI / 2) * r * .45); g.stroke();
  g.lineWidth = 5; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(mA - Math.PI / 2) * r * .7, Math.sin(mA - Math.PI / 2) * r * .7); g.stroke();
  g.beginPath(); g.arc(0, 0, 8, 0, Math.PI * 2); g.fill();
  g.restore();
}
function rosette(g, x, y, r, lt, label, sub) { // selo/cartaz de carnaval tipográfico
  g.save(); g.translate(x, y); g.rotate((-8 + Math.sin(lt * 1.2) * 3) * DEG);
  g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 20; g.shadowOffsetY = 10;
  starShape(g, 0, 0, r, r * .86, 28); g.fillStyle = "#b8473b"; g.fill(); g.shadowColor = "transparent";
  g.beginPath(); g.arc(0, 0, r * .78, 0, Math.PI * 2); g.fillStyle = "#efe4c8"; g.fill();
  g.strokeStyle = "#b8473b"; g.lineWidth = 4; g.beginPath(); g.arc(0, 0, r * .7, 0, Math.PI * 2); g.stroke();
  g.setLineDash([3, 9]); g.beginPath(); g.arc(0, 0, r * .64, 0, Math.PI * 2); g.stroke(); g.setLineDash([]);
  g.fillStyle = "#1b1712"; g.textAlign = "center"; g.textBaseline = "alphabetic";
  g.font = `italic 900 ${r * .4}px "Playfair"`; g.fillText(label, 0, r * .14);
  g.font = `600 ${r * .095}px "Playfair"`; g.fillText(sub, 0, r * .4);
  g.restore();
}
function headlights(g, x, y, dir, lt, len = 900, alpha = .5) {
  g.save(); g.globalCompositeOperation = "screen";
  const fl = alpha * (.85 + .15 * noise1(lt * 12, 2));
  const lg = g.createLinearGradient(x, y, x + dir * len, y);
  lg.addColorStop(0, `rgba(255,240,190,${fl})`); lg.addColorStop(1, "rgba(255,240,190,0)");
  g.fillStyle = lg; g.beginPath(); g.moveTo(x, y - 12); g.lineTo(x + dir * len, y - 170); g.lineTo(x + dir * len, y + 150); g.lineTo(x, y + 12); g.closePath(); g.fill();
  const rg = g.createRadialGradient(x, y, 0, x, y, 70); rg.addColorStop(0, `rgba(255,250,225,${fl * 1.6})`); rg.addColorStop(1, "rgba(255,250,225,0)");
  g.fillStyle = rg; g.fillRect(x - 80, y - 80, 160, 160);
  g.restore();
}
function lamppost(g, x, y, h, lt) {
  g.save(); g.fillStyle = "#14110d"; g.fillRect(x - 6, y - h, 12, h);
  g.beginPath(); g.moveTo(x - 30, y - h); g.lineTo(x + 30, y - h); g.lineTo(x + 18, y - h - 50); g.lineTo(x - 18, y - h - 50); g.closePath(); g.fill();
  const fl = .8 + .2 * noise1(lt * 7, x);
  const rg = g.createRadialGradient(x, y - h - 20, 4, x, y - h - 20, 260);
  rg.addColorStop(0, `rgba(255,220,150,${.55 * fl})`); rg.addColorStop(1, "rgba(255,220,150,0)");
  g.globalCompositeOperation = "screen"; g.fillStyle = rg; g.fillRect(x - 270, y - h - 290, 540, 540); g.restore();
}
/** lápide procedural com nome gravado (revela letra a letra) */
function tombstone(g, x, y, w, h, lt, opt = {}) {
  g.save(); g.translate(x, y);
  g.shadowColor = "rgba(0,0,0,.6)"; g.shadowBlur = 40; g.shadowOffsetY = 20;
  const path = () => { g.beginPath(); g.moveTo(-w / 2, h / 2); g.lineTo(-w / 2, -h / 2 + w / 2); g.arc(0, -h / 2 + w / 2, w / 2, Math.PI, 0); g.lineTo(w / 2, h / 2); g.closePath(); };
  path(); g.fillStyle = "#8a8780"; g.fill(); g.shadowColor = "transparent";
  g.save(); path(); g.clip();
  if (IMG.stone) g.drawImage(IMG.stone, -w / 2, -h / 2, w, h); else { g.globalAlpha = .55; g.drawImage(CACHE.paper, -w / 2, -h / 2, w, h); g.globalAlpha = 1; }
  g.globalCompositeOperation = "multiply"; g.fillStyle = "#9b9890"; g.fillRect(-w / 2, -h / 2, w, h); g.globalCompositeOperation = "source-over";
  const sh = g.createLinearGradient(-w / 2, 0, w / 2, 0); sh.addColorStop(0, "rgba(255,255,255,.18)"); sh.addColorStop(.5, "rgba(0,0,0,0)"); sh.addColorStop(1, "rgba(0,0,0,.35)");
  g.fillStyle = sh; g.fillRect(-w / 2, -h / 2, w, h);
  // musgo / manchas
  for (let i = 0; i < 26; i++) { g.fillStyle = `rgba(40,45,35,${.05 + .08 * hash(i)})`; g.beginPath(); g.arc((hash(i * 3) - .5) * w, (hash(i * 7) - .5) * h, 8 + 40 * hash(i * 11), 0, 7); g.fill(); }
  g.restore();
  path(); g.strokeStyle = "rgba(30,28,25,.6)"; g.lineWidth = 4; g.stroke();
  // cruz
  engrave(g, () => { g.fillRect(-7, -h / 2 + w * .18, 14, 70); g.fillRect(-26, -h / 2 + w * .18 + 18, 52, 13); });
  // nome
  const name = opt.name || "TEODORA", reveal = opt.reveal == null ? 1 : opt.reveal;
  const n = Math.floor(name.length * reveal + .0001), part = name.length * reveal - n;
  g.font = `600 ${w * .155}px "Playfair"`; g.textAlign = "center"; g.textBaseline = "alphabetic";
  const spacing = w * .02;
  const chars = name.split(""); const widths = chars.map(ch => g.measureText(ch).width + spacing);
  const total = widths.reduce((a, b) => a + b, 0) - spacing;
  let cx = -total / 2; const ny = -h / 2 + w * .62;
  chars.forEach((ch, i) => {
    const vis = i < n ? 1 : i === n ? part : 0;
    if (vis > 0) { g.save(); g.globalAlpha = vis; engrave(g, () => g.fillText(ch, cx + widths[i] / 2 - spacing / 2, ny)); g.restore(); }
    cx += widths[i];
  });
  if (opt.dates) { g.globalAlpha = opt.datesAlpha == null ? 1 : opt.datesAlpha; g.font = `italic 500 ${w * .07}px "Playfair"`; engrave(g, () => g.fillText(opt.dates, 0, ny + w * .13)); g.globalAlpha = 1; }
  if (opt.epitaph) { g.font = `italic 400 ${w * .06}px "Garamond"`; engrave(g, () => g.fillText(opt.epitaph, 0, ny + w * .25)); }
  g.restore();
}
function engrave(g, draw) {
  g.save(); g.fillStyle = "rgba(255,255,255,.35)"; g.translate(2, 2.5); draw(); g.restore();
  g.save(); g.fillStyle = "rgba(25,22,20,.85)"; draw(); g.restore();
}
/** capa de chuva dobrada (procedural, cara de recorte): pilha dobrada + manga caindo pela borda */
function foldedCoat(g, x, y, w, lt, rot = -4) {
  const h = w * .36;
  g.save(); g.translate(x, y); g.rotate(rot * DEG);
  const fabric = (x0, y0, ww, hh, light) => {
    g.beginPath(); g.moveTo(x0 + 14, y0); g.bezierCurveTo(x0 + ww * .3, y0 - 6, x0 + ww * .7, y0 + 5, x0 + ww - 12, y0 + 2);
    g.quadraticCurveTo(x0 + ww + 4, y0 + hh * .5, x0 + ww - 8, y0 + hh); g.bezierCurveTo(x0 + ww * .6, y0 + hh + 6, x0 + ww * .3, y0 + hh - 4, x0 + 10, y0 + hh + 2);
    g.quadraticCurveTo(x0 - 6, y0 + hh * .5, x0 + 14, y0); g.closePath();
    const cg = g.createLinearGradient(0, y0, 0, y0 + hh); cg.addColorStop(0, light); cg.addColorStop(1, "#6f6249"); g.fillStyle = cg; g.fill();
    g.strokeStyle = "rgba(40,32,20,.5)"; g.lineWidth = 2.5; g.stroke();
  };
  g.shadowColor = "rgba(0,0,0,.55)"; g.shadowBlur = 22; g.shadowOffsetY = 10;
  // manga pendurada pela frente do túmulo
  g.fillStyle = "#8a7c5e"; g.beginPath(); g.moveTo(w * .22, h * .3); g.bezierCurveTo(w * .36, h * .5, w * .3, h * 1.3, w * .38, h * 1.9);
  g.lineTo(w * .26, h * 1.95); g.bezierCurveTo(w * .2, h * 1.3, w * .2, h * .7, w * .08, h * .4); g.closePath(); g.fill();
  g.shadowColor = "transparent";
  g.fillStyle = "#5e5340"; g.fillRect(w * .25, h * 1.82, w * .14, h * .12);       // punho
  fabric(-w / 2, -h * .2, w, h * .8, "#a29473");                  // camada de baixo
  g.shadowColor = "rgba(0,0,0,.35)"; g.shadowBlur = 10; g.shadowOffsetY = 5;
  fabric(-w / 2 + 12, -h * .62, w - 24, h * .62, "#bcae8b");      // camada de cima (dobra)
  g.shadowColor = "transparent";
  // gola e lapelas
  g.fillStyle = "#857858"; g.beginPath(); g.moveTo(-w * .2, -h * .6); g.lineTo(0, -h * .18); g.lineTo(w * .2, -h * .6); g.lineTo(w * .1, -h * .62); g.lineTo(0, -h * .38); g.lineTo(-w * .1, -h * .62); g.closePath(); g.fill();
  g.strokeStyle = "rgba(30,25,15,.6)"; g.lineWidth = 2; g.stroke();
  // vincos
  g.strokeStyle = "rgba(50,40,25,.35)"; g.lineWidth = 2;
  for (const xx of [-.32, -.18, .27, .38]) { g.beginPath(); g.moveTo(w * xx, -h * .55); g.quadraticCurveTo(w * xx + 10, -h * .3, w * xx - 4, -h * .05); g.stroke(); }
  // cinto com fivela atravessando
  g.fillStyle = "#7d7052"; g.beginPath(); g.moveTo(-w / 2 + 4, h * .18); g.lineTo(w / 2 - 6, h * .12); g.lineTo(w / 2 - 6, h * .28); g.lineTo(-w / 2 + 4, h * .34); g.closePath(); g.fill();
  g.strokeStyle = "#3b3326"; g.lineWidth = 4; g.strokeRect(-w * .07, h * .12, w * .1, h * .2);
  for (const bx of [-w * .3, w * .3]) { g.fillStyle = "#2a241b"; g.beginPath(); g.arc(bx, -h * .36, w * .02, 0, 7); g.fill(); }
  g.restore();
}
/** livro de registros aberto (procedural) */
const NAMES = ["Benedicta Maria da Silva", "Joaquim Pereira Leite", "Anna Rosa de Campos", "Manoel Antônio Corrêa", "Rita de Cássia Ourives", "Francisco de Paula Mello", "Teodora ··· ", "Maria Thereza Duarte", "João Baptista Paes", "Escolástica Ribeiro", "Antônio Ferreira Mendes", "Luiza de Arruda"];
function ledger(g, x, y, w, lt, opt = {}) {
  const h = w * .66;
  g.save(); g.translate(x, y); g.rotate((opt.rot || -2) * DEG);
  g.shadowColor = "rgba(0,0,0,.6)"; g.shadowBlur = 40; g.shadowOffsetY = 20;
  g.fillStyle = "#3b2a1e"; g.fillRect(-w / 2 - 18, -h / 2 - 16, w + 36, h + 32); g.shadowColor = "transparent";
  for (const side of [-1, 1]) {
    g.save();
    g.beginPath(); g.rect(side < 0 ? -w / 2 : 0, -h / 2, w / 2, h); g.clip();
    g.drawImage(CACHE.paper, side < 0 ? -w / 2 : 0, -h / 2, w / 2, h);
    g.globalCompositeOperation = "multiply"; g.fillStyle = "#d6c9a8"; g.fillRect(-w / 2, -h / 2, w, h); g.globalCompositeOperation = "source-over";
    const gut = g.createLinearGradient(0, 0, side * w * .12, 0); gut.addColorStop(0, "rgba(0,0,0,.4)"); gut.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = gut; g.fillRect(side < 0 ? -w * .12 : 0, -h / 2, w * .12, h);
    // pautas
    g.strokeStyle = "rgba(90,60,40,.35)"; g.lineWidth = 1.5;
    const x0 = side < 0 ? -w / 2 + 30 : 30, x1 = side < 0 ? -30 : w / 2 - 30;
    for (let i = 0; i < 13; i++) { const yy = -h / 2 + 70 + i * (h - 100) / 13; g.beginPath(); g.moveTo(x0, yy); g.lineTo(x1, yy); g.stroke(); }
    g.strokeStyle = "rgba(140,40,30,.35)"; g.beginPath(); g.moveTo(x0 + 60, -h / 2 + 40); g.lineTo(x0 + 60, h / 2 - 20); g.stroke();
    // título
    g.fillStyle = "rgba(40,28,18,.85)"; g.font = `italic 600 ${w * .03}px "Garamond"`; g.textAlign = "left";
    g.fillText(side < 0 ? "Registro de Sepultamentos" : "Cemitério da Piedade", x0, -h / 2 + 48);
    // entradas manuscritas
    g.font = `italic 500 ${w * .026}px "Garamond"`;
    const list = side < 0 ? NAMES.slice(0, 6) : NAMES.slice(6, 12);
    list.forEach((nm, i) => {
      const yy = -h / 2 + 64 + (i + 1) * (h - 100) / 13 * 1.9;
      const isT = nm.startsWith("Teodora");
      const yr = isT ? "1941" : String(1938 + ((i * 7 + (side > 0 ? 3 : 0)) % 5));
      g.fillStyle = isT ? "rgba(20,12,8,.95)" : "rgba(45,30,20,.78)";
      g.fillText(`${(side < 0 ? 210 : 216) + i}`, x0 + 6, yy);
      g.fillText(isT ? "Teodora" : nm, x0 + 72, yy);
      g.fillText(yr, x1 - 70, yy);
      if (isT && opt.highlight) { // círculo de tinta
        const k = E.inOutCubic(clamp(opt.highlight));
        g.strokeStyle = "rgba(120,20,15,.85)"; g.lineWidth = 4; g.beginPath();
        g.ellipse(x0 + 150, yy - 10, 130, 36, -.03, -1.6, -1.6 + k * 6.6); g.stroke();
      }
    });
    g.restore();
  }
  // página virando
  if (opt.flip != null && opt.flip > 0 && opt.flip < 1) {
    const k = E.inOutCubic(opt.flip), sx = Math.cos(k * Math.PI);
    g.save(); g.scale(1, 1);
    g.beginPath(); g.rect(0, -h / 2, (w / 2) * sx, h);
    g.fillStyle = sx > 0 ? "#e2d6b8" : "#d3c6a6"; g.fill();
    const pg = g.createLinearGradient(0, 0, (w / 2) * sx, 0); pg.addColorStop(0, "rgba(0,0,0,.35)"); pg.addColorStop(1, "rgba(255,255,255,.1)");
    g.fillStyle = pg; g.fill(); g.restore();
  }
  g.restore();
}

/* ---------- partículas globais: confete → pétalas/cinzas ---------- */
function particles(g, t) {
  const drain = clamp((t - T.colorDrainStart) / (T.colorDrainEnd - T.colorDrainStart));
  const baile = t < 12.6 ? 1 : t < 26.4 ? .45 : .7;
  const N = Math.floor(95 * baile);
  const fast = t > 12.6 && t < 26.4 ? 2.2 : 1;      // com chuva, cai mais rápido
  for (let i = 0; i < N; i++) {
    const sp = (90 + hash(i * 3.1) * 140) * (drain > 0 ? lerp(1, .45, drain) : fast);
    const x0 = hash(i * 7.7) * W;
    const yy = ((hash(i * 1.3) * (H + 120) + t * sp) % (H + 120)) - 60;
    const xx = x0 + Math.sin(t * (1 + hash(i)) + i) * 40;
    const rot = t * (2 + hash(i * 2) * 5) + i;
    const isAsh = i % 3 === 0;
    g.save(); g.translate(xx, yy); g.rotate(rot);
    const flip = Math.cos(t * (3 + hash(i) * 4) + i);
    if (drain < 1) {
      g.globalAlpha = 1 - drain;
      g.scale(1, flip); g.fillStyle = PAL.confetti[i % PAL.confetti.length];
      if (i % 4 === 0) { g.beginPath(); g.arc(0, 0, 9, 0, 7); g.fill(); } else g.fillRect(-11, -6, 22, 12);
    }
    if (drain > 0) {
      g.globalAlpha = drain;
      if (isAsh) { g.fillStyle = PAL.ash[i % 3]; g.beginPath(); g.moveTo(-5, -3); g.lineTo(6, -1); g.lineTo(3, 5); g.lineTo(-4, 3); g.closePath(); g.fill(); }
      else { g.scale(1, Math.abs(flip) * .8 + .2); g.fillStyle = PAL.petal[i % 4]; g.beginPath(); g.ellipse(0, 0, 15, 8, 0, 0, 7); g.fill(); g.strokeStyle = "rgba(0,0,0,.35)"; g.lineWidth = 1.5; g.beginPath(); g.moveTo(-12, 0); g.lineTo(12, 0); g.stroke(); }
    }
    g.restore();
  }
}

/* ---------- CENAS ---------- */
// cada cena: (g, lt, dur, t) — lt = tempo local
SCN = {
  gancho(g, lt) {
    bg(g, "night", lt, { glow: [760, 330, 600], glowCol: "rgba(240,220,160,.35)" });
    stars(g, lt);
    // lua = confete gigante
    if (lt > .1) {
      const k = E.outBack(prog(lt, .1, .7));
      g.save(); g.translate(760, 330); g.rotate(lt * .15); g.scale(k, k);
      g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 30; g.beginPath(); g.arc(0, 0, 205, 0, 7); g.fillStyle = "#d9b148"; g.fill(); g.shadowColor = "transparent";
      g.restore();
      piece(g, "moon", lt, { x: 760, y: 330, w: 370, t0: .1, d: .7, shadow: false, sway: 2, swayF: .2 });
    }
    // fachada (foto real do Cemitério da Piedade)
    photoCard(g, "facade", lt, { x: 540, y: 1130, w: 1060, rot: -1.5, t0: 0, d: .7, mode: "bottom", tint: "#7f93bd", filter: "brightness(.8) contrast(1.15)", zoom: 1.25, pan: [0, 40], seed: 41, sway: .4, swayF: .3 });
    fog(g, lt, 1300, .55, 7, 2);
    // globo de baile gigante
    if (lt > .35) { const k = E.outCubic(prog(lt, .35, .8)); mirrorBall(g, 380, lerp(-200, 360, k), 150, lt, 1); }
    if (lt > .9) for (let i = 0; i < 4; i++) serpentine(g, 330 + i * 34, 500, 260 + i * 60, lt, PAL.confetti[i], i * 2, 30);
    lightSpots(g, 380, 360, lt, 12, .14);
    // túmulo + Teodora dançando em cima
    if (lt > .6) { const k = E.outBack(prog(lt, .6, .5)); g.save(); g.translate(600, 1010); g.scale(k, k); tombBox(g, 0, 0, 380, 190); g.restore(); }
    if (lt > 1.0) {
      const spin = Math.cos(lt * 1.7); const sx = Math.sign(spin) * Math.max(.55, Math.abs(spin));
      piece(g, "teodora_full", lt, { x: 600, y: 700, h: 470, t0: 1.0, d: .55, flip: sx, sway: 5, swayF: .9 });
    }
    piece(g, "cat", lt, { x: 175, y: 1060, h: 250, t0: 1.6, d: .5, sway: 2 });
  },
  clube(g, lt) {
    bg(g, "sepia", lt, { glow: [540, 600, 800] });
    photoCard(g, "cuiaba_old", lt, { x: 520, y: 470, w: 960, rot: -3, t0: 0, mode: "left", zoom: 1.05 + lt * .02, seed: 11 });
    photoCard(g, "cuiaba_rosario", lt, { x: 600, y: 930, w: 760, rot: 4, t0: .35, mode: "bottom", zoom: 1.1 + lt * .02, seed: 13, sway: .5, swayF: .4 });
    garland(g, -20, 640, 1100, 600, 110, lt, 1);
    garland(g, -20, 760, 1100, 800, 80, lt, 3, 16);
    // faixa CLUBE FEMININO
    if (lt > .7) {
      const k = E.outBack(prog(lt, .7, .5));
      g.save(); g.translate(540, 700); g.rotate((-2 + Math.sin(lt * 1.5) * 1.2) * DEG); g.scale(k, k);
      g.shadowColor = "rgba(0,0,0,.45)"; g.shadowBlur = 16; g.shadowOffsetY = 8;
      g.fillStyle = "#efe4c8"; g.beginPath(); g.moveTo(-330, -48); g.lineTo(330, -48); g.lineTo(300, 0); g.lineTo(330, 48); g.lineTo(-330, 48); g.lineTo(-300, 0); g.closePath(); g.fill();
      g.shadowColor = "transparent"; g.fillStyle = "#1b1712"; g.font = '700 54px "Playfair"'; g.textAlign = "center"; g.textBaseline = "middle";
      g.fillText("CLUBE  FEMININO", 0, 3); g.restore();
    }
    piece(g, "couple1", lt, { x: 250, y: 1110, h: 420, t0: 1.0, d: .5, mode: "left", sway: 4, swayF: 1.1 });
    if (lt > .1) { const k = E.outBack(prog(lt, .1, .6)); g.save(); g.translate(790, 250); g.scale(k, k); rosette(g, 0, 0, 165, lt, "Anos 40", "BAILE DE CARNAVAL"); g.restore(); }
    for (let i = 0; i < 3; i++) serpentine(g, 880 + i * 30, -10, 520 + i * 70, lt, PAL.confetti[i + 1], i * 3, 26);
  },
  danca(g, lt) {
    bg(g, "warm", lt, { glow: [540, 760, 700], glowCol: "rgba(255,225,170,.5)" });
    photoCard(g, "ballroom", lt, { x: 540, y: 380, w: 980, rot: 2, t0: 0, mode: "top", filter: "grayscale(1) sepia(.45) contrast(1.15)", zoom: 1.08 + lt * .025, seed: 21 });
    mirrorBall(g, 540, 120, 90, lt, 1);
    lightSpots(g, 540, 300, lt, 12, .18);
    // casais girando como bonecos de caixinha de música
    const couples = [["couple1", 210, 1000, 330], ["couple2", 880, 990, 330]];
    couples.forEach(([k, x, y, h], i) => piece(g, k, lt, { x: x + Math.sin(lt * 1.6 + i) * 30, y, h, t0: .25 + i * .15, d: .5, flip: Math.cos(lt * 1.8 + i * 2) > 0 ? 1 : -1, sway: 6, swayF: .8, phase: i }));
    // o casal principal
    if (lt > .45) {
      const spin = Math.cos(lt * 1.6); const sx = Math.sign(spin) * Math.max(.6, Math.abs(spin));
      g.save(); g.translate(540, 0);
      piece(g, "rapaz", lt, { x: -70 * sx, y: 900, h: 560, t0: .45, d: .5, flip: sx });
      piece(g, "teodora_full", lt, { x: 80 * sx, y: 925, h: 520, t0: .55, d: .5, flip: -sx });
      g.restore();
    }
    if (lt > .9) { const k = E.outBack(prog(lt, .9, .5)); g.save(); g.translate(165, 230); g.scale(k, k); clockFace(g, 0, 0, 120, lt, 1.1); g.restore(); }
  },
  nome(g, lt) {
    bg(g, "sepia", lt, { glow: [540, 640, 600], glowCol: "rgba(255,230,190,.45)" });
    // moldura oval dourada com retrato
    const k = E.outBack(prog(lt, 0, .6));
    g.save(); g.translate(540, 620); g.scale(k, k); g.rotate(Math.sin(lt * 1.1) * 1.5 * DEG);
    g.shadowColor = "rgba(0,0,0,.55)"; g.shadowBlur = 40; g.shadowOffsetY = 18;
    g.beginPath(); g.ellipse(0, 0, 330, 430, 0, 0, 7); const fr = g.createLinearGradient(-330, -430, 330, 430); fr.addColorStop(0, "#e8cf86"); fr.addColorStop(.5, "#9c7a35"); fr.addColorStop(1, "#e2c271"); g.fillStyle = fr; g.fill();
    g.shadowColor = "transparent";
    for (let i = 0; i < 48; i++) { const a = i / 48 * Math.PI * 2; g.fillStyle = i % 2 ? "#f3e2a6" : "#7c5e25"; g.beginPath(); g.arc(Math.cos(a) * 312, Math.sin(a) * 410, 9, 0, 7); g.fill(); }
    g.beginPath(); g.ellipse(0, 0, 285, 382, 0, 0, 7); g.fillStyle = "#2b241c"; g.fill(); g.clip();
    if (IMG.teodora_face) { const im = IMG.teodora_face, hh = 820, ww = hh * im.width / im.height; g.filter = "grayscale(1) sepia(.35) contrast(1.1)"; g.drawImage(im, -ww / 2, -hh / 2 + 30 - lt * 10, ww * (1 + lt * .02), hh * (1 + lt * .02)); g.filter = "none"; }
    else placeholder(g, 560, 760, "teodora_face");
    g.restore();
    piece(g, "mask", lt, { x: 790, y: 960, w: 380, t0: .6, d: .5, rot: 14, sway: 5, swayF: .7 });
    // cartão de dança com o nome
    if (lt > .8) {
      const k2 = E.outBack(prog(lt, .8, .5));
      g.save(); g.translate(560, 1060); g.rotate((-6 + Math.sin(lt * 2) * 1.5) * DEG); g.scale(k2, k2);
      g.shadowColor = "rgba(0,0,0,.45)"; g.shadowBlur = 16; g.shadowOffsetY = 8;
      g.fillStyle = "#f1e8d2"; g.fillRect(-170, -60, 340, 120); g.shadowColor = "transparent";
      g.strokeStyle = "#b8473b"; g.lineWidth = 3; g.strokeRect(-160, -50, 320, 100);
      g.fillStyle = "#1b1712"; g.font = 'italic 600 26px "Garamond"'; g.textAlign = "center"; g.fillText("carnet de baile", 0, -16);
      g.font = 'italic 700 46px "Garamond"'; g.fillText("Teodora", 0, 32);
      g.restore();
    }
  },
  chuva(g, lt, dur, t) {
    bg(g, "night", lt);
    photoCard(g, "ballroom", lt, { x: 540, y: 600, w: 1000, rot: -2, t0: 0, mode: "none", filter: "contrast(1.1) brightness(.7)", tint: "#6f86b5", zoom: 1.2 + lt * .03, seed: 21 });
    mirrorBall(g, 540, 300, 120, lt, 2.5);
    darkClouds(g, lt, E.outCubic(prog(lt, 0, .7)));
    // casal correndo da chuva
    if (lt > .3) {
      const run = E.inOutSine(prog(lt, .3, 1.7));
      piece(g, "rapaz_capa", lt, { x: lerp(330, 450, run), y: 1000 - Math.abs(Math.sin(lt * 9)) * 10, h: 560, t0: .3, d: .4 });
      piece(g, "teodora_full", lt, { x: lerp(560, 680, run), y: 1010 - Math.abs(Math.sin(lt * 9 + 1)) * 10, h: 520, t0: .35, d: .4 });
    }
    rain(g, t, 1);
    const fl = Math.max(0, 1 - Math.abs(lt - .18) * 10) + Math.max(0, .6 - Math.abs(lt - .42) * 12);
    if (fl > 0) { g.fillStyle = `rgba(235,240,255,${fl * .75})`; g.fillRect(0, 0, W, H); }
  },
  taxi(g, lt, dur, t) {
    bg(g, "deepnight", lt);
    const rg = g.createLinearGradient(0, 1000, 0, 1500); rg.addColorStop(0, "rgba(20,25,40,0)"); rg.addColorStop(1, "rgba(10,12,20,.75)"); g.fillStyle = rg; g.fillRect(0, 1000, W, 500);
    lamppost(g, 120, 1080, 720, lt); lamppost(g, 980, 1060, 640, lt + 2);
    const k = E.outCubic(prog(lt, 0, 1.0));
    const tx = lerp(-600, 600, k);
    if (IMG.taxi) { g.save(); g.globalAlpha = .22; g.translate(tx, 1250); g.scale(1, -.4); g.filter = "blur(5px)"; const im = IMG.taxi, w = 860, h = w * im.height / im.width; g.drawImage(im, -w / 2, -h / 2 - 60, w, h); g.filter = "none"; g.restore(); }
    piece(g, "taxi", lt, { x: tx, y: 1010 + Math.sin(lt * 14) * 2 * (1 - k), w: 860, t0: 0, d: .01, mode: "none", shadowBlur: 30 });
    headlights(g, tx + 400, 1060, 1, lt, 600, .55);
    if (lt > .2) { g.save(); g.translate(tx + 10, 800); g.fillStyle = "#e9c75c"; g.shadowColor = "rgba(255,220,120,.9)"; g.shadowBlur = 30; g.fillRect(-70, -24, 140, 48); g.shadowColor = "transparent"; g.fillStyle = "#1b1712"; g.font = '800 34px "Playfair"'; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("TÁXI", 0, 2); g.restore(); }
    // ele empresta a capa: a capa (mesma da lápide) cai sobre os ombros dela
    piece(g, "rapaz", lt, { x: 210, y: 820, h: 640, t0: .5, d: .5, mode: "left" });
    piece(g, "teodora_full", lt, { x: 420, y: 840, h: 600, t0: .6, d: .5, mode: "left" });
    if (lt > 1.2) { const kc = E.outBack(prog(lt, 1.2, .6)); drapedCoat(g, 425, lerp(520, 820, kc), 300, lt, clamp(kc * 2)); }
    rain(g, t, 1.1);
  },
  pedido(g, lt, dur, t) {
    bg(g, "night", lt);
    if (lt < 2.3) {
      const a = 1 - prog(lt, 1.9, .4);
      g.save(); g.globalAlpha = a;
      inkMap(g, lt);
      const route = [[200, 980], [200, 760], [470, 760], [470, 520], [720, 520], [720, 330], [860, 330]];
      const L = route.slice(1).reduce((acc, p, i) => acc + Math.hypot(p[0] - route[i][0], p[1] - route[i][1]), 0);
      const rk = E.inOutSine(prog(lt, .3, 1.5));
      g.strokeStyle = "#b8473b"; g.lineWidth = 9; g.setLineDash([22, 14]); g.lineCap = "round"; g.beginPath();
      let acc = 0, pos = route[0], ang = 0; g.moveTo(route[0][0], route[0][1]);
      for (let i = 1; i < route.length; i++) {
        const p0 = route[i - 1], p1 = route[i], sl = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
        ang = Math.atan2(p1[1] - p0[1], p1[0] - p0[0]);
        if (acc + sl <= rk * L) { g.lineTo(p1[0], p1[1]); pos = p1; } else { const f = (rk * L - acc) / sl; pos = [lerp(p0[0], p1[0], f), lerp(p0[1], p1[1], f)]; g.lineTo(pos[0], pos[1]); break; }
        acc += sl;
      }
      g.stroke(); g.setLineDash([]);
      // cruz do cemitério no mapa
      g.fillStyle = "#1b1712"; g.fillRect(851, 230, 18, 90); g.fillRect(826, 254, 68, 16);
      g.font = 'italic 700 40px "Playfair"'; g.textAlign = "center"; g.fillText("Piedade", 860, 372);
      piece(g, "taxi", lt, { x: pos[0], y: pos[1] - 26, w: 210, t0: .15, d: .3, shadowBlur: 10, flip: Math.cos(ang) < -.1 ? -1 : 1 });
      g.restore();
    }
    if (lt > 1.8) {
      photoCard(g, "facade", lt, { x: 540, y: 640, w: 1040, rot: 1.5, t0: 1.8, d: .7, mode: "grow", tint: "#7f93bd", filter: "brightness(.75) contrast(1.2)", zoom: 1.3, pan: [0, 20], seed: 43 });
      fog(g, lt, 980, .6, 7, 4);
      piece(g, "teodora_back", lt, { x: 540, y: 960, h: 470, t0: 2.4, d: .5, sway: 1.5, swayF: .5 });
      if (lt > 2.4) drapedCoat(g, 540, 935, 220, lt, prog(lt, 2.5, .4) * .9);
    }
    rain(g, t, .7);
  },
  portao(g, lt, dur, t) {
    bg(g, "deepnight", lt);
    const Gd = gateGeom();
    const open = E.inOutCubic(prog(lt, .2, 1.3));
    const D = Gd.door;
    // interior além do portão: túmulos, anjo, velas, névoa
    g.save(); g.beginPath(); g.rect(D.x, D.y, D.w, D.h); g.clip();
    const ig = g.createLinearGradient(0, D.y, 0, D.y + D.h); ig.addColorStop(0, "#05070d"); ig.addColorStop(1, "#1a2236");
    g.fillStyle = ig; g.fillRect(D.x, D.y, D.w, D.h);
    piece(g, "angel", lt, { x: D.x + D.w * .5, y: D.y + D.h * .42, h: D.h * .72, t0: 0, d: .01, mode: "none", alpha: .8, shadow: false });
    piece(g, "cross", lt, { x: D.x + D.w * .14, y: D.y + D.h * .68, h: D.h * .55, t0: 0, d: .01, mode: "none", alpha: .55, shadow: false });
    piece(g, "cross", lt, { x: D.x + D.w * .88, y: D.y + D.h * .74, h: D.h * .42, t0: 0, d: .01, mode: "none", alpha: .45, flip: -1, shadow: false });
    candle(g, D.x + D.w * .28, D.y + D.h * .97, .55, lt, 1); candle(g, D.x + D.w * .74, D.y + D.h * .98, .45, lt, 2);
    fog(g, lt, D.y + D.h * .85, .75, 6, 9);
    const walk = prog(lt, .9, 1.25);
    if (walk < 1) piece(g, "teodora_back", lt, { x: D.x + D.w * lerp(.5, .55, walk), y: D.y + D.h * lerp(.72, .58, walk), h: D.h * lerp(.75, .32, walk), t0: 0, d: .01, mode: "none", alpha: 1 - walk * walk });
    g.restore();
    // fachada real com o vão recortado
    if (IMG.gate_bg) {
      g.save(); g.beginPath(); g.rect(0, 0, W, H); g.rect(D.x + D.w, D.y, -D.w, D.h); g.clip("evenodd");
      g.filter = "brightness(.62) contrast(1.15)"; g.drawImage(IMG.gate_bg, Gd.x, Gd.y, Gd.w, Gd.h); g.filter = "none";
      g.globalCompositeOperation = "multiply"; g.fillStyle = "#6b7fae"; g.fillRect(Gd.x, Gd.y, Gd.w, Gd.h); g.globalCompositeOperation = "source-over";
      g.restore();
      gateLeaf(g, Gd, -1, open, lt); gateLeaf(g, Gd, 1, open, lt);
    } else placeholder(g, 900, 1200, "gate_bg");
    // luz da lua lavando a fachada
    const mg = g.createRadialGradient(820, 150, 20, 820, 150, 900); mg.addColorStop(0, "rgba(200,215,255,.22)"); mg.addColorStop(1, "rgba(0,0,0,0)");
    g.save(); g.globalCompositeOperation = "screen"; g.fillStyle = mg; g.fillRect(0, 0, W, H); g.restore();
    fog(g, lt, 1300, .5, 7, 5);
    // lascas de papel voando no rasgo
    for (let i = 0; i < 14; i++) { const k = prog(lt, .25 + hash(i) * .5, 1.1); if (k <= 0 || k >= 1) continue; const s = hash(i * 3) > .5 ? 1 : -1; g.save(); g.globalAlpha = 1 - k; g.translate(D.x + D.w / 2 + s * k * (200 + hash(i * 7) * 300), D.y + D.h * (.15 + .7 * hash(i * 5)) + k * k * 300); g.rotate(k * 8 + i); g.fillStyle = "#efe6d0"; g.fillRect(-10, -4, 20 + hash(i) * 14, 8); g.restore(); }
  },
  fuga(g, lt, dur, t) {
    bg(g, "deepnight", lt);
    const shake = (1 - prog(lt, 0, 2)) * 10;
    g.save(); g.translate((noise1(lt * 30) - .5) * shake, (noise1(lt * 30, 4) - .5) * shake);
    lamppost(g, 980 - (lt * 700) % 1400, 1080, 700, lt);
    const k = E.inCubic(prog(lt, .1, 2.1));
    const tx = lerp(520, 1750, k);
    if (IMG.taxi) for (let i = 4; i >= 1; i--) { g.save(); g.globalAlpha = .13 * k; const im = IMG.taxi, w = 860, h = w * im.height / im.width; g.drawImage(im, tx - i * 70 * k - w / 2, 1010 - h / 2, w, h); g.restore(); }
    piece(g, "taxi", lt, { x: tx, y: 1010 + Math.sin(lt * 30) * 3, w: 860, t0: 0, d: .01, mode: "none", rot: -1.5 * k });
    headlights(g, tx + 400, 1060, 1, lt, 600, .6);
    for (let i = 0; i < 7; i++) { const a = prog(lt, .15 + i * .14, 1); if (a <= 0 || a >= 1) continue; g.globalAlpha = (1 - a) * .5; g.drawImage(CACHE.fog, tx - 470 - a * 260 - 100, 1030 - a * 70, 260 + a * 220, 130 + a * 110); }
    g.globalAlpha = 1;
    g.restore();
    piece(g, "owl", lt, { x: 200, y: 430, h: 330, t0: .5, d: .5, sway: 3 });
    rain(g, t, 1.2, 20);
  },
  silencio(g, lt, dur, t) {
    bg(g, "deepnight", lt);
    const z = 1 + lt * .05;
    g.save(); g.translate(540, 900); g.scale(z, z); g.translate(-540, -900);
    photoCard(g, "facade", lt, { x: 540, y: 700, w: 1040, rot: 1.5, t0: 0, d: .01, mode: "none", tint: "#7f93bd", filter: "brightness(.6) contrast(1.2)", zoom: 1.3, pan: [0, 20], seed: 43 });
    fog(g, lt, 1000, .75, 8, 6);
    piece(g, "mask", lt, { x: 540, y: 1110, w: 330, t0: .15, d: .7, rot: -10, mode: "grow" });
    g.restore();
    mirrorBall(g, 540, 200, 100, lt * .2, .15, .85);
  },
  registros(g, lt) {
    bg(g, "day", lt, { glow: [800, 200, 900], glowCol: "rgba(255,255,255,.25)" });
    // feixes de janela
    g.save(); g.globalCompositeOperation = "screen"; g.globalAlpha = .12 + .04 * Math.sin(lt * 1.3);
    for (let i = 0; i < 3; i++) { g.fillStyle = "#fff"; g.beginPath(); g.moveTo(700 + i * 110, -50); g.lineTo(780 + i * 110, -50); g.lineTo(380 + i * 150, 1300); g.lineTo(260 + i * 150, 1300); g.closePath(); g.fill(); }
    g.restore();
    piece(g, "rapaz_jornal", lt, { x: 840, y: 520, h: 700, t0: .1, d: .5, mode: "right", alpha: .95 });
    const k = E.outCubic(prog(lt, 0, .6));
    ledger(g, 520, lerp(1500, 880, k), 900, lt, { flip: prog(lt, .8, 1.1) });
    candle(g, 120, 470, .9, lt, 3);
  },
  morta(g, lt) {
    bg(g, "gray", lt);
    const z = 1.55 + lt * .06;
    g.save(); g.translate(540, 700); g.scale(z, z); g.translate(-480 + 0, -620);
    ledger(g, 520, 800, 900, lt, { rot: -2, highlight: prog(lt, .6, .9) });
    g.restore();
    // retrato de porcelana de túmulo
    if (lt > .3) {
      const k = E.outBack(prog(lt, .3, .5));
      g.save(); g.translate(770, 300); g.scale(k, k); g.rotate((6 + Math.sin(lt) * 1.5) * DEG);
      g.shadowColor = "rgba(0,0,0,.6)"; g.shadowBlur = 24; g.shadowOffsetY = 10;
      g.beginPath(); g.ellipse(0, 0, 150, 195, 0, 0, 7); g.fillStyle = "#b9b4a8"; g.fill(); g.shadowColor = "transparent";
      g.beginPath(); g.ellipse(0, 0, 132, 176, 0, 0, 7); g.clip();
      if (IMG.teodora_face) { const im = IMG.teodora_face, hh = 400, ww = hh * im.width / im.height; g.filter = "grayscale(1) contrast(1.2) brightness(.95)"; g.drawImage(im, -ww / 2, -hh / 2 + 20, ww, hh); g.filter = "none"; }
      // rachadura
      g.strokeStyle = "rgba(20,20,20,.8)"; g.lineWidth = 2.5; g.beginPath(); g.moveTo(-60, -180); g.lineTo(-20, -60); g.lineTo(-40, 10); g.lineTo(10, 90); g.lineTo(0, 190); g.stroke();
      g.restore();
    }
    // carimbo
    if (lt > 1.2) {
      const k = prog(lt, 1.2, .18), s = lerp(2.2, 1, E.outCubic(k));
      g.save(); g.translate(330, 1010); g.rotate(-12 * DEG); g.scale(s, s); g.globalAlpha = clamp(k * 2) * .85;
      g.strokeStyle = "#2a2522"; g.lineWidth = 7; g.strokeRect(-230, -60, 460, 120);
      g.fillStyle = "#2a2522"; g.font = '900 72px "Playfair"'; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("FALECIDA", 0, 4);
      g.restore();
    }
  },
  tumulo(g, lt, dur) {
    bg(g, "deepnight", lt);
    const z = 1 + E.inOutSine(prog(lt, 0, dur)) * .38;   // zoom lento
    g.save(); g.translate(540, 760); g.scale(z, z); g.translate(-540, -760);
    piece(g, "angel", lt, { x: 180, y: 640, h: 760, t0: 0, d: .5, mode: "left", alpha: .85 });
    piece(g, "cross", lt, { x: 900, y: 700, h: 560, t0: .1, d: .5, mode: "right", alpha: .8 });
    piece(g, "owl", lt, { x: 905, y: 395, h: 210, t0: .5, d: .5, sway: 2 });
    fog(g, lt, 1000, .55, 7, 7);
    tombstone(g, 540, 690, 450, 620, lt, { reveal: prog(lt, 2.0, 1.4), dates: "✝ 1941", datesAlpha: prog(lt, 3.3, .5) });
    tombBox(g, 540, 1060, 660, 180);
    foldedCoat(g, 540, 975, 400, lt, -4);
    candle(g, 210, 1000, .75, lt, 4); candle(g, 880, 1010, .65, lt, 5);
    piece(g, "cat", lt, { x: 880, y: 1080, h: 200, t0: 1.0, d: .5, flip: -1 });
    fog(g, lt, 1200, .6, 7, 8);
    g.restore();
  },
  prancha(g, lt, dur, t) {
    bg(g, "board", lt);
    // grade de prancha
    g.save(); g.strokeStyle = "rgba(60,45,30,.18)"; g.lineWidth = 1.5; for (let x = 60; x < W; x += 60) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); } for (let y = 60; y < H; y += 60) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); } g.restore();
    const P = T.prancha;
    // título espaçado
    g.save(); g.fillStyle = "#1b1712"; g.textAlign = "center";
    g.globalAlpha = prog(lt, 0, .5);
    g.font = '700 62px "Playfair"'; letterSpaced(g, P.titulo, 490, 170, 16);
    g.font = 'italic 400 40px "Playfair"'; letterSpaced(g, P.subtitulo, 490, 232, 4);
    g.fillRect(310, 262, 360, 2);
    g.restore();
    // lápide central com a capa
    g.save(); g.translate(490, 700); const s = E.outBack(prog(lt, .1, .6)); g.scale(s * .78, s * .78); g.translate(-540, -760);
    candle(g, 300, 1100, .7, lt, 6); candle(g, 780, 1110, .6, lt, 7);
    tombstone(g, 540, 690, 450, 620, lt, { reveal: 1, dates: "✝ 1941" });
    tombBox(g, 540, 1060, 660, 180);
    foldedCoat(g, 540, 975, 400, lt, -4);
    g.restore();
    // polaroids caindo
    const pol = [["gancho", 1.6, 160, 470, -14], ["danca", 1.1, 830, 430, 11], ["taxi", .8, 150, 980, 9], ["portao", 1.7, 840, 960, -8], ["registros", 2.0, 500, 1110, 4]];
    pol.forEach(([id, at, x, y, rot], i) => polaroid(g, id, at, lt, x, y, rot, .35 + i * .22));
    // frase final
    g.save(); g.textAlign = "center";
    revealLine(g, P.fraseItalico, t, P.fraseItalicoAt, 1.6, 490, 1300, 'italic 400 39px "Playfair"', "#1b1712");
    revealLine(g, P.fraseCaixaAlta, t, P.fraseCaixaAltaAt, .8, 490, 1385, '900 66px "Playfair"', "#1b1712", "#7a1d14");
    g.restore();
  },
};
function letterSpaced(g, s, x, y, sp) { const ws = [...s].map(ch => g.measureText(ch).width); const tot = ws.reduce((a, b) => a + b, 0) + sp * (s.length - 1); let cx = x - tot / 2; g.textAlign = "left"; [...s].forEach((ch, i) => { g.fillText(ch, cx, y); cx += ws[i] + sp; }); g.textAlign = "center"; }
function revealLine(g, text, t, at, dur, x, y, font, col, col2) {
  if (t < at) return;
  g.font = font; const words = text.split(" ");
  const widths = words.map(w => g.measureText(w + " ").width); const tot = widths.reduce((a, b) => a + b, 0);
  let cx = x - tot / 2;
  words.forEach((w, i) => {
    const wt = at + dur * i / words.length, k = E.outCubic(prog(t, wt, .3));
    if (k > 0) { g.save(); g.globalAlpha = k; g.fillStyle = col2 && k > .99 ? col2 : col; g.textAlign = "left"; g.fillText(w, cx, y + (1 - k) * 18); g.restore(); }
    cx += widths[i];
  });
}
function polaroid(g, sceneId, at, lt, x, y, rot, t0) {
  if (lt < t0) return;
  const k = E.outCubic(prog(lt, t0, .7));
  const snap = sceneSnap(sceneId, at);
  g.save(); g.translate(x + (1 - k) * (x < 540 ? -200 : 200), lerp(-300, y, k)); g.rotate((rot + (1 - k) * rot * 3 + Math.sin(lt * 1.3 + x) * 1.2) * DEG);
  const w = 230, h = 270;
  g.shadowColor = "rgba(0,0,0,.45)"; g.shadowBlur = 20; g.shadowOffsetY = 10;
  g.fillStyle = "#f4efe3"; g.fillRect(-w / 2, -h / 2, w, h); g.shadowColor = "transparent";
  g.filter = "grayscale(1) contrast(1.1)"; g.drawImage(snap, 0, 160, snap.width, snap.width, -w / 2 + 14, -h / 2 + 14, w - 28, w - 28); g.filter = "none";
  // fita adesiva
  g.fillStyle = "rgba(230,220,190,.75)"; g.save(); g.rotate(-8 * DEG); g.fillRect(-45, -h / 2 - 14, 90, 30); g.restore();
  g.restore();
}
function sceneSnap(id, at) {
  if (CACHE.snap[id]) return CACHE.snap[id];
  const k = mkCanvas(432, 768), x = k.getContext("2d"); x.scale(.4, .4);
  const line = T.lines.find(l => l.scene === id); SCN[id](x, at, line ? line.end - line.start : 3, (line ? line.start : 0) + at);
  CACHE.snap[id] = k; return k;
}
/* geometria do portão (foto real gate_bg; vão da porta em px da foto, ver assets.json → _gate) */
let GATE = { w: 1140, h: 1290, door: [290, 665, 725, 1290], leafW: 215 };
function gateGeom() {
  const s = 1180 / GATE.w, w = GATE.w * s, h = GATE.h * s, x = 540 - w / 2, y = 90;
  const d = GATE.door;
  return { s, x, y, w, h, door: { x: x + d[0] * s, y: y + d[1] * s, w: (d[2] - d[0]) * s, h: (d[3] - d[1]) * s } };
}
function gateLeaf(g, Gd, side, open, lt) {
  const im = IMG.gate_leaf; if (!im) return;
  const D = Gd.door, half = D.w / 2;
  const hingeX = side < 0 ? D.x : D.x + D.w;
  const sc = Math.cos(open * 1.38);               // giro em perspectiva
  const dir = side < 0 ? 1 : -1;                  // para onde fica a junção
  g.save(); g.translate(hingeX, D.y); g.scale(sc, 1 + .03 * open);
  const seam = y => dir * (half + (open > .001 ? (hash(Math.floor(y / 9) * .37 + side) - .5) * 30 + Math.sin(y * .02 + side) * 10 : 0));
  g.beginPath(); g.moveTo(0, 0);
  for (let y = 0; y <= D.h; y += 9) g.lineTo(seam(y), y);
  g.lineTo(0, D.h); g.closePath();
  g.save(); g.clip();
  g.filter = `brightness(${.62 - open * .3}) contrast(1.15)`;
  if (side < 0) g.drawImage(im, 0, 0, half + 20, D.h);
  else { g.scale(-1, 1); g.drawImage(im, 0, 0, half + 20, D.h); }
  g.filter = "none";
  g.globalCompositeOperation = "multiply"; g.fillStyle = "#6b7fae"; g.fillRect(-half - 30, 0, 2 * half + 60, D.h); g.globalCompositeOperation = "source-over";
  g.restore();
  if (open > .001) { // fibra branca do papel rasgado
    g.strokeStyle = "rgba(240,232,214,.95)"; g.lineWidth = 7; g.beginPath();
    for (let y = 0; y <= D.h; y += 9) { const xx = seam(y) - dir * 3; y ? g.lineTo(xx, y) : g.moveTo(xx, y); }
    g.stroke();
  }
  g.restore();
}
function tombBox(g, x, y, w, h) { // túmulo (jazigo) procedural
  g.save(); g.translate(x, y);
  g.shadowColor = "rgba(0,0,0,.6)"; g.shadowBlur = 30; g.shadowOffsetY = 14;
  g.fillStyle = "#9a978f"; g.fillRect(-w / 2, -h / 2, w, h); g.shadowColor = "transparent";
  g.save(); g.beginPath(); g.rect(-w / 2, -h / 2, w, h); g.clip(); g.globalAlpha = .5; g.drawImage(CACHE.paper, -w / 2, -h / 2, w, h * 3); g.restore();
  g.globalCompositeOperation = "multiply"; g.fillStyle = "#8f8c86"; g.fillRect(-w / 2, -h / 2, w, h); g.globalCompositeOperation = "source-over";
  g.fillStyle = "#b9b6ae"; g.fillRect(-w / 2 - 16, -h / 2 - 22, w + 32, 26);
  g.fillStyle = "rgba(0,0,0,.25)"; g.fillRect(-w / 2 - 16, -h / 2 + 2, w + 32, 6);
  g.strokeStyle = "rgba(30,28,25,.55)"; g.lineWidth = 3; g.strokeRect(-w / 2 + 24, -h / 2 + 30, w - 48, h - 54);
  engrave(g, () => { g.fillRect(-6, -h / 2 + 46, 12, 70); g.fillRect(-24, -h / 2 + 64, 48, 11); });
  g.restore();
}
function darkClouds(g, lt, k) {
  g.save(); g.globalAlpha = k;
  for (let i = 0; i < 9; i++) {
    const x = (i / 8) * (W + 300) - 150 + Math.sin(lt * .4 + i) * 40, y = lerp(-200, 120 + hash(i) * 160, k);
    const s = 2.2 + hash(i * 3) * 1.5;
    g.filter = "brightness(.25) contrast(1.4)"; g.drawImage(CACHE.fog, x - 256 * s, y - 128 * s, 512 * s, 256 * s);
  }
  g.filter = "none"; g.restore();
}
function inkMap(g, lt) { // mapa de ruas desenhado a nanquim
  g.save(); g.translate(540, 640); g.rotate(-2 * DEG);
  g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 24; g.shadowOffsetY = 12;
  deckle(g, 960, 900, 77); g.fillStyle = "#d8ccae"; g.fill(); g.shadowColor = "transparent";
  g.save(); deckle(g, 960, 900, 77); g.clip(); g.globalAlpha = .6; g.drawImage(CACHE.paper, -480, -450, 960, 900); g.globalAlpha = 1;
  g.strokeStyle = "rgba(40,30,20,.75)"; g.lineWidth = 3;
  for (let i = -4; i <= 4; i++) { g.beginPath(); g.moveTo(-500, i * 110 + Math.sin(i) * 20); g.lineTo(500, i * 104 - 30 + Math.cos(i) * 18); g.stroke(); }
  for (let i = -4; i <= 4; i++) { g.beginPath(); g.moveTo(i * 120 + 10 * Math.sin(i * 2), -480); g.lineTo(i * 112 + 30, 480); g.stroke(); }
  g.lineWidth = 9; g.strokeStyle = "rgba(60,80,110,.55)"; g.beginPath(); g.moveTo(-500, 380); g.bezierCurveTo(-200, 300, 100, 470, 500, 360); g.stroke();
  g.fillStyle = "rgba(40,30,20,.85)"; g.font = 'italic 500 26px "Garamond"'; g.textAlign = "left";
  g.fillText("R. Barão de Melgaço", -440, 150); g.fillText("Clube Feminino", -440, 335); g.fillText("rio Cuiabá", 120, 440);
  g.font = 'italic 600 34px "Playfair"'; g.fillText("Cuyabá", 230, -390);
  g.restore(); g.restore();
}
/** capa de chuva caindo sobre os ombros (mesma cor da capa dobrada da lápide) */
function drapedCoat(g, x, y, h, lt, a = 1) {
  if (a <= 0) return;
  const w = h * .5;
  g.save(); g.translate(x, y); g.rotate(Math.sin(lt * 2) * 1.5 * DEG); g.globalAlpha *= a;
  g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 18; g.shadowOffsetY = 8;
  g.beginPath(); g.moveTo(-w * .22, -h * .5); g.lineTo(w * .22, -h * .5);
  g.quadraticCurveTo(w * .5, -h * .42, w * .52, -h * .2); g.lineTo(w * .6, h * .5); g.lineTo(-w * .6, h * .5); g.lineTo(-w * .52, -h * .2);
  g.quadraticCurveTo(-w * .5, -h * .42, -w * .22, -h * .5); g.closePath();
  const cg = g.createLinearGradient(-w / 2, 0, w / 2, 0); cg.addColorStop(0, "#8e8062"); cg.addColorStop(.5, "#b4a582"); cg.addColorStop(1, "#7a6d52");
  g.fillStyle = cg; g.fill(); g.shadowColor = "transparent";
  g.save(); g.clip();
  g.strokeStyle = "rgba(40,32,20,.45)"; g.lineWidth = 3;
  for (let i = -2; i <= 2; i++) { g.beginPath(); g.moveTo(i * w * .14, -h * .3); g.quadraticCurveTo(i * w * .2 + 8, h * .1, i * w * .26, h * .5); g.stroke(); }
  g.fillStyle = "#857858"; g.fillRect(-w, h * .02, 2 * w, h * .06);
  g.fillStyle = "#6f6449"; g.beginPath(); g.moveTo(-w * .24, -h * .5); g.lineTo(0, -h * .3); g.lineTo(w * .24, -h * .5); g.lineTo(w * .3, -h * .38); g.lineTo(0, -h * .2); g.lineTo(-w * .3, -h * .38); g.closePath(); g.fill();
  g.restore(); g.restore();
}
/* ---------- transição de papel rasgado ---------- */
function tornClipPath(g, k, angle, seed) {
  // região que AINDA mostra a cena antiga
  g.save(); g.translate(W / 2, H / 2); g.rotate(angle);
  const R = 1300, edge = lerp(R, -R, k);
  g.beginPath(); g.moveTo(-R, -R);
  for (let y = -R; y <= R; y += 12) g.lineTo(edge + tornOffset(y, seed), y);
  g.lineTo(-R, R); g.closePath();
  g.restore();
}
function tornOffset(y, seed) { return Math.sin(y * .006 + seed) * 40 + Math.sin(y * .021 + seed * 2) * 16 + (hash(Math.floor(y / 12) + seed * 100) - .5) * 22; }
function tornStrip(g, k, angle, seed) {
  g.save(); g.translate(W / 2, H / 2); g.rotate(angle);
  const R = 1300, edge = lerp(R, -R, k);
  g.beginPath();
  for (let y = -R; y <= R; y += 12) g.lineTo(edge + tornOffset(y, seed), y);
  for (let y = R; y >= -R; y -= 12) g.lineTo(edge + tornOffset(y, seed) + 10 + hash(y * .1 + seed) * 18, y);
  g.closePath();
  g.shadowColor = "rgba(0,0,0,.55)"; g.shadowBlur = 26; g.shadowOffsetX = 12;
  g.fillStyle = "#efe6d0"; g.fill();
  g.restore();
}

/* ---------- texto da narração ---------- */
function parseLine(text) {
  const out = []; let gold = false;
  text.split(" ").forEach(raw => {
    let w = raw; let start = false, end = false;
    if (w.startsWith("*")) { gold = true; start = true; w = w.slice(1); }
    let isGold = gold;
    const m = w.match(/^(.*?)\*([^*]*)$/);
    if (m) { w = m[1] + m[2]; end = true; }
    out.push({ w, gold: isGold, trail: m ? m[2] : "" });
    if (end) gold = false;
  });
  return out;
}
function drawCaption(g, t) {
  const line = T.lines.find(l => t >= l.start && t < l.end);
  if (!line || !line.text) return;
  const words = parseLine(line.text);
  const fs = 64, lh = fs * 1.22, maxW = SAFE.x1 - SAFE.x0;
  const fontN = `500 ${fs}px "Playfair"`, fontG = `italic 600 ${fs + 4}px "Playfair"`;
  // medir e quebrar
  const meas = words.map(o => { g.font = o.gold ? fontG : fontN; return g.measureText(o.w).width; });
  g.font = fontN; const sp = g.measureText(" ").width;
  const rows = [[]]; let rw = 0;
  words.forEach((o, i) => { const add = (rows[rows.length - 1].length ? sp : 0) + meas[i]; if (rw + add > maxW && rows[rows.length - 1].length) { rows.push([]); rw = 0; } rows[rows.length - 1].push(i); rw += (rows[rows.length - 1].length > 1 ? sp : 0) + meas[i]; });
  // tempos das palavras
  const dur = line.end - line.start;
  let times = line.wordsAt;
  if (!times) {
    const wts = words.map(o => o.w.length + 3), tot = wts.reduce((a, b) => a + b, 0), span = Math.min(dur * .8, dur - .35);
    let acc = 0; times = wts.map(x => { const v = line.start + .05 + span * acc / tot; acc += x; return v; });
  }
  const fadeOut = 1 - prog(t, line.end - .18, .18);
  const yBottom = SAFE.yMax - 40;
  const y0 = yBottom - (rows.length - 1) * lh;
  const cx = (SAFE.x0 + SAFE.x1) / 2;
  // faixa escura suave para leitura
  g.save();
  const bandTop = y0 - fs - 90, bandBot = yBottom + 150;
  const bgr = g.createLinearGradient(0, bandTop, 0, bandBot); bgr.addColorStop(0, "rgba(8,6,4,0)"); bgr.addColorStop(.3, "rgba(8,6,4,.5)"); bgr.addColorStop(.7, "rgba(8,6,4,.5)"); bgr.addColorStop(1, "rgba(8,6,4,0)");
  g.globalAlpha = fadeOut * clamp((t - line.start) * 4); g.fillStyle = bgr; g.fillRect(0, bandTop, W, bandBot - bandTop);
  g.restore();
  rows.forEach((row, ri) => {
    const rowW = row.reduce((a, i, j) => a + meas[i] + (j ? sp : 0), 0);
    let x = cx - rowW / 2; const y = y0 + ri * lh;
    row.forEach(i => {
      const o = words[i], k = E.outCubic(prog(t, times[i], .32));
      if (k > 0) {
        g.save(); g.globalAlpha = k * fadeOut;
        g.font = o.gold ? fontG : fontN; g.textAlign = "left"; g.textBaseline = "alphabetic";
        g.shadowColor = "rgba(0,0,0,.9)"; g.shadowBlur = 16; g.shadowOffsetY = 3;
        if (o.gold) { const gr = g.createLinearGradient(0, y - fs, 0, y + 8); gr.addColorStop(0, "#f3dc94"); gr.addColorStop(.6, "#d2a849"); gr.addColorStop(1, "#a97e2c"); g.fillStyle = gr; }
        else g.fillStyle = PAL.white;
        g.fillText(o.w, x, y + (1 - k) * 16);
        g.restore();
      }
      x += meas[i] + sp;
    });
  });
}

/* ---------- composição do quadro ---------- */
function renderScene(buf, line, t) {
  const g = buf.getContext("2d"); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.filter = "none";
  g.clearRect(0, 0, W, H);
  SCN[line.scene](g, t - line.start, line.end - line.start, t);
}
function renderFrame(t) {
  const L = T.lines; let idx = L.findIndex(l => t >= l.start && t < l.end); if (idx < 0) idx = L.length - 1;
  const line = L[idx];
  const C = CACHE.bufC, gc = C.getContext("2d");
  gc.setTransform(1, 0, 0, 1, 0, 0); gc.globalAlpha = 1; gc.filter = "none";
  renderScene(CACHE.bufB, line, t);
  gc.drawImage(CACHE.bufB, 0, 0);
  // transição rasgada: cena anterior sendo arrancada
  const td = T.tearDuration;
  if (idx > 0 && t - line.start < td) {
    const prev = L[idx - 1]; const k = E.inOutCubic((t - line.start) / td);
    renderScene(CACHE.bufA, prev, t);
    const angle = [0, .35, -.3, Math.PI / 2, .2, -.4][idx % 6], seed = idx * 3.7;
    gc.save(); tornStrip(gc, k, angle, seed); gc.restore();
    gc.save(); tornClipPath(gc, k, angle, seed); gc.clip(); gc.drawImage(CACHE.bufA, 0, 0); gc.restore();
  }
  fog(gc, t, 1700, .35, 6, 99);      // névoa baixa contínua (zona dos ícones do Reels)
  particles(gc, t);
  // saída final: saturação (a cor some na virada)
  const drain = clamp((t - T.colorDrainStart) / (T.colorDrainEnd - T.colorDrainStart));
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  ctx.filter = `saturate(${lerp(1.08, 0, drain)}) contrast(${lerp(1.02, 1.1, drain)})`;
  ctx.drawImage(C, 0, 0); ctx.filter = "none";
  // película: vinheta, grão, poeira, flicker
  ctx.drawImage(CACHE.vignette, 0, 0);
  const fr = Math.floor(t * 30);
  ctx.save(); ctx.globalCompositeOperation = "overlay"; ctx.globalAlpha = .22; ctx.drawImage(CACHE.grain[fr % 6], 0, 0, W, H); ctx.restore();
  ctx.save(); ctx.strokeStyle = "rgba(240,230,210,.35)"; ctx.lineWidth = 1.5;
  for (let i = 0; i < 3; i++) if (hash(fr * 3 + i) > .6) { const x = hash(fr * 7 + i) * W; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + (hash(fr + i) - .5) * 30, H); ctx.stroke(); }
  for (let i = 0; i < 5; i++) { const x = hash(fr * 11 + i) * W, y = hash(fr * 13 + i) * H; ctx.fillStyle = `rgba(20,15,10,${.4 * hash(fr + i * 5)})`; ctx.beginPath(); ctx.arc(x, y, 1 + hash(i + fr) * 3, 0, 7); ctx.fill(); }
  ctx.restore();
  const flick = .035 * (noise1(t * 8) - .5); if (flick > 0) { ctx.fillStyle = `rgba(255,245,225,${flick})`; ctx.fillRect(0, 0, W, H); } else { ctx.fillStyle = `rgba(0,0,0,${-flick})`; ctx.fillRect(0, 0, W, H); }
  drawCaption(ctx, t);
  if (window.SHOW_GUIDES) guides(ctx);
}
function guides(g) {
  g.save(); g.fillStyle = "rgba(255,0,0,.18)"; g.fillRect(0, H * .75, W, H * .25); g.fillRect(SAFE.x1 + 40, 0, W - SAFE.x1 - 40, H);
  g.strokeStyle = "rgba(255,80,80,.9)"; g.lineWidth = 3; g.strokeRect(SAFE.x0, 0, SAFE.x1 - SAFE.x0, SAFE.yMax); g.restore();
}

/* ---------- boot / prévia ---------- */
window.renderFrame = renderFrame;
window.READY = loadAll().then(async () => {
  try { const m = await (await fetch("assets.json?" + Date.now())).json(); if (m._gate) GATE = m._gate; } catch (e) { }
  const params = new URLSearchParams(location.search);
  if (params.has("render")) { document.body.classList.add("render"); }
  const t0 = parseFloat(params.get("t") || "0"); renderFrame(t0);
  if (params.has("render")) return true;
  const scrub = document.getElementById("scrub"), tc = document.getElementById("tc"), btn = document.getElementById("play");
  scrub.max = T.duration;
  let playing = false, startWall = 0, startT = 0, audio = null;
  const draw = tt => { renderFrame(tt); tc.textContent = tt.toFixed(2) + " s"; scrub.value = tt; };
  scrub.oninput = () => { playing = false; if (audio) audio.pause(); draw(parseFloat(scrub.value)); };
  document.getElementById("guides").onchange = e => { window.SHOW_GUIDES = e.target.checked; draw(parseFloat(scrub.value)); };
  btn.onclick = () => {
    playing = !playing; btn.textContent = playing ? "❚❚ pausar" : "▶ tocar";
    if (playing) {
      startWall = performance.now(); startT = parseFloat(scrub.value); if (startT >= T.duration - .05) startT = 0;
      if (document.getElementById("withAudio").checked) { audio = audio || new Audio("../out/audio_mix.wav"); audio.currentTime = startT; audio.play().catch(() => { }); }
      const loop = () => { if (!playing) return; const tt = startT + (performance.now() - startWall) / 1000; if (tt >= T.duration) { playing = false; btn.textContent = "▶ tocar"; return; } draw(tt); requestAnimationFrame(loop); };
      loop();
    } else if (audio) audio.pause();
  };
  draw(t0);
  return true;
});
