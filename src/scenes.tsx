import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate } from "remotion";
import { C, FAM, SAFE, SAFE_W, W, H } from "./theme";
import { BigNum, Bookmark, Caption, Cut, DashedLink, Grid, Logo, Plane, Row, Stack, Star, Viewfinder, Word, clamp01, outCubic, useScene } from "./kit";

export type WFn = (line: string, i: number) => number;
type P = { w: WFn };

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
        <Img src={staticFile("cut/blair_olhos2.png")} style={{ position: "absolute", left: cross, top: 900, width: 1100, filter: "url(#hblur)", opacity: 0.95 }} />
      ) : null}
      <Viewfinder at={fr[1]} />
      <Stack>
        <Row toks={[{ t: "3", at: fr[0] - 4, font: "serif", rel: 1.3, dy: 0.02 }, { t: "found", at: fr[1], ghost: true }]} gap={0.07} />
        <Row toks={[{ t: "footage", at: fr[2], ghost: true }]} mt={-6} />
        <Row toks={[{ t: "que", at: fr[3], small: true, rel: 0.45 }, { t: "parecem", at: fr[4], font: "serif" }]} width={640} max={150} mt={18} />
        <Row toks={[{ t: "gravação", at: fr[5], font: "serif", rel: 0.52 }, { t: "real", at: fr[6], hi: true }]} mt={6} />
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
    <Row toks={[{ t: "o", at: w("h2", 0), small: true }, { t: "último", at: w("h2", 1), font: "serif" }, { t: "cê", at: w("h2", 2), small: true, rel: 0.45 }, { t: "não", at: w("h2", 3) }]} gap={0.05} />
    <Row toks={[{ t: "termina", at: w("h2", 4) }]} />
    <Row toks={[{ t: "sozinho", at: w("h2", 5), hi: true }]} />
  </>
);
export const GanchoC: React.FC<{ fr: number[] }> = ({ fr }) => {
  const { s } = useScene();
  return (
    <>
      <Grid at={s} color={C.black} max={0.16} />
      <Star cx={520} cy={1470} r={470} at={fr[7]} />
      <Cut name="blair_olhos2" h={640} cx={520} bottom={1800} at={s} from="left" />
      <Viewfinder at={fr[2]} color={C.black} />
      <Stack>
        <Row toks={[{ t: "esse", at: fr[0] }, { t: "filme", at: fr[1] }]} />
        <Row toks={[{ t: "muita", at: fr[2], font: "serif" }, { t: "gente", at: fr[3], font: "serif" }]} width={700} max={150} mt={10} />
        <Row toks={[{ t: "jura", at: fr[4] }, { t: "que", at: fr[5], small: true }, { t: "é", at: fr[6], small: true }, { t: "real", at: fr[7], hi: true }]} mt={10} gap={0.05} />
      </Stack>
    </>
  );
};

/* ───────────── FILMES ───────────── */
const Title: React.FC<{ num: string; numAt: number; numColor: string; children: React.ReactNode; left?: number; top?: number }> = ({ num, numAt, numColor, children, left = 330, top = 300 }) => (
  <>
    <BigNum n={num} at={numAt} size={640} x={SAFE.left - 20} y={190} color={numColor} />
    <Stack left={left} width={W - SAFE.right - left} top={top}>{children}</Stack>
  </>
);
export const F3: React.FC<P & { phone: React.ReactNode }> = ({ w, phone }) => {
  const t = w("f3b", 0);
  return (
    <>
      {phone}
      <Star cx={520} cy={1400} r={520} at={t} />
      <Cut name="blair_olhos2" h={660} cx={520} bottom={1730} at={t} />
      <Title num="3" numAt={w("f3a", 0)} numColor={C.red}>
        <Row toks={[{ t: "A", at: t, font: "serif", rel: 0.5 }, { t: "Bruxa", at: w("f3b", 1), font: "serif" }]} gap={0.05} />
        <Row toks={[{ t: "de", at: w("f3b", 2), font: "serif", rel: 0.5 }, { t: "Blair", at: w("f3b", 3), font: "serif" }]} gap={0.05} mt={-10} />
      </Title>
    </>
  );
};
export const F3c: React.FC<P> = ({ w }) => {
  const { s } = useScene();
  return (
    <>
      {/* recorte duplicado: cópia pequena ao fundo, grande na frente */}
      <Cut name="blair_medo" h={470} cx={770} bottom={1420} at={s + 3} opacity={0.55} rot={6} />
      <Cut name="blair_medo" h={1000} cx={400} bottom={1990} at={s} from="bottom" rot={-3} />
      <Stack>
        <Row toks={[{ t: "juraram", at: w("f3c", 0) }]} />
        <Row toks={[{ t: "que", at: w("f3c", 1), font: "serif", rel: 0.42 }, { t: "era", at: w("f3c", 2), font: "serif", rel: 0.42 }, { t: "real", at: w("f3c", 3), hi: true }]} gap={0.05} mt={-4} />
      </Stack>
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
      <Star cx={300} cy={1090} r={245} at={s + 1} points={14} />
      <Cut name={cut} h={400} cx={300} bottom={1290} at={s + 1} from="left" />
      <DashedLink id={id} d={`M 540 1010 C 780 960, 900 1080, ${lx + logoW * 0.6} ${ly - 28}`} at={logoAt - 5} color={ink} />
      <Logo name={logo} w={logoW} x={lx} y={ly} color={logoColor} at={logoAt} />
    </>
  );
};
export const F3d: React.FC<P> = ({ w }) => (
  <Where id="l3" cut="blair_medo" label="A Bruxa de Blair" logo="netflix" logoW={600} logoAt={w("f3d", 2)} ink={C.white} logoColor={C.white}
    rows={<Row toks={[{ t: "tá", at: w("f3d", 0), small: true }, { t: "na", at: w("f3d", 1), small: true }, { t: "Netflix", at: w("f3d", 2) }]} gap={0.05} />} />
);
export const M1: React.FC<P> = ({ w }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="demo_host" h={640} cx={520} bottom={1700} at={s} sil />
      <Q x={430} y={1130} at={w("m1", 1)} size={360} color={C.red} />
      <Stack>
        <Row toks={[{ t: "o", at: w("m1", 0), small: true }, { t: "próximo", at: w("m1", 1) }]} gap={0.05} />
        <Row toks={[{ t: "é", at: w("m1", 2), small: true }, { t: "pior", at: w("m1", 3), hi: true }]} gap={0.05} max={400} />
      </Stack>
    </>
  );
};
export const F2: React.FC<P> = ({ w }) => {
  const t = w("f2b", 0);
  const f = useCurrentFrame();
  const { s } = useScene();
  return (
    <>
      <Grid at={s} color={C.gray} max={0.22} />
      {f < t ? <Cut name="demo_host" h={860} cx={540} bottom={1965} at={s} from="bottom" sil /> : null}
      <Star cx={540} cy={1400} r={500} at={t} />
      <Cut name="demo_host" h={940} cx={540} bottom={1965} at={t} />
      <Title num="2" numAt={w("f2a", 0)} numColor={C.yellow} left={345} top={320}>
        <Row toks={[{ t: "Entrevista", at: t, font: "serif" }]} />
        <Row toks={[{ t: "com", at: w("f2b", 1), font: "serif", rel: 0.5 }, { t: "o", at: w("f2b", 2), font: "serif", rel: 0.5 }, { t: "Demônio", at: w("f2b", 3), font: "serif" }]} gap={0.05} mt={-6} />
      </Title>
    </>
  );
};
export const F2c: React.FC<P> = ({ w }) => {
  const f = useCurrentFrame();
  const { s } = useScene();
  const blink = Math.floor((f - s) / 6) % 2 === 0;
  return (
    <>
      <Cut name="demo_grito" h={1230} cx={600} bottom={1960} at={s} from="right" drift={0.12} />
      <Stack>
        <Row toks={[{ t: "ao", at: w("f2c", 2), hi: true }, { t: "vivo", at: w("f2c", 3), hi: true }]} width={620} />
      </Stack>
      {f >= w("f2c", 2) ? <div style={{ position: "absolute", left: SAFE.left + 660, top: SAFE.top + 70, width: 80, height: 80, borderRadius: 40, background: C.red, opacity: blink ? 1 : 0.15 }} /> : null}
      <Caption color={C.gray} bg={C.black} chunks={[{ t: "talk show", at: w("f2c", 0) }, { t: "ao vivo", at: w("f2c", 2) }, { t: "que dá", at: w("f2c", 4) }, { t: "errado", at: w("f2c", 6) }]} />
    </>
  );
};
export const F2d: React.FC<P> = ({ w }) => (
  <Where id="l2" cut="demo_menina" label="Entrevista com o Demônio" logo="hbomax" logoW={350} logoAt={w("f2d", 1)} ink={C.white} logoColor={C.white}
    rows={<Row toks={[{ t: "na", at: w("f2d", 0), small: true }, { t: "HBO", at: w("f2d", 1) }, { t: "Max", at: w("f2d", 2) }]} gap={0.06} />} />
);
export const S1: React.FC<P> = ({ w }) => {
  const { s } = useScene();
  return (
    <>
      <Cut name="blair_medo" h={600} cx={330} bottom={1960} at={s} from="bottom" />
      <Plane x={610} y={1290} s={250} at={w("s1", 0)} color={C.yellow} />
      <Stack>
        <Row toks={[{ t: "manda", at: w("s1", 0) }]} max={360} />
        <Row toks={[{ t: "pra", at: w("s1", 1), small: true, rel: 0.4 }, { t: "quem", at: w("s1", 2), small: true, rel: 0.4 }, { t: "não", at: w("s1", 3), font: "serif" }, { t: "tem", at: w("s1", 4), font: "serif" }]} gap={0.06} max={200} />
        <Row toks={[{ t: "medo", at: w("s1", 5), hi: true }]} max={400} />
      </Stack>
    </>
  );
};
export const F1: React.FC<P> = ({ w }) => {
  const t = w("f1b", 0);
  const f = useCurrentFrame();
  const { s } = useScene();
  return (
    <>
      {f < t ? <Cut name="gon_medo" h={860} cx={540} bottom={1965} at={s} from="bottom" sil /> : null}
      <Star cx={540} cy={1400} r={520} at={t} />
      <Cut name="gon_medo" h={940} cx={540} bottom={1965} at={t} />
      <Title num="1" numAt={w("f1a", 0)} numColor={C.yellow} left={300} top={330}>
        <Row toks={[{ t: "Gonjiam", at: t, font: "serif" }]} />
        <Row toks={[{ t: "manicômio", at: t + 4 }, { t: "assombrado", at: t + 7 }]} mt={14} />
      </Title>
    </>
  );
};
export const F1c: React.FC<P> = ({ w }) => {
  const f = useCurrentFrame();
  const { s } = useScene();
  const blink = Math.floor((f - s) / 6) % 2 === 0;
  return (
    <>
      <Cut name="gon_predio" h={640} cx={520} bottom={1900} at={s} from="bottom" />
      <Cut name="gon_grupo" h={330} cx={560} bottom={1930} at={w("f1c", 2)} from="right" />
      <Viewfinder at={w("f1c", 0)} color={C.black} />
      <Stack>
        <Row toks={[{ t: "live", at: w("f1c", 0), hi: true }, { t: "num", at: w("f1c", 1), small: true }]} width={520} max={300} gap={0.06} />
        <Row toks={[{ t: "manicômio", at: w("f1c", 2) }]} mt={16} />
        <Row toks={[{ t: "abandonado", at: w("f1c", 3), font: "serif" }]} max={170} mt={4} />
        <Row toks={[{ t: "de", at: w("f1c", 4), small: true }, { t: "verdade", at: w("f1c", 5) }]} gap={0.05} mt={8} />
      </Stack>
      <div style={{ position: "absolute", left: SAFE.left + 640, top: SAFE.top + 70, width: 76, height: 76, borderRadius: 38, background: C.red, opacity: blink ? 1 : 0.15 }} />
    </>
  );
};
export const F1d: React.FC<P> = ({ w }) => (
  <Where id="l1" cut="gon_medo" label="Gonjiam" logo="primevideo" logoW={560} logoAt={w("f1d", 1)} ink={C.gray} logoColor={C.yellow}
    rows={<Row toks={[{ t: "no", at: w("f1d", 0), small: true }, { t: "Prime", at: w("f1d", 1) }, { t: "Video", at: w("f1d", 2) }]} gap={0.06} />} />
);

/* ───────────── CTAs ───────────── */
export const C1: React.FC<P> = ({ w }) => (
  <>
    <Cut name="blair_medo" h={360} cx={225} bottom={1500} at={w("c1", 1)} />
    <Cut name="demo_host" h={430} cx={520} bottom={1500} at={w("c1", 2)} />
    <Cut name="gon_medo" h={380} cx={790} bottom={1500} at={w("c1", 4)} />
    <Bookmark x={720} y={SAFE.top + 20} h={250} at={w("c1", 0)} fillAt={w("c1", 0) + 7} stroke={C.white} fill={C.yellow} />
    <Stack>
      <Row toks={[{ t: "salva", at: w("c1", 0), hi: true }]} width={610} />
      <Row toks={[{ t: "pro", at: w("c1", 1), small: true, rel: 0.4 }, { t: "fim", at: w("c1", 2), font: "serif" }, { t: "de", at: w("c1", 3), small: true, rel: 0.4 }]} width={600} max={230} gap={0.06} mt={10} />
      <Row toks={[{ t: "semana", at: w("c1", 4), font: "serif" }]} mt={-10} />
    </Stack>
  </>
);
export const C2: React.FC<P> = ({ w }) => {
  const f = useCurrentFrame();
  const two = w("c2", 5);
  const shake = f >= two ? Math.sin((f - two) * 2.4) * Math.max(0, 14 - (f - two)) : 0;
  const strike = outCubic(clamp01((f - two + 1) / 5));
  const cols = [
    { n: "3", cut: "blair_medo", cx: 215, h: 300 },
    { n: "2", cut: "demo_host", cx: 510, h: 330 },
    { n: "1", cut: "gon_medo", cx: 800, h: 300 },
  ];
  return (
    <>
      <Stack>
        <Row toks={[{ t: "qual", at: w("c2", 0) }, { t: "dá", at: w("c2", 1), small: true }, { t: "mais", at: w("c2", 2), small: true }]} gap={0.05} max={330} />
        <Row toks={[{ t: "medo?", at: w("c2", 3), hi: true }]} max={400} />
      </Stack>
      {cols.map((c, i) => (
        <div key={i} style={{ position: "absolute", left: 0, top: 0, width: W, height: H, transform: i === 1 ? `translateX(${shake}px)` : undefined }}>
          <Cut name={c.cut} h={c.h} cx={c.cx} bottom={1340} at={w("c2", 3) + i * 2} />
          <BigNum n={c.n} at={w("c2", 3) + i * 2} size={250} x={c.cx - 110} y={985} color={C.black} />
        </div>
      ))}
      {f >= two ? (
        <svg width={W} height={H} style={{ position: "absolute" }}>
          <line x1={370} y1={1320} x2={370 + 290 * strike} y2={1320 - 330 * strike} stroke={C.red} strokeWidth={26} strokeLinecap="round" />
          <line x1={370} y1={990} x2={370 + 290 * strike} y2={990 + 330 * strike} stroke={C.red} strokeWidth={26} strokeLinecap="round" />
        </svg>
      ) : null}
      <Caption color={C.gray} bg={C.black} y={1395} chunks={[{ t: "o 2", at: w("c2", 4) }, { t: "nem devia", at: w("c2", 6) }, { t: "tá aqui", at: w("c2", 8) }]} />
    </>
  );
};
export const C3: React.FC<P> = ({ w }) => {
  const { s } = useScene();
  return (
    <>
      <Grid at={s} color={C.gray} max={0.3} />
      <Cut name="blair_olhos2" h={560} cx={520} bottom={1900} at={s} from="bottom" />
      <Stack>
        <Row toks={[{ t: "segue", at: w("c3", 0) }]} max={400} />
        <Row toks={[{ t: "@talking_horror", at: w("c3", 2), font: "serif", hi: true }]} mt={6} />
        <Row toks={[{ t: "pra", at: w("c3", 4), small: true }, { t: "mais", at: w("c3", 5) }]} width={520} gap={0.06} mt={14} />
      </Stack>
    </>
  );
};
