// EP01 v3 com a narração do Guilherme. Lê timeline_v3.json (pipeline/montar_timeline_v3.py).
// Cenas da v2 entram numa "casca" v3 (grão, câmera em deriva, página editorial); cold open, colagem, fala TED e painel são v3.
import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import timeline from "../timeline_v3.json";
import { C, FAIXA, MONO } from "../theme";
import { Cena } from "../cenas/Cenas";
import { Academico } from "../cenas/bits";
import { Card, Destaque, Grao, PaginaEditorial, Recorte } from "./kit";
import { Painel, CAPITULOS } from "./transicoes";
import { Colagem, FalaCtx, FalaT04, Sfx } from "./Amostra";
import { ColdOpenV2 } from "./Rodada1";

type Cn = { tipo: string; t: number; [k: string]: any };
type Lat = { t: number; src: string; tipo: "rec" | "card" | "print"; lado: "esq" | "dir"; y: number };
type Tr = { tipo: string; id: string; start: number; dur: number; pre?: number; cenas: Cn[]; audio?: any; regravar?: string | null;
  laterais?: Lat[]; passos?: number[];
  comp?: string; de?: number; para?: number; regancho?: string[] | null; titulo?: string };
const TL = timeline as unknown as { trechos: Tr[]; fx: { t: number; som: string }[]; duracao: number };

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
const ESCALA: Record<string, number> = { titulo: 1.2, contador: 1.2, pergunta: 1.25, citacao: 1.2, medidor: 1.25, cheque: 1.2, botao: 1.3, pessoas: 1.25,
  anzol: 1.3, fluxo: 1.25, lista: 1.2, aovivo: 1.0, barras: 1.25, mapa: 1.1, envelope: 1.3, logoN: 1.0 };

/** Câmera em degraus: a cada "passo" (palavra da fala), um pequeno salto de zoom e de posição, com 5 quadros de assentamento. */
const CameraPassos: React.FC<{ passos: number[]; base: number; children: React.ReactNode; arquivo: boolean }> = ({ passos, base, children, arquivo }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  let z = base, x = 0, y = 0;
  passos.forEach((p, i) => {
    const k = interpolate(f - Math.round(p * fps), [0, 5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    z += 0.035 * k; x += (i % 2 ? 14 : -14) * k; y += (i % 3 === 0 ? -8 : 6) * k;
  });
  if (arquivo) return <AbsoluteFill>{children}</AbsoluteFill>;
  return <AbsoluteFill style={{ transform: `translate(${x}px, ${y}px) scale(${z})`, transformOrigin: "50% 48%" }}>{children}</AbsoluteFill>;
};

const Lateral: React.FC<{ l: Lat; i: number }> = ({ l, i }) => {
  const { fps } = useVideoConfig();
  const ini = Math.round(l.t * fps);
  const rot = (i % 2 ? 1 : -1) * (2 + (i % 3));
  // laterais: esquerda até x=560, direita a partir de x=1380 (a faixa central 656–1264 e a cena ampliada ficam livres)
  if (l.tipo === "rec") {
    const wr = l.src.includes("controle") ? 150 : l.src.includes("vhs") ? 360 : 380;
    return <Recorte src={l.src} x={l.lado === "esq" ? 60 : 1920 - wr - 60} y={l.y} w={wr} inicio={ini} rot={rot} seed={l.src + i} de={l.lado === "esq" ? "esq" : "dir"} />;
  }
  const w = l.tipo === "print" ? 480 : l.src.includes("poster") ? 290 : 450;
  const h = l.tipo === "print" ? 340 : l.src.includes("poster") ? 425 : 320;
  const x = l.lado === "esq" ? 60 : 1920 - w - 60;
  return (
    <Card x={x} y={l.y} w={w} h={h} inicio={ini} rotY={l.lado === "esq" ? 10 : -10} rotZ={rot} seed={l.src + i}>
      <Img src={staticFile(l.src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: l.tipo === "print" ? "50% 0%" : "50% 30%" }} />
    </Card>
  );
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
        const passos = (tr.passos ?? []).filter((p) => p * fps >= from && p * fps < next).map((p) => p - c.t);
        return (
          <Sequence key={i} from={from} durationInFrames={Math.max(1, next - from)} layout="none">
            <CameraPassos passos={passos} base={ESCALA[c.tipo] ?? 1.0} arquivo={arquivo}>
              <AbsoluteFill><Cena c={c} dur={(next - from) / fps} trecho={tr} /></AbsoluteFill>
            </CameraPassos>
          </Sequence>
        );
      })}
      {(tr.laterais ?? []).map((l, i) => <Lateral key={i} l={l} i={i} />)}
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

export const EpisodioV3: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
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
        {TL.fx.map((e, i) => <Sfx key={i} s={e.t} nome={e.som} />)}
      </FalaCtx.Provider>
    </AbsoluteFill>
  );
};
