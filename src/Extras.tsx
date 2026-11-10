import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, Bg, FAM, W, H, SAFE } from "./theme";
import { TLS, wf } from "./timeline";
import { SceneCtx, Row, Stack, Cut, Star } from "./kit";
import { Filters } from "./Reel";
import * as S from "./scenes";

const Shell: React.FC<{ bg: Bg; children: React.ReactNode }> = ({ bg, children }) => (
  <AbsoluteFill style={{ background: C[bg], overflow: "hidden" }}>
    <Filters />
    <SceneCtx.Provider value={{ s: 0, e: 90, bg, exit: false }}>{children}</SceneCtx.Provider>
  </AbsoluteFill>
);
const fr = (k: string) => TLS[k].words.map((x) => wf(x.t));
/** Gancho A (promessa) */
export const GanchoA: React.FC = () => (
  <Shell bg="black"><S.H1 fr={fr("gA")} extra={{ t: "e o nº 1 quase ninguém viu", at: 74 }} /></Shell>
);
/** Gancho B (desafio) */
export const GanchoB: React.FC = () => {
  const a = fr("gB");
  return (
    <Shell bg="red">
      <S.H2 qAt={a[4]} qY={1400} rows={<>
        <Row toks={[{ t: "cê", at: a[0], small: true }, { t: "não", at: a[1] }]} width={560} gap={0.05} />
        <Row toks={[{ t: "termina", at: a[2] }]} />
        <Row toks={[{ t: "o", at: a[3], small: true }, { t: "número", at: a[4], font: "serif", rel: 0.62 }, { t: "1", at: a[5], font: "serif", hi: true, rel: 1.25 }]} width={640} max={230} gap={0.05} />
        <Row toks={[{ t: "sozinho", at: a[6], hi: true }]} />
      </>} />
    </Shell>
  );
};
/** Gancho C (dúvida) */
export const GanchoC: React.FC = () => (<Shell bg="gray"><S.GanchoC fr={fr("gC")} /></Shell>);

/** Capa 1080x1920: fundo vermelho, recorte P&B, título enorme (legível em miniatura) */
export const Capa: React.FC = () => (
  <AbsoluteFill style={{ background: C.red, overflow: "hidden" }}>
    <SceneCtx.Provider value={{ s: -100, e: 9999, bg: "red", exit: false }}>
      <Star cx={540} cy={1560} r={540} at={-50} />
      <Cut name="gon_medo" h={800} cx={540} bottom={1975} at={-50} drift={0} />
      <Stack top={270} left={80} width={920}>
        <Row toks={[{ t: "3", at: -50, font: "serif", rel: 1.3, hi: true }, { t: "terrores", at: -50 }]} gap={0.03} />
        <Row toks={[{ t: "que", at: -50, small: true, rel: 0.34 }, { t: "parecem", at: -50, font: "serif" }]} gap={0.05} mt={6} />
        <Row toks={[{ t: "reais", at: -50, hi: true }]} max={400} mt={-6} />
      </Stack>
    </SceneCtx.Provider>
  </AbsoluteFill>
);
