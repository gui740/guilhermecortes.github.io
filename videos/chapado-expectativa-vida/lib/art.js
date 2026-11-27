// Ilustrações estilo gravura/xilogravura, 100% desenhadas em código (SVG).
// Cada função devolve markup desenhado numa caixa (largura x altura) indicada no comentário.
const INK = () => PALETA.tinta;

const ART = {
  // 600 x 470 — bolo de dois andares (sem velas; as velas são recortes separados)
  bolo() {
    const P = PALETA, k = INK();
    const drips = (cx, cy, rx, ry, n, depth, seed) => {
      const r = K.rng(seed);
      let d = `M${cx - rx},${cy} `;
      for (let i = 0; i <= n; i++) {
        const a = Math.PI - (i / n) * Math.PI;
        const x = cx + Math.cos(a) * rx, y = cy + Math.sin(a) * ry;
        const dd = depth * (0.35 + r());
        if (i > 0 && i < n && i % 1 === 0) {
          d += `L${x - 9},${y} Q${x - 9},${y + dd} ${x},${y + dd} Q${x + 9},${y + dd} ${x + 9},${y} `;
        } else d += `L${x},${y} `;
      }
      d += `L${cx + rx},${cy - 2} A${rx} ${ry} 0 0 0 ${cx - rx} ${cy - 2} Z`;
      return d;
    };
    return `
    <ellipse cx="300" cy="452" rx="292" ry="26" fill="#2a1d10" opacity="0.25"/>
    <ellipse cx="300" cy="438" rx="285" ry="34" fill="#f8f3e6" stroke="${k}" stroke-width="5"/>
    <ellipse cx="300" cy="434" rx="245" ry="22" fill="none" stroke="${k}" stroke-width="2" opacity="0.5"/>
    <!-- andar de baixo -->
    <path d="M70,300 L70,420 A230 34 0 0 0 530,420 L530,300 Z" fill="#f4e2bd" stroke="${k}" stroke-width="5"/>
    <path d="M70,300 L70,420 A230 34 0 0 0 530,420 L530,300 Z" fill="url(#hatchFino)" opacity="0.22"/>
    <path d="M420,300 L420,446 A230 34 0 0 0 530,420 L530,300 Z" fill="url(#hatch)" opacity="0.35"/>
    <rect x="70" y="372" width="460" height="22" fill="${P.petroleo}" stroke="${k}" stroke-width="3"/>
    ${Array.from({ length: 11 }, (_, i) => `<circle cx="${95 + i * 41}" cy="${410 + Math.sin(i) * 4}" r="7" fill="${P.mostarda}" stroke="${k}" stroke-width="2.5"/>`).join("")}
    <ellipse cx="300" cy="300" rx="230" ry="36" fill="#fbf2dc" stroke="${k}" stroke-width="5"/>
    <path d="${drips(300, 300, 230, 36, 14, 55, 3)}" fill="${P.tomate}" stroke="${k}" stroke-width="4"/>
    <path d="${drips(300, 300, 230, 36, 14, 55, 3)}" fill="url(#dots)" opacity="0.18"/>
    <!-- andar de cima -->
    <path d="M160,175 L160,292 A140 24 0 0 0 440,292 L440,175 Z" fill="#f7e9cc" stroke="${k}" stroke-width="5"/>
    <path d="M370,175 L370,312 A140 24 0 0 0 440,292 L440,175 Z" fill="url(#hatch)" opacity="0.35"/>
    <rect x="160" y="232" width="280" height="14" fill="${P.mostarda}" stroke="${k}" stroke-width="3"/>
    <ellipse cx="300" cy="175" rx="140" ry="24" fill="#fff8e8" stroke="${k}" stroke-width="5"/>
    <path d="${drips(300, 175, 140, 24, 9, 40, 8)}" fill="${P.rosa}" stroke="${k}" stroke-width="4"/>
    <path d="${drips(300, 175, 140, 24, 9, 40, 8)}" fill="url(#dotsTomate)" opacity="0.35"/>`;
  },

  // 640 x 500 — bolo grande de um andar, topo largo para muitas velas (as velas são desenhadas por cima)
  boloGrande() {
    const P = PALETA, k = INK();
    const r = K.rng(5);
    const cx = 320, cy = 190, rx = 270, ry = 64;
    let drip = `M${cx - rx},${cy} `;
    const n = 18;
    for (let i = 0; i <= n; i++) {
      const a = Math.PI - (i / n) * Math.PI;
      const x = cx + Math.cos(a) * rx, y = cy + Math.sin(a) * ry;
      const dd = 30 + r() * 70;
      if (i > 0 && i < n) drip += `L${x - 11},${y} Q${x - 11},${y + dd} ${x},${y + dd} Q${x + 11},${y + dd} ${x + 11},${y} `;
      else drip += `L${x},${y} `;
    }
    drip += `L${cx + rx},${cy - 2} A${rx} ${ry} 0 0 0 ${cx - rx} ${cy - 2} Z`;
    return `
    <ellipse cx="320" cy="470" rx="312" ry="30" fill="#2a1d10" opacity="0.25"/>
    <ellipse cx="320" cy="456" rx="305" ry="40" fill="#f8f3e6" stroke="${k}" stroke-width="5"/>
    <ellipse cx="320" cy="452" rx="262" ry="26" fill="none" stroke="${k}" stroke-width="2" opacity="0.5"/>
    <path d="M50,190 L50,420 A270 64 0 0 0 590,420 L590,190 Z" fill="#f4e2bd" stroke="${k}" stroke-width="5"/>
    <path d="M50,190 L50,420 A270 64 0 0 0 590,420 L590,190 Z" fill="url(#hatchFino)" opacity="0.18"/>
    <path d="M470,190 L470,474 A270 64 0 0 0 590,420 L590,190 Z" fill="url(#hatch)" opacity="0.35"/>
    <path d="M50,330 A270 64 0 0 0 590,330 L590,356 A270 64 0 0 1 50,356 Z" fill="${P.petroleo}" stroke="${k}" stroke-width="3"/>
    ${Array.from({ length: 13 }, (_, i) => { const a = Math.PI - (i + 0.5) / 13 * Math.PI; return `<circle cx="${320 + Math.cos(a) * 262}" cy="${396 + Math.sin(a) * 60}" r="8" fill="${P.mostarda}" stroke="${k}" stroke-width="2.5"/>`; }).join("")}
    <ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="#fbf2dc" stroke="${k}" stroke-width="5"/>
    <ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="url(#dots)" opacity="0.07"/>
    <path d="${drip}" fill="${P.tomate}" stroke="${k}" stroke-width="4"/>
    <path d="${drip}" fill="url(#dots)" opacity="0.18"/>`;
  },

  // 40 x 150 — vela listrada (base em y=150). A chama é desenhada à parte (ART.chama).
  vela(azul = false) {
    const k = INK();
    return `<rect x="8" y="40" width="24" height="110" rx="4" fill="url(#${azul ? "candyAzul" : "candy"})" stroke="${k}" stroke-width="3.5"/>
      <rect x="22" y="44" width="7" height="102" fill="#fff" opacity="0.35"/>
      <line x1="20" y1="40" x2="20" y2="24" stroke="${k}" stroke-width="3"/>`;
  },

  // chama (caixa 40 x 60, base em y=60); flick = 0..1 para variar a forma
  chama(flick = 0) {
    const w = 13 + flick * 4, h = 46 + flick * 10;
    const top = 60 - h;
    return `<ellipse cx="20" cy="${60 - h * 0.45}" rx="${w * 2.2}" ry="${h * 0.9}" fill="url(#brilho)"/>
      <path d="M20,${top} C${20 + w},${top + h * 0.45} ${20 + w},${60} 20,60 C${20 - w},60 ${20 - w},${top + h * 0.45} 20,${top} Z"
        fill="url(#chama)" stroke="${INK()}" stroke-width="2.5"/>
      <path d="M20,${top + h * 0.45} C${20 + w * 0.45},${top + h * 0.7} ${20 + w * 0.4},60 20,58 C${20 - w * 0.4},58 ${20 - w * 0.45},${top + h * 0.7} 20,${top + h * 0.45} Z" fill="#fffbe0"/>`;
  },

  // 360 x 420 — caveira de gravura (olhos vivos dentro das órbitas). jaw: abertura 0..1, lid: pálpebra 0..1
  caveira(jaw = 0, lid = 0, look = 0) {
    const k = INK(), P = PALETA;
    const eye = (cx) => {
      const ly = lid * 26;
      return `<circle cx="${cx}" cy="178" r="21" fill="#fbf7ec"/>
        <circle cx="${cx + look * 7}" cy="180" r="11" fill="${P.tomate}" stroke="${k}" stroke-width="2"/>
        <circle cx="${cx + look * 7}" cy="180" r="5" fill="${k}"/>
        <circle cx="${cx + look * 7 - 4}" cy="176" r="2.5" fill="#fff"/>
        ${lid > 0.02 ? `<rect x="${cx - 24}" y="154" width="48" height="${ly * 1.9}" fill="#161310"/>` : ""}`;
    };
    return `
    <path d="M180,20 C292,18 342,100 336,190 C333,238 312,262 302,290 L292,330 L68,330 L58,290 C48,262 27,238 24,190 C18,100 68,22 180,20 Z"
      fill="#efe7d3" stroke="${k}" stroke-width="6"/>
    <path d="M60,90 C40,140 36,200 50,250 L80,300 L100,300 C70,250 66,170 92,96 Z" fill="url(#hatch)" opacity="0.6"/>
    <path d="M300,110 C318,150 320,210 306,260 L296,300" fill="none" stroke="url(#hatchFino)" stroke-width="22" opacity="0.55"/>
    <path d="M150,40 L162,72 L150,96 M236,48 L226,80" stroke="${k}" stroke-width="3" fill="none"/>
    <path d="M92,172 C92,138 156,132 160,170 C163,206 140,222 124,220 C100,218 92,198 92,172 Z" fill="#161310"/>
    <path d="M268,172 C268,138 204,132 200,170 C197,206 220,222 236,220 C260,218 268,198 268,172 Z" fill="#161310"/>
    ${eye(126)}${eye(234)}
    <path d="M180,222 L163,264 Q180,274 197,264 Z" fill="#161310"/>
    <rect x="112" y="290" width="136" height="34" fill="#f7f1e1" stroke="${k}" stroke-width="5"/>
    ${Array.from({ length: 6 }, (_, i) => `<line x1="${131 + i * 19.5}" y1="290" x2="${131 + i * 19.5}" y2="324" stroke="${k}" stroke-width="3.5"/>`).join("")}
    <g transform="translate(0 ${jaw * 26}) rotate(${jaw * 6} 180 330)">
      <path d="M82,326 L278,326 L270,372 C262,398 232,412 180,412 C128,412 98,398 90,372 Z" fill="#efe7d3" stroke="${k}" stroke-width="6"/>
      <path d="M90,340 L120,340 L114,400 C100,392 92,380 90,370 Z" fill="url(#hatch)" opacity="0.6"/>
      <rect x="112" y="328" width="136" height="30" fill="#f7f1e1" stroke="${k}" stroke-width="5"/>
      ${Array.from({ length: 6 }, (_, i) => `<line x1="${131 + i * 19.5}" y1="328" x2="${131 + i * 19.5}" y2="358" stroke="${k}" stroke-width="3.5"/>`).join("")}
    </g>`;
  },

  // 260 x 200 — mão de esqueleto agarrando uma borda (dedos curvados para a esquerda)
  maoOsso() {
    const k = INK();
    const bone = (x1, y1, x2, y2, w) => {
      const a = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
      const L = Math.hypot(x2 - x1, y2 - y1);
      return `<g transform="translate(${x1} ${y1}) rotate(${a})">
        <rect x="0" y="${-w / 2}" width="${L}" height="${w}" rx="${w / 2}" fill="#efe7d3" stroke="${k}" stroke-width="4"/>
        <circle cx="${w * 0.35}" cy="0" r="${w * 0.62}" fill="#efe7d3" stroke="${k}" stroke-width="4"/>
        <line x1="${w}" y1="${w * 0.15}" x2="${L - w}" y2="${w * 0.15}" stroke="${k}" stroke-width="1.5" opacity="0.6"/></g>`;
    };
    let s = "";
    [[40, 0], [80, 6], [120, 4], [160, 14]].forEach(([y, dx], i) => {
      const bx = 250, by = 30 + y;
      s += bone(bx, by, 170 - dx, by - 10, 22) + bone(170 - dx, by - 10, 110 - dx, by + 8, 19) + bone(110 - dx, by + 8, 80 - dx, by + 38, 16);
    });
    return s;
  },

  // 340 x 170 — mão apontando (manícula de tipografia antiga)
  maoAponta() {
    const k = INK(), P = PALETA;
    return `
    <rect x="0" y="22" width="78" height="100" fill="#f7f1e1" stroke="${k}" stroke-width="5"/>
    <rect x="0" y="22" width="78" height="100" fill="url(#hatchFino)" opacity="0.5"/>
    <line x1="18" y1="22" x2="18" y2="122" stroke="${k}" stroke-width="3"/>
    <path d="M78,30 L300,30 C334,30 336,64 302,64 L188,64 C206,72 206,96 186,100 C206,104 206,128 184,131
      C200,137 197,158 176,159 L118,160 C92,160 78,142 78,122 Z" fill="${P.pele}" stroke="${k}" stroke-width="5" stroke-linejoin="round"/>
    <path d="M150,64 L188,64 M150,100 L186,100 M146,131 L184,131" stroke="${k}" stroke-width="4"/>
    <path d="M78,90 C110,150 150,150 176,159 L118,160 C92,160 78,142 78,122 Z" fill="url(#hatch)" opacity="0.45"/>
    <path d="M286,36 C296,38 300,46 296,52" stroke="${k}" stroke-width="2.5" fill="none"/>`;
  },

  // 120 x 80 — olho isolado (pálpebra lid 0..1)
  olho(lid = 0, look = 0) {
    const k = INK(), P = PALETA;
    const ly = 40 - 34 + lid * 34;
    return `<path d="M6,40 C30,6 90,6 114,40 C90,74 30,74 6,40 Z" fill="#fbf7ec" stroke="${k}" stroke-width="5"/>
      <circle cx="${60 + look * 14}" cy="40" r="22" fill="${P.petroleo}" stroke="${k}" stroke-width="3"/>
      <circle cx="${60 + look * 14}" cy="40" r="10" fill="${k}"/>
      <circle cx="${53 + look * 14}" cy="33" r="5" fill="#fff"/>
      ${lid > 0.02 ? `<path d="M6,40 C30,6 90,6 114,40 L114,${ly + 6} C90,${ly + 30} 30,${ly + 30} 6,${ly + 6} Z" fill="${P.rosa}" stroke="${k}" stroke-width="5"/>` : ""}
      <path d="M6,40 C30,6 90,6 114,40" fill="none" stroke="${k}" stroke-width="6"/>`;
  },

  // 260 x 260 — lua crescente-cheia de gravura (com retícula)
  lua() {
    const k = INK(), P = PALETA;
    return `<circle cx="130" cy="130" r="120" fill="#f3e3b0" stroke="${k}" stroke-width="5"/>
      <circle cx="130" cy="130" r="120" fill="url(#dots)" opacity="0.12"/>
      <path d="M130,10 A120 120 0 0 1 130,250 A92 120 0 0 0 130,10 Z" fill="url(#hatch)" opacity="0.5"/>
      <circle cx="80" cy="80" r="16" fill="none" stroke="${k}" stroke-width="3"/>
      <circle cx="175" cy="190" r="22" fill="none" stroke="${k}" stroke-width="3"/>
      <circle cx="95" cy="190" r="10" fill="none" stroke="${k}" stroke-width="3"/>`;
  },

  // 320 x 170 — nuvem de gravura
  nuvem() {
    const k = INK();
    return `<path d="M40,140 C10,140 8,96 44,92 C40,56 92,42 112,70 C126,30 190,26 204,66 C230,44 280,60 274,98
      C306,100 312,140 280,142 Z" fill="#fbf7ec" stroke="${k}" stroke-width="5"/>
      <path d="M40,140 C30,128 34,116 52,112 C80,124 240,128 280,120 C298,124 300,138 280,142 Z" fill="url(#hatch)" opacity="0.45"/>`;
  },

  // 60 x 60 — estrela de papel
  estrela(cor) {
    let p = "";
    for (let i = 0; i < 10; i++) {
      const a = -Math.PI / 2 + (i * Math.PI) / 5, r = i % 2 ? 12 : 28;
      p += `${30 + Math.cos(a) * r},${30 + Math.sin(a) * r} `;
    }
    return `<polygon points="${p}" fill="${cor}" stroke="${INK()}" stroke-width="3"/>`;
  },

  // 70 x 30 — tira de confete
  confete(cor) {
    return `<rect x="2" y="4" width="66" height="22" fill="${cor}"/><rect x="2" y="4" width="66" height="22" fill="url(#dots)" opacity="0.15"/>`;
  },
};
