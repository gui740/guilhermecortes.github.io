import React from "react";
import { AbsoluteFill, Freeze, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FAIXA, FONT, MONO, SOMBRA } from "../theme";
import { CRTOverlay, Carimbo, Faixa, Kinetic, Legenda, LowerThird, Medidor, Mono, NLogo, Picto, ease, useEntra, useMola } from "./bits";

type P = { c: any; dur: number; trecho: any };

/* ------------------------------------------------------------------ ARQUIVO (CRT) */
const Arquivo: React.FC<P> = ({ c, trecho }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pre = Math.round((trecho.pre ?? 0) * fps);
  const clipF = Math.round(c.clipDur * fps);
  const fimClip = pre + clipF;
  const total = Math.round(trecho.dur * fps);
  // liga a TV: cresce na vertical a partir de uma linha
  const liga = interpolate(f - pre, [0, 6], [0.004, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const flash = interpolate(f - pre, [0, 2, 6], [1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const push = interpolate(f, [pre, fimClip], [1, 1.06], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // saída: frame congelado que encolhe e se isola no branco (ou desliga como TV, no hook)
  const saida = interpolate(f, [fimClip, total], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const desliga = !!c.desliga;
  const sx = desliga ? interpolate(saida, [0, 0.5, 1], [1, 1, 0.002]) : 1;
  const sy = desliga ? interpolate(saida, [0, 0.45, 1], [1, 0.004, 0.004]) : 1;
  const enc = desliga ? 1 : interpolate(saida, [0, 1], [1, 0.6]);
  const video = (
    <OffthreadVideo src={staticFile(c.clip)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
  );
  return (
    <AbsoluteFill style={{ backgroundColor: f < pre ? C.branco : f >= fimClip ? C.branco : "black" }}>
      <AbsoluteFill style={{ transform: `scale(${enc}) scaleY(${liga * sy}) scaleX(${sx})`, boxShadow: f >= fimClip && !desliga ? SOMBRA : "none" }}>
        <AbsoluteFill style={{ backgroundColor: "black", transform: `scale(${push})` }}>
          {f >= pre && (f < fimClip ? <Sequence from={pre} layout="none">{video}</Sequence> :
            <Freeze frame={Math.max(0, clipF - 2)}>{video}</Freeze>)}
        </AbsoluteFill>
        <CRTOverlay />
        <AbsoluteFill style={{ background: "white", opacity: flash }} />
      </AbsoluteFill>
      {f >= pre && f < fimClip + 4 && (
        <>
          <LowerThird {...c.lt} delay={pre + 8} />
          <Sequence from={pre} layout="none"><Legenda linhas={c.legenda} dur={c.clipDur} /></Sequence>
        </>
      )}
      {c.poster && f >= pre && f < fimClip && <PosterLateral src={c.poster} />}
      {c.estrelas && f >= pre && f < fimClip && <Estrelas />}
    </AbsoluteFill>
  );
};

const PosterLateral: React.FC<{ src: string }> = ({ src }) => {
  const k = useEntra(40, 16);
  return (
    <div style={{ position: "absolute", right: 120, top: 250, width: 300, opacity: k, transform: `translateX(${(1 - k) * 60}px)` }}>
      <Img src={staticFile(src)} style={{ width: "100%", boxShadow: SOMBRA, border: "6px solid white" }} />
      <Mono size={14} cor="#DDD" style={{ marginTop: 10 }}>HOUSE OF CARDS · NETFLIX · 2013</Mono>
    </div>
  );
};

const Estrelas: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: 120, top: 300, display: "flex", flexDirection: "column", gap: 18 }}>
      <Mono size={16} cor="#DDD">NOTA DADA</Mono>
      <div style={{ display: "flex", gap: 10 }}>
        {[0, 1, 2, 3, 4].map((i) => (
          <svg key={i} width={46} height={46} viewBox="0 0 24 24" style={{ opacity: f > 20 + i * 6 ? 1 : 0.15 }}>
            <path d="M12 2l3 7h7l-5.5 4.5L18.5 21 12 16.8 5.5 21l2-7.5L2 9h7z" fill={C.ambar} />
          </svg>
        ))}
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ COR (material da Netflix, sem filtro) */
const Cor: React.FC<P> = ({ c, trecho }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pre = Math.round((trecho.pre ?? 0) * fps);
  const fimClip = pre + Math.round(c.clipDur * fps);
  const k = interpolate(f - pre, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      {f >= pre && f < fimClip && (
        <AbsoluteFill style={{ opacity: k }}>
          <Sequence from={pre} layout="none"><OffthreadVideo src={staticFile(c.clip)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} /></Sequence>
          <LowerThird {...c.lt} delay={pre + 6} />
          <Sequence from={pre} layout="none"><Legenda linhas={c.legenda} dur={c.clipDur} /></Sequence>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

const CorClip: React.FC<P> = ({ c }) => (
  <AbsoluteFill><OffthreadVideo src={staticFile(c.clip)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} /></AbsoluteFill>
);

/* ------------------------------------------------------------------ TV desenhada (comercial #FU2016) */
const TV: React.FC<P> = ({ c, trecho }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pre = Math.round((trecho.pre ?? 0) * fps);
  const fimClip = pre + Math.round(c.clipDur * fps);
  const k = useMola(0, 16);
  const sw = 1100, sh = 619;
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
      <div style={{ transform: `scale(${interpolate(k, [0, 1], [0.9, 1])})`, opacity: k }}>
        <div style={{ background: C.tinta, padding: "34px 34px 70px", borderRadius: 34, boxShadow: SOMBRA, position: "relative" }}>
          <div style={{ width: sw, height: sh, borderRadius: 26, overflow: "hidden", background: "black", position: "relative" }}>
            {f >= pre && f < fimClip && (
              <Sequence from={pre} layout="none"><OffthreadVideo src={staticFile(c.clip)} muted style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scale(1.2)", transformOrigin: "50% 8%" }} /></Sequence>
            )}
            <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.12) 0px, rgba(0,0,0,0.12) 1px, transparent 1px, transparent 3px)", borderRadius: 26 }} />
          </div>
          <div style={{ position: "absolute", bottom: 22, right: 50, display: "flex", gap: 16 }}>
            {[0, 1].map((i) => <div key={i} style={{ width: 26, height: 26, borderRadius: 13, border: `3px solid ${C.apoio}` }} />)}
          </div>
        </div>
      </div>
      {f >= pre && f < fimClip && (
        <>
          <LowerThird {...c.lt} delay={pre + 6} />
          <Sequence from={pre} layout="none"><Legenda linhas={c.legenda} dur={c.clipDur} /></Sequence>
        </>
      )}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ FICHA DE EVIDÊNCIA */
const Evidencia: React.FC<P> = ({ c, dur }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const entra = useMola(0, 17);
  const cw = 1180, ch = 700;
  const tr: number[] = c.trecho ?? [0.05, 0.3, 0.9, 0.1];
  const iw = c.w, ih = c.h;
  // escala para o trecho ocupar ~88% da largura do cartão
  const base = Math.min((cw * 0.88) / (tr[2] * iw), (ch * 0.9) / (tr[3] * ih * 3.2));
  const zoom = interpolate(f, [0, dur * fps], [0.92, 1.04], { extrapolateRight: "clamp" });
  const s = base * zoom;
  const cxImg = (tr[0] + tr[2] / 2) * iw, cyImg = (tr[1] + tr[3] / 2) * ih;
  const left = cw / 2 - cxImg * s, top = ch / 2 - cyImg * s;
  const sub = interpolate(f, [14, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const temFrase = !!c.frase;
  const fraseK = temFrase ? interpolate(f, [dur * fps * 0.42, dur * fps * 0.42 + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease }) : 0;
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: cw, height: ch, position: "relative", overflow: "hidden", background: "white", boxShadow: SOMBRA,
        transform: `translateY(${(1 - entra) * 80}px) scale(${1 - fraseK * 0.06})`, opacity: Math.min(1, entra * 1.5) * (1 - fraseK * 0.9) }}>
        <Img src={staticFile(c.img)} style={{ position: "absolute", left, top, width: iw * s, height: ih * s, maxWidth: "none" }} />
        <div style={{ position: "absolute", left: cw / 2 - (tr[2] * iw * s) / 2, top: ch / 2 - (tr[3] * ih * s) / 2 - 6,
          width: tr[2] * iw * s, height: tr[3] * ih * s + 12, background: "rgba(41,41,41,0.06)" }} />
        <div style={{ position: "absolute", left: cw / 2 - (tr[2] * iw * s) / 2, top: ch / 2 + (tr[3] * ih * s) / 2 + 8,
          width: tr[2] * iw * s * sub, height: 4, background: C.tinta }} />
      </div>
      <div style={{ position: "absolute", left: FAIXA.x + 12, top: 150 + (1 - entra) * 80 }}>
        <Carimbo texto={c.carimbo} />
      </div>
      {temFrase && fraseK > 0 && (
        <Faixa style={{ opacity: fraseK }}>
          <Kinetic texto={c.frase} size={50} delay={Math.round(dur * fps * 0.42)} passo={2} />
        </Faixa>
      )}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ TIPOGRAFIA */
const Titulo: React.FC<P> = ({ c }) => {
  const size = c.grande ? (c.texto.length <= 5 ? 230 : 104) : c.texto.length > 26 ? 66 : 82;
  const k = useEntra(10, 14);
  return (
    <Faixa>
      <Kinetic texto={c.texto} size={size} />
      {c.sub && <Mono size={20} style={{ marginTop: 26, opacity: k }}>{c.sub}</Mono>}
    </Faixa>
  );
};

const Pergunta: React.FC<P> = ({ c }) => (
  <Faixa>
    <div style={{ marginBottom: 34 }}><Carimbo texto={c.rotulo} delay={4} /></div>
    <Kinetic texto={c.texto} size={c.texto.length > 30 ? 60 : 96} delay={8} />
  </Faixa>
);

const Citacao: React.FC<P> = ({ c }) => {
  const k = useEntra(16, 14);
  return (
    <Faixa>
      <Kinetic texto={c.texto} size={c.texto.length > 50 ? 50 : 62} peso={700} passo={2} />
      <Mono size={18} cor={C.tinta} style={{ marginTop: 30, opacity: k }}>{c.credito}</Mono>
      {c.nota && <div style={{ fontFamily: FONT, fontSize: 19, color: C.secundario, marginTop: 18, opacity: k, maxWidth: 560 }}>{c.nota}</div>}
    </Faixa>
  );
};

const Lista: React.FC<P> = ({ c, dur }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const riscarEm = (c.riscarEm ?? 2) * dur * fps;
  return (
    <Faixa>
      {c.titulo && <Mono size={20} cor={C.tinta} style={{ marginBottom: 24 }}>{c.titulo}</Mono>}
      {c.itens.map((it: string, i: number) => {
        const k = interpolate(f - i * 7, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
        return (
          <div key={i} style={{ fontFamily: FONT, fontWeight: 800, fontSize: c.itens.length > 5 ? 50 : 70, lineHeight: 1.08, color: C.tinta,
            opacity: k, transform: `translateY(${(1 - k) * 30}px)` }}>{it}</div>
        );
      })}
      {(c.riscados ?? []).map((it: string, i: number) => {
        const k = interpolate(f - riscarEm - i * 6, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
        const risco = interpolate(f - riscarEm - i * 6 - 8, [0, 10], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <div key={"r" + i} style={{ position: "relative", fontFamily: FONT, fontWeight: 800, fontSize: 70, lineHeight: 1.08, color: C.apoio, opacity: k }}>
            {it}
            <div style={{ position: "absolute", left: 0, top: "52%", height: 6, width: `${risco}%`, background: C.tinta }} />
          </div>
        );
      })}
    </Faixa>
  );
};

const Abertura: React.FC<P> = ({ c }) => {
  const k = useEntra(0, 16);
  const k2 = useEntra(30, 16);
  return (
    <Faixa>
      <Mono size={20} cor={C.tinta} style={{ opacity: k, marginBottom: 40 }}>BRAND BY IZOTON · {c.ep}</Mono>
      <div style={{ opacity: k, marginBottom: 56 }}><NLogo altura={150} /></div>
      <Kinetic texto={c.titulo} size={62} delay={14} />
      <div style={{ opacity: k2, marginTop: 18 }}><Kinetic texto={c.sub} size={62} peso={500} cor={C.secundario} delay={30} /></div>
    </Faixa>
  );
};

const Fim: React.FC<P> = ({ c, dur }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const k = useEntra(0, 18);
  const off = interpolate(f, [dur * fps - 40, dur * fps - 20], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <Faixa style={{ opacity: off }}>
      <div style={{ opacity: k }}><Picto nome="ATOMO" size={110} /></div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.tinta, marginTop: 26, opacity: k, letterSpacing: 2 }}>{c.marca}</div>
      <Mono size={20} style={{ marginTop: 18, opacity: k }}>{c.sub}</Mono>
    </Faixa>
  );
};

const Respiro: React.FC<P> = ({ c }) => {
  const k = useEntra(0, 12);
  const r = useCurrentFrame() * 0.6;
  return (
    <Faixa>
      <div style={{ opacity: k, transform: `rotate(${r}deg)` }}><Picto nome="ATOMO" size={70} cor={C.secundario} /></div>
      <Mono size={22} cor={C.tinta} style={{ marginTop: 22, opacity: k }}>{String(c.num).padStart(2, "0")} / {c.titulo}</Mono>
    </Faixa>
  );
};

/* ------------------------------------------------------------------ DADOS E DIAGRAMAS */
const MedidorCena: React.FC<P> = ({ c }) => <Faixa><Medidor rotulo={c.rotulo} marcas={c.marcas} de={c.de} ate={c.ate} /></Faixa>;

const Contador: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const k = useEntra(4, 12);
  const digitos = c.valor.replace(/\D/g, "");
  const num = parseInt(digitos || "0", 10);
  const prog = interpolate(f, [0, 34], [0, 1], { extrapolateRight: "clamp", easing: ease });
  let mostra = c.valor;
  if (/^[\d.]+$/.test(c.valor) && num > 0) {
    mostra = Math.round(num * prog).toLocaleString("pt-BR");
  }
  const size = mostra.length > 9 ? 92 : mostra.length > 6 ? 118 : 170;
  return (
    <Faixa>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: size, color: C.tinta, letterSpacing: -2, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>{mostra}</div>
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 34, color: C.tinta, marginTop: 16, opacity: k }}>{c.sufixo}</div>
      <Mono size={18} style={{ marginTop: 20, opacity: k }}>{c.rotulo}</Mono>
      {c.nota && <Mono size={16} cor={C.tinta} style={{ marginTop: 12, opacity: k }}>{c.nota}</Mono>}
    </Faixa>
  );
};

const Botao: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const press = interpolate(f, [8, 11, 15], [1, 0.9, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const k = useEntra(18, 12);
  const prog = interpolate(f, [18, 54], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  return (
    <Faixa>
      <div style={{ transform: `scale(${press})`, border: `4px solid ${C.tinta}`, borderRadius: 8, padding: "20px 34px", display: "flex", alignItems: "center", gap: 18,
        background: f > 10 ? C.tinta : C.branco, color: f > 10 ? C.branco : C.tinta, fontFamily: FONT, fontWeight: 700, fontSize: 40 }}>
        <svg width="40" height="40" viewBox="0 0 24 24"><path d="M3 5l8 7-8 7zM12 5l8 7-8 7z" fill="currentColor" /></svg>
        {c.texto}
      </div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 104, color: C.tinta, marginTop: 50, opacity: k, fontVariantNumeric: "tabular-nums" }}>
        {Math.round(136000000 * prog).toLocaleString("pt-BR")}
      </div>
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 34, color: C.tinta, opacity: k }}>{c.sufixo}</div>
      <Mono size={16} cor={C.tinta} style={{ marginTop: 16, opacity: k }}>{c.nota}</Mono>
    </Faixa>
  );
};

const Fluxo: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  return (
    <Faixa>
      <Mono size={20} cor={C.tinta} style={{ marginBottom: 28 }}>{c.rotulo}</Mono>
      {c.itens.map((it: string, i: number) => {
        const k = interpolate(f - i * 16, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
        return (
          <React.Fragment key={i}>
            {i > 0 && <div style={{ width: 3, height: 34 * k, background: C.tinta }} />}
            <div style={{ border: `3px solid ${C.tinta}`, padding: "16px 26px", width: 460, fontFamily: MONO, fontSize: 24, letterSpacing: 2, color: C.tinta,
              opacity: k, transform: `translateY(${(1 - k) * 18}px)`, background: i === 2 ? C.tinta : C.branco, ...(i === 2 ? { color: C.branco } : {}) }}>{it}</div>
          </React.Fragment>
        );
      })}
    </Faixa>
  );
};

const Linha: React.FC<P> = ({ c, dur }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = c.itens.length;
  const prog = interpolate(f, [0, Math.min(dur * fps, 9 * fps)], [0, 1], { extrapolateRight: "clamp" });
  const ativo = Math.min(n - 1, Math.floor(prog * n));
  const passo = 360;
  const desloc = interpolate(prog * (n - 1), [0, n - 1], [0, (n - 1) * passo]);
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 560, height: 3, background: C.tinta }} />
      <div style={{ position: "absolute", left: 960 - desloc, top: 380, display: "flex" }}>
        {c.itens.map((it: string, i: number) => (
          <div key={i} style={{ width: passo, marginLeft: i === 0 ? -passo / 2 : 0, display: "flex", flexDirection: "column", alignItems: "center",
            opacity: i === ativo ? 1 : 0.28, transform: `scale(${i === ativo ? 1.15 : 0.9})` }}>
            <Picto nome={it} size={120} />
            <div style={{ width: 16, height: 16, borderRadius: 8, background: C.tinta, marginTop: 28 }} />
            <Mono size={20} cor={C.tinta} style={{ marginTop: 22 }}>{it}</Mono>
          </div>
        ))}
      </div>
      <Mono size={18} style={{ position: "absolute", top: 230, left: FAIXA.x, width: FAIXA.w, textAlign: "center" }}>TECNOLOGIAS DE CONTROLE DA TV</Mono>
    </AbsoluteFill>
  );
};

const Envelope: React.FC<P> = ({ c, dur }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const k = useMola(4, 15);
  const porta = c.porta ? interpolate(f, [0, dur * fps], [1, 1.9], { easing: ease }) : 1;
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", fontFamily: FONT, fontWeight: 800, fontSize: 420, color: "#F1F1F1", letterSpacing: -10 }}>{c.ano}</div>
      <div style={{ transform: `scale(${k * porta})`, filter: "drop-shadow(18px 18px 22px rgba(0,0,0,0.22))" }}>
        <svg width="460" height="300" viewBox="0 0 460 300">
          <rect x="0" y="0" width="460" height="300" rx="10" fill={C.netflix} />
          <path d="M 0 10 L 230 170 L 460 10" fill="none" stroke={C.netflixEscuro} strokeWidth="10" />
          <rect x="300" y="200" width="120" height="60" fill="none" stroke="#FFFFFF" strokeWidth="4" opacity="0.8" />
        </svg>
      </div>
      <Mono size={22} cor={C.tinta} style={{ position: "absolute", bottom: 210, left: FAIXA.x, width: FAIXA.w, textAlign: "center", opacity: k }}>{c.rotulo}</Mono>
    </AbsoluteFill>
  );
};

const Posters: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const n = c.imgs.length;
  const w = n === 1 ? 430 : 330;
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", gap: 40, alignItems: "flex-end" }}>
        {c.imgs.map((src: string, i: number) => {
          const k = interpolate(f - i * 10, [0, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
          const pb = c.pb?.[i];
          return (
            <div key={i} style={{ width: pb ? w * 0.82 : w, opacity: k, transform: `translateY(${(1 - k) * 60}px)`, display: "flex", flexDirection: "column", alignItems: "center" }}>
              <Img src={staticFile(src)} style={{ width: "100%", boxShadow: SOMBRA, border: "8px solid white", filter: pb ? "grayscale(1) contrast(1.1)" : "none" }} />
              <Mono size={17} cor={C.tinta} style={{ marginTop: 18 }}>{c.rotulos?.[i]}</Mono>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Mapa: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const pts = Array.from({ length: 46 }, (_, i) => ({ x: 120 + ((i * 397) % 1680), y: 220 + ((i * 251) % 620) }));
  const k = useEntra(0, 20);
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <svg width="1920" height="1080" style={{ position: "absolute" }}>
        {pts.map((p, i) => i > 0 && i % 3 !== 0 ? (
          <line key={"l" + i} x1={pts[i - 1].x} y1={pts[i - 1].y} x2={p.x} y2={p.y} stroke={C.apoio} strokeWidth={1.5} opacity={k} />
        ) : null)}
        {pts.map((p, i) => <circle key={i} cx={p.x} cy={p.y} r={f > i * 1.2 ? 6 : 0} fill={i % 5 === 0 ? C.tinta : C.secundario} />)}
      </svg>
      <Faixa>
        <div style={{ background: C.branco, padding: "30px 20px" }}>
          <Kinetic texto={c.titulo} size={62} />
          {c.pontos?.length > 0 && <Mono size={22} cor={C.tinta} style={{ marginTop: 22 }}>{c.pontos.join(" · ")}</Mono>}
          <Mono size={18} style={{ marginTop: 14 }}>{c.sub}</Mono>
        </div>
      </Faixa>
    </AbsoluteFill>
  );
};

const Cheque: React.FC<P> = ({ c }) => {
  const k = useMola(0, 16);
  return (
    <Faixa>
      <div style={{ width: 580, height: 270, border: `4px solid ${C.tinta}`, background: C.branco, position: "relative", transform: `scale(${k})`, boxShadow: SOMBRA,
        display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
        <Mono size={16} cor={C.tinta} style={{ position: "absolute", top: 18, left: 22 }}>PAGUE A QUEM MELHORAR O ALGORITMO</Mono>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 62, color: C.tinta, whiteSpace: "nowrap" }}>{c.valor}</div>
        <div style={{ position: "absolute", right: -30, bottom: -26 }}><Carimbo texto={c.carimbo} delay={18} style={{ fontSize: 40, padding: "8px 18px", borderWidth: 4 }} /></div>
      </div>
      <Mono size={20} cor={C.tinta} style={{ marginTop: 50 }}>{c.rotulo}</Mono>
    </Faixa>
  );
};

const Colunas: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const barra = interpolate(f, [16, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  return (
    <Faixa style={{ flexDirection: "row", gap: 40 }}>
      <div style={{ width: 270, display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
        <Mono size={18} cor={C.tinta}>{c.esquerda}</Mono>
        <div style={{ display: "flex" }}>{[0, 1, 2, 3, 4].map((i) => (
          <svg key={i} width={46} height={46} viewBox="0 0 24 24" style={{ opacity: f > i * 4 ? 1 : 0.15 }}><path d="M12 2l3 7h7l-5.5 4.5L18.5 21 12 16.8 5.5 21l2-7.5L2 9h7z" fill={C.tinta} /></svg>
        ))}</div>
        <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 26, color: C.tinta }}>A LISTA DE SCHINDLER</div>
      </div>
      <div style={{ width: 3, height: 340, background: C.apoio }} />
      <div style={{ width: 270, display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
        <Mono size={18} cor={C.tinta}>{c.direita}</Mono>
        <div style={{ width: 70, height: 220, border: `3px solid ${C.tinta}`, display: "flex", alignItems: "flex-end" }}>
          <div style={{ width: "100%", height: `${barra * 100}%`, background: C.tinta }} />
        </div>
        <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 26, color: C.tinta }}>ADAM SANDLER</div>
      </div>
    </Faixa>
  );
};

const Pessoas: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const corta = interpolate(f, [20, 60], [0, 40], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const k = useEntra(60, 14);
  return (
    <Faixa>
      <Mono size={20} cor={C.tinta} style={{ marginBottom: 20 }}>{c.ano} · DEMISSÃO DE UM TERÇO</Mono>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 44px)", gap: 4 }}>
        {Array.from({ length: c.de }, (_, i) => (
          <Picto key={i} nome="PESSOA" size={44} cor={i >= c.de - corta ? C.apoio : C.tinta} />
        ))}
      </div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 92, color: C.tinta, marginTop: 24 }}>
        {c.de} → {Math.round(c.de - corta)}
      </div>
      <Mono size={20} cor={C.tinta} style={{ opacity: k, marginTop: 6 }}>E FIZERAM MAIS ↑</Mono>
    </Faixa>
  );
};

const Anzol: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const sw = interpolate(f, [0, 30], [0, 1], { extrapolateRight: "clamp" });
  return (
    <Faixa>
      <svg width="360" height="300" viewBox="0 0 360 300">
        <line x1="180" y1="0" x2="180" y2={120 * sw} stroke={C.tinta} strokeWidth="3" />
        <path d="M 180 120 L 180 170 Q 180 205 150 205 Q 125 205 125 182" fill="none" stroke={C.tinta} strokeWidth="5" strokeLinecap="round" opacity={sw} />
        <g transform={`translate(${70 + 40 * sw} 240)`} opacity={sw}>
          <path d="M 0 0 Q 60 -40 140 0 Q 60 40 0 0 Z" fill="none" stroke={C.tinta} strokeWidth="4" />
          <path d="M 140 0 L 180 -26 L 180 26 Z" fill="none" stroke={C.tinta} strokeWidth="4" />
          <circle cx="34" cy="-4" r="5" fill={C.tinta} />
        </g>
      </svg>
      <Kinetic texto={c.texto} size={52} delay={14} />
      <Mono size={18} style={{ marginTop: 18 }}>A ORIGEM DO NOME · NETFLIX CULTURE MEMO</Mono>
    </Faixa>
  );
};

const LogoN: React.FC<P> = ({ c }) => {
  const k = useEntra(c.silencio ? 20 : 0, 18);
  const kl = useEntra(26, 14);
  return (
    <Faixa>
      <div style={{ opacity: k, transform: `scale(${interpolate(k, [0, 1], [0.96, 1])})` }}><NLogo altura={380} /></div>
      {c.legenda && <div style={{ marginTop: 90, opacity: kl }}><Kinetic texto={c.legenda} size={40} peso={700} delay={26} passo={2} /></div>}
    </Faixa>
  );
};

const Cores: React.FC<P> = () => {
  const k = useEntra(0, 14);
  const k2 = useEntra(14, 14);
  const sw = (cor: string, hex: string, pms: string, kk: number) => (
    <div style={{ display: "flex", alignItems: "center", gap: 20, opacity: kk }}>
      <div style={{ width: 90, height: 90, background: cor }} />
      <div style={{ textAlign: "left" }}>
        <div style={{ fontFamily: MONO, fontSize: 28, color: C.tinta, fontWeight: 600 }}>{hex}</div>
        <Mono size={16}>{pms}</Mono>
      </div>
    </div>
  );
  return (
    <Faixa>
      <div style={{ opacity: k, marginBottom: 80 }}><NLogo altura={260} /></div>
      <div style={{ display: "flex", flexDirection: "column", gap: 26 }}>
        {sw(C.netflix, "#E50914", "NETFLIX RED · PMS 1795 C", k)}
        {sw(C.netflixEscuro, "#B20710", "SYMBOL DARK RED · PMS 7627 C", k2)}
      </div>
    </Faixa>
  );
};

const Proibicoes: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const tf = [
    "scaleX(1.6)", "rotate(25deg)", "none", "none", "none", "none", "perspective(200px) rotateX(55deg)", "none",
  ];
  return (
    <Faixa>
      <Mono size={20} cor={C.tinta} style={{ marginBottom: 26 }}>O QUE O GUIA PROÍBE</Mono>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 140px)", gap: "26px 14px" }}>
        {c.itens.map((it: string, i: number) => {
          const k = interpolate(f - i * 6, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
          const bg = i === 2 ? C.tinta : i === 4 ? "repeating-linear-gradient(45deg,#BBB 0 6px,#EEE 6px 12px)" : i === 5 ? C.secundario : i === 7 ? C.branco : C.apoio;
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", opacity: k }}>
              <div style={{ width: 120, height: 120, position: "relative", display: "flex", alignItems: "center", justifyContent: "center", background: i === 4 || i === 5 ? bg : "transparent" }}>
                <div style={{ width: 54, height: 54, background: i === 4 || i === 5 ? C.apoio : bg, transform: tf[i], boxShadow: i === 3 ? "0 0 22px 8px #999" : "none",
                  border: i === 7 ? `3px dashed ${C.tinta}` : "none", borderRadius: i === 7 ? 27 : 0 }} />
                <svg width="120" height="120" style={{ position: "absolute" }}><line x1="14" y1="14" x2="106" y2="106" stroke={C.tinta} strokeWidth="4" /><line x1="106" y1="14" x2="14" y2="106" stroke={C.tinta} strokeWidth="4" /></svg>
              </div>
              <Mono size={14} cor={C.tinta} style={{ marginTop: 8 }}>{it}</Mono>
            </div>
          );
        })}
      </div>
      <div style={{ fontFamily: FONT, fontSize: 18, color: C.secundario, marginTop: 26 }}>Demonstração genérica: o logo verdadeiro nunca é distorcido.</div>
    </Faixa>
  );
};

const Barras: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const bar = (lab: string, v: number, i: number, cor: string) => {
    const k = interpolate(f - 8 - i * 10, [0, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
    return (
      <div style={{ width: 560, marginBottom: 34, textAlign: "left" }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontFamily: FONT, fontWeight: 700, fontSize: 34, color: C.tinta }}>
          <span>{lab}</span><span style={{ fontVariantNumeric: "tabular-nums" }}>{(v * k).toFixed(1).replace(".", ",")}%</span>
        </div>
        <div style={{ height: 34, background: "#F0F0F0", marginTop: 10 }}><div style={{ height: "100%", width: `${v * k}%`, background: cor }} /></div>
      </div>
    );
  };
  return (
    <Faixa>
      <Mono size={20} cor={C.tinta} style={{ marginBottom: 36 }}>{c.titulo}</Mono>
      {bar(c.a[0], c.a[1], 0, C.secundario)}
      {bar(c.b[0], c.b[1], 1, C.tinta)}
      <Mono size={16} style={{ marginTop: 8 }}>NOV. 2019 – JAN. 2020</Mono>
    </Faixa>
  );
};

const AoVivo: React.FC<P> = ({ c }) => {
  const f = useCurrentFrame();
  const k = useMola(0, 16);
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: C.tinta, padding: "30px 30px 60px", borderRadius: 30, boxShadow: SOMBRA, transform: `scale(${k})` }}>
        <div style={{ width: 580, height: 400, background: "#111", borderRadius: 22, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", position: "relative", overflow: "hidden" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ width: 22, height: 22, borderRadius: 11, background: C.ambar, opacity: Math.floor(f / 12) % 2 ? 1 : 0.25 }} />
            <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 80, color: "#EEE" }}>{c.linha1}</div>
          </div>
          <Mono size={18} cor="#CCC" style={{ marginTop: 18, maxWidth: 480 }}>{c.linha2}</Mono>
          <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0px, rgba(0,0,0,0.25) 1px, transparent 1px, transparent 3px)" }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ roteador */
export const Cena: React.FC<P> = (p) => {
  const map: Record<string, React.FC<P>> = {
    arquivo: Arquivo, cor: Cor, tv: TV, cor_clip: CorClip, evidencia: Evidencia, titulo: Titulo, pergunta: Pergunta, citacao: Citacao,
    lista: Lista, abertura: Abertura, fim: Fim, respiro: Respiro, medidor: MedidorCena, contador: Contador, botao: Botao, fluxo: Fluxo,
    linha: Linha, envelope: Envelope, posters: Posters, mapa: Mapa, cheque: Cheque, colunas: Colunas, pessoas: Pessoas, anzol: Anzol,
    logoN: LogoN, cores: Cores, proibicoes: Proibicoes, barras: Barras, aovivo: AoVivo,
  };
  const Comp = map[p.c.tipo];
  if (!Comp) return <Faixa><Mono>{p.c.tipo}</Mono></Faixa>;
  return <Comp {...p} />;
};
