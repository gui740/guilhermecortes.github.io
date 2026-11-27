// CENA 3 — RESPOSTA: gráfico de barbante e fita sobre papel quadriculado, subindo; post-its; número contando.
SCENES.cena3 = function (stage, cfg) {
  const sc = new Scene(stage, cfg);
  const { W, H, u } = stage, P = PALETA, cx = stage.cx;
  const [L0, L1, L2, L3, L4] = sc.layers([0.02, 0.3, 0.6, 0.8, 1.0]);
  new PaperBackground(stage, L0, 5, P.mostarda);
  new Sunburst(stage, L0, { x: cx, y: H * 0.55, color: "#f2c45a", opacity: 0.6, speed: 4 });
  [[0.1, 0.12], [0.9, 0.35], [0.06, 0.78]].forEach(([x, y], i) => new PaperCutout(L1, { art: ART.estrela([P.tomate, P.petroleo, P.papel][i]), w: 60, h: 60, x: W * x, y: H * y, scale: 1.3 * u, pivot: "center", seed: 70 + i, t0: 0.2 }));
  const g = new StringGraph(L2, { x: cx, y: H * 0.56, scale: 0.86 * u, t0: 0.15 });
  g.notes.push([2010, "74,4", "2010", "#f7e36a", 2.6, 60, -190], [2019, "76,4", "2019", "#9fd8e0", 11.4, -40, -200]);
  const num = new AnimatedNumber(L3, { x: cx, y: H * 0.15, size: 210 * u, from: 74.4, to: 76.6, dec: 1, t0: 0.4, dur: 11, bg: P.papel, fg: P.tomate, seed: 4 });
  sc.updaters.push((t) => num.update(t));
  new RansomText(L3, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.78, text: "ANOS DE VIDA", x: cx, y: H * 0.255, size: 64 * u, t0: 1.0, stagger: 0.05, seed: 44 });
  const aponta = new PaperCutout(L4, { art: ART.maoAponta(), w: 340, h: 170, x: 0, y: 0, scale: 0.9 * u, pivot: "center", rot: 20, seed: 12, t0: 3 });
  sc.updaters.push((t) => {
    g.year = 2010 + 9 * K.ease.inOut(K.clamp((K.step12(t) - 2) / 10));
    const [px, py] = g.screen(g.year);
    aponta.o.x = px - 230 * u; aponta.o.y = py + 150 * u;
  });
  return sc;
};
