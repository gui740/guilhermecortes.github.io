import React, { useId } from "react";
import { staticFile } from "remotion";
import { COR, PELE, TomPele, TRACO } from "../estilo/tokens";

/**
 * Personagem chibi vetorial riggado (viewBox 500x900, pés em y≈880).
 * Cabeça ≈ 43% da altura. Peças trocáveis: olhos, sobrancelhas, boca, braços (pose).
 * O escudo oficial é aplicado por cima do peito liso, na âncora ESCUDO_ANCORA.
 */

export type Olhos = "aberto" | "fechado" | "chocado" | "bravo" | "triste" | "convencido" | "feliz";
export type Boca = "neutra" | "aberta" | "o" | "dentes" | "triste" | "sorriso_lado" | "grito" | "sorriso";
export type Sobrancelha = "normal" | "brava" | "triste" | "erguida" | "convencida";
export type Pose = "baixo" | "cruzados" | "apontando" | "comemorando" | "maos_cabeca" | "ombros" | "segurando" | "martelo" | "acenando" | "aperto" | "suor" | "telefone";
export type Expressao = "neutro" | "boca_aberta" | "olhos_fechados" | "bravo" | "triste" | "chocado" | "convencido" | "comemorando" | "apontando" | "bracos_cruzados";
export type Cabelo = "espetado" | "liso" | "cacheado" | "raspado" | "grisalho" | "penteado";

export type Uniforme = {
  tipo: "liso" | "listras_v" | "listras_h" | "toga" | "terno";
  cores: string[]; // cor(es) da camisa (listras na ordem)
  detalhe: string; // gola/punho
  calcao: string;
  meiao: string;
  meiaoFaixa?: string;
  escudo?: string; // caminho em public/
  gravata?: string;
};

export const PRESETS: Record<Expressao, { olhos: Olhos; boca: Boca; sobr: Sobrancelha; pose: Pose }> = {
  neutro: { olhos: "aberto", boca: "neutra", sobr: "normal", pose: "baixo" },
  boca_aberta: { olhos: "aberto", boca: "aberta", sobr: "normal", pose: "baixo" },
  olhos_fechados: { olhos: "fechado", boca: "neutra", sobr: "normal", pose: "baixo" },
  bravo: { olhos: "bravo", boca: "dentes", sobr: "brava", pose: "baixo" },
  triste: { olhos: "triste", boca: "triste", sobr: "triste", pose: "baixo" },
  chocado: { olhos: "chocado", boca: "grito", sobr: "erguida", pose: "maos_cabeca" },
  convencido: { olhos: "convencido", boca: "sorriso_lado", sobr: "convencida", pose: "cruzados" },
  comemorando: { olhos: "feliz", boca: "grito", sobr: "erguida", pose: "comemorando" },
  apontando: { olhos: "bravo", boca: "aberta", sobr: "brava", pose: "apontando" },
  bracos_cruzados: { olhos: "convencido", boca: "neutra", sobr: "convencida", pose: "cruzados" },
};

/** Âncora do escudo no peito (coordenadas do viewBox) e tamanho. */
export const ESCUDO_ANCORA = { x: 296, y: 478, tam: 58 };

export type ChibiProps = {
  uniforme: Uniforme;
  pele?: TomPele;
  cabelo?: Cabelo;
  corCabelo?: string;
  expressao?: Expressao;
  olhos?: Olhos; // sobrescreve (piscada)
  boca?: Boca; // sobrescreve (lip-sync)
  sobrancelha?: Sobrancelha;
  pose?: Pose;
  altura?: number; // px na tela
  espelhar?: boolean;
  /** -1..1: inclinação leve da cabeça (respiração/reação) */
  cabeca?: number;
  /** objeto na mão (pose segurando/martelo) */
  objeto?: React.ReactNode;
  style?: React.CSSProperties;
};

const O = COR.contorno;

/* ----------------------------------------------------------- partes */

const Mao: React.FC<{ x: number; y: number; pele: { base: string; sombra: string }; r?: number }> = ({ x, y, pele, r = 23 }) => (
  <g>
    <circle cx={x} cy={y} r={r} fill={pele.base} stroke={O} strokeWidth={TRACO} />
    <path d={`M${x - r * 0.55} ${y + r * 0.35} A${r * 0.8} ${r * 0.8} 0 0 0 ${x + r * 0.55} ${y + r * 0.35}`} stroke={pele.sombra} strokeWidth={5} fill="none" strokeLinecap="round" />
  </g>
);

/** Braço: ombro → cotovelo → mão; manga da camisa no primeiro trecho. */
const Braco: React.FC<{ pts: [number, number][]; manga: string; punho: string; pele: { base: string; sombra: string }; mangaComprida?: boolean }> = ({ pts, manga, punho, pele, mangaComprida }) => {
  const [a, b, c] = pts;
  const m = mangaComprida ? c : ([a[0] + (b[0] - a[0]) * 0.75, a[1] + (b[1] - a[1]) * 0.75] as [number, number]);
  const pele1 = `M${m[0]} ${m[1]} L${b[0]} ${b[1]} L${c[0]} ${c[1]}`;
  const manga1 = mangaComprida ? `M${a[0]} ${a[1]} L${b[0]} ${b[1]} L${c[0]} ${c[1]}` : `M${a[0]} ${a[1]} L${m[0]} ${m[1]}`;
  return (
    <g>
      <path d={`M${a[0]} ${a[1]} L${b[0]} ${b[1]} L${c[0]} ${c[1]}`} stroke={O} strokeWidth={36 + TRACO * 2} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      {!mangaComprida && <path d={pele1} stroke={pele.base} strokeWidth={34} strokeLinecap="round" strokeLinejoin="round" fill="none" />}
      <path d={manga1} stroke={manga} strokeWidth={42} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      {!mangaComprida && (() => {
        const L = Math.hypot(m[0] - a[0], m[1] - a[1]) || 1;
        const ux = (m[0] - a[0]) / L, uy = (m[1] - a[1]) / L;
        return <path d={`M${m[0] - ux * 9} ${m[1] - uy * 9} L${m[0]} ${m[1]}`} stroke={punho} strokeWidth={44} strokeLinecap="butt" />;
      })()}
      <Mao x={c[0]} y={c[1]} pele={pele} />
    </g>
  );
};

/** Pontos dos braços por pose: [esquerdo, direito] (esquerdo = lado esquerdo da tela). */
const POSES: Record<Pose, { e: [number, number][]; d: [number, number][]; frente?: boolean }> = {
  baixo: { e: [[158, 430], [126, 520], [132, 600]], d: [[342, 430], [374, 520], [368, 600]] },
  cruzados: { e: [[158, 430], [150, 540], [300, 540]], d: [[342, 430], [350, 545], [205, 548]], frente: true },
  apontando: { e: [[158, 430], [126, 520], [132, 600]], d: [[342, 430], [420, 440], [492, 405]] },
  comemorando: { e: [[158, 430], [92, 330], [70, 215]], d: [[342, 430], [408, 330], [430, 215]] },
  maos_cabeca: { e: [[158, 430], [96, 410], [118, 330]], d: [[342, 430], [404, 410], [382, 330]], frente: true },
  ombros: { e: [[158, 430], [90, 470], [72, 390]], d: [[342, 430], [410, 470], [428, 390]] },
  segurando: { e: [[158, 430], [140, 520], [212, 560]], d: [[342, 430], [360, 520], [288, 560]], frente: true },
  martelo: { e: [[158, 430], [126, 520], [132, 600]], d: [[342, 430], [416, 380], [430, 280]] },
  acenando: { e: [[158, 430], [126, 520], [132, 600]], d: [[342, 430], [420, 360], [440, 250]] },
  aperto: { e: [[158, 430], [126, 520], [132, 600]], d: [[342, 430], [420, 500], [520, 520]] },
  suor: { e: [[158, 430], [126, 520], [132, 600]], d: [[342, 430], [400, 300], [330, 170]], frente: true },
  telefone: { e: [[158, 430], [126, 520], [132, 600]], d: [[342, 430], [420, 400], [420, 300]], frente: true },
};

const OlhoUm: React.FC<{ cx: number; tipo: Olhos; lado: -1 | 1; id: string }> = ({ cx, tipo, lado, id }) => {
  const cy = 278;
  if (tipo === "fechado")
    return <path d={`M${cx - 36} ${cy + 4} Q${cx} ${cy + 26} ${cx + 36} ${cy + 4}`} stroke={O} strokeWidth={10} fill="none" strokeLinecap="round" />;
  if (tipo === "feliz")
    return <path d={`M${cx - 34} ${cy + 14} Q${cx} ${cy - 26} ${cx + 34} ${cy + 14}`} stroke={O} strokeWidth={11} fill="none" strokeLinecap="round" />;
  const rx = tipo === "chocado" ? 44 : 39;
  const ry = tipo === "chocado" ? 52 : 47;
  const iris = tipo === "chocado" ? 0.55 : 0.8;
  const clip = `olho-${id}-${lado}`;
  // pálpebra que corta o olho conforme a emoção
  const corte =
    tipo === "bravo"
      ? `M${cx - 60} ${cy - 70} L${cx + 60} ${cy - 70} L${cx + 60} ${lado === -1 ? cy - 4 : cy - 34} L${cx - 60} ${lado === -1 ? cy - 34 : cy - 4} Z`
      : tipo === "triste"
        ? `M${cx - 60} ${cy - 70} L${cx + 60} ${cy - 70} L${cx + 60} ${lado === -1 ? cy - 40 : cy - 12} L${cx - 60} ${lado === -1 ? cy - 12 : cy - 40} Z`
        : tipo === "convencido"
          ? `M${cx - 60} ${cy - 70} L${cx + 60} ${cy - 70} L${cx + 60} ${cy - 2} L${cx - 60} ${cy - 2} Z`
          : null;
  const ix = cx + (tipo === "convencido" ? lado * -6 : 0);
  return (
    <g>
      <defs>
        <clipPath id={clip}>
          <ellipse cx={cx} cy={cy} rx={rx} ry={ry} />
        </clipPath>
        <radialGradient id={`${clip}-iris`} cx="50%" cy="38%" r="60%">
          <stop offset="0" stopColor="#8A5A34" />
          <stop offset="0.6" stopColor="#4A2A16" />
          <stop offset="1" stopColor="#24130A" />
        </radialGradient>
      </defs>
      <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="#FFFFFF" />
      <g clipPath={`url(#${clip})`}>
        <ellipse cx={cx} cy={cy - ry * 0.45} rx={rx * 1.1} ry={ry * 0.5} fill="#DCE3F2" />
        <ellipse cx={ix} cy={cy + 6} rx={30 * iris} ry={38 * iris} fill={`url(#${clip}-iris)`} />
        <ellipse cx={ix} cy={cy + 8} rx={15 * iris} ry={19 * iris} fill="#120A06" />
        <circle cx={ix + 11 * iris} cy={cy - 10 * iris} r={11 * iris} fill="#FFFFFF" />
        <circle cx={ix - 10 * iris} cy={cy + 18 * iris} r={5 * iris} fill="#FFFFFF" opacity={0.9} />
        {corte && <path d={corte} fill={O} />}
      </g>
      <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="none" stroke={O} strokeWidth={TRACO} />
      {/* cílio superior grosso */}
      {!corte && <path d={`M${cx - rx - 2} ${cy - 6} Q${cx} ${cy - ry - 16} ${cx + rx + 2} ${cy - 6}`} stroke={O} strokeWidth={11} fill="none" strokeLinecap="round" />}
    </g>
  );
};

const Sobrancelhas: React.FC<{ tipo: Sobrancelha; cor: string }> = ({ tipo, cor }) => {
  const s = (cx: number, lado: -1 | 1) => {
    const y = 208;
    let a = 0;
    let dy = 0;
    if (tipo === "brava") { a = lado * 18; dy = 6; }
    if (tipo === "triste") { a = lado * -16; dy = -2; }
    if (tipo === "erguida") { dy = -18; }
    if (tipo === "convencida") { a = lado === -1 ? 8 : -6; dy = lado === -1 ? 4 : -8; }
    return (
      <g key={lado} transform={`rotate(${a} ${cx} ${y + dy})`}>
        <path d={`M${cx - 34} ${y + dy + 6} Q${cx} ${y + dy - 10} ${cx + 34} ${y + dy + 6}`} stroke={cor} strokeWidth={15} fill="none" strokeLinecap="round" />
      </g>
    );
  };
  return <g>{[s(178, -1), s(322, 1)]}</g>;
};

const BocaUm: React.FC<{ tipo: Boca }> = ({ tipo }) => {
  const x = 250;
  const y = 352;
  const lingua = "#E86A6A";
  const dentro = "#5A1414";
  switch (tipo) {
    case "neutra":
      return <path d={`M${x - 20} ${y - 2} Q${x} ${y + 12} ${x + 20} ${y - 2}`} stroke={O} strokeWidth={8} fill="none" strokeLinecap="round" />;
    case "sorriso":
      return (
        <g>
          <path d={`M${x - 34} ${y - 8} Q${x} ${y + 34} ${x + 34} ${y - 8} Z`} fill={dentro} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
          <path d={`M${x - 26} ${y - 4} L${x + 26} ${y - 4}`} stroke="#fff" strokeWidth={8} />
        </g>
      );
    case "aberta":
      return (
        <g>
          <path d={`M${x - 26} ${y - 8} Q${x} ${y - 14} ${x + 26} ${y - 8} Q${x + 24} ${y + 30} ${x} ${y + 32} Q${x - 24} ${y + 30} ${x - 26} ${y - 8} Z`} fill={dentro} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
          <ellipse cx={x} cy={y + 20} rx={14} ry={8} fill={lingua} />
        </g>
      );
    case "o":
      return <ellipse cx={x} cy={y + 6} rx={14} ry={18} fill={dentro} stroke={O} strokeWidth={TRACO} />;
    case "grito":
      return (
        <g>
          <path d={`M${x - 36} ${y - 12} Q${x} ${y - 22} ${x + 36} ${y - 12} Q${x + 34} ${y + 44} ${x} ${y + 48} Q${x - 34} ${y + 44} ${x - 36} ${y - 12} Z`} fill={dentro} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
          <path d={`M${x - 28} ${y - 10} Q${x} ${y - 16} ${x + 28} ${y - 10} L${x + 26} ${y} Q${x} ${y - 6} ${x - 26} ${y} Z`} fill="#fff" />
          <ellipse cx={x} cy={y + 32} rx={18} ry={10} fill={lingua} />
        </g>
      );
    case "dentes":
      return (
        <g>
          <rect x={x - 36} y={y - 12} width={72} height={32} rx={12} fill="#fff" stroke={O} strokeWidth={TRACO} />
          <path d={`M${x - 36} ${y + 4} L${x + 36} ${y + 4} M${x - 12} ${y - 12} L${x - 12} ${y + 20} M${x + 12} ${y - 12} L${x + 12} ${y + 20}`} stroke={O} strokeWidth={4} />
        </g>
      );
    case "triste":
      return <path d={`M${x - 24} ${y + 12} Q${x} ${y - 10} ${x + 24} ${y + 12}`} stroke={O} strokeWidth={8} fill="none" strokeLinecap="round" />;
    case "sorriso_lado":
      return <path d={`M${x - 22} ${y + 2} Q${x + 6} ${y + 14} ${x + 30} ${y - 12}`} stroke={O} strokeWidth={8} fill="none" strokeLinecap="round" />;
  }
};

const CabeloUm: React.FC<{ tipo: Cabelo; cor: string; frente: boolean }> = ({ tipo, cor, frente }) => {
  const brilho = "rgba(255,255,255,0.22)";
  if (!frente) {
    // volume de trás (atrás da cabeça)
    if (tipo === "raspado" || tipo === "grisalho") return null;
    return <path d="M62 250 Q60 70 250 52 Q440 70 438 250 Q440 300 420 320 L80 320 Q60 300 62 250 Z" fill={cor} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />;
  }
  switch (tipo) {
    case "espetado":
      return (
        <g>
          <path d="M70 230 Q62 110 150 70 L140 30 L200 62 L222 14 L262 58 L312 18 L322 70 L388 44 L372 100 Q440 140 430 232 Q400 168 340 160 Q300 190 250 150 Q200 186 160 158 Q100 170 70 230 Z" fill={cor} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
          <path d="M160 92 Q210 70 250 82 Q205 96 170 120 Z" fill={brilho} />
        </g>
      );
    case "liso":
      return (
        <g>
          <path d="M68 236 Q58 84 250 60 Q442 84 432 236 Q410 150 320 132 Q240 196 120 168 Q86 190 68 236 Z" fill={cor} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
          <path d="M300 82 Q360 92 392 140 Q350 112 300 100 Z" fill={brilho} />
        </g>
      );
    case "cacheado":
      return (
        <g>
          {[[110, 140], [160, 92], [222, 70], [288, 70], [348, 94], [396, 142], [86, 206], [416, 206]].map(([x, y], i) => (
            <circle key={i} cx={x} cy={y} r={52} fill={cor} stroke={O} strokeWidth={TRACO} />
          ))}
          <path d="M80 220 Q120 150 250 150 Q380 150 420 220 Q400 130 250 110 Q100 130 80 220 Z" fill={cor} />
        </g>
      );
    case "raspado":
      return <path d="M74 220 Q70 82 250 66 Q430 82 426 220 Q380 140 250 134 Q120 140 74 220 Z" fill={cor} opacity={0.85} stroke={O} strokeWidth={4} />;
    case "grisalho":
      return (
        <g>
          <path d="M66 270 Q60 190 100 170 Q110 230 104 290 Z" fill={cor} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
          <path d="M434 270 Q440 190 400 170 Q390 230 396 290 Z" fill={cor} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
        </g>
      );
    case "penteado":
      return (
        <g>
          <path d="M68 232 Q60 76 250 58 Q442 76 432 232 Q420 130 300 120 Q330 150 300 160 Q220 120 130 150 Q90 170 68 232 Z" fill={cor} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
          <path d="M150 96 Q220 76 280 86 Q220 100 170 118 Z" fill={brilho} />
        </g>
      );
  }
};

/* ----------------------------------------------------------- personagem */

export const Chibi: React.FC<ChibiProps> = ({
  uniforme: u,
  pele = "clara",
  cabelo = "espetado",
  corCabelo = "#3A2418",
  expressao = "neutro",
  olhos,
  boca,
  sobrancelha,
  pose,
  altura = 900,
  espelhar,
  cabeca = 0,
  objeto,
  style,
}) => {
  const id = useId().replace(/:/g, "");
  const p = PELE[pele];
  const pr = PRESETS[expressao];
  const ol = olhos ?? pr.olhos;
  const bo = boca ?? pr.boca;
  const so = sobrancelha ?? pr.sobr;
  const po = pose ?? pr.pose;
  const arms = POSES[po];
  const toga = u.tipo === "toga";
  const terno = u.tipo === "terno";
  const corManga = u.cores[0];
  const torso = "M152 444 Q150 404 204 398 L296 398 Q350 404 348 444 L360 606 Q362 646 320 646 L180 646 Q138 646 140 606 Z";
  const torsoToga = "M140 440 Q140 400 204 396 L296 396 Q360 400 360 440 L392 760 Q394 790 364 790 L136 790 Q106 790 108 760 Z";
  const cBraco = (pts: [number, number][]) => <Braco pts={pts} manga={corManga} punho={u.detalhe} pele={p} mangaComprida={toga || terno} />;

  const pernas = (
    <g>
      {[[190, 1], [272, -1]].map(([x]) => (
        <g key={x}>
          <rect x={x} y={700} width={40} height={110} rx={16} fill={p.base} stroke={O} strokeWidth={TRACO} />
          {!toga && !terno && (
            <>
              <rect x={x - 4} y={760} width={48} height={84} rx={14} fill={u.meiao} stroke={O} strokeWidth={TRACO} />
              {u.meiaoFaixa && <rect x={x - 4} y={772} width={48} height={12} fill={u.meiaoFaixa} />}
            </>
          )}
          {terno && <rect x={x - 6} y={700} width={52} height={140} rx={14} fill={u.calcao} stroke={O} strokeWidth={TRACO} />}
          <path d={`M${x - 14} ${878} Q${x - 18} ${836} ${x + 20} ${832} Q${x + 58} ${836} ${x + 62} ${862} Q${x + 64} ${880} ${x + 44} ${880} Z`} fill="#16161C" stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
          <path d={`M${x - 2} ${846} Q${x + 14} ${838} ${x + 34} ${842}`} stroke="rgba(255,255,255,0.35)" strokeWidth={5} fill="none" strokeLinecap="round" />
        </g>
      ))}
    </g>
  );

  const calcao = !toga && (
    <g>
      <path d="M146 630 L354 630 L366 714 Q367 726 352 726 L266 726 L250 692 L234 726 L148 726 Q133 726 134 714 Z" fill={u.calcao} stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
      <path d="M146 630 L180 630 L170 726 L148 726 Q133 726 134 714 Z" fill={COR.sombra} />
    </g>
  );

  const padrao = () => {
    if (u.tipo === "listras_v") {
      const n = 9;
      return Array.from({ length: n }).map((_, i) => <rect key={i} x={130 + i * 28} y={390} width={28} height={262} fill={u.cores[i % u.cores.length]} />);
    }
    if (u.tipo === "listras_h") {
      return Array.from({ length: 8 }).map((_, i) => <rect key={i} x={120} y={398 + i * 32} width={260} height={32} fill={u.cores[i % u.cores.length]} />);
    }
    return <rect x={100} y={380} width={300} height={430} fill={u.cores[0]} />;
  };

  const corpo = (
    <g>
      <defs>
        <clipPath id={`torso-${id}`}>
          <path d={toga ? torsoToga : torso} />
        </clipPath>
      </defs>
      <g clipPath={`url(#torso-${id})`}>
        {padrao()}
        {terno && (
          <g>
            <path d="M206 398 L250 520 L294 398 Z" fill="#FFFFFF" />
            <path d="M240 420 L260 420 L266 520 L250 548 L234 520 Z" fill={u.gravata ?? "#B22"} stroke={O} strokeWidth={4} />
            <path d="M204 398 L250 520 L224 560 L176 420 Z M296 398 L250 520 L276 560 L324 420 Z" fill={u.cores[0]} stroke={O} strokeWidth={4} />
          </g>
        )}
        {/* sombra cel do lado esquerdo + aro de luz quente na direita */}
        <path d={toga ? "M100 390 L196 390 Q170 560 190 800 L100 800 Z" : "M120 390 L196 390 Q176 520 192 660 L120 660 Z"} fill={COR.sombra} />
        <path d={toga ? "M352 420 Q372 600 386 790" : "M346 430 Q356 520 356 630"} stroke={COR.aro} strokeWidth={9} fill="none" strokeLinecap="round" opacity={0.85} />
      </g>
      <path d={toga ? torsoToga : torso} fill="none" stroke={O} strokeWidth={TRACO} strokeLinejoin="round" />
      {!toga && !terno && (
        <g>
          <path d="M204 400 L250 450 L296 400" stroke={O} strokeWidth={22} fill="none" strokeLinejoin="round" strokeLinecap="round" />
          <path d="M204 400 L250 450 L296 400" stroke={u.detalhe} strokeWidth={12} fill="none" strokeLinejoin="round" strokeLinecap="round" />
          <path d="M146 618 Q250 632 354 618" stroke={u.detalhe} strokeWidth={7} fill="none" opacity={0.9} />
        </g>
      )}
      {toga && <path d="M206 398 L250 470 L294 398" stroke="#FFFFFF" strokeWidth={14} fill="none" strokeLinejoin="round" />}
      {u.escudo && !toga && !terno && (
        <image href={staticFile(u.escudo)} x={ESCUDO_ANCORA.x - ESCUDO_ANCORA.tam / 2} y={ESCUDO_ANCORA.y - ESCUDO_ANCORA.tam / 2} width={ESCUDO_ANCORA.tam} height={ESCUDO_ANCORA.tam} preserveAspectRatio="xMidYMid meet" />
      )}
    </g>
  );

  const cabecaG = (
    <g transform={`rotate(${cabeca * 5} 250 400)`}>
      <CabeloUm tipo={cabelo} cor={corCabelo} frente={false} />
      {/* orelhas */}
      <ellipse cx={70} cy={286} rx={26} ry={34} fill={p.base} stroke={O} strokeWidth={TRACO} />
      <ellipse cx={430} cy={286} rx={26} ry={34} fill={p.base} stroke={O} strokeWidth={TRACO} />
      <defs>
        <clipPath id={`rosto-${id}`}>
          <ellipse cx={250} cy={252} rx={182} ry={170} />
        </clipPath>
      </defs>
      <ellipse cx={250} cy={252} rx={182} ry={170} fill={p.base} />
      <g clipPath={`url(#rosto-${id})`}>
        <path d="M60 140 Q120 240 120 300 Q130 380 230 430 L40 430 Z" fill={p.sombra} opacity={0.55} />
        <path d="M410 150 Q440 250 404 360" stroke={COR.aro} strokeWidth={10} fill="none" strokeLinecap="round" opacity={0.8} />
      </g>
      <ellipse cx={250} cy={252} rx={182} ry={170} fill="none" stroke={O} strokeWidth={TRACO} />
      {/* bochechas */}
      <ellipse cx={148} cy={330} rx={26} ry={14} fill="#FF8A8A" opacity={0.45} />
      <ellipse cx={352} cy={330} rx={26} ry={14} fill="#FF8A8A" opacity={0.45} />
      <OlhoUm cx={178} tipo={ol} lado={-1} id={id} />
      <OlhoUm cx={322} tipo={ol} lado={1} id={id} />
      <Sobrancelhas tipo={so} cor={cabelo === "grisalho" ? "#8A8A8A" : corCabelo} />
      <path d="M244 318 Q250 324 256 318" stroke={p.sombra} strokeWidth={5} fill="none" strokeLinecap="round" />
      <BocaUm tipo={bo} />
      <CabeloUm tipo={cabelo} cor={corCabelo} frente />
    </g>
  );

  const larg = altura * (500 / 900);
  return (
    <svg width={larg} height={altura} viewBox="0 0 500 900" style={{ overflow: "visible", transform: espelhar ? "scaleX(-1)" : undefined, ...style }}>
      {pernas}
      {calcao}
      {!arms.frente && cBraco(arms.e)}
      {!arms.frente && cBraco(arms.d)}
      {corpo}
      {/* pescoço sob a cabeça */}
      <rect x={226} y={386} width={48} height={30} fill={p.sombra} />
      {cabecaG}
      {arms.frente && cBraco(arms.e)}
      {arms.frente && cBraco(arms.d)}
      {objeto}
    </svg>
  );
};

/* ----------------------------------------------------------- elenco deste canal */

export const ELENCO: Record<string, Omit<ChibiProps, "expressao">> = {
  LUSA: {
    uniforme: { tipo: "liso", cores: ["#D7262E"], detalhe: "#138A44", calcao: "#FFFFFF", meiao: "#D7262E", meiaoFaixa: "#138A44", escudo: "escudos/portuguesa.png" },
    pele: "clara", cabelo: "espetado", corCabelo: "#3A2418",
  },
  FLU: {
    uniforme: { tipo: "listras_v", cores: ["#7A1A34", "#FFFFFF", "#0E6B3E", "#FFFFFF"], detalhe: "#FFFFFF", calcao: "#FFFFFF", meiao: "#FFFFFF", meiaoFaixa: "#7A1A34", escudo: "escudos/fluminense.png" },
    pele: "media", cabelo: "liso", corCabelo: "#24160E",
  },
  FLA: {
    uniforme: { tipo: "listras_h", cores: ["#D11F26", "#121212"], detalhe: "#FFFFFF", calcao: "#FFFFFF", meiao: "#121212", meiaoFaixa: "#D11F26", escudo: "escudos/flamengo.png" },
    pele: "morena", cabelo: "cacheado", corCabelo: "#1B110B",
  },
  GREMIO: {
    uniforme: { tipo: "listras_v", cores: ["#1A8AD0", "#121212", "#FFFFFF", "#121212"], detalhe: "#FFFFFF", calcao: "#121212", meiao: "#FFFFFF", meiaoFaixa: "#1A8AD0", escudo: "escudos/gremio.png" },
    pele: "clara", cabelo: "raspado", corCabelo: "#6B4A2E",
  },
  JUIZ: {
    uniforme: { tipo: "toga", cores: ["#18181E"], detalhe: "#18181E", calcao: "#18181E", meiao: "#18181E" },
    pele: "clara", cabelo: "grisalho", corCabelo: "#B8B8B8",
  },
  ADVOGADO: {
    uniforme: { tipo: "terno", cores: ["#2E3A55"], detalhe: "#2E3A55", calcao: "#26304A", meiao: "#26304A", gravata: "#A3242C" },
    pele: "escura", cabelo: "penteado", corCabelo: "#1A120C",
  },
};
