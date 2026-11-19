import React from "react";
import { AbsoluteFill, Freeze, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FAIXA, FONT, MONO, SOMBRA } from "../theme";
import { CRTOverlay, Carimbo, Faixa, Kinetic, Legenda, LowerThird, Medidor, Mono, NLogo, Picto, ease, useEntra, useMola } from "./bits";

import * as A from "./acoes";

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
  const zoom = interpolate(Math.floor(f / 3) * 3, [0, dur * fps], [0.9, 1.08], { extrapolateRight: "clamp" }); // aproximação lenta em degraus de 3 quadros (stop-motion)
  // leitura em degraus ("lupa"), presa às palavras dele (AcoesCtx, >= 1,8 s entre passos): a câmera vai para outro pedaço do trecho,
  // um marca-texto varre o pedaço em foco, e no último passo volta ao todo e o trecho é "recortado" (contorno tracejado e sombra)
  const ctxA = React.useContext(A.AcoesCtx);
  const passos: number[] = [];
  if (c.lupa !== false) {
    const fonte = ctxA && ctxA.length ? ctxA : Array.from({ length: 12 }, (_, i) => 1.6 + i * 2.1);
    for (const t of fonte) if (t >= 1.4 && t <= dur - 0.6 && (!passos.length || t - passos[passos.length - 1] >= 1.5)) passos.push(t);
    while (passos.length && dur - 0.5 - passos[passos.length - 1] > 2.0) passos.push(passos[passos.length - 1] + 1.6); // sem pausa longa no fim
  }
  const alvos: [number, number, number][] = [[0, 0, 1], [-0.28, -0.22, 1.45], [0.26, 0.05, 1.5], [-0.12, 0.26, 1.4], [0.22, -0.2, 1.45]];
  const nPassos = passos.length;
  let lx = 0, ly = 0, lz = 1, passoAtual = -1, ePasso = 0;
  passos.forEach((t, k) => {
    const fk = Math.round(t * fps);
    const ultimo = k === nPassos - 1 && nPassos > 1;
    const a = ultimo ? alvos[0] : alvos[(k % (alvos.length - 1)) + 1];
    const e = interpolate(f, [fk, fk + 9], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
    if (f >= fk) { lx += (a[0] - lx) * e; ly += (a[1] - ly) * e; lz += (a[2] - lz) * e; passoAtual = k; ePasso = interpolate(f - fk, [6, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }); }
  });
  const recortado = nPassos > 1 && passoAtual === nPassos - 1;
  const s = base * zoom * lz;
  const cxImg = (tr[0] + tr[2] / 2 + lx * tr[2]) * iw, cyImg = (tr[1] + tr[3] / 2 + ly * tr[3]) * ih;
  const left = cw / 2 - cxImg * s, top = ch / 2 - cyImg * s;
  const sub = interpolate(f, [14, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  // vaivém lateral lento do cartão (±34 px a cada 3 s, em degraus de 3 quadros): documento longo não fica parado; a leitura não é afetada
  const vaiDoc = 34 * (Math.abs(((Math.floor(f / 3) * 3 / 90) % 2) - 1) * 2 - 1);
  const temFrase = !!c.frase;
  const fraseK = temFrase ? interpolate(f, [dur * fps * 0.42, dur * fps * 0.42 + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease }) : 0;
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: cw, height: ch, position: "relative", overflow: "hidden", background: "white", boxShadow: SOMBRA,
        transform: `translateY(${(1 - entra) * 80}px) translateX(${vaiDoc}px) scale(${1 - fraseK * 0.06})`, opacity: Math.min(1, entra * 1.5) * (1 - fraseK * 0.9) }}>
        <Img src={staticFile(c.img)} style={{ position: "absolute", left, top, width: iw * s, height: ih * s, maxWidth: "none" }} />
        <div style={{ position: "absolute", left: left + tr[0] * iw * s, top: top + tr[1] * ih * s - 6,
          width: tr[2] * iw * s, height: tr[3] * ih * s + 12, background: "rgba(41,41,41,0.06)" }} />
        <div style={{ position: "absolute", left: left + tr[0] * iw * s, top: top + (tr[1] + tr[3]) * ih * s + 8,
          width: tr[2] * iw * s * sub, height: 4, background: C.tinta }} />
        {passoAtual >= 0 && !recortado && (
          <div style={{ position: "absolute", left: cw / 2 - 260, top: ch / 2 + 34, width: 520 * ePasso, height: 30, background: "rgba(41,41,41,0.14)", mixBlendMode: "multiply" }} />
        )}
        {recortado && (
          <div style={{ position: "absolute", left: left + tr[0] * iw * s - 14, top: top + tr[1] * ih * s - 18, width: tr[2] * iw * s + 28, height: tr[3] * ih * s + 36,
            border: `3px dashed ${C.tinta}`, opacity: ePasso, boxShadow: `0 0 0 ${2000 * ePasso}px rgba(255,255,255,${0.55 * ePasso})` }} />
        )}
        {/* leitura contínua: um marca-texto claro desce pelas linhas em degraus de 3 quadros (documento longo nunca fica parado) */}
        <div style={{ position: "absolute", left: 40, right: 40, top: 30 + ((Math.floor(f / 3) * 3 * 3) % (ch - 90)), height: 34, background: "rgba(41,41,41,0.11)", mixBlendMode: "multiply" }} />
      </div>
      <div style={{ position: "absolute", left: FAIXA.x + 12, top: 150 + (1 - entra) * 80 }}>
        <Carimbo texto={c.carimbo} />
      </div>
      {temFrase && fraseK > 0 && (
        <Faixa style={{ opacity: fraseK }}>
          <FrasePose>
          <A.AcoesTexto carimbo="CITAÇÃO" largura={480}><Kinetic texto={c.frase} size={50} delay={Math.round(dur * fps * 0.42)} passo={2} /></A.AcoesTexto>
          </FrasePose>
        </Faixa>
      )}
    </AbsoluteFill>
  );
};

// a frase do documento se reposiciona em degrau a cada ação e se aproxima devagar entre elas (o documento em si não balança: leitura)
const POSES_F = [[0, 0, 0], [18, -10, 1.2], [-16, 8, -1], [12, 12, 0.8], [-18, -8, -1.3]];
const FrasePose: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { n, desde } = A.useAcoes();
  const a = POSES_F[(n + POSES_F.length - 1) % POSES_F.length], b = POSES_F[n % POSES_F.length];
  const k = n === 0 ? 1 : Math.min(1, Math.floor(desde(n) / 2) * 2 / 4);
  const v = a.map((x, i) => x + (b[i] - x) * k);
  // entre uma ação e outra o cartão da frase continua a se aproximar devagar, em degraus de 3 quadros (nunca fica parado)
  // aproximação contínua em rampas de 2 s, sem teto: frase longa também não fica parada
  const q = Math.floor((n === 0 ? desde(0) : desde(n)) / 3) * 3;
  const d = (q % 60) / 60; // rampa de 2 s que recomeça (sem ponto de virada lento)
  const z = 1 + 0.09 * d, dx = (b[0] >= 0 ? -1 : 1) * 26 * d;
  return <div style={{ transform: `translate(${v[0] + dx}px, ${v[1]}px) rotate(${v[2]}deg) scale(${z})` }}>{children}</div>;
};

/* ------------------------------------------------------------------ TIPOGRAFIA */
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
    arquivo: Arquivo, cor: Cor, tv: TV, cor_clip: CorClip, evidencia: Evidencia, titulo: A.TituloA, pergunta: A.PerguntaA, citacao: A.CitacaoA,
    lista: A.ListaA, abertura: Abertura, fim: A.FimA, respiro: Respiro, medidor: A.MedidorA, contador: A.ContadorA, botao: A.BotaoA, fluxo: A.FluxoA,
    linha: Linha, envelope: A.EnvelopeA, posters: A.PostersA, mapa: A.MapaA, cheque: A.ChequeA, colunas: A.ColunasA, pessoas: A.PessoasA, anzol: A.AnzolA,
    logoN: A.LogoNA, cores: A.CoresA, proibicoes: A.ProibicoesA, barras: A.BarrasA, aovivo: A.AoVivoA,
  };
  const Comp = map[p.c.tipo];
  if (!Comp) return <Faixa><Mono>{p.c.tipo}</Mono></Faixa>;
  return <Comp {...p} />;
};
