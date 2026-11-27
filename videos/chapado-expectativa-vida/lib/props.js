// Objetos de cena reutilizáveis: bolo com N velas e gráfico de barbante.

// ---------------------------------------------------------------------------
class CakeWithCandles {
  // bolo recortado com n velas que vão surgindo (cada vez mais rápido) e acendendo sem parar
  constructor(layer, o) {
    this.o = Object.assign({ n: 45, x: 0, y: 0, scale: 1, seed: 1, tA: 0.9, tB: 7.1, vs: 0.72, sway: [3.5, 1.4, 0] }, o);
    const pos = [];
    const rows = this.o.n <= 45 ? [[8, -0.62], [11, -0.22], [12, 0.2], [14, 0.6]]
      : [[11, -0.7], [14, -0.38], [17, -0.05], [18, 0.28], [20, 0.62]];
    rows.forEach(([n, fy]) => {
      const y = 190 + fy * 64 * 0.92, half = 270 * Math.sqrt(1 - fy * fy) * 0.86;
      for (let i = 0; i < n; i++) pos.push([320 - half + (2 * half * i) / (n - 1), y + Math.sin(i * 1.7) * 3]);
    });
    this.pos = pos.slice(0, Math.max(this.o.n, pos.length));
    const rr = K.rng(this.o.seed * 42);
    const ordem = this.pos.map((p, i) => [rr(), i]).sort((a, b) => a[0] - b[0]).map((x) => x[1]);
    this.tv = new Array(this.pos.length);
    const N = this.pos.length;
    ordem.forEach((idx, k) => (this.tv[idx] = this.o.tA + (this.o.tB - this.o.tA) * Math.pow(k / Math.max(1, N - 1), 0.72)));
    this.draw = this.pos.map((p, i) => [p[1], i]).sort((a, b) => a[0] - b[0]).map((x) => x[1]);
    this.base = ART.boloGrande();
    this.cut = new PaperCutout(layer, { art: this.base, w: 640, h: 500, x: this.o.x, y: this.o.y, scale: this.o.scale,
      seed: this.o.seed, sway: this.o.sway, boil: 1 });
    this.layer = layer;
    if (layer.items) layer.items.splice(layer.items.indexOf(this.cut), 0, this);
  }
  lit(t) { const tq = K.step12(t); return this.tv.filter((tv) => tq > tv + 0.3).length; }
  update(t) {
    const tq = K.step12(t), VS = this.o.vs;
    let s = "";
    for (const i of this.draw) {
      const p = K.pop(t, this.tv[i], 0.35);
      if (p <= 0) continue;
      const [x, y] = this.pos[i];
      const sv = VS * p;
      s += `<g transform="translate(${x} ${y}) rotate(${K.boil(t, i + 300, 2.5)}) scale(${sv}) translate(-20 -150)">${ART.vela(i % 3 === 0)}</g>`;
      const lit = tq - this.tv[i] - 0.3;
      const off = lit > 1.5 && (tq * 0.9 + i * 0.37) % 4.2 < 0.25;
      if (lit > 0 && !off) {
        const pf = K.pop(t, this.tv[i] + 0.3, 0.3), fl = 0.5 + K.boil(t, i + 500, 0.5);
        s += `<g transform="translate(${x} ${y - 150 * sv + 24 * sv}) scale(${sv * pf * (0.9 + 0.2 * fl)}) translate(-20 -60)">${ART.chama(fl)}</g>`;
      }
    }
    this.cut.setArt(this.base + s);
  }
}

// ---------------------------------------------------------------------------
// Expectativa de vida ao nascer, Brasil (IBGE; valores anuais aproximados entre os pontos do roteiro)
const DADOS_BR = [[2010, 74.4], [2011, 74.6], [2012, 74.9], [2013, 75.1], [2014, 75.4], [2015, 75.6], [2016, 75.8],
  [2017, 76.0], [2018, 76.2], [2019, 76.4], [2020, 74.8], [2021, 72.8], [2022, 75.5], [2023, 76.4], [2024, 76.6]];

class StringGraph {
  // gráfico de barbante sobre papel quadriculado, com fita adesiva nos pontos e post-its.
  constructor(layer, o) {
    this.o = Object.assign({ x: 0, y: 0, scale: 1, seed: 61, rot: -2 }, o);
    this.sheet = ART.folhaGrafico();
    this.cut = new PaperCutout(layer, { art: this.sheet, w: 900, h: 1000, x: this.o.x, y: this.o.y, scale: this.o.scale,
      pivot: "center", seed: this.o.seed, rot: this.o.rot, sway: [5, 0.6, 0], boil: 0.6, t0: this.o.t0 ?? null });
    this.year = 2010;          // até onde o barbante já foi esticado (fracionário)
    this.notes = [];           // [ano, linha1, linha2, cor, t0]
    this.tear = 0;             // 0..1 abertura do rasgo no ponto de 2021
    if (layer.items) layer.items.splice(layer.items.indexOf(this.cut), 0, this);
  }
  X(y) { return 140 + (y - 2010) / 14 * 680; }
  Y(v) { return 880 - (v - 72) / 5 * 720; }
  val(year) {
    const i = Math.max(0, Math.min(DADOS_BR.length - 2, Math.floor(year - 2010)));
    const [y0, v0] = DADOS_BR[i], [, v1] = DADOS_BR[i + 1];
    return K.lerp(v0, v1, K.clamp(year - y0));
  }
  // ponto (ano) em coordenadas da tela (aprox., ignora a rotação leve da folha)
  screen(year) {
    const s = this.o.scale;
    return [this.o.x + (this.X(year) - 450) * s, this.o.y + (this.Y(this.val(year)) - 500) * s];
  }
  update(t) {
    const k = INK(), P = PALETA;
    let s = this.sheet;
    // eixos e anos
    s += `<line x1="120" y1="900" x2="850" y2="900" stroke="${k}" stroke-width="5"/>`;
    [2010, 2014, 2018, 2021, 2024].forEach((y) => (s += `<text x="${this.X(y)}" y="950" text-anchor="middle" font-family="Courier 10 Pitch" font-weight="700" font-size="34" fill="${k}">${y}</text>`));
    [73, 74, 75, 76, 77].forEach((v) => (s += `<text x="70" y="${this.Y(v) + 12}" text-anchor="middle" font-family="Anton" font-size="34" fill="${P.petroleo}">${v}</text>`));
    // rasgo
    if (this.tear > 0.01) {
      const cx = this.X(2021), cy = this.Y(72.8) + 20, w = 120 * this.tear, h = 200 * this.tear;
      let pts = "";
      for (let i = 0; i < 18; i++) {
        const a = (i / 18) * 2 * Math.PI, j = 0.65 + K.hash(i * 3.3) * 0.5;
        pts += `${cx + Math.cos(a) * w * j},${cy + Math.sin(a) * h * j} `;
      }
      s += `<polygon points="${pts}" fill="#120d08" stroke="#fbf7ec" stroke-width="${10 * this.tear}"/>`;
    }
    // barbante
    const end = this.year;
    const pts = [];
    for (let y = 2010; y <= end + 1e-6; y += 0.25) pts.push([this.X(y), this.Y(this.val(y))]);
    pts.push([this.X(end), this.Y(this.val(end))]);
    const d = "M" + pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" L");
    s += `<path d="${d}" fill="none" stroke="${k}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="${d}" fill="none" stroke="${P.tomate}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="${d}" fill="none" stroke="#ff9a85" stroke-width="3" stroke-dasharray="6 9" stroke-linecap="round"/>`;
    // fita adesiva nos pontos já alcançados
    DADOS_BR.forEach(([y, v], i) => {
      if (y <= end && i % 2 === 0 || y === 2021 && end >= 2021) {
        const a = K.hash(y) * 40 - 20;
        s += `<g transform="translate(${this.X(y)} ${this.Y(v)}) rotate(${a}) scale(0.55) translate(-60 -20)">${ART.fita()}</g>`;
      }
    });
    // ponta do barbante
    s += `<circle cx="${this.X(end)}" cy="${this.Y(this.val(end))}" r="14" fill="${P.tomate}" stroke="${k}" stroke-width="5"/>`;
    // post-its
    this.notes.forEach(([y, l1, l2, cor, t0, dx, dy]) => {
      const p = K.pop(t, t0, 0.4);
      if (p <= 0) return;
      const x = this.X(y) + (dx || 0), yy = this.Y(this.val(y)) + (dy || -170);
      s += `<g transform="translate(${x} ${yy}) rotate(${K.hash(y * 7) * 14 - 7 + K.boil(t, y, 1)}) scale(${0.85 * p}) translate(-115 -110)">${ART.postit(l1, l2, cor)}</g>`;
    });
    this.cut.setArt(s);
  }
}
