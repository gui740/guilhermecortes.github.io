// CENA 5 — RECUPERAÇÃO: o gráfico volta a subir; globo recortado gira com "73,3 ANOS" no mundo.
SCENES.cena5 = function (stage, cfg) {
  const sc = new Scene(stage, cfg);
  const tMundo = K.quando(cfg, "mundo", 5.4), t733 = K.quando(cfg, "setenta", 7.0, 1), t2024 = K.quando(cfg, "dois", 3.4);
  const { W, H, u } = stage, P = PALETA, cx = stage.cx;
  const [L0, L1, L2, L3, L4] = sc.layers([0.02, 0.3, 0.6, 0.8, 1.0]);
  new PaperBackground(stage, L0, 7, P.petroleo);
  new Sunburst(stage, L0, { x: cx, y: H * 0.62, color: "#2f8090", opacity: 0.7, speed: 6 });
  const g = new StringGraph(L1, { x: cx - 30 * u, y: H * 0.25, scale: 0.5 * u, rot: -5 });
  g.year = 2021; g.tear = 1;
  g.notes.push([2021, "72,8", "2021", "#ff8f7a", -1, 120, 120], [2024, "76,6", "2024", "#b6e3a8", t2024, -60, -200]);
  const blob = new PaperCutout(L2, { art: tornBlob(760, 760, 12, P.papel), w: 760, h: 760, x: cx, y: H * 0.66, scale: u, pivot: "center", seed: 8, t0: tMundo - 0.6 });
  const globo = new PaperCutout(L2, { art: ART.globo(0), w: 300, h: 300, x: cx, y: H * 0.66, scale: 1.75 * u, pivot: "center", seed: 3, t0: tMundo - 0.4, sway: [3, 2, 0] });
  new RansomText(L3, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.78, text: "NO MUNDO", x: cx, y: H * 0.43, size: 80 * u, t0: tMundo, stagger: 0.06, seed: 51 });
  const num = new AnimatedNumber(L3, { x: cx - 60 * u, y: H * 0.515, size: 170 * u, from: 60, to: 73.3, dec: 1, t0: t733 - 1.2, dur: 1.4, bg: P.mostarda, fg: P.tinta, seed: 9, rot: 4 });
  new RansomText(L3, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.78, text: "ANOS", x: cx + 280 * u, y: H * 0.52, size: 80 * u, t0: t733 + 0.2, stagger: 0.06, seed: 52 });
  sc.updaters.push((t) => {
    const tq = K.step12(t);
    g.year = 2021 + 3 * K.ease.inOut(K.clamp((tq - 0.4) / 3.0));
    // gráfico começa grande no centro e encolhe para o topo quando o globo entra
    const sh = K.ease.inOut(K.clamp((tq - (tMundo - 1.2)) / 0.9));
    g.o.x = K.lerp(cx, cx - 30 * u, sh); g.o.y = K.lerp(H * 0.52, H * 0.25, sh);
    g.o.scale = K.lerp(0.86, 0.5, sh) * u;
    g.cut.o.x = g.o.x; g.cut.o.y = g.o.y; g.cut.o.scale = g.o.scale;
    globo.setArt(ART.globo((tq * 0.12) % 1));
    num.update(t);
  });
  return sc;
};
