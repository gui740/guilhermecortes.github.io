// CENA 6 — PENSAMENTO CHAPADO: balança com bebês de um lado e idosos do outro; cabeça que abre e solta engrenagens.
SCENES.cena6 = function (stage, cfg) {
  const sc = new Scene(stage, cfg);
  const { W, H, u } = stage, P = PALETA, cx = stage.cx;
  const [L0, L1, L2, L3, L4] = sc.layers([0.02, 0.3, 0.6, 0.8, 1.0]);
  new PaperBackground(stage, L0, 9, P.mostarda);
  new Sunburst(stage, L0, { x: cx, y: H * 0.45, color: P.petroleo, opacity: 0.35, speed: 14, rays: 26 });
  const cab = new PaperCutout(L1, { art: ART.cabeca(), w: 360, h: 420, x: W * 0.27, y: H * 0.25, scale: 0.75 * u, pivot: "center", seed: 6, t0: 0.3, rot: 6 });
  const gears = [0, 1, 2].map((i) => new PaperCutout(L1, { art: ART.engrenagem([P.tomate, P.petroleo, P.papel][i]), w: 140, h: 140, x: 0, y: 0, scale: (0.6 + i * 0.15) * u, pivot: "center", seed: 80 + i, t0: 2.4 + i * 0.3, sway: [9, 0, 0] }));
  new RansomText(L3, { maxW: (stage.safe.x1 - stage.safe.x0) * 0.78, text: "MAS\nPERA...", x: W * 0.68, y: H * 0.17, size: 110 * u, t0: 0.4, stagger: 0.07, seed: 61 });
  const BX = cx, BY = H * 0.74, BS = 1.12 * u;
  const bal = new PaperCutout(L2, { art: ART.balanca(0), w: 760, h: 560, x: BX, y: BY, scale: BS, seed: 2, sway: [6, 0.5, 0], boil: 0.6 });
  const bebes = [0, 1, 2].map((i) => new PaperCutout(L3, { art: ART.bebe([P.rosa, "#bfe0e6", "#f2d38a"][i]), w: 220, h: 260, x: 0, y: 0, scale: 0.5 * u, seed: 90 + i, t0: 7.4 + i * 0.25 }));
  const idosos = [0, 1].map((i) => new PaperCutout(L3, { art: ART.idoso([P.petroleo, P.tomate][i]), w: 240, h: 380, x: 0, y: 0, scale: 0.46 * u, seed: 95 + i, t0: 6.6 + i * 0.3 }));
  sc.updaters.push((t) => {
    const tq = K.step12(t);
    cab.setArt(ART.cabeca(K.ease.outBack(K.clamp((tq - 1.8) / 0.6), 2)));
    gears.forEach((gr, i) => {
      const u2 = K.clamp((tq - 2.4 - i * 0.3) / 3);
      gr.o.x = W * 0.27 + (60 + i * 90) * u * K.ease.out(u2) - 20 * u;
      gr.o.y = H * 0.17 - (120 + i * 70) * u * K.ease.out(u2) + Math.sin(tq * 2 + i) * 10 * u;
      gr.o.rot = tq * (i % 2 ? -90 : 70);
    });
    // bebês pesam (mortalidade infantil puxa a média) e depois vão saindo -> equilibra
    const leave = (i) => K.clamp((tq - (12.5 + i * 1.2)) / 0.5);
    const nBaby = 3 - [0, 1].reduce((a, i) => a + leave(i), 0);
    const tilt = K.lerp(-2, 15, K.clamp((tq - 7.4) / 1.2)) - (15 - 2) * (3 - nBaby) / 2.2;
    bal.setArt(ART.balanca(tilt));
    const [pl, pr] = ART.balancaPratos(tilt);
    const toScr = (p) => [BX + (p[0] - 380) * BS, BY + (p[1] - 560) * BS];
    const [lx, ly] = toScr(pl), [rx, ry] = toScr(pr);
    bebes.forEach((b, i) => {
      const lv = i < 2 ? leave(i) : 0;
      b.o.x = lx + (i - 1) * 70 * u + lv * 500 * u * (i ? 1 : -1);
      b.o.y = ly - 2 * u - lv * 300 * u;
      b.o.rot = (i - 1) * 8 + lv * 120;
    });
    idosos.forEach((d, i) => { d.o.x = rx + (i - 0.5) * 90 * u; d.o.y = ry - 2 * u; });
  });
  return sc;
};
