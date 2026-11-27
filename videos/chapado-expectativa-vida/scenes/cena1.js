// CENA 1 — GANCHO: bolo recortado, velas acendendo sem parar, "45 ANOS" em letras de revista,
// esqueleto de gravura espiando pela borda.
SCENES.cena1 = function (stage, cfg) {
  const sc = new Scene(stage, cfg);
  const { W, H, u } = stage;
  const P = PALETA;
  const V = stage.vertical;
  const L_ = (h, v) => (V ? v : h);           // posição para horizontal / vertical
  const [L0, L1, L2, L3, L4] = sc.layers([0.02, 0.3, 0.6, 0.78, 1.0]);
  new PaperBackground(stage, L0, 3);

  // --- distante: lua com olho, nuvens, estrelas
  const lua = new PaperCutout(L1, { art: ART.lua(), w: 260, h: 260, x: W * L_(0.84, 0.74), y: H * L_(0.22, 0.09), scale: L_(1.1, 0.95) * u, pivot: "center", seed: 2, t0: 0.2 });
  const nuvens = [
    new PaperCutout(L1, { art: ART.nuvem(), w: 320, h: 170, x: W * L_(0.14, 0.2), y: H * L_(0.30, 0.31), scale: 0.95 * u, seed: 5, t0: 0.1 }),
    new PaperCutout(L1, { art: ART.nuvem(), w: 320, h: 170, x: W * L_(0.64, 0.3), y: H * L_(0.17, 0.08), scale: 0.7 * u, seed: 8, t0: 0.35 }),
  ];
  (V ? [[0.12, 0.17, P.mostarda], [0.08, 0.45, P.tomate], [0.80, 0.30, P.mostarda], [0.55, 0.05, P.petroleo], [0.86, 0.62, P.tomate]] : [[0.30, 0.10, P.mostarda], [0.08, 0.55, P.tomate], [0.93, 0.50, P.mostarda], [0.40, 0.33, P.petroleo], [0.72, 0.40, P.tomate]])
    .forEach(([x, y, c], i) => new PaperCutout(L1, { art: ART.estrela(c), w: 60, h: 60, x: W * x, y: H * y, scale: 1.1 * u, pivot: "center", seed: 20 + i, t0: 0.15 + i * 0.12 }));

  // --- meio: bolo com velas (o bolo é um recorte só; as velas ficam dentro dele)
  const pos = [];
  // 45 velas em 4 fileiras em perspectiva sobre o topo elíptico (cx 320, cy 190, rx 270, ry 64)
  [[8, -0.62], [11, -0.22], [12, 0.2], [14, 0.6]].forEach(([n, fy]) => {
    const y = 190 + fy * 64 * 0.92;
    const half = 270 * Math.sqrt(1 - fy * fy) * 0.86;
    for (let i = 0; i < n; i++) pos.push([320 - half + (2 * half * i) / (n - 1), y + Math.sin(i * 1.7) * 3]);
  });
  const rr = K.rng(42);
  const ordem = pos.map((p, i) => [rr(), i]).sort((a, b) => a[0] - b[0]).map((x) => x[1]);
  const tVela = new Array(45);
  ordem.forEach((idx, k) => (tVela[idx] = 0.9 + 6.2 * Math.pow(k / 44, 0.72)));
  const draw = pos.map((p, i) => [p[1], i]).sort((a, b) => a[0] - b[0]).map((x) => x[1]);
  const VS = 0.72;
  const bolo = new PaperCutout(L2, { art: ART.boloGrande(), w: 640, h: 500, x: L_(W * 0.5, stage.cx), y: H * L_(0.80, 0.715), scale: L_(1.12, 1.42) * u, seed: 1, sway: [3.5, 1.4, 0], boil: 1 });
  const boloArt = ART.boloGrande();
  function velas(t) {
    let s = "";
    const tq = K.step12(t);
    for (const i of draw) {
      const p = K.pop(t, tVela[i], 0.35);
      if (p <= 0) continue;
      const [x, y] = pos[i];
      const sv = VS * p;
      s += `<g transform="translate(${x} ${y}) rotate(${K.boil(t, i + 300, 2.5)}) scale(${sv}) translate(-20 -150)">${ART.vela(i % 3 === 0)}</g>`;
      // chama: acende 0,3 s depois; de vez em quando apaga e reacende ("sem parar")
      const lit = tq - tVela[i] - 0.3;
      const cyc = (tq * 0.9 + i * 0.37) % 4.2;
      const off = lit > 1.5 && cyc < 0.25;
      if (lit > 0 && !off) {
        const pf = K.pop(t, tVela[i] + 0.3, 0.3);
        const fl = 0.5 + K.boil(t, i + 500, 0.5);
        s += `<g transform="translate(${x} ${y - 150 * sv + 24 * sv}) scale(${sv * pf * (0.9 + 0.2 * fl)}) translate(-20 -60)">${ART.chama(fl)}</g>`;
      }
    }
    return s;
  }
  // brilho quente das velas
  const glow = K.el("ellipse", { cx: L_(W * 0.5, stage.cx), cy: H * L_(0.40, 0.52), rx: 520 * u, ry: 300 * u, fill: "url(#brilho)", opacity: 0 }, L2.el);
  L2.el.insertBefore(glow, L2.el.firstChild.nextSibling);

  // --- texto: 45 ANOS
  const titulo = new RansomText(L3, { text: L_("45 ANOS", "45\nANOS"), x: L_(W * 0.47, stage.cx), y: H * L_(0.13, 0.21), size: L_(140, 190) * u, t0: 0.5, stagger: 0.1, seed: 7 });

  // --- primeiro plano: esqueleto espiando pela direita, mão óssea na borda, mão apontando, confetes
  const caveira = new PaperCutout(L4, { art: ART.caveira(), w: 360, h: 420, x: W + 40 * u, y: H * L_(0.62, 0.43), scale: L_(1.05, 0.95) * u,
    pivot: "center", rot: -14, seed: 4, sway: [2.6, 3, 1], boil: 1.5 });
  const maoOsso = new PaperCutout(L4, { art: ART.maoOsso(), w: 260, h: 200, x: W - 60 * u, y: H * L_(0.86, 0.56), scale: 0.9 * u,
    pivot: "center", rot: -8, seed: 9, sway: [2.2, 2, 0], t0: 3.8 });
  const aponta = new PaperCutout(L4, { art: ART.maoAponta(), w: 340, h: 170, x: -40 * u, y: H * L_(0.70, 0.66), scale: 1.0 * u,
    pivot: "center", rot: -10, seed: 11, sway: [2.4, 3, 2], t0: 8.4 });
  if (V) {   // pé da tela (faixa da interface do Shorts): só decoração
    new PaperCutout(L4, { art: ART.jornal(), w: 1200, h: 260, x: W * 0.5, y: H + 40 * u, scale: 1.0 * u, seed: 13, rot: -3, sway: [4, 1, 0] });
    new PaperCutout(L4, { art: ART.estrela(P.mostarda), w: 60, h: 60, x: W * 0.16, y: H * 0.87, scale: 1.4 * u, pivot: "center", seed: 31, t0: 0.4 });
    new PaperCutout(L4, { art: ART.confete(P.petroleo), w: 70, h: 30, x: W * 0.78, y: H * 0.88, scale: 1.6 * u, pivot: "center", seed: 33, rot: 25 });
  }
  const confetes = Array.from({ length: 14 }, (_, i) => {
    const r = K.rng(700 + i);
    const c = [P.tomate, P.mostarda, P.petroleo, P.papel][i % 4];
    return { cut: new PaperCutout(L4, { art: ART.confete(c), w: 70, h: 30, x: 0, y: 0, scale: (0.6 + r() * 0.6) * u, pivot: "center", seed: 40 + i }),
      x: r() * W, sp: 60 + r() * 90, ph: r() * 10, rot: r() * 360 };
  });

  sc.updaters.push((t) => {
    const tq = K.step12(t);
    bolo.setArt(boloArt + velas(t));
    const acesas = tVela.filter((tv) => tq > tv + 0.3).length;
    glow.setAttribute("opacity", (0.15 + 0.6 * acesas / 45 + K.boil(t, 77, 0.05)).toFixed(3));
    // lua com olho que pisca
    const blink = [2.2, 5.9, 9.3].some((b) => tq >= b && tq < b + 0.25) ? 1 : 0;
    lua.setArt(ART.lua() + `<g transform="translate(70 90) scale(1)">${ART.olho(blink, Math.sin(t * 0.8))}</g>`);
    nuvens.forEach((n, i) => (n.o.x = (i ? W * L_(0.64, 0.3) : W * L_(0.14, 0.2)) + Math.sin(t * 0.4 + i * 2) * 30 * u));
    // esqueleto: entra espiando aos 3,6 s, ri (mandíbula batendo) e olha para o bolo
    const peek = K.ease.outBack(K.clamp((tq - 3.6) / 0.7), 1.4);
    caveira.o.x = W + 260 * u - peek * L_(450, 400) * u;
    const ri = tq > 4.4 && tq < 6.4;
    const jaw = ri ? 0.5 + 0.5 * Math.sin(tq * 30) : 0.1;
    const lidC = [7.4, 10.6].some((b) => tq >= b && tq < b + 0.25) ? 1 : 0;
    caveira.setArt(ART.caveira(jaw, lidC, -0.9));
    aponta.o.x = -40 * u + K.ease.outBack(K.clamp((tq - 8.4) / 0.5)) * L_(260, 200) * u;
    confetes.forEach((c, i) => {
      const y = ((tq * c.sp + c.ph * 100) % (H * 1.3)) - H * 0.15;
      c.cut.o.x = c.x + Math.sin(tq * 1.5 + c.ph) * 40;
      c.cut.o.y = y;
      c.cut.o.rot = c.rot + tq * 90 * (i % 2 ? 1 : -1);
    });
  });
  return sc;
};
