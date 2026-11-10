import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate } from "remotion";
import { C, FAM, SAFE, SAFE_W, W, H } from "./theme";
import { Badge, BigNum, Bookmark, Caption, Cut, DashedLink, Grid, Logo, Plane, Row, Stack, Star, Viewfinder, Word, clamp01, outCubic, useScene } from "./kit";

export type WFn = (line: string, i: number) => number;
export type CapFn = (...ids: string[]) => { t: string; at: number }[];
type P = { w: WFn; cap: CapFn };

/** rótulo pequeno do filme (serifada itálica) usado nas cenas de streaming */
const FilmLabel: React.FC<{ t: string; x: number; y: number; at: number; color: string; size?: number }> = ({ t, x, y, at, color, size = 58 }) => (
  <div style={{ position: "absolute", left: x, top: y, whiteSpace: "nowrap" }}>
    <Word at={at}>
      <span style={{ fontFamily: FAM.serif, fontSize: size, color, display: "inline-block", transform: "scaleX(0.8)", transformOrigin: "0 50%" }}>{t}</span>
    </Word>
  </div>
);
const Q: React.FC<{ x: number; y: number; at: number; size?: number; color?: string }> = ({ x, y, at, size = 420, color = C.yellow }) => {
  const f = useCurrentFrame();
  const wob = Math.sin(Math.floor(f / 4) * 2.1) * 5;
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `rotate(${wob}deg)` }}>
      <Word at={at}>
        <span style={{ fontFamily: FAM.serif, fontSize: size, color, lineHeight: 1 }}>?</span>
      </Word>
    </div>
  );
};

/* ───────────── GANCHO ───────────── */
/** Abertura: grade, visor + REC em "found footage", recorte atravessando a tela com motion blur */
export const H1: React.FC<{ fr: number[]; extra?: { t: string; at: number } }> = ({ fr, extra }) => {
  const f = useCurrentFrame();
  const { s } = useScene();
  const k = f - s;
  const cross = interpolate(k, [0, 9], [-900, 1500], { extrapolateRight: "clamp" });
  return (
    <>
      <Grid at={s} color={C.gray} />
      <Cut name="gon_grupo" h={600} cx={500} bottom={1935} at={s + 5} from="bottom" />
      {k < 10 ? (
        <Img src={staticFile("cut/blair_olhos.png")} style={{ position: "absolute", left: cross, top: 880, width: 1000, filter: "url(#hblur)", opacity: 0.95 }} />
      ) : null}
      <Viewfinder at={fr[1]} />
      <Stack>
        <Row toks={[{ t: "3", at: fr[0] - 4, font: "serif", rel: 1.3, dy: 0.02 }, { t: "found", at: fr[1], ghost: true }]} gap={0.07} />
        <Row toks={[{ t: "footage", at: fr[2], ghost: true }]} mt={-6} />
        <Row toks={[{ t: "que", at: fr[3], small: true, rel: 0.45 }, { t: "parecem", at: fr[4], font: "serif" }]} width={640} max={150} mt={18} />
        <Row toks={[{ t: "gravação", at: fr[5], font: "serif", rel: 0.62 }, { t: "de", at: fr[6], small: true, rel: 0.34 }]} width={560} max={150} mt={14} />
        <Row toks={[{ t: "verdade", at: fr[7], hi: true }]} mt={-4} />
      </Stack>
      {extra ? <Caption chunks={[extra]} y={1235} color={C.black} bg={C.yellow} /> : null}
    </>
  );
};
/** "o último, cê não termina sozinho": antecipa o nº 1 sem revelar (silhueta + ?) */
export const H2: React.FC<{ rows: React.ReactNode; qAt: number; qY?: number }> = ({ rows, qAt, qY = 1180 }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="gon_medo" h={860} cx={520} bottom={1960} at={s} from="bottom" sil />
      <Q x={410} y={qY} at={qAt} />
      <Stack>{rows}</Stack>
    </>
  );
};
export const h2Rows = (w: WFn) => (
  <>
    <Row toks={[{ t: "o", at: w("h2", 1), small: true }, { t: "último", at: w("h2", 2), font: "serif" }, { t: "cê", at: w("h2", 3), small: true, rel: 0.45 }, { t: "não", at: w("h2", 4) }]} gap={0.05} />
    <Row toks={[{ t: "termina", at: w("h2", 5) }]} />
    <Row toks={[{ t: "sozinho", at: w("h2", 6), hi: true }]} />
  </>
);
export const GanchoC: React.FC<{ fr: number[] }> = ({ fr }) => {
  const { s } = useScene();
  return (
    <>
      <Grid at={s} color={C.black} max={0.16} />
      <Star cx={520} cy={1500} r={500} at={fr[7]} />
      <Cut name="blair_olhos" h={800} cx={520} bottom={1965} at={s} from="left" />
      <Viewfinder at={fr[2]} color={C.black} />
      <Stack>
        <Row toks={[{ t: "esse", at: fr[0] }, { t: "filme", at: fr[1] }]} />
        <Row toks={[{ t: "muita", at: fr[2], font: "serif" }, { t: "gente", at: fr[3], font: "serif" }]} width={700} max={150} mt={10} />
        <Row toks={[{ t: "jura", at: fr[4] }, { t: "que", at: fr[5], small: true }, { t: "é", at: fr[6], small: true }, { t: "real", at: fr[7], hi: true }]} mt={10} gap={0.05} />
      </Stack>
    </>
  );
};

/* ───────────── PEÇAS DOS FILMES ───────────── */
const Dot: React.FC<{ x: number; y: number; at: number; color?: string; d?: number }> = ({ x, y, at, color = C.red, d = 76 }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  return <div style={{ position: "absolute", left: x, top: y, width: d, height: d, borderRadius: d / 2, background: color, opacity: Math.floor((f - at) / 6) % 2 === 0 ? 1 : 0.15 }} />;
};
const capInk = (bg: string) => (bg === "black" ? { color: C.black, bg: C.yellow } : { color: C.gray, bg: C.black });
const Cap: React.FC<{ chunks: { t: string; at: number }[] }> = ({ chunks }) => {
  const { bg } = useScene();
  return <Caption chunks={chunks} {...capInk(bg)} />;
};
/** número gigante + título do filme; silhueta antes da revelação, estrela + recorte quando o título é dito */
const TitleScene: React.FC<{ num: string; numAt: number; numColor: string; t: number; cut: string; left?: number; top?: number; pre?: React.ReactNode; children: React.ReactNode; grid?: string; noSil?: boolean }> = ({ num, numAt, numColor, t, cut, left = 330, top = 300, pre, children, grid, noSil }) => {
  const f = useCurrentFrame();
  const { s } = useScene();
  return (
    <>
      {grid ? <Grid at={s} color={grid} max={0.22} /> : null}
      {pre}
      {f < t && !noSil ? <Cut name={cut} h={860} cx={540} bottom={1965} at={s} from="bottom" sil /> : null}
      <Star cx={540} cy={1430} r={520} at={t} />
      <Cut name={cut} h={cut === "blair_olhos" ? 860 : 940} cx={540} bottom={1965} at={t} drift={0.1} />
      <BigNum n={num} at={numAt} size={640} x={SAFE.left - 20} y={190} color={numColor} />
      <Stack left={left} width={W - SAFE.right - left} top={top}>{children}</Stack>
    </>
  );
};
const Where: React.FC<{ rows: React.ReactNode; cut: string; label: string; logo: "netflix" | "primevideo" | "hbomax"; logoW: number; logoAt: number; ink: string; logoColor: string; id: string }> = ({ rows, cut, label, logo, logoW, logoAt, ink, logoColor, id }) => {
  const { s } = useScene();
  const ar = { netflix: 3.7, primevideo: 3.18, hbomax: 1.386 }[logo];
  const lh = logoW / ar;
  const lx = W - SAFE.right - logoW - 10, ly = 1480 - lh;
  return (
    <>
      <Stack>
        {rows}
        <Row toks={[{ t: label, at: s + 2, font: "serif", color: ink }]} max={112} mt={16} />
      </Stack>
      <Star cx={300} cy={1090} r={255} at={s + 1} points={14} />
      <Badge name={cut} cx={300} cy={1090} r={170} at={s + 1} bg={C.gray} />
      <DashedLink id={id} d={`M 540 1010 C 780 960, 900 1080, ${lx + logoW * 0.6} ${ly - 28}`} at={logoAt - 5} color={ink} />
      <Logo name={logo} w={logoW} x={lx} y={ly} color={logoColor} at={logoAt} />
    </>
  );
};

/* ───────────── 3 · A BRUXA DE BLAIR ───────────── */
export const A: React.FC<P & { phone: React.ReactNode }> = ({ w, phone }) => {
  const t = w("a2", 0);
  return (
    <TitleScene num="3" numAt={w("a1", 0)} numColor={C.red} t={t} cut="blair_olhos" pre={phone} noSil>
      <Row toks={[{ t: "A", at: t, font: "serif", rel: 0.5 }, { t: "Bruxa", at: w("a2", 1), font: "serif" }]} gap={0.05} />
      <Row toks={[{ t: "de", at: w("a2", 2), font: "serif", rel: 0.5 }, { t: "Blair", at: w("a2", 3), font: "serif" }]} gap={0.05} mt={-10} />
      <Row toks={[{ t: "1999", at: w("a2", 3) + 6 }]} width={170} mt={10} />
    </TitleScene>
  );
};
export const A3: React.FC<P> = ({ w, cap }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="blair_lanterna" h={1080} cx={560} bottom={1975} at={s} from="right" drift={0.1} />
      <Stack>
        <Row toks={[{ t: "3", at: w("a3", 0), font: "serif", rel: 1.25 }, { t: "estudantes", at: w("a3", 1) }]} gap={0.06} />
        <Row toks={[{ t: "numa", at: w("a3", 3), small: true }, { t: "floresta", at: w("a3", 4), hi: true }]} gap={0.05} mt={4} />
      </Stack>
      <Cap chunks={cap("a3")} />
    </>
  );
};
export const A4: React.FC<P> = ({ w }) => {
  const f = useCurrentFrame();
  const { s } = useScene();
  const gone = clamp01((f - w("a4", 1)) / 10);
  return (
    <>
      <div style={{ position: "absolute", inset: 0, opacity: 1 - gone, transform: `scale(${1 - gone * 0.25})`, transformOrigin: "50% 80%" }}>
        <Cut name="blair_lanterna" h={900} cx={540} bottom={1975} at={s} sil drift={0} />
      </div>
      <Stack>
        <Row toks={[{ t: "e", at: w("a4", 0), small: true }, { t: "somem", at: w("a4", 1), hi: true }]} gap={0.05} max={400} />
      </Stack>
    </>
  );
};
export const A5: React.FC<P> = ({ w, cap }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="blair_medo" h={820} cx={540} bottom={1975} at={s} from="bottom" drift={0.14} />
      <Stack>
        <Row toks={[{ t: "em", at: w("a5", 0), small: true }, { t: "1999", at: w("a5", 1), font: "serif" }]} gap={0.05} width={560} max={250} />
        <Row toks={[{ t: "o", at: w("a5", 4), small: true }, { t: "site", at: w("a5", 5) }, { t: "do filme", at: w("a5", 6), small: true }]} gap={0.06} width={560} max={190} mt={2} />
        <Row toks={[{ t: "desaparecidos", at: w("a5", 12), hi: true }]} mt={6} />
        <Row toks={[{ t: "de", at: w("a5", 13), small: true }, { t: "verdade", at: w("a5", 14) }]} gap={0.05} mt={4} />
      </Stack>
      <Cap chunks={cap("a5")} />
    </>
  );
};
export const A6: React.FC<P> = ({ w }) => {
  const { s } = useScene();
  return (
    <>
      {/* recorte duplicado: cópia pequena ao fundo, grande na frente */}
      <Cut name="blair_medo" h={620} cx={800} bottom={1965} at={s + 3} opacity={0.5} from="right" />
      <Cut name="blair_medo" h={1040} cx={400} bottom={1975} at={s} from="bottom" />
      <Stack>
        <Row toks={[{ t: "e", at: w("a6", 0), small: true }, { t: "muita", at: w("a6", 1), font: "serif" }, { t: "gente", at: w("a6", 2), font: "serif" }]} gap={0.06} max={190} />
        <Row toks={[{ t: "acreditou", at: w("a6", 3), hi: true }]} mt={4} />
      </Stack>
    </>
  );
};
export const A7: React.FC<P> = ({ w }) => (
  <Where id="l3" cut="blair_medo" label="A Bruxa de Blair" logo="netflix" logoW={600} logoAt={w("a7", 2)} ink={C.white} logoColor={C.white}
    rows={<Row toks={[{ t: "tá", at: w("a7", 0), small: true }, { t: "na", at: w("a7", 1), small: true }, { t: "Netflix", at: w("a7", 2) }]} gap={0.05} />} />
);
export const M1: React.FC<P> = ({ w }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="demo_host" h={800} cx={520} bottom={1965} at={s} sil from="bottom" />
      <Q x={430} y={1260} at={w("m1", 2)} size={360} color={C.red} />
      <Stack>
        <Row toks={[{ t: "e", at: w("m1", 0), small: true }, { t: "o", at: w("m1", 1), small: true }, { t: "próximo", at: w("m1", 2) }]} gap={0.05} />
        <Row toks={[{ t: "é", at: w("m1", 3), small: true }, { t: "pior", at: w("m1", 4), hi: true }]} gap={0.05} max={400} />
      </Stack>
    </>
  );
};

/* ───────────── 2 · ENTREVISTA COM O DEMÔNIO ───────────── */
export const B: React.FC<P> = ({ w }) => {
  const t = w("b2", 0);
  return (
    <TitleScene num="2" numAt={w("b1", 0)} numColor={C.yellow} t={t} cut="demo_host" left={345} top={320} grid={C.gray}>
      <Row toks={[{ t: "Entrevista", at: t, font: "serif" }]} />
      <Row toks={[{ t: "com", at: w("b2", 1), font: "serif", rel: 0.5 }, { t: "o", at: w("b2", 2), font: "serif", rel: 0.5 }, { t: "Demônio", at: w("b2", 3), font: "serif" }]} gap={0.05} mt={-6} />
      <Row toks={[{ t: "2023", at: w("b2", 3) + 6, color: C.gray }]} width={170} mt={10} />
    </TitleScene>
  );
};
export const B3: React.FC<P> = ({ w, cap }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="demo_host" h={860} cx={600} bottom={1975} at={s} from="right" drift={0.1} />
      <Viewfinder at={w("b3", 2)} color={C.black} />
      <Stack>
        <Row toks={[{ t: "a", at: w("b3", 1), small: true }, { t: "fita", at: w("b3", 2), font: "serif" }, { t: "de um", at: w("b3", 3), small: true }]} gap={0.06} width={520} max={220} />
        <Row toks={[{ t: "talk", at: w("b3", 5) }, { t: "show", at: w("b3", 6) }]} mt={4} />
        <Row toks={[{ t: "de", at: w("b3", 7), small: true }, { t: "1977", at: w("b3", 8), font: "serif", hi: true }]} gap={0.05} width={520} max={230} mt={4} />
      </Stack>
      <Cap chunks={cap("b3")} />
    </>
  );
};
export const B4: React.FC<P> = ({ w, cap }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="demo_palco" h={820} cx={520} bottom={1975} at={s} from="bottom" drift={0.1} />
      <Stack>
        <Row toks={[{ t: "ao", at: w("b4", 0) }, { t: "vivo", at: w("b4", 1) }]} width={620} />
        <Row toks={[{ t: "na", at: w("b4", 2), small: true }, { t: "noite", at: w("b4", 3), font: "serif" }, { t: "de", at: w("b4", 4), small: true }]} gap={0.06} width={520} max={190} mt={8} />
        <Row toks={[{ t: "Halloween", at: w("b4", 5), hi: true }]} mt={2} />
      </Stack>
      <Dot x={SAFE.left + 660} y={SAFE.top + 70} at={w("b4", 0)} color={C.white} d={80} />
      <Cap chunks={cap("b4")} />
    </>
  );
};
export const B5: React.FC<P> = ({ w, cap }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="demo_menina" h={1060} cx={540} bottom={1975} at={s} from="bottom" drift={0.12} />
      <Stack>
        <Row toks={[{ t: "o", at: w("b5", 0), small: true, rel: 0.5 }, { t: "apresentador", at: w("b5", 1), font: "serif" }]} gap={0.05} max={130} />
        <Row toks={[{ t: "leva uma", at: w("b5", 2), small: true }, { t: "menina", at: w("b5", 4) }]} gap={0.05} mt={6} />
        <Row toks={[{ t: "possuída", at: w("b5", 5), font: "serif", hi: true }]} mt={-4} />
      </Stack>
      <Cap chunks={cap("b5")} />
    </>
  );
};
export const B6: React.FC<P> = ({ w }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="demo_grito" h={1180} cx={600} bottom={1960} at={s} from="right" drift={0.14} />
      <Stack>
        <Row toks={[{ t: "e", at: w("b6", 0), small: true }, { t: "perde", at: w("b6", 1) }]} gap={0.05} width={640} />
        <Row toks={[{ t: "o", at: w("b6", 2), small: true }, { t: "controle", at: w("b6", 3), hi: true }]} gap={0.05} mt={4} />
      </Stack>
    </>
  );
};
export const B7: React.FC<P> = ({ w }) => (
  <Where id="l2" cut="demo_host" label="Entrevista com o Demônio" logo="hbomax" logoW={350} logoAt={w("b7", 2)} ink={C.white} logoColor={C.white}
    rows={<Row toks={[{ t: "tá", at: w("b7", 0), small: true }, { t: "na", at: w("b7", 1), small: true }, { t: "HBO", at: w("b7", 2) }, { t: "Max", at: w("b7", 3) }]} gap={0.05} />} />
);
export const S1: React.FC<P> = ({ w }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="gon_camera" h={640} cx={300} bottom={1975} at={s} from="bottom" />
      <Plane x={610} y={1330} s={250} at={w("s1", 0)} color={C.yellow} />
      <Stack>
        <Row toks={[{ t: "manda", at: w("s1", 0) }]} max={340} />
        <Row toks={[{ t: "pra", at: w("s1", 1), small: true, rel: 0.4 }, { t: "quem", at: w("s1", 2), small: true, rel: 0.4 }, { t: "diz", at: w("s1", 3), small: true, rel: 0.4 }, { t: "que", at: w("s1", 4), small: true, rel: 0.4 }, { t: "não", at: w("s1", 5), font: "serif" }, { t: "tem", at: w("s1", 6), font: "serif" }]} gap={0.05} max={170} />
        <Row toks={[{ t: "medo", at: w("s1", 7), hi: true }]} max={360} />
        <Row toks={[{ t: "de", at: w("s1", 8), small: true, rel: 0.4 }, { t: "nada", at: w("s1", 9), font: "serif" }]} gap={0.06} width={480} max={190} />
      </Stack>
    </>
  );
};

/* ───────────── 1 · GONJIAM ───────────── */
export const Cn: React.FC<P> = ({ w }) => {
  const t = w("c3", 0);
  return (
    <TitleScene num="1" numAt={w("c1", 2)} numColor={C.yellow} t={t} cut="gon_medo" left={300} top={290}>
      <Row toks={[{ t: "quase", at: w("c2", 1), small: true, rel: 1 }, { t: "ninguém", at: w("c2", 2), small: true, rel: 1 }, { t: "viu", at: w("c2", 3), small: true, rel: 1 }]} gap={0.22} max={64} />
      <Row toks={[{ t: "Gonjiam", at: t, font: "serif" }]} mt={6} />
      <Row toks={[{ t: "manicômio", at: t + 4 }, { t: "assombrado", at: t + 7 }]} mt={14} />
      <Row toks={[{ t: "2018", at: t + 10 }]} width={170} mt={14} />
    </TitleScene>
  );
};
export const C4: React.FC<P> = ({ w, cap }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="gon_predio" h={720} cx={390} bottom={1965} at={s} from="bottom" drift={0.03} />
      <Cut name="gon_grupo" h={340} cx={420} bottom={1965} at={w("c4", 1)} from="right" />
      <Viewfinder at={w("c4", 4)} color={C.black} />
      <Stack>
        <Row toks={[{ t: "uma", at: w("c4", 0), small: true, rel: 0.5 }, { t: "equipe", at: w("c4", 1), font: "serif" }, { t: "faz", at: w("c4", 2), small: true, rel: 0.5 }]} gap={0.06} max={130} />
        <Row toks={[{ t: "uma", at: w("c4", 3), small: true }, { t: "live", at: w("c4", 4), hi: true }]} width={520} max={280} gap={0.06} mt={6} />
        <Row toks={[{ t: "manicômio", at: w("c4", 8) }]} mt={16} />
        <Row toks={[{ t: "abandonado", at: w("c4", 9), font: "serif" }]} max={170} mt={4} />
      </Stack>
      <Dot x={SAFE.left + 640} y={SAFE.top + 200} at={w("c4", 4)} />
      <Cap chunks={cap("c4")} />
    </>
  );
};
export const C5: React.FC<P> = ({ w, cap }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="gon_close" h={820} cx={540} bottom={1975} at={s} from="bottom" drift={0.12} />
      <Stack>
        <Row toks={[{ t: "existiu", at: w("c5", 1) }]} />
        <Row toks={[{ t: "de", at: w("c5", 2), small: true }, { t: "verdade", at: w("c5", 3), hi: true }]} gap={0.05} mt={2} />
        <Row toks={[{ t: "na", at: w("c5", 4), small: true, rel: 0.4 }, { t: "Coreia", at: w("c5", 5), font: "serif" }, { t: "do", at: w("c5", 6), small: true, rel: 0.4 }, { t: "Sul", at: w("c5", 7), font: "serif" }]} gap={0.06} max={150} mt={10} />
      </Stack>
      <Cap chunks={cap("c5")} />
    </>
  );
};
export const C6: React.FC<P> = ({ w, cap }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="gon_camera" h={880} cx={600} bottom={1975} at={s} from="right" drift={0.1} />
      <Viewfinder at={w("c6", 4)} color={C.black} />
      <Stack>
        <Row toks={[{ t: "cada", at: w("c6", 0), font: "serif" }, { t: "um", at: w("c6", 1), font: "serif" }, { t: "com uma", at: w("c6", 2), small: true, rel: 0.5 }]} gap={0.07} max={130} />
        <Row toks={[{ t: "câmera", at: w("c6", 4), hi: true }]} mt={34} />
        <Row toks={[{ t: "no", at: w("c6", 5), small: true }, { t: "rosto", at: w("c6", 6) }]} gap={0.05} mt={2} />
      </Stack>
      <Cap chunks={cap("c6")} />
    </>
  );
};
export const C7: React.FC<P> = ({ w }) => (
  <Where id="l1" cut="gon_medo" label="Gonjiam" logo="primevideo" logoW={560} logoAt={w("c7", 2)} ink={C.gray} logoColor={C.yellow}
    rows={<Row toks={[{ t: "tá", at: w("c7", 0), small: true }, { t: "no", at: w("c7", 1), small: true }, { t: "Prime", at: w("c7", 2) }, { t: "Video", at: w("c7", 3) }]} gap={0.05} />} />
);

/* ───────────── CTAs ───────────── */
export const E1: React.FC<P> = ({ w }) => (
  <>
    <Badge name="blair_medo" cx={215} cy={1330} r={140} at={w("e1", 2)} bg={C.gray} />
    <Badge name="demo_host" cx={505} cy={1330} r={140} at={w("e1", 4)} bg={C.gray} />
    <Badge name="gon_medo" cx={795} cy={1330} r={140} at={w("e1", 6)} bg={C.gray} />
    <Bookmark x={720} y={SAFE.top + 20} h={250} at={w("e1", 0)} fillAt={w("e1", 0) + 7} stroke={C.white} fill={C.yellow} />
    <Stack>
      <Row toks={[{ t: "salva", at: w("e1", 0), hi: true }]} width={610} />
      <Row toks={[{ t: "pra", at: w("e1", 1), small: true, rel: 0.4 }, { t: "assistir", at: w("e1", 2), font: "serif" }]} gap={0.06} max={170} mt={10} />
      <Row toks={[{ t: "no", at: w("e1", 3), small: true, rel: 0.4 }, { t: "fim", at: w("e1", 4), font: "serif" }, { t: "de", at: w("e1", 5), small: true, rel: 0.4 }, { t: "semana", at: w("e1", 6), font: "serif" }]} gap={0.05} mt={-4} />
    </Stack>
  </>
);
export const E2: React.FC<P> = ({ w }) => {
  const f = useCurrentFrame();
  const cols = [
    { n: "3", cut: "blair_medo", cx: 205 },
    { n: "2", cut: "demo_host", cx: 505 },
    { n: "1", cut: "gon_medo", cx: 805 },
  ];
  const c0 = w("e3", 0);
  const bob = Math.sin(f / 3) * 10;
  return (
    <>
      <Stack>
        <Row toks={[{ t: "qual", at: w("e2", 0) }, { t: "dos", at: w("e2", 1), small: true }, { t: "3", at: w("e2", 2), font: "serif", rel: 1.1 }]} gap={0.06} max={300} />
        <Row toks={[{ t: "te", at: w("e2", 3), small: true }, { t: "dá", at: w("e2", 4), small: true }, { t: "mais", at: w("e2", 5), small: true }, { t: "medo?", at: w("e2", 6), hi: true }]} gap={0.04} />
      </Stack>
      {cols.map((c, i) => (
        <React.Fragment key={i}>
          <Badge name={c.cut} cx={c.cx} cy={1090} r={130} at={w("e2", 2) + i * 3} bg={C.yellow} />
          <BigNum n={c.n} at={w("e2", 2) + i * 3} size={170} x={c.cx - 150} y={900} color={C.black} />
        </React.Fragment>
      ))}
      <Stack top={1270} left={SAFE.left} width={640}>
        <Row toks={[{ t: "comenta", at: c0 }, { t: "aqui", at: w("e3", 1), hi: true }]} gap={0.08} />
      </Stack>
      {f >= c0 ? (
        <svg width={150} height={170} viewBox="0 0 100 110" style={{ position: "absolute", left: 760, top: 1300 + bob, overflow: "visible" }}>
          <path d="M50 4 V92 M14 58 L50 96 L86 58" fill="none" stroke={C.red} strokeWidth={15} strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      ) : null}
    </>
  );
};
export const E4: React.FC<P> = ({ w }) => {
  const { s } = useScene();
  return (
    <>
      <Grid at={s} color={C.gray} max={0.3} />
      <Cut name="blair_olhos" h={640} cx={520} bottom={1965} at={s} from="bottom" />
      <Stack>
        <Row toks={[{ t: "e", at: w("e4", 0), small: true }, { t: "segue", at: w("e4", 1) }]} gap={0.05} max={400} />
        <Row toks={[{ t: "@talking_horror", at: w("e4", 3), font: "serif", hi: true }]} mt={6} />
        <Row toks={[{ t: "pra", at: w("e4", 5), small: true }, { t: "mais", at: w("e4", 6) }]} width={520} gap={0.06} mt={14} />
      </Stack>
    </>
  );
};
