// CENA 1 — GANCHO: bolo recortado com velas acendendo sem parar, "45 ANOS" em letras de revista,
// esqueleto de gravura espiando pela borda. Fundo petróleo com raios mostarda.
SCENES.cena1 = function (stage, cfg) {
  const sc = new Scene(stage, cfg);
  const tCav = K.quando(cfg, "provavelmente", 3.2), tHoje = K.quando(cfg, "hoje", 7.0);
  const { W, H, u } = stage;
  const P = PALETA, V = stage.vertical, L_ = (h, v) => (V ? v : h), cx = stage.cx;
  const [L0, L1, L2, L3, L4] = sc.layers([0.02, 0.3, 0.6, 0.78, 1.0]);
  new PaperBackground(stage, L0, 3, P.petroleo);
  new Sunburst(stage, L0, { x: cx, y: H * L_(0.5, 0.5), color: P.mostarda, opacity: 0.32, speed: 5 });

  const lua = new PaperCutout(L1, { art: ART.lua(), w: 260, h: 260, x: W * L_(0.84, 0.76), y: H * L_(0.22, 0.09), scale: 0.95 * u, pivot: "center", seed: 2, t0: 0.2 });
  const nuvens = [0, 1].map((i) => new PaperCutout(L1, { art: ART.nuvem(), w: 320, h: 170, x: 0, y: H * L_(i ? 0.17 : 0.30, i ? 0.07 : 0.31),
    scale: (i ? 0.7 : 0.95) * u, seed: 5 + i * 3, t0: 0.1 + i * 0.25 }));
  (V ? [[0.12, 0.17], [0.08, 0.45], [0.84, 0.30], [0.55, 0.04], [0.88, 0.64]] : [[0.3, 0.1], [0.08, 0.55], [0.93, 0.5], [0.4, 0.33], [0.72, 0.4]])
    .forEach(([x, y], i) => new PaperCutout(L1, { art: ART.estrela([P.mostarda, P.tomate, P.papel][i % 3]), w: 60, h: 60, x: W * x, y: H * y, scale: 1.2 * u, pivot: "center", seed: 20 + i, t0: 0.15 + i * 0.12 }));

  // mancha de papel creme atrás do bolo (ponto focal)
  new PaperCutout(L2, { art: tornBlob(1000, 900, 4, P.papel), w: 1000, h: 900, x: cx, y: H * L_(0.55, 0.53), scale: u, pivot: "center", seed: 3, rot: -4, sway: [6, 1, 0] });
  const glow = K.el("ellipse", { cx, cy: H * L_(0.40, 0.50), rx: 520 * u, ry: 300 * u, fill: "url(#brilho)", opacity: 0 }, L2.el);
  const bolo = new CakeWithCandles(L2, { n: 45, x: L_(W * 0.5, cx), y: H * L_(0.8, 0.715), scale: L_(1.12, 1.42) * u, seed: 1 });

  new RansomText(L3, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.78, text: L_("45 ANOS", "45\nANOS"), x: L_(W * 0.47, cx), y: H * L_(0.13, 0.21), size: L_(140, 200) * u, t0: 0.5, stagger: 0.1, seed: 7 });

  const caveira = new PaperCutout(L4, { art: ART.caveira(), w: 360, h: 420, x: W + 300 * u, y: H * L_(0.62, 0.43), scale: 0.95 * u, pivot: "center", rot: -14, seed: 4, sway: [2.6, 3, 1], boil: 1.5 });
  new PaperCutout(L4, { art: ART.maoOsso(), w: 260, h: 200, x: W - 60 * u, y: H * L_(0.86, 0.56), scale: 0.9 * u, pivot: "center", rot: -8, seed: 9, sway: [2.2, 2, 0], t0: tCav + 0.5 });
  const aponta = new PaperCutout(L4, { art: ART.maoAponta(), w: 340, h: 170, x: -300 * u, y: H * L_(0.70, 0.66), scale: u, pivot: "center", rot: -10, seed: 11, sway: [2.4, 3, 2], t0: tHoje });
  if (V) new PaperCutout(L4, { art: ART.jornal(), w: 1200, h: 260, x: W * 0.5, y: H + 40 * u, scale: u, seed: 13, rot: -3, sway: [4, 1, 0] });
  const confetes = makeConfetti(L4, stage, 14, 700);

  sc.updaters.push((t) => {
    const tq = K.step12(t);
    glow.setAttribute("opacity", (0.15 + 0.6 * bolo.lit(t) / 45 + K.boil(t, 77, 0.05)).toFixed(3));
    const blink = [2.2, 5.9, 8.6].some((b) => tq >= b && tq < b + 0.25) ? 1 : 0;
    lua.setArt(ART.lua() + `<g transform="translate(70 90)">${ART.olho(blink, Math.sin(t * 0.8))}</g>`);
    nuvens.forEach((n, i) => (n.o.x = W * L_(i ? 0.64 : 0.14, i ? 0.3 : 0.2) + Math.sin(t * 0.4 + i * 2) * 30 * u));
    const peek = K.ease.outBack(K.clamp((tq - tCav) / 0.7), 1.4);
    caveira.o.x = W + 300 * u - peek * 440 * u;
    const jaw = tq > tCav + 0.8 && tq < tCav + 2.8 ? 0.5 + 0.5 * Math.sin(tq * 30) : 0.1;
    const lid = [6.8, 9.0].some((b) => tq >= b && tq < b + 0.25) ? 1 : 0;
    caveira.setArt(ART.caveira(jaw, lid, -0.9));
    aponta.o.x = -300 * u + K.ease.outBack(K.clamp((tq - tHoje) / 0.5)) * L_(520, 460) * u;
    confetes(t);
  });
  return sc;
};

// confetes de papel caindo (reutilizável)
function makeConfetti(layer, stage, n, seed) {
  const { W, H, u } = stage, P = PALETA;
  const items = Array.from({ length: n }, (_, i) => {
    const r = K.rng(seed + i);
    return { cut: new PaperCutout(layer, { art: ART.confete([P.tomate, P.mostarda, P.petroleo, P.papel][i % 4]), w: 70, h: 30, x: 0, y: -999,
      scale: (0.6 + r() * 0.6) * u, pivot: "center", seed: 40 + i }), x: r() * W, sp: 60 + r() * 90, ph: r() * 10, rot: r() * 360 };
  });
  return (t) => {
    const tq = K.step12(t);
    items.forEach((c, i) => {
      c.cut.o.x = c.x + Math.sin(tq * 1.5 + c.ph) * 40;
      c.cut.o.y = ((tq * c.sp + c.ph * 100) % (H * 1.3)) - H * 0.15;
      c.cut.o.rot = c.rot + tq * 90 * (i % 2 ? 1 : -1);
    });
  };
}
