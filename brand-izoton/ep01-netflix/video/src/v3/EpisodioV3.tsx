// EP01 v3 com a narração do Guilherme. Lê timeline_v3.json (pipeline/montar_timeline_v3.py).
// Cenas da v2 entram numa "casca" v3 (grão, câmera em deriva, página editorial); cold open, colagem, fala TED e painel são v3.
import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import timeline from "../timeline_v3.json";
import { C, FAIXA, MONO } from "../theme";
import { Cena } from "../cenas/Cenas";
import { Academico } from "../cenas/bits";
import { Camera, Destaque, Grao, PaginaEditorial } from "./kit";
import { Painel, CAPITULOS } from "./transicoes";
import { Colagem, FalaCtx, FalaT04, Sfx } from "./Amostra";
import { ColdOpenV2 } from "./Rodada1";

type Cn = { tipo: string; t: number; [k: string]: any };
type Tr = { tipo: string; id: string; start: number; dur: number; pre?: number; cenas: Cn[]; audio?: any; regravar?: string | null;
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

const TrechoV2: React.FC<{ tr: Tr }> = ({ tr }) => {
  const { fps } = useVideoConfig();
  const total = Math.round(tr.dur * fps);
  const principais = tr.cenas.filter((c) => c.tipo !== "academico");
  const overlays = tr.cenas.filter((c) => c.tipo === "academico");
  const cap = capDe[tr.id] ?? 0;
  const arquivo = tr.tipo === "arq";
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <Camera dur={total} de={1.0} ate={arquivo ? 1.0 : 1.045} dx={arquivo ? 0 : -24}>
        {principais.map((c, i) => {
          const from = Math.round(c.t * fps);
          const next = i + 1 < principais.length ? Math.round(principais[i + 1].t * fps) : total;
          return (
            <Sequence key={i} from={from} durationInFrames={Math.max(1, next - from)} layout="none">
              <AbsoluteFill><Cena c={c} dur={(next - from) / fps} trecho={tr} /></AbsoluteFill>
            </Sequence>
          );
        })}
      </Camera>
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
