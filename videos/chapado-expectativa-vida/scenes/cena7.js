// CENA 7 — LADO RUIM: coração e cérebro pulsando, "58% -> 74%", idoso procurando a chave que flutua atrás dele.
SCENES.cena7 = function (stage, cfg) {
  const sc = new Scene(stage, cfg);
  const { W, H, u } = stage, P = PALETA, cx = stage.cx;
  const [L0, L1, L2, L3, L4] = sc.layers([0.02, 0.3, 0.6, 0.8, 1.0]);
  new PaperBackground(stage, L0, 10, P.tinta);
  new Sunburst(stage, L0, { x: cx, y: H * 0.35, color: P.tomate, opacity: 0.5, speed: 7 });
  new PaperCutout(L1, { art: tornBlob(900, 640, 14, P.papel), w: 900, h: 640, x: cx, y: H * 0.30, scale: u, pivot: "center", seed: 4, rot: -3, t0: 0.1 });
  const cor = new PaperCutout(L2, { art: ART.coracao(), w: 340, h: 400, x: W * 0.28, y: H * 0.31, scale: 0.95 * u, pivot: "center", seed: 7, t0: 0.4, rot: -8 });
  const cer = new PaperCutout(L2, { art: ART.cerebro(), w: 380, h: 300, x: W * 0.66, y: H * 0.28, scale: 0.95 * u, pivot: "center", seed: 8, t0: 0.9, rot: 6 });
  new RansomText(L3, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.78, text: "58%", x: W * 0.24, y: H * 0.50, size: 110 * u, t0: 4.6, stagger: 0.08, seed: 71 });
  const seta = new PaperCutout(L3, { art: `<path d="M0,30 L120,30 L120,0 L180,50 L120,100 L120,70 L0,70 Z" fill="${P.mostarda}" stroke="${INK()}" stroke-width="6"/>`, w: 180, h: 100, x: W * 0.45, y: H * 0.50, scale: 0.8 * u, pivot: "center", seed: 10, t0: 5.4, rot: 0 });
  const num = new AnimatedNumber(L3, { x: W * 0.68, y: H * 0.50, size: 170 * u, from: 58, to: 74, dec: 0, suffix: "%", t0: 6.0, dur: 2.0, bg: P.tomate, fg: P.papel, seed: 11 });
  new RansomText(L3, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.78, text: "DAS MORTES", x: cx, y: H * 0.585, size: 62 * u, t0: 8.2, stagger: 0.05, seed: 72 });
  const vo = new PaperCutout(L4, { art: ART.idoso(P.petroleo), w: 240, h: 380, x: W * 0.30, y: H * 0.785, scale: 0.85 * u, seed: 13, t0: 10.6, sway: [2.4, 5, 0] });
  const chave = new PaperCutout(L4, { art: ART.chave(), w: 200, h: 90, x: W * 0.72, y: H * 0.64, scale: 0.9 * u, pivot: "center", seed: 14, t0: 12.6 });
  sc.updaters.push((t) => {
    const tq = K.step12(t);
    const beat = Math.max(0, Math.sin(tq * 2 * Math.PI * 1.2)) ** 3;
    cor.setArt(ART.coracao(beat));
    const lid = [3.0, 7.4, 13.2].reduce((m, b) => (tq >= b && tq < b + 0.3 ? Math.sin(Math.PI * (tq - b) / 0.3) : m), 0);
    cer.setArt(ART.cerebro(beat * 0.6, lid));
    num.update(t);
    // vô procurando: olha pra um lado e pro outro; a chave flutua sempre atrás dele
    const look = Math.sin(tq * 1.4);
    vo.o.x = W * 0.30 + look * 90 * u;
    vo.o.sx = look > 0 ? -1 : 1;
    chave.o.x = vo.o.x + (vo.o.sx === -1 ? 300 : -300) * u;   // sempre do lado contrário de onde ele olha
    chave.o.y = H * 0.64 + Math.sin(tq * 2.3) * 30 * u;
    chave.o.rot = Math.sin(tq * 1.7) * 20;
  });
  // espelhar o vô (olhando pro lado oposto)
  const upd = vo.update.bind(vo);
  vo.update = (t) => upd(t, { sx: vo.o.sx || 1 });
  return sc;
};
