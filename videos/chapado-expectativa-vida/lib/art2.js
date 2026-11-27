// Mais ilustrações de gravura (cenas 2–8). Mesma convenção de ART: caixa indicada no comentário.
Object.assign(ART, {
  // 220 x 260 — bebê de gravura (enrolado em manta)
  bebe(cor = PALETA.rosa) {
    const k = INK();
    return `<path d="M40,140 C30,90 190,90 180,140 L196,226 C200,252 20,252 24,226 Z" fill="${cor}" stroke="${k}" stroke-width="5"/>
      <path d="M40,140 C30,90 190,90 180,140 L196,226 C200,252 20,252 24,226 Z" fill="url(#hatchFino)" opacity="0.35"/>
      <path d="M36,168 C80,190 140,190 186,168" fill="none" stroke="${k}" stroke-width="4"/>
      <circle cx="110" cy="92" r="66" fill="#f6d9b8" stroke="${k}" stroke-width="5"/>
      <path d="M58,120 C70,150 96,158 110,158 L110,158 C80,150 64,132 58,120 Z" fill="url(#hatch)" opacity="0.5"/>
      <path d="M102,30 C96,16 120,12 116,30" fill="none" stroke="${k}" stroke-width="4"/>
      <path d="M78,86 Q88,78 98,86 M122,86 Q132,78 142,86" fill="none" stroke="${k}" stroke-width="4"/>
      <ellipse cx="110" cy="116" rx="12" ry="8" fill="${PALETA.tomate}" stroke="${k}" stroke-width="3"/>
      <circle cx="76" cy="106" r="9" fill="${PALETA.rosa}" opacity="0.7"/><circle cx="144" cy="106" r="9" fill="${PALETA.rosa}" opacity="0.7"/>`;
  },

  // 240 x 380 — idoso de gravura com bengala
  idoso(cor = PALETA.petroleo) {
    const k = INK();
    return `<path d="M70,150 C70,120 170,118 176,150 L196,330 L60,330 Z" fill="${cor}" stroke="${k}" stroke-width="5"/>
      <path d="M150,150 L176,150 L196,330 L160,330 Z" fill="url(#hatch)" opacity="0.5"/>
      <rect x="78" y="326" width="40" height="40" fill="${k}"/><rect x="138" y="326" width="40" height="40" fill="${k}"/>
      <path d="M176,190 L214,250" stroke="${k}" stroke-width="16" stroke-linecap="round"/>
      <path d="M214,240 L222,372" stroke="#8a5a2b" stroke-width="9" stroke-linecap="round"/>
      <path d="M214,240 C214,224 236,224 236,238" fill="none" stroke="#8a5a2b" stroke-width="9" stroke-linecap="round"/>
      <circle cx="122" cy="82" r="56" fill="#f2d3ae" stroke="${k}" stroke-width="5"/>
      <path d="M70,70 C74,30 172,30 176,70 C160,52 86,52 70,70 Z" fill="#fbf7ec" stroke="${k}" stroke-width="4"/>
      <path d="M86,104 C100,140 146,140 160,104 C150,128 96,128 86,104 Z" fill="#fbf7ec" stroke="${k}" stroke-width="4"/>
      <circle cx="102" cy="80" r="15" fill="none" stroke="${k}" stroke-width="4"/><circle cx="142" cy="80" r="15" fill="none" stroke="${k}" stroke-width="4"/>
      <line x1="117" y1="80" x2="127" y2="80" stroke="${k}" stroke-width="4"/>
      <circle cx="102" cy="80" r="4" fill="${k}"/><circle cx="142" cy="80" r="4" fill="${k}"/>
      <path d="M74,96 C80,118 92,126 104,128" fill="none" stroke="url(#hatch)" stroke-width="12" opacity="0.6"/>`;
  },

  // 300 x 300 — vírus de gravura (esfera com espinhos)
  virus(rot = 0) {
    const k = INK(), P = PALETA;
    let sp = "";
    for (let i = 0; i < 14; i++) {
      const a = (i / 14) * 2 * Math.PI + rot;
      const x1 = 150 + Math.cos(a) * 92, y1 = 150 + Math.sin(a) * 92, x2 = 150 + Math.cos(a) * 132, y2 = 150 + Math.sin(a) * 132;
      sp += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${k}" stroke-width="7"/>
        <circle cx="${x2}" cy="${y2}" r="13" fill="${P.tomate}" stroke="${k}" stroke-width="4"/>`;
    }
    return `${sp}<circle cx="150" cy="150" r="96" fill="#9fb59a" stroke="${k}" stroke-width="6"/>
      <circle cx="150" cy="150" r="96" fill="url(#dots)" opacity="0.25"/>
      <path d="M70,190 C90,240 180,250 220,210 C190,236 110,236 70,190 Z" fill="url(#hatch)" opacity="0.6"/>
      <circle cx="120" cy="120" r="14" fill="${P.tomate}" stroke="${k}" stroke-width="3"/>
      <circle cx="180" cy="170" r="10" fill="${P.tomate}" stroke="${k}" stroke-width="3"/>
      <circle cx="160" cy="105" r="8" fill="${P.mostarda}" stroke="${k}" stroke-width="3"/>`;
  },

  // 300 x 300 — globo recortado; rot 0..1 faz os continentes deslizarem (rotação)
  globo(rot = 0) {
    const k = INK(), P = PALETA;
    const cont = [
      "M20,90 C40,60 90,70 100,100 C110,130 80,150 90,180 C70,200 40,170 30,140 Z",
      "M130,60 C170,40 220,60 210,100 C200,120 170,110 160,140 C140,130 120,100 130,60 Z",
      "M150,170 C180,160 210,180 200,220 C190,250 160,250 150,220 Z",
      "M240,120 C270,110 290,140 270,160 C255,170 238,150 240,120 Z",
    ];
    const off = -rot * 300;
    const land = [0, 300].map((dx) => cont.map((d) => `<path d="${d}" transform="translate(${off + dx} 0)" fill="${P.mostarda}" stroke="${k}" stroke-width="4"/>`).join("")).join("");
    return `<defs><clipPath id="gclip"><circle cx="150" cy="150" r="130"/></clipPath></defs>
      <circle cx="150" cy="150" r="130" fill="${P.petroleo}" stroke="${k}" stroke-width="6"/>
      <g clip-path="url(#gclip)">${land}
        <path d="M150,20 A130 130 0 0 1 150,280 A70 130 0 0 0 150,20 Z" fill="url(#hatch)" opacity="0.45"/>
        <ellipse cx="150" cy="150" rx="130" ry="40" fill="none" stroke="${k}" stroke-width="2" opacity="0.5"/>
        <ellipse cx="150" cy="150" rx="50" ry="130" fill="none" stroke="${k}" stroke-width="2" opacity="0.5"/></g>
      <circle cx="150" cy="150" r="130" fill="none" stroke="${k}" stroke-width="6"/>
      <circle cx="105" cy="95" r="22" fill="#fff" opacity="0.25"/>`;
  },

  // 760 x 560 — balança antiga; tilt = inclinação do braço (graus, + = esquerda desce)
  balanca(tilt = 0) {
    const k = INK(), P = PALETA;
    const a = tilt * Math.PI / 180;
    const L = 300, cx = 380, cy = 120;
    const lx = cx - Math.cos(a) * L, ly = cy + Math.sin(a) * L, rx = cx + Math.cos(a) * L, ry = cy - Math.sin(a) * L;
    const pan = (x, y) => `<line x1="${x}" y1="${y}" x2="${x - 90}" y2="${y + 170}" stroke="${k}" stroke-width="4"/>
      <line x1="${x}" y1="${y}" x2="${x + 90}" y2="${y + 170}" stroke="${k}" stroke-width="4"/>
      <path d="M${x - 120},${y + 170} L${x + 120},${y + 170} C${x + 100},${y + 220} ${x - 100},${y + 220} ${x - 120},${y + 170} Z" fill="${P.mostarda}" stroke="${k}" stroke-width="5"/>
      <path d="M${x - 120},${y + 170} L${x + 120},${y + 170} C${x + 100},${y + 220} ${x - 100},${y + 220} ${x - 120},${y + 170} Z" fill="url(#hatch)" opacity="0.4"/>`;
    return `<path d="M330,540 L430,540 L410,500 L350,500 Z" fill="${P.petroleo}" stroke="${k}" stroke-width="5"/>
      <rect x="366" y="130" width="28" height="372" fill="${P.petroleo}" stroke="${k}" stroke-width="5"/>
      <rect x="366" y="130" width="12" height="372" fill="url(#hatch)" opacity="0.5"/>
      ${pan(lx, ly)}${pan(rx, ry)}
      <line x1="${lx}" y1="${ly}" x2="${rx}" y2="${ry}" stroke="${k}" stroke-width="16" stroke-linecap="round"/>
      <line x1="${lx}" y1="${ly}" x2="${rx}" y2="${ry}" stroke="${P.mostarda}" stroke-width="8" stroke-linecap="round"/>
      <circle cx="${cx}" cy="${cy}" r="24" fill="${P.tomate}" stroke="${k}" stroke-width="5"/>
      <path d="M380,96 L370,60 L390,60 Z" fill="${k}"/>`;
  },
  balancaPratos(tilt = 0) {   // posições (na caixa da balança) do centro de cada prato
    const a = tilt * Math.PI / 180;
    return [[380 - Math.cos(a) * 300, 120 + Math.sin(a) * 300 + 170], [380 + Math.cos(a) * 300, 120 - Math.sin(a) * 300 + 170]];
  },

  // 360 x 420 — cabeça de perfil cuja tampa do crânio abre (open 0..1)
  cabeca(open = 0) {
    const k = INK(), P = PALETA;
    const ang = -open * 55;
    return `<path d="M120,150 C100,200 96,250 110,280 L80,320 C76,330 86,338 98,336 L110,334 L112,360 C114,372 130,372 136,364
      L140,380 C150,404 200,410 220,396 L230,420 L330,420 L300,330 C340,280 350,220 340,150 Z" fill="${P.pele}" stroke="${k}" stroke-width="6"/>
      <path d="M260,170 C300,220 300,300 290,340 L320,420 L330,420 L300,330 C340,280 350,220 340,150 Z" fill="url(#hatch)" opacity="0.5"/>
      <circle cx="170" cy="220" r="10" fill="${k}"/>
      <path d="M150,198 Q170,188 190,198" fill="none" stroke="${k}" stroke-width="5"/>
      <path d="M110,334 C126,330 140,326 150,330" fill="none" stroke="${k}" stroke-width="4"/>
      <ellipse cx="230" cy="150" rx="112" ry="20" fill="#3a1d16" stroke="${k}" stroke-width="5"/>
      <g transform="rotate(${ang} 340 150)">
        <path d="M118,150 C110,60 200,20 260,30 C320,40 350,90 342,150 Z" fill="${P.pele}" stroke="${k}" stroke-width="6"/>
        <path d="M118,150 C110,60 200,20 260,30 C220,40 160,80 150,150 Z" fill="#5a3a22" stroke="${k}" stroke-width="5"/>
        <path d="M260,40 C320,50 344,100 340,150 L320,150 C324,110 300,70 260,40 Z" fill="url(#hatch)" opacity="0.5"/>
      </g>`;
  },

  // 140 x 140 — engrenagem
  engrenagem(cor = PALETA.mostarda) {
    const k = INK();
    let p = "";
    for (let i = 0; i < 24; i++) {
      const a = (i / 24) * 2 * Math.PI, r = i % 2 ? 50 : 66;
      const a2 = ((i + 1) / 24) * 2 * Math.PI;
      p += `${70 + Math.cos(a) * r},${70 + Math.sin(a) * r} ${70 + Math.cos(a2) * r},${70 + Math.sin(a2) * r} `;
    }
    return `<polygon points="${p}" fill="${cor}" stroke="${k}" stroke-width="5" stroke-linejoin="round"/>
      <circle cx="70" cy="70" r="20" fill="#fbf7ec" stroke="${k}" stroke-width="5"/>
      <circle cx="70" cy="70" r="50" fill="url(#hatchFino)" opacity="0.3"/>`;
  },

  // 340 x 400 — coração anatômico de gravura; beat 0..1 incha
  coracao(beat = 0) {
    const k = INK(), P = PALETA;
    const s = 1 + beat * 0.08;
    return `<g transform="translate(170 220) scale(${s}) translate(-170 -220)">
      <path d="M130,40 L130,110 M190,30 L190,100 M228,60 L210,118" stroke="${k}" stroke-width="30" stroke-linecap="round"/>
      <path d="M130,40 L130,110 M190,30 L190,100 M228,60 L210,118" stroke="${P.petroleo}" stroke-width="20" stroke-linecap="round"/>
      <path d="M90,130 C40,150 30,230 70,290 C110,350 160,384 180,390 C220,370 290,320 300,250 C312,170 270,110 210,110
        C180,110 160,120 150,126 C130,110 110,116 90,130 Z" fill="${P.tomate}" stroke="${k}" stroke-width="6"/>
      <path d="M90,130 C40,150 30,230 70,290 C100,336 140,368 170,384 C120,330 100,260 120,170 Z" fill="url(#hatch)" opacity="0.5"/>
      <path d="M190,140 C200,200 190,280 180,390" fill="none" stroke="${k}" stroke-width="5"/>
      <path d="M200,180 C230,200 260,190 280,170 M190,250 C220,270 260,260 286,236 M120,200 C140,220 160,214 176,200" fill="none" stroke="${k}" stroke-width="3.5"/>
      <path d="M220,130 C250,140 270,160 280,190" fill="none" stroke="#ffb3a0" stroke-width="6" opacity="0.7"/></g>`;
  },

  // 380 x 300 — cérebro de gravura com um olho no meio (surreal); pulse 0..1, lid 0..1
  cerebro(pulse = 0, lid = 0) {
    const k = INK(), P = PALETA;
    const s = 1 + pulse * 0.05;
    let folds = "";
    const r = K.rng(4);
    for (let i = 0; i < 14; i++) {
      const x = 60 + r() * 260, y = 60 + r() * 170;
      folds += `<path d="M${x},${y} q${20 + r() * 20},${-20 + r() * 40} ${40 + r() * 20},${r() * 20} q${10},${20} ${-10},${30}" fill="none" stroke="${k}" stroke-width="4"/>`;
    }
    return `<g transform="translate(190 150) scale(${s}) translate(-190 -150)">
      <path d="M60,170 C20,140 40,70 100,60 C120,20 200,16 230,44 C280,24 350,60 340,120 C376,150 356,230 300,236
        C280,270 200,280 170,250 C120,276 50,250 60,170 Z" fill="${P.rosa}" stroke="${k}" stroke-width="6"/>
      ${folds}
      <path d="M190,50 C180,120 200,180 186,250" fill="none" stroke="${k}" stroke-width="5"/>
      <path d="M60,170 C70,230 140,262 170,250 C120,240 80,210 70,160 Z" fill="url(#hatch)" opacity="0.5"/>
      <g transform="translate(130 110)">${ART.olho(lid, Math.sin(lid * 3))}</g></g>`;
  },

  // 200 x 90 — chave antiga
  chave() {
    const k = INK(), P = PALETA;
    return `<circle cx="45" cy="45" r="34" fill="${P.mostarda}" stroke="${k}" stroke-width="6"/>
      <circle cx="45" cy="45" r="14" fill="#fbf7ec" stroke="${k}" stroke-width="5"/>
      <rect x="76" y="37" width="118" height="16" fill="${P.mostarda}" stroke="${k}" stroke-width="5"/>
      <rect x="150" y="50" width="14" height="24" fill="${P.mostarda}" stroke="${k}" stroke-width="5"/>
      <rect x="174" y="50" width="14" height="32" fill="${P.mostarda}" stroke="${k}" stroke-width="5"/>`;
  },

  // 230 x 220 — post-it com texto (2 linhas)
  postit(l1, l2 = "", cor = "#f7e36a") {
    const k = INK();
    return `<path d="M0,0 L230,0 L230,190 L200,220 L0,220 Z" fill="${cor}"/>
      <path d="M230,190 L200,190 L200,220 Z" fill="#c9b448"/>
      <text x="115" y="${l2 ? 92 : 118}" text-anchor="middle" font-family="Anton" font-size="${l2 ? 74 : 92}" fill="${k}">${l1}</text>
      ${l2 ? `<text x="115" y="168" text-anchor="middle" font-family="Courier 10 Pitch" font-weight="700" font-size="44" fill="${k}">${l2}</text>` : ""}`;
  },

  // 120 x 40 — fita adesiva
  fita() {
    return `<path d="M4,6 L116,0 L114,34 L2,40 Z" fill="#efe6c8" opacity="0.85"/>
      <path d="M4,6 L8,10 L4,14 L8,18 L4,22 L8,26 L4,30 L8,34 L2,40 M116,0 L112,4 L116,8 L112,12 L116,16 L112,20 L116,24 L112,28 L114,34" fill="none" stroke="#c9bd98" stroke-width="2"/>`;
  },

  // 360 x 200 — nuvem de fumaça ondulada
  fumaca(cor = "#e8e2d4") {
    const k = INK();
    return `<path d="M20,150 C0,110 40,80 70,96 C70,50 130,40 150,76 C170,30 240,34 250,80 C290,60 340,90 320,130
      C350,150 330,190 290,180 C260,200 210,196 190,176 C160,198 100,196 90,170 C60,186 30,176 20,150 Z" fill="${cor}" stroke="${k}" stroke-width="5"/>
      <path d="M70,140 C110,110 150,150 190,130 C220,116 250,140 280,128" fill="none" stroke="${k}" stroke-width="3" opacity="0.6"/>
      <path d="M20,150 C40,170 70,176 90,170 C100,196 160,198 190,176 C140,180 90,170 60,150 Z" fill="url(#hatch)" opacity="0.4"/>`;
  },

  // 900 x 1000 — folha de papel quadriculado (fundo do gráfico)
  folhaGrafico() {
    let g = "";
    for (let x = 60; x <= 860; x += 40) g += `<line x1="${x}" y1="40" x2="${x}" y2="960" stroke="#7fb3bd" stroke-width="${(x - 60) % 200 ? 1.2 : 2.4}"/>`;
    for (let y = 40; y <= 960; y += 40) g += `<line x1="60" y1="${y}" x2="860" y2="${y}" stroke="#7fb3bd" stroke-width="${(y - 40) % 200 ? 1.2 : 2.4}"/>`;
    return `<rect width="900" height="1000" fill="#f8f4e8"/>${g}<line x1="100" y1="0" x2="100" y2="1000" stroke="${PALETA.tomate}" stroke-width="3"/>`;
  },
});
