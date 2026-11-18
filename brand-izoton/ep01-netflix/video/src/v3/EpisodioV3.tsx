// EP01 v3 com a narração do Guilherme. Lê timeline_v3.json (pipeline/montar_timeline_v3.py).
// Cenas da v2 entram numa "casca" v3 (grão, câmera em deriva, página editorial); cold open, colagem, fala TED e painel são v3.
import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import timeline from "../timeline_v3.json";
import { C, FAIXA, FONT, MONO } from "../theme";
import { Cena } from "../cenas/Cenas";
import { AcoesCtx } from "../cenas/acoes";
import { Academico } from "../cenas/bits";
import { Camada, Card, Destaque, Grao, PaginaEditorial, Recorte, Terminal } from "./kit";
import { Painel, CAPITULOS, Mascara } from "./transicoes";
import { Colagem, FalaCtx, FalaT04, Sfx } from "./Amostra";
import { ColdOpenV2 } from "./Rodada1";

type Cn = { tipo: string; t: number; [k: string]: any };
type Lat = { t: number; src: string; tipo: "rec" | "card" | "print"; lado: "esq" | "dir"; y: number; grande?: boolean; fim?: number };
type Etq = { t: number; texto: string; lado: "esq" | "dir"; estreita: boolean };
type Tr = { tipo: string; id: string; start: number; dur: number; pre?: number; cenas: Cn[]; audio?: any; regravar?: string | null;
  laterais?: Lat[]; passos?: number[]; etiquetas?: Etq[]; ritmo?: number[];
  comp?: string; de?: number; para?: number; regancho?: string[] | null; titulo?: string };
const TL = timeline as unknown as { trechos: Tr[]; fx: { t: number; som: string; vol?: number }[]; duracao: number };

// capítulo corrente de cada trecho (para a página editorial)
const capDe = (() => {
  const m: Record<string, number> = {}; let cap = 0;
  for (const tr of TL.trechos) { if (tr.tipo === "painel") cap = (tr.para ?? 0) + 1; m[tr.id] = cap; }
  return m;
})();
// trechos com fala (para o ducking dos efeitos)
const FALAS: [number, number][] = TL.trechos.filter((t) => (t.tipo === "narr" && t.audio) || t.tipo === "arq" || (t.tipo === "painel" && t.audio))
  .map((t) => [t.start, t.start + t.dur]);

const Regravar: React.FC<{ bloco: string }> = ({ bloco }) => (
  <div style={{ position: "absolute", left: 40, top: 96, fontFamily: MONO, fontSize: 22, letterSpacing: 3, color: C.branco, background: C.ambar, padding: "6px 12px", zIndex: 50 }}>
    [REGRAVAR · BLOCO {bloco}] silêncio estimado
  </div>
);

// cenas só de tipografia/dado ficam maiores (Passo 3: elementos principais com 50–70% da altura)
const ESCALA: Record<string, number> = { titulo: 1.3, contador: 1.45, pergunta: 1.35, citacao: 1.3, medidor: 1.7, cheque: 1.4, botao: 1.45, pessoas: 1.4,
  anzol: 1.4, fluxo: 1.3, lista: 1.25, aovivo: 1.15, barras: 1.4, mapa: 1.2, envelope: 1.3, logoN: 1.0, cores: 1.15, proibicoes: 1.45, posters: 1.2, colunas: 1.1 };
// transições de entrada entre cenas, em rodízio (nunca a mesma duas vezes seguidas)
const TRANS = ["dir", "circulo", "baixo", "desliza"] as const;
const Entrada: React.FC<{ tipo: typeof TRANS[number]; children: React.ReactNode }> = ({ tipo, children }) => {
  const f = useCurrentFrame();
  if (tipo === "desliza") {
    const k = interpolate(f, [0, 9], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return <AbsoluteFill style={{ transform: `translateX(${(1 - k) * 220}px)`, opacity: k, filter: k < 1 ? `blur(${(1 - k) * 8}px)` : "none" }}>{children}</AbsoluteFill>;
  }
  return <Mascara inicio={0} direcao={tipo}>{children}</Mascara>;
};
let contTrans = 0;
const transDe = (() => { const m: Record<string, number> = {}; for (const tr of TL.trechos) tr.cenas.forEach((c, i) => { if (c.tipo !== "academico") m[`${tr.id}:${i}`] = contTrans++ % TRANS.length; }); return m; })();

/** Câmera em degraus: a cada "passo" (palavra da fala), um pequeno salto de zoom e de posição, com 5 quadros de assentamento. */
// pulso de câmera: até 1,5% de escala, com easing, no começo das palavras (ritmo da fala, nunca metrônomo);
// desligado nas cenas de documento e foto. Não conta como conteúdo novo. `semPulso` desliga tudo (medida de controle).
const SEM_PULSO = new Set(["evidencia", "posters", "cores", "proibicoes", "logoN"]);
const PulsoCtx = React.createContext(false);
// deriva: câmera flutua devagar e contínua sobre a cena (CLAUDE.md 4.3): órbita lenta de 26 px a cada 7 s (velocidade constante,
// ~23 px/s, sem paradas e sem metrônomo) + zoom lento de 0,5%/s. Não é o pulso: tem chave própria (semDeriva) para a medida "só conteúdo".
const DERIVA_R = 26, DERIVA_T = 7, DERIVA_ZOOM_S = 0.005, DERIVA_ZOOM_MAX = 0.04;
const DerivaCtx = React.createContext(false);
const CameraPassos: React.FC<{ ritmo: number[]; base: number; children: React.ReactNode; arquivo: boolean; tipo: string; idx?: number; durF?: number }> = ({ ritmo, base, children, arquivo, tipo, idx = 0, durF = 90 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const semPulso = React.useContext(PulsoCtx);
  if (arquivo) return <AbsoluteFill>{children}</AbsoluteFill>;
  let z = base, x = 0, y = 0;
  const semDeriva = React.useContext(DerivaCtx);
  if (!semDeriva) {
    const seg = durF / fps;
    const k = f / Math.max(1, durF);
    const zMax = Math.min(DERIVA_ZOOM_MAX, DERIVA_ZOOM_S * seg);
    const dz = idx % 4 === 3 ? zMax * (1 - k) : zMax * k; // às vezes afasta em vez de aproximar
    z = base * (1 + dz);
    const dir = idx % 2 ? 1 : -1, fase = (idx * 1.7) % (2 * Math.PI);
    const ang = fase + dir * (2 * Math.PI * f) / (DERIVA_T * fps);
    x = DERIVA_R * (Math.cos(ang) - Math.cos(fase));
    y = DERIVA_R * 0.6 * (Math.sin(ang) - Math.sin(fase));
  }
  const zDeriva = z, xDeriva = x;
  if (!semPulso && !SEM_PULSO.has(tipo)) {
    ritmo.forEach((p, i) => {
      const k = interpolate(f - Math.round(p * fps), [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (t) => 1 - Math.pow(1 - t, 3) });
      const alvoZ = i % 2 ? 0.015 : 0, alvoX = i % 2 ? 8 : 0;
      const antZ = i % 2 ? 0 : 0.015, antX = i % 2 ? 0 : 8;
      if (f >= Math.round(p * fps)) { z = zDeriva + (i === 0 ? alvoZ * k : antZ + (alvoZ - antZ) * k); x = xDeriva + (i === 0 ? alvoX * k : antX + (alvoX - antX) * k); }
    });
  }
  return <AbsoluteFill style={{ transform: `translate(${x}px, ${y}px) scale(${z})`, transformOrigin: "50% 48%" }}>{children}</AbsoluteFill>;
};

const Lateral: React.FC<{ l: Lat; i: number }> = ({ l, i }) => {
  const { fps } = useVideoConfig();
  const ini = Math.round(l.t * fps);
  const fim = l.fim !== undefined ? Math.round(l.fim * fps) : undefined;
  const rot = (i % 2 ? 1 : -1) * (2 + (i % 3));
  // laterais: esquerda até x=560, direita a partir de x=1380 (a faixa central 656–1264 e a cena ampliada ficam livres)
  if (l.tipo === "rec") {
    const wr = l.src.includes("controle") ? 150 : l.src.includes("vhs") ? 360 : 380;
    return <Recorte src={l.src} x={l.lado === "esq" ? 60 : 1920 - wr - 60} y={l.y} w={l.grande ? 480 : wr} inicio={ini} fim={fim} rot={rot} seed={l.src + i} de={l.lado === "esq" ? "esq" : "dir"} />;
  }
  const w = l.grande ? 490 : l.tipo === "print" ? 480 : l.src.includes("poster") ? 290 : 450;
  const h = l.grande ? 700 : l.tipo === "print" ? 340 : l.src.includes("poster") ? 425 : 320;
  const x = l.lado === "esq" ? 60 : 1920 - w - 60;
  return (
    <Card x={x} y={l.y} w={w} h={h} inicio={ini} fim={fim} rotY={l.lado === "esq" ? 10 : -10} rotZ={rot} seed={l.src + i}>
      <Img src={staticFile(l.src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: l.tipo === "print" ? "50% 0%" : "50% 30%" }} />
    </Card>
  );
};

const Etiqueta: React.FC<{ e: Etq; fim: number }> = ({ e, fim }) => {
  const { fps } = useVideoConfig();
  const f = useCurrentFrame();
  const ini = Math.round(e.t * fps);
  if (f < ini || f >= fim) return null;
  return (
    <div style={{ position: "absolute", top: 930, ...(e.lado === "esq" ? { left: 60 } : { right: 60 }),
      transform: `translateX(${interpolate(f - ini, [0, 6], [e.lado === "esq" ? -60 : 60, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px) rotate(${e.lado === "esq" ? -2 : 2}deg)` }}>
      <Destaque texto={e.texto} inicio={ini} size={58} tom={/\d/.test(e.texto) ? "ambar" : "tinta"} />
    </div>
  );
};

// Ficha de dossiê na lateral livre: a palavra-chave que ele diz, em papel, com o código do arquivo (CLAUDE.md 5: laterais trabalham).
// Entra deslizando da borda em degraus de stop-motion e sai quando a próxima do mesmo lado chega.
const Ficha: React.FC<{ e: Etq; n: number; cap: number; fim: number }> = ({ e, n, cap, fim }) => {
  const { fps } = useVideoConfig();
  const f = useCurrentFrame();
  const ini = Math.round(e.t * fps);
  if (f < ini || f >= fim + 6) return null;
  const passo = (v: number) => Math.floor(v / 3) * 3; // degraus "em três"
  const sinal = e.lado === "esq" ? -1 : 1;
  const ent = interpolate(passo(f - ini), [0, 9], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (t) => 1 - Math.pow(1 - t, 3) });
  const sai = interpolate(passo(f - fim), [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const y = Math.floor(n / 2) % 2 === 0 ? 300 : 560;
  const rot = sinal * (1.5 + (n % 3) * 0.8);
  const num = /\d/.test(e.texto);
  const w = e.estreita ? 340 : 290, x = e.lado === "esq" ? (e.estreita ? 40 : 20) : 1920 - (e.estreita ? 40 : 20) - w; // cena larga (documento): ficha menor, colada na borda
  const size = Math.min(70, Math.floor((w - 50) / (Math.max(4, e.texto.length) * 0.8)));
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, background: C.branco, border: `1px solid ${C.apoio}`, boxShadow: SOMBRA_F,
      padding: "18px 22px 16px", transform: `translateX(${sinal * (ent + sai) * 460}px) rotate(${rot}deg)` }}>
      <div style={{ fontFamily: MONO, fontSize: 16, letterSpacing: 2, color: "#777777" }}>ARQ {String(cap).padStart(2, "0")} · Nº {String(n + 1).padStart(2, "0")}</div>
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: size, lineHeight: 1.05, color: num ? C.ambar : "#292929", marginTop: 10, whiteSpace: "nowrap" }}>{e.texto}</div>
      <div style={{ height: 2, background: "#292929", marginTop: 14, width: "40%" }} />
    </div>
  );
};
const SOMBRA_F = "10px 12px 22px rgba(0,0,0,0.18)";

// tempos das ações do objeto principal: palavras dele (>= 1,25 s entre si, a partir de 0,9 s); pausas maiores que 2,2 s ganham ação a cada 1,5 s
const acoesDe = (ritmo: number[], dur: number): number[] => {
  const out: number[] = [];
  const push = (t: number) => { if (t >= 0.9 && t <= dur - 0.5 && (!out.length || t - out[out.length - 1] >= 1.25)) out.push(Math.round(t * 100) / 100); };
  for (const t of ritmo) {
    for (let g = 0; g < 20 && (out.length ? t - out[out.length - 1] > 2.2 : t > 2.6); g++) push((out.length ? out[out.length - 1] : 0.9 - 1.5) + 1.5);
    push(t);
  }
  while ((out.length ? out[out.length - 1] : 0) + 1.5 <= dur - 0.5) { const n0 = out.length; push((out.length ? out[out.length - 1] : -0.6) + 1.5); if (out.length === n0) break; }
  return out;
};

const TrechoV2: React.FC<{ tr: Tr }> = ({ tr }) => {
  const { fps } = useVideoConfig();
  const total = Math.round(tr.dur * fps);
  const principais = tr.cenas.filter((c) => c.tipo !== "academico");
  const overlays = tr.cenas.filter((c) => c.tipo === "academico");
  const cap = capDe[tr.id] ?? 0;
  const arquivo = tr.tipo === "arq";
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      {principais.map((c, i) => {
        const from = Math.round(c.t * fps);
        const next = i + 1 < principais.length ? Math.round(principais[i + 1].t * fps) : total;
        const ritmo = (tr.ritmo ?? []).filter((p) => p * fps >= from && p * fps < next).map((p) => p - c.t);
        return (
          <Sequence key={i} from={from} durationInFrames={Math.max(1, next - from)} layout="none">
            {arquivo ? <AbsoluteFill><Cena c={c} dur={(next - from) / fps} trecho={tr} /></AbsoluteFill> : (
              <Entrada tipo={TRANS[transDe[`${tr.id}:${tr.cenas.indexOf(c)}`] ?? 0]}>
                <CameraPassos ritmo={ritmo} base={ESCALA[c.tipo] ?? 1.0} arquivo={arquivo} tipo={c.tipo} idx={i + tr.id.length} durF={Math.max(1, next - from)}>
                  <AcoesCtx.Provider value={acoesDe(ritmo, (next - from) / fps)}>
                    <AbsoluteFill><Cena c={c} dur={(next - from) / fps} trecho={tr} /></AbsoluteFill>
                  </AcoesCtx.Provider>
                </CameraPassos>
              </Entrada>
            )}
          </Sequence>
        );
      })}
      <Camada vel={0.6} dur={total}>{(tr.laterais ?? []).filter((l) => l.lado === "esq").map((l, i) => <Lateral key={i} l={l} i={i} />)}</Camada>
      <Camada vel={1.1} dur={total}>{(tr.laterais ?? []).filter((l) => l.lado === "dir").map((l, i) => <Lateral key={i} l={l} i={i + 1} />)}</Camada>
      {(tr.etiquetas ?? []).map((e, i, a) => {
        const prox = a.slice(i + 1).find((x) => x.lado === e.lado);
        const fimE = prox ? Math.round(prox.t * fps) : total;
        const ocupado = (tr.laterais ?? []).some((l) => l.lado === e.lado && l.t - 0.3 <= e.t + 1.6 && e.t < (l.fim ?? tr.dur));
        return ocupado || arquivo ? <Etiqueta key={i} e={e} fim={fimE} /> : <Ficha key={i} e={e} n={i} cap={cap} fim={fimE} />;
      })}
      {overlays.map((c, i) => (
        <Sequence key={"o" + i} from={Math.round(c.t * fps)} layout="none"><Academico texto={c.texto} /></Sequence>
      ))}
      {!arquivo && cap > 0 && <PaginaEditorial capitulo={`${String(cap).padStart(2, "0")} · ${CAPITULOS[cap - 1]}`} arquivo={`ARQUIVO ${String(cap).padStart(2, "0")}/10`} />}
      <Grao opacidade={arquivo ? 0.3 : 0.5} />
      {tr.regravar && <Regravar bloco={tr.regravar} />}
    </AbsoluteFill>
  );
};

const PainelV3: React.FC<{ tr: Tr }> = ({ tr }) => {
  const { fps } = useVideoConfig();
  const f = useCurrentFrame();
  const dur = Math.round(tr.dur * fps);
  const meio = Math.round(dur * 0.45);
  return (
    <AbsoluteFill>
      <Painel de={tr.de ?? 0} para={tr.para ?? 0} dur={dur} preenchidos={tr.para ?? 0} />
      {tr.regancho && (
        <div style={{ position: "absolute", left: FAIXA.x + 10, width: FAIXA.w - 20, top: 900, textAlign: "center" }}>
          {f < meio ? <Destaque texto={tr.regancho[0]} inicio={4} size={38} /> : <Destaque texto={tr.regancho[1]} inicio={meio} size={34} tom="ambar" />}
        </div>
      )}
      {!tr.audio && !tr.regancho && (
        <div style={{ position: "absolute", left: FAIXA.x - 120, width: FAIXA.w + 240, top: 880, display: "flex", justifyContent: "center" }}>
          <div style={{ background: C.tinta, padding: "14px 22px" }}>
            <Terminal texto={`CAPÍTULO ${String((tr.para ?? 0) + 1).padStart(2, "0")} · ${CAPITULOS[tr.para ?? 0]}`} inicio={Math.round(0.5 * fps)} cps={26} size={34} w={FAIXA.w + 200} />
          </div>
        </div>
      )}
      <Grao opacidade={0.4} />
      {tr.regravar && <Regravar bloco={tr.regravar} />}
    </AbsoluteFill>
  );
};

const Som: React.FC<{ tr: Tr }> = ({ tr }) => {
  const { fps } = useVideoConfig();
  if (tr.tipo === "arq") return <Sequence from={Math.round((tr.pre ?? 0) * fps)} layout="none"><Audio src={staticFile(`media/arquivo/${tr.id}.mp4`)} volume={0.95} /></Sequence>;
  if (!tr.audio) return null;
  if (Array.isArray(tr.audio)) return (
    <>
      <Audio src={staticFile(`media/${tr.audio[0]}`)} />
      <Sequence from={Math.round(tr.audio[2] * fps)} layout="none"><Audio src={staticFile(`media/${tr.audio[1]}`)} /></Sequence>
    </>
  );
  return <Sequence from={tr.tipo === "painel" ? Math.round(0.5 * fps) : 0} layout="none"><Audio src={staticFile(`media/${tr.audio}`)} /></Sequence>;
};

export const EPISODIO_V3_DUR = TL.duracao;

export const EpisodioV3: React.FC<{ semPulso?: boolean; semDeriva?: boolean }> = ({ semPulso = false, semDeriva = false }) => {
  const { fps } = useVideoConfig();
  return (
    <PulsoCtx.Provider value={semPulso}><DerivaCtx.Provider value={semDeriva}>
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      {TL.trechos.map((tr) => (
        <Sequence key={tr.id} from={Math.round(tr.start * fps)} durationInFrames={Math.round(tr.dur * fps)}>
          {tr.tipo === "v3" ? (
            tr.comp === "coldopen" ? <ColdOpenV2 voz="gui" /> : tr.comp === "colagem" ? <Colagem v2 voz="gui" /> : <FalaT04 />
          ) : tr.tipo === "painel" ? <PainelV3 tr={tr} /> : <TrechoV2 tr={tr} />}
          {tr.tipo !== "v3" && <Som tr={tr} />}
          {/* trilha baixa por baixo (as cenas v3 já trazem a delas) */}
          {tr.tipo !== "v3" && <Audio src={staticFile("media/som/trilha.wav")} startFrom={Math.round(tr.start * fps)} volume={0.055} />}
        </Sequence>
      ))}
      <FalaCtx.Provider value={FALAS}>
        {TL.fx.map((e, i) => <Sfx key={i} s={e.t} nome={e.som} vol={e.vol ?? 0.45} />)}
      </FalaCtx.Provider>
    </AbsoluteFill>
    </DerivaCtx.Provider></PulsoCtx.Provider>
  );
};
