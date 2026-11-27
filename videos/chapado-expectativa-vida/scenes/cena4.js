// CENA 4 — PLOT TWIST: o gráfico despenca em 2021; o papel rasga e um vírus de gravura sai do rasgo.
SCENES.cena4 = function (stage, cfg) {
  const sc = new Scene(stage, cfg);
  const { W, H, u } = stage, P = PALETA, cx = stage.cx;
  const [L0, L1, L2, L3, L4] = sc.layers([0.02, 0.3, 0.6, 0.8, 1.0]);
  new PaperBackground(stage, L0, 6, P.tomate);
  new Sunburst(stage, L0, { x: cx, y: H * 0.55, color: "#a8240f", opacity: 0.6, speed: 9 });
  const g = new StringGraph(L2, { x: cx, y: H * 0.56, scale: 0.86 * u });
  g.year = 2019;
  g.notes.push([2010, "74,4", "2010", "#f7e36a", -1, 60, -190], [2019, "76,4", "2019", "#9fd8e0", -1, -40, -200], [2021, "72,8", "2021", "#ff8f7a", 4.8, 120, 120]);
  const T_DROP = 4.4;
  const virus = new PaperCutout(L3, { art: ART.virus(), w: 300, h: 300, x: 0, y: 0, scale: u, pivot: "center", seed: 5, t0: T_DROP + 0.2, sway: [1.6, 6, 0] });
  const num = new AnimatedNumber(L3, { x: cx, y: H * 0.15, size: 210 * u, from: 76.4, to: 72.8, dec: 1, t0: 2.6, dur: 2.0, bg: P.papel, fg: P.tinta, seed: 7 });
  const vig = K.el("rect", { x: -W * 0.2, y: -H * 0.2, width: W * 1.4, height: H * 1.4, fill: "url(#vinhetaVermelha)", opacity: 0 }, L4.el);
  sc.shake = (t) => {
    const dt = t - T_DROP;
    if (dt < 0 || dt > 1.6) return [0, 0];
    const a = 38 * u * Math.exp(-dt * 3);
    return [a * Math.sin(dt * 70), a * Math.cos(dt * 53)];
  };
  sc.updaters.push((t) => {
    const tq = K.step12(t);
    g.year = 2019 + 2 * K.ease.in(K.clamp((tq - 2.4) / 2.0));
    g.tear = K.ease.outBack(K.clamp((tq - T_DROP) / 0.5), 1.5);
    const [px, py] = g.screen(2021);
    const em = K.ease.out(K.clamp((tq - T_DROP - 0.2) / 1.2));
    virus.o.x = px + 40 * u * em; virus.o.y = py + 20 * u - 260 * u * em;
    virus.o.scale = (0.5 + 0.9 * em) * u;
    virus.setArt(ART.virus(tq * 0.8));
    num.update(t);
    vig.setAttribute("opacity", t > T_DROP ? (0.55 + 0.35 * Math.abs(Math.sin(tq * 3))).toFixed(2) : 0);
  });
  return sc;
};
