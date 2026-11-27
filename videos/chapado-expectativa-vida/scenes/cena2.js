// CENA 2 — VINHETA: logo em letras de revista, fumaça recortada em parallax, olho gigante piscando.
SCENES.cena2 = function (stage, cfg) {
  const sc = new Scene(stage, cfg);
  sc.camOpts = { z0: 1.0, z1: 1.1, drift: 30 };
  const { W, H, u } = stage, P = PALETA, cx = stage.cx;
  const [L0, L1, L2, L3, L4] = sc.layers([0.02, 0.3, 0.55, 0.8, 1.0]);
  new PaperBackground(stage, L0, 8, P.tinta);
  new Sunburst(stage, L0, { x: cx, y: H * 0.42, color: P.tomate, opacity: 0.55, speed: 22, rays: 18 });
  const fumacas = [];
  [[L1, 0.15, 0.8, 0.9, "#cfc6b4"], [L1, 0.85, 0.3, 0.8, "#cfc6b4"], [L2, 0.2, 0.55, 1.1, "#e8e2d4"], [L2, 0.82, 0.62, 1.0, "#e8e2d4"],
    [L4, 0.05, 0.9, 1.5, "#f7f1e1"], [L4, 0.95, 0.15, 1.4, "#f7f1e1"]].forEach(([L, x, y, s, c], i) => {
    fumacas.push({ cut: new PaperCutout(L, { art: ART.fumaca(c), w: 360, h: 200, x: W * x, y: H * y, scale: s * u, pivot: "center", seed: 60 + i, t0: 0.1 + i * 0.1 }), x: W * x, y: H * y, i });
  });
  new PaperCutout(L2, { art: tornBlob(700, 520, 9, P.papel), w: 700, h: 520, x: cx, y: H * 0.42, scale: u, pivot: "center", seed: 2, rot: 3 });
  const olho = new PaperCutout(L2, { art: ART.olho(), w: 120, h: 80, x: cx, y: H * 0.42, scale: 4.6 * u, pivot: "center", seed: 1, t0: 0.3, rot: -2, sway: [3, 2, 0] });
  new RansomText(L3, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.78, text: "PERGUNTAS QUE\nEU ME FIZ\nQUANDO", x: cx, y: H * 0.15, size: 96 * u, t0: 0.6, stagger: 0.045, seed: 21 });
  new RansomText(L3, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.78, text: "ESTAVA\nCHAPADO", x: cx, y: H * 0.66, size: 150 * u, t0: 1.5, stagger: 0.07, seed: 33 });
  sc.updaters.push((t) => {
    const tq = K.step12(t);
    const lid = [1.2, 3.4, 4.1].reduce((m, b) => (tq >= b && tq < b + 0.3 ? Math.sin(Math.PI * (tq - b) / 0.3) : m), 0);
    olho.setArt(ART.olho(lid, Math.sin(t * 1.3)));
    fumacas.forEach((f) => {
      f.cut.o.y = f.y - ((tq * (20 + f.i * 6)) % 120) * u + Math.sin(tq + f.i) * 10;
      f.cut.o.x = f.x + Math.sin(tq * 0.7 + f.i) * 30 * u;
    });
  });
  return sc;
};
