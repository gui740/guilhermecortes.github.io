// Hooks falados dos Shorts (S01–S08), prontos para trocar.
// Enquanto o bloco "S0N" não existe em palavras_gui.json, o Short fica exatamente como está (hook só em texto ou aberto pelo bloco do episódio).
// Quando o Guilherme manda o áudio e o pipeline/narracao_gui/trocar_audio.py grava "S0N" em palavras_gui.json + media/narr_gui/bS0N.wav,
// o hook entra antes do Short: voz dele, texto do hook na tela e legenda palavra a palavra; o resto do Short começa depois.
import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame } from "remotion";
import PAL from "./palavras_gui.json";
import { C } from "../theme";
import { Destaque, Grao, Papel, useS } from "./kit";
import { FalaCtx, LegendaPalavra, Narr, Sfx } from "./Amostra";

type W = [number, number, string];
const P = PAL as unknown as Record<string, { dur: number; palavras: W[] }>;

export const HOOK_TEXTO: Record<string, string[]> = {
  S01: ["O CEO DA NETFLIX DISSE", "QUE ELA COMPETE", "COM O SEU SONO."],
  S02: ["ESSE BOTÃO É APERTADO", "136 MILHÕES", "DE VEZES POR DIA."],
  S03: ["VOCÊ DÁ 5 ESTRELAS", "PARA UM FILME", "E ASSISTE OUTRO."],
  S04: ["TODO CHEFE DA NETFLIX", "PRECISA RESPONDER", "UMA PERGUNTA."],
  S05: ["EM MUITOS PAÍSES,", "A NETFLIX NEM ESCREVE", "O PRÓPRIO NOME."],
  S06: ["UM CANDIDATO NO", "DEBATE DA CNN.", "ELE NÃO EXISTE."],
  S07: ["A NETFLIX PROIBIU", "DIVIDIR A SENHA."],
  S08: ["UMA CASA ONDE VOCÊ", "ENTRA NAS SÉRIES."],
};
const GAP = 0.3;
export const chaveHook = (shortId: string) => shortId.replace("SHORT", "S");
export const temHook = (shortId: string) => !!P[chaveHook(shortId)];
/** segundos que o hook gravado acrescenta no começo do Short (0 enquanto não foi gravado) */
export const hookDur = (shortId: string) => (temHook(shortId) ? P[chaveHook(shortId)].dur + GAP : 0);

export const ComHook: React.FC<{ shortId: string; children: React.ReactNode }> = ({ shortId, children }) => {
  const S = useS();
  const f = useCurrentFrame();
  if (!temHook(shortId)) return <>{children}</>;
  const k = chaveHook(shortId);
  const H = hookDur(shortId);
  const linhas = HOOK_TEXTO[k] ?? [];
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <Sequence from={0} durationInFrames={S(H)}>
        <FalaCtx.Provider value={[[0, P[k].dur]]}>
          <AbsoluteFill style={{ backgroundColor: C.branco }}>
            <Papel />
            <div style={{ position: "absolute", left: 60, right: 60, top: 420, display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
              {linhas.map((l, i) => {
                // cada linha entra na palavra dele que a abre (ou em sequência, se não achar)
                const w0 = l.split(" ")[0].toLowerCase().replace(/[.,?!%]/g, "");
                const t = P[k].palavras.find((w) => w[2].toLowerCase().replace(/[.,?!%]/g, "").startsWith(w0))?.[0] ?? i * 0.6;
                return f >= S(t) ? <Destaque key={i} texto={l} inicio={S(t)} size={i === linhas.length - 1 ? 104 : 76} tom={i === linhas.length - 1 ? "ambar" : "tinta"} /> : null;
              })}
            </div>
            <LegendaPalavra palavras={P[k].palavras} chave={{}} />
            <Grao />
            <Narr s={0} arq={`media/narr_gui/b${k}.wav`} />
            <Sfx s={0} nome="carimbo_0" vol={0.3} />
          </AbsoluteFill>
        </FalaCtx.Provider>
      </Sequence>
      <Sequence from={S(H)}>{children}</Sequence>
    </AbsoluteFill>
  );
};
