// Componentes reutilizáveis do canal:
//   Stage, PaperBackground, ParallaxLayer (+ câmera), PaperCutout, RansomText, AnimatedNumber,
//   TornTransition, Caption.
// Uso típico numa cena:
//   const L = scene.layers(4)                 // fundo, distante, meio, frente
//   new PaperCutout(L[2], { art: ART.bolo(), w: 600, h: 520, x, y, t0: 0.5 })
//   scene.update(t) -> câmera + parallax + update de todos os recortes

const FONTES_RANSOM = [
  ["Anton", 400], ["Montserrat", 900], ["DejaVu Serif", 700], ["Bitstream Charter", 700],
  ["Courier 10 Pitch", 700], ["Caladea", 700], ["Inter", 900], ["JetBrains Mono", 800], ["FreeSerif", 700],
];

class Stage {
  constructor(svg, W, H) {
    this.svg = svg; this.W = W; this.H = H;
    this.u = Math.min(W, H) / 1080;           // unidade relativa (1 = 1px em 1080p)
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.setAttribute("width", W); svg.setAttribute("height", H);
    this.defs = K.el("defs", {}, svg);
    this.root = K.el("g", {}, svg);
    this._defs();
  }

  _defs() {
    const P = PALETA;
    let s = "";
    // bordas de papel recortado: 6 variações de irregularidade
    for (let i = 0; i < 6; i++) {
      s += `<filter id="cut${i}" x="-25%" y="-25%" width="150%" height="150%" color-interpolation-filters="sRGB">
        <feMorphology in="SourceAlpha" operator="dilate" radius="${7 + (i % 3) * 2}" result="d"/>
        <feTurbulence type="fractalNoise" baseFrequency="${0.035 + i * 0.006}" numOctaves="2" seed="${i * 7 + 3}" result="n"/>
        <feDisplacementMap in="d" in2="n" scale="${12 + (i % 2) * 6}" xChannelSelector="R" yChannelSelector="G" result="edge"/>
        <feFlood flood-color="#fbf7ec"/><feComposite in2="edge" operator="in" result="paper"/>
        <feGaussianBlur in="edge" stdDeviation="7" result="b"/><feOffset dx="7" dy="11" result="o"/>
        <feFlood flood-color="#2a1d10" flood-opacity="0.38"/><feComposite in2="o" operator="in" result="shadow"/>
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="${i}" result="grain"/>
        <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.38  0 0 0 0 0.28  0 0 0 0.22 0" result="g2"/>
        <feComposite in="g2" in2="SourceGraphic" operator="in" result="g3"/>
        <feMerge><feMergeNode in="shadow"/><feMergeNode in="paper"/><feMergeNode in="SourceGraphic"/><feMergeNode in="g3"/></feMerge>
      </filter>`;
    }
    s += `
      <filter id="paperTex" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="3" seed="4" result="fine"/>
        <feColorMatrix in="fine" type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.27  0 0 0 0 0.16  0 0 0 0.20 0" result="f2"/>
        <feTurbulence type="fractalNoise" baseFrequency="0.004" numOctaves="4" seed="9" result="big"/>
        <feColorMatrix in="big" type="matrix" values="0 0 0 0 0.55  0 0 0 0 0.40  0 0 0 0 0.20  0 0 0 0.32 -0.08" result="b2"/>
        <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="b2"/><feMergeNode in="f2"/></feMerge>
      </filter>
      <filter id="stain" x="-30%" y="-30%" width="160%" height="160%">
        <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" seed="2" result="n"/>
        <feDisplacementMap in="SourceGraphic" in2="n" scale="40" xChannelSelector="R" yChannelSelector="G"/>
      </filter>
      <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="14"/></filter>
      <filter id="soft"><feGaussianBlur stdDeviation="3"/></filter>
      <radialGradient id="vinheta" cx="50%" cy="50%" r="72%">
        <stop offset="55%" stop-color="#3a2410" stop-opacity="0"/><stop offset="100%" stop-color="#3a2410" stop-opacity="0.55"/>
      </radialGradient>
      <radialGradient id="vinhetaVermelha" cx="50%" cy="50%" r="70%">
        <stop offset="45%" stop-color="${P.tomate}" stop-opacity="0"/><stop offset="100%" stop-color="#8a0d00" stop-opacity="0.75"/>
      </radialGradient>
      <radialGradient id="chama" cx="50%" cy="60%" r="60%">
        <stop offset="0%" stop-color="#fff7c2"/><stop offset="55%" stop-color="#ffc23a"/><stop offset="100%" stop-color="#f06a1d"/>
      </radialGradient>
      <radialGradient id="brilho" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#ffd76a" stop-opacity="0.75"/><stop offset="100%" stop-color="#ffd76a" stop-opacity="0"/>
      </radialGradient>
      <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <line x1="0" y1="0" x2="0" y2="7" stroke="${P.tinta}" stroke-width="2.2"/></pattern>
      <pattern id="hatchFino" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
        <line x1="0" y1="0" x2="0" y2="6" stroke="${P.tinta}" stroke-width="1.2"/></pattern>
      <pattern id="cross" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
        <path d="M0 0V8M0 0H8" stroke="${P.tinta}" stroke-width="1.6"/></pattern>
      <pattern id="dots" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(20)">
        <circle cx="4.5" cy="4.5" r="2.1" fill="${P.tinta}"/></pattern>
      <pattern id="dotsTomate" width="11" height="11" patternUnits="userSpaceOnUse" patternTransform="rotate(15)">
        <circle cx="5.5" cy="5.5" r="2.6" fill="${P.tomate}"/></pattern>
      <pattern id="dotsMostarda" width="12" height="12" patternUnits="userSpaceOnUse">
        <circle cx="6" cy="6" r="3" fill="${P.mostarda}"/></pattern>
      <pattern id="candy" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
        <rect width="14" height="14" fill="#fbf6ea"/><rect width="6" height="14" fill="${P.tomate}"/></pattern>
      <pattern id="candyAzul" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
        <rect width="14" height="14" fill="#fbf6ea"/><rect width="6" height="14" fill="${P.petroleo}"/></pattern>
      <pattern id="jornal" width="120" height="14" patternUnits="userSpaceOnUse">
        <rect width="120" height="14" fill="#ddd5c2"/><rect y="5" width="${90}" height="3" fill="#8f8676"/></pattern>`;
    this.defs.innerHTML = s;
  }
}

// ---------------------------------------------------------------------------
class ParallaxLayer {
  // depth: 0 = fundo (quase parado) ... 1 = primeiro plano (rápido, pode sair da tela)
  constructor(stage, parent, depth) {
    this.stage = stage; this.depth = depth;
    this.el = K.el("g", {}, parent);
    this.items = [];
  }
  apply(cam) {
    const { W, H } = this.stage;
    const d = this.depth;
    const z = 1 + (cam.z - 1) * (0.25 + 1.1 * d);
    const dx = cam.x * (0.1 + d) * this.stage.u;
    const dy = cam.y * (0.1 + d) * this.stage.u;
    const sx = cam.shakeX || 0, sy = cam.shakeY || 0;
    this.el.setAttribute("transform",
      `translate(${W / 2 + dx + sx * (0.3 + d)} ${H / 2 + dy + sy * (0.3 + d)}) scale(${z}) translate(${-W / 2} ${-H / 2})`);
  }
}

// ---------------------------------------------------------------------------
class PaperCutout {
  /*
   art: markup SVG desenhado na caixa 0..w x 0..h
   x, y: posição do pivô na tela; scale; rot (graus); seed
   t0: entrada (stop-motion pop). null = já está em cena
   sway: [período s, amplitude graus, fase]; pivot: "base" | "center"
   boil: tremida de stop-motion (px); cut: false para sem borda de papel
  */
  constructor(layer, o) {
    this.o = Object.assign({ x: 0, y: 0, scale: 1, rot: null, seed: 1, t0: null, sway: null, pivot: "base",
      boil: 1.2, cut: true, exit: null }, o);
    const r = K.rng(this.o.seed * 17 + 3);
    if (this.o.rot === null) this.o.rot = (r() - 0.5) * 8;          // ±4°
    if (this.o.sway === null) this.o.sway = [2 + r() * 2, 3 + r() * 3, r() * 6.28];
    this.el = K.el("g", {}, layer.el || layer);
    this.inner = K.el("g", this.o.cut ? { filter: `url(#cut${this.o.seed % 6})` } : {}, this.el);
    this.inner.innerHTML = this.o.art;
    if (layer.items) layer.items.push(this);
  }
  setArt(markup) {               // troca o desenho (ex.: chama tremendo, olho piscando) só quando muda
    if (markup !== this._art) { this.inner.innerHTML = markup; this._art = markup; }
  }
  update(t, extra = {}) {
    const o = this.o;
    let s = o.t0 === null ? 1 : K.pop(t, o.t0);
    if (o.exit !== null && t >= o.exit) s *= 1 - K.ease.inOut(K.clamp((K.step12(t) - o.exit) / 0.3));
    if (s <= 0.001) { this.el.setAttribute("display", "none"); return; }
    this.el.removeAttribute("display");
    const ts = K.step12(t);
    const rot = o.rot + K.sway(ts, o.sway[0], o.sway[1], o.sway[2]) + K.boil(t, o.seed, 0.6) + (extra.rot || 0);
    const bx = K.boil(t, o.seed + 1, o.boil), by = K.boil(t, o.seed + 2, o.boil);
    const px = o.w / 2, py = o.pivot === "base" ? o.h : o.h / 2;
    const sc = s * o.scale * (extra.scale || 1);
    this.el.setAttribute("transform",
      `translate(${o.x + bx + (extra.x || 0)} ${o.y + by + (extra.y || 0)}) rotate(${rot}) scale(${sc * (extra.sx || 1)} ${sc * (extra.sy || 1)}) translate(${-px} ${-py})`);
  }
}

// ---------------------------------------------------------------------------
class RansomText {
  // letras de revista recortada: cada uma com fonte, cor e papel diferentes, entrando uma a uma
  constructor(layer, o) {
    this.o = Object.assign({ x: 0, y: 0, size: 120, t0: 0, stagger: 0.09, seed: 1, align: "middle", lineGap: 1.15 }, o);
    this.letters = [];
    const r = K.rng(this.o.seed * 31 + 7);
    const P = PALETA;
    const pares = [[P.papel, P.tinta], [P.tinta, P.papel], [P.tomate, P.papel], [P.mostarda, P.tinta],
      [P.petroleo, P.papel], ["#ffffff", P.tomate], ["#d8d0bd", P.tinta], [P.creme, P.petroleo], [P.papel, P.tomate]];
    const lines = this.o.text.split("\n");
    const S = this.o.size;
    let idx = 0;
    lines.forEach((line, li) => {
      const ws = [...line].map((c) => (c === " " ? S * 0.35 : S * (0.62 + r() * 0.22)));
      const total = ws.reduce((a, b) => a + b, 0);
      let cx = this.o.x - (this.o.align === "middle" ? total / 2 : 0);
      const cy = this.o.y + (li - (lines.length - 1) / 2) * S * this.o.lineGap;
      [...line].forEach((c, i) => {
        const w = ws[i];
        if (c !== " ") {
          const [font, weight] = FONTES_RANSOM[Math.floor(r() * FONTES_RANSOM.length)];
          const [bg, fg] = pares[Math.floor(r() * pares.length)];
          const fs = S * (0.78 + r() * 0.3);
          const bw = w * (0.96 + r() * 0.12), bh = S * (1.0 + r() * 0.2);
          const shape = r() < 0.75
            ? `<rect x="0" y="0" width="${bw}" height="${bh}" fill="${bg}"/>`
            : `<polygon points="${bw * 0.05},${bh * 0.02} ${bw},0 ${bw * 0.95},${bh} 0,${bh * 0.96}" fill="${bg}"/>`;
          const art = `${shape}<text x="${bw / 2}" y="${bh * 0.5}" dominant-baseline="central" text-anchor="middle"
            font-family="${font}" font-weight="${weight}" font-size="${fs}" fill="${fg}">${c}</text>`;
          const cut = new PaperCutout(layer, {
            art, w: bw, h: bh, x: cx + w / 2, y: cy, seed: this.o.seed * 50 + idx, pivot: "center",
            rot: (r() - 0.5) * 16, t0: this.o.t0 + idx * this.o.stagger, sway: [2.2 + r() * 1.6, 2 + r() * 2, r() * 6.28], boil: 1.5,
          });
          cut.o.y += (r() - 0.5) * S * 0.12;
          this.letters.push(cut);
          idx++;
        }
        cx += w;
      });
    });
  }
  update(t, extra) { this.letters.forEach((l) => l.update(t, extra)); }
  get end() { return this.o.t0 + this.letters.length * this.o.stagger + 0.4; }
}

// ---------------------------------------------------------------------------
class AnimatedNumber {
  // número gigante recortado contando (ex.: 74,4 -> 76,6)
  constructor(layer, o) {
    this.o = Object.assign({ x: 0, y: 0, size: 260, from: 0, to: 45, t0: 0, dur: 1.6, dec: 0, suffix: "",
      bg: PALETA.papel, fg: PALETA.tomate, font: "Anton", seed: 3 }, o);
    const S = this.o.size;
    const chars = (K.fmt(this.o.to, this.o.dec) + this.o.suffix).length;
    this.w = S * 0.58 * chars + S * 0.4;
    this.h = S * 1.25;
    const art = `<rect width="${this.w}" height="${this.h}" fill="${this.o.bg}"/>
      <rect width="${this.w}" height="${this.h}" fill="url(#dots)" opacity="0.10"/>
      <text class="num" x="${this.w / 2}" y="${this.h * 0.53}" dominant-baseline="central" text-anchor="middle"
        font-family="${this.o.font}" font-size="${S}" fill="${this.o.fg}" stroke="${PALETA.tinta}" stroke-width="${S * 0.025}"
        paint-order="stroke"></text>`;
    this.cut = new PaperCutout(layer, { art, w: this.w, h: this.h, x: this.o.x, y: this.o.y, seed: this.o.seed,
      pivot: "center", t0: this.o.t0, rot: this.o.rot ?? -3, sway: [3, 2, 0] });
    this.txt = this.cut.inner.querySelector(".num");
  }
  value(t) {
    const u = K.clamp((K.step12(t) - this.o.t0 - 0.15) / this.o.dur);
    return K.lerp(this.o.from, this.o.to, K.ease.out(u));
  }
  update(t, extra) {
    this.txt.textContent = K.fmt(this.value(t), this.o.dec) + this.o.suffix;
    this.cut.update(t, extra);
  }
}

// ---------------------------------------------------------------------------
class TornTransition {
  // papel rasgando: a cena que sai fica recortada por uma borda irregular que atravessa a tela
  constructor(stage, seed = 1) {
    this.stage = stage;
    this.id = "torn" + seed + "_" + Math.floor(Math.random() * 1e6);
    this.clip = K.el("clipPath", { id: this.id }, stage.defs);
    this.path = K.el("path", {}, this.clip);
    const r = K.rng(seed * 91);
    this.jag = Array.from({ length: 60 }, () => (r() - 0.5));
    this.fiber = K.el("path", { fill: "#fbf7ec", filter: "url(#cut0)" });
    this.shadow = K.el("path", { fill: "#2a1d10", opacity: 0.35, filter: "url(#soft)" });
  }
  edge(u) {
    const { W, H } = this.stage;
    const x0 = K.lerp(W * 1.15, -W * 0.25, K.ease.inOut(u));
    const pts = [];
    for (let i = 0; i <= 59; i++) {
      const y = (i / 59) * (H + 40) - 20;
      const x = x0 + (y / H - 0.5) * W * 0.18 + this.jag[i] * 46 * this.stage.u + Math.sin(i * 1.7) * 14 * this.stage.u;
      pts.push([x, y]);
    }
    return pts;
  }
  // outGroup: a cena que sai (desenhada por cima); overlayParent: onde desenhar a fibra branca do rasgo
  apply(outGroup, overlayParent, u) {
    if (u <= 0) { outGroup.removeAttribute("clip-path"); this.fiber.remove(); this.shadow.remove(); return; }
    const { H } = this.stage;
    const pts = this.edge(u);
    const d = "M-50,-50 " + pts.map((p) => `L${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ") + ` L-50,${H + 50} Z`;
    this.path.setAttribute("d", d);
    outGroup.setAttribute("clip-path", `url(#${this.id})`);
    const off = 16 * this.stage.u;
    const strip = "M" + pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" L") + " " +
      pts.slice().reverse().map((p) => `L${(p[0] + off).toFixed(1)},${p[1].toFixed(1)}`).join(" ") + " Z";
    this.fiber.setAttribute("d", strip);
    this.shadow.setAttribute("d", strip);
    this.shadow.setAttribute("transform", `translate(${off * 1.2} ${off * 0.4})`);
    overlayParent.appendChild(this.shadow);
    overlayParent.appendChild(this.fiber);
  }
}

// ---------------------------------------------------------------------------
class Caption {
  // legenda: sans-serif bold mostarda com contorno preto, terço inferior
  constructor(stage) {
    this.stage = stage;
    const u = stage.u;
    this.el = K.el("text", {
      x: stage.W / 2, y: stage.H * 0.90, "text-anchor": "middle", "dominant-baseline": "central",
      "font-family": "Montserrat", "font-weight": 900, "font-size": 66 * u, fill: PALETA.mostarda,
      stroke: PALETA.tinta, "stroke-width": 12 * u, "stroke-linejoin": "round", "paint-order": "stroke",
    }, stage.svg);
  }
  update(t, legendas) {
    let cur = null, t0 = 0;
    for (const [ts, txt] of legendas) if (t >= ts) { cur = txt; t0 = ts; }
    if (!cur) { this.el.textContent = ""; return; }
    this.el.textContent = cur;
    const s = K.pop(t, t0, 0.3) || 0;
    const { W, H } = this.stage;
    this.el.setAttribute("transform", `translate(${W / 2} ${H * 0.86}) scale(${s}) rotate(${K.boil(t, 99, 0.8)}) translate(${-W / 2} ${-H * 0.90})`);
  }
}

// ---------------------------------------------------------------------------
class PaperBackground {
  constructor(stage, layer, seed = 1, tint = PALETA.creme) {
    const { W, H } = stage;
    const r = K.rng(seed * 7 + 1);
    const g = K.el("g", {}, layer.el);
    K.el("rect", { x: -W * 0.15, y: -H * 0.15, width: W * 1.3, height: H * 1.3, fill: tint, filter: "url(#paperTex)" }, g);
    // vincos (dobras do papel)
    for (let i = 0; i < 2; i++) {
      const x = W * (0.25 + r() * 0.5);
      const a = (r() - 0.5) * 0.3;
      const x1 = x + Math.tan(a) * H * 0.7, x2 = x - Math.tan(a) * H * 0.7;
      K.el("line", { x1, y1: -H * 0.2, x2, y2: H * 1.2, stroke: "#fffaf0", "stroke-width": 3 * stage.u, opacity: 0.5 }, g);
      K.el("line", { x1: x1 + 4, y1: -H * 0.2, x2: x2 + 4, y2: H * 1.2, stroke: "#6b5236", "stroke-width": 2.5 * stage.u, opacity: 0.18 }, g);
    }
    // manchas de café
    for (let i = 0; i < 3; i++) {
      const cx = W * (0.1 + r() * 0.8), cy = H * (0.1 + r() * 0.8), rr = (60 + r() * 90) * stage.u;
      K.el("circle", { cx, cy, r: rr, fill: "#8a5a2b", opacity: 0.06, filter: "url(#stain)" }, g);
      K.el("circle", { cx, cy, r: rr, fill: "none", stroke: "#7a4a20", "stroke-width": 5 * stage.u, opacity: 0.2, filter: "url(#stain)" }, g);
    }
    K.el("rect", { x: -W * 0.15, y: -H * 0.15, width: W * 1.3, height: H * 1.3, fill: "url(#vinheta)" }, g);
    this.el = g;
  }
}

// ---------------------------------------------------------------------------
class Scene {
  // camada base para todas as cenas: câmera com push-in contínuo + drift lateral
  constructor(stage, cfg) {
    this.stage = stage; this.cfg = cfg;
    this.el = K.el("g", {}, stage.root);
    this.layerList = [];
    this.updaters = [];
    this.camOpts = { z0: 1.0, z1: 1.08, drift: 26 };
  }
  layers(depths = [0.02, 0.3, 0.6, 1.0]) {
    this.layerList = depths.map((d) => new ParallaxLayer(this.stage, this.el, d));
    return this.layerList;
  }
  camera(t) {
    const { z0, z1, drift } = this.camOpts;
    const u = K.clamp(t / this.cfg.dur);
    return {
      z: K.lerp(z0, z1, K.ease.inOut(u) * 0.6 + u * 0.4),
      x: Math.sin(t * 0.45) * drift,
      y: Math.cos(t * 0.33) * drift * 0.4,
      shakeX: 0, shakeY: 0,
    };
  }
  update(t) {
    const cam = this.camera(t);
    if (this.shake) { const s = this.shake(t); cam.shakeX = s[0]; cam.shakeY = s[1]; }
    this.updaters.forEach((f) => f(t, cam));          // primeiro a lógica da cena (posições, desenhos)...
    this.layerList.forEach((L) => { L.apply(cam); L.items.forEach((it) => it.update(t)); });   // ...depois aplica
  }
}
