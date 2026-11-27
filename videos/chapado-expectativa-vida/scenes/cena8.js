// CENA 8 — FECHAMENTO: o bolo volta com MUITAS velas e "COMENTA SUA PERGUNTA" em letras de revista. Push-in final.
SCENES.cena8 = function (stage, cfg) {
  const sc = new Scene(stage, cfg);
  const tCom = K.quando(cfg, "comenta", 4.6);
  sc.camOpts = { z0: 1.0, z1: 1.28, drift: 20 };
  const { W, H, u } = stage, P = PALETA, cx = stage.cx, V = stage.vertical;
  const [L0, L1, L2, L3, L4] = sc.layers([0.02, 0.3, 0.6, 0.8, 1.0]);
  new PaperBackground(stage, L0, 11, P.tomate);
  new Sunburst(stage, L0, { x: cx, y: H * 0.5, color: P.mostarda, opacity: 0.45, speed: 10 });
  new PaperCutout(L2, { art: tornBlob(1000, 900, 15, P.papel), w: 1000, h: 900, x: cx, y: H * 0.56, scale: u, pivot: "center", seed: 3, rot: 3 });
  const glow = K.el("ellipse", { cx, cy: H * 0.5, rx: 560 * u, ry: 320 * u, fill: "url(#brilho)", opacity: 0 }, L2.el);
  const bolo = new CakeWithCandles(L2, { n: 80, x: cx, y: H * 0.74, scale: 1.42 * u, seed: 2, tA: 0.2, tB: 3.2, vs: 0.6 });
  new RansomText(L1, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.74, text: "COMENTA SUA\nPERGUNTA", x: cx, y: H * 0.17, size: 120 * u, t0: tCom, stagger: 0.06, seed: 81 });
  const caveira = new PaperCutout(L4, { art: ART.caveira(), w: 360, h: 420, x: -200 * u, y: H * 0.40, scale: 0.8 * u, pivot: "center", rot: 14, seed: 4, sway: [2.6, 3, 1] });
  if (V) new PaperCutout(L4, { art: ART.jornal(), w: 1200, h: 260, x: W * 0.5, y: H + 40 * u, scale: u, seed: 13, rot: 2, sway: [4, 1, 0] });
  const confetes = makeConfetti(L4, stage, 18, 900);
  sc.updaters.push((t) => {
    const tq = K.step12(t);
    glow.setAttribute("opacity", (0.2 + 0.65 * bolo.lit(t) / 80).toFixed(3));
    const peek = K.ease.outBack(K.clamp((tq - 7.5) / 0.7), 1.4);
    caveira.o.x = -200 * u + peek * 330 * u;
    caveira.setArt(ART.caveira(tq > 8.4 ? 0.5 + 0.5 * Math.sin(tq * 30) : 0.1, 0, 0.9));
    confetes(t);
  });
  return sc;
};
