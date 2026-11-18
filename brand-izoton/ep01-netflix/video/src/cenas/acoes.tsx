// Ações do objeto principal (rodada v3b, nota do Guilherme: "a imagem fica estática, o envelope não abre, não faz nada").
// Cada cena recebe os tempos das palavras de conteúdo da fala (AcoesCtx, relativos à cena, >= 1,25 s entre si) e o próprio
// objeto age a cada um: abre, desliza, sobe, é sublinhado, carimbado, assinado. Sem contexto (Shorts antigos), uma ação a cada 1,5 s.
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FAIXA, FONT, MONO, SOMBRA } from "../theme";
import { Carimbo, Faixa, Kinetic, Medidor, Mono, NLogo, Picto, ease, useEntra, useMola } from "./bits";

type P = { c: any; dur: number; trecho: any };
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const AcoesCtx = React.createContext<number[] | null>(null);

/** n = quantas ações já aconteceram; p(i) = progresso (0–1, 9 quadros) da ação i (1 = primeira). */
export const useAcoes = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ctx = React.useContext(AcoesCtx);
  const ts = ctx && ctx.length ? ctx : Array.from({ length: 40 }, (_, i) => 1.2 + i * 1.5);
  const fr = ts.map((t) => Math.round(t * fps));
  const n = fr.filter((x) => f >= x).length;
  const p = (i: number) => (i < 1 ? 1 : i > fr.length ? 0 : interpolate(f - fr[i - 1], [0, 9], [0, 1], { ...cl, easing: ease }));
  const desde = (i: number) => (i < 1 ? f : i > fr.length ? -1 : f - fr[i - 1]);
  return { n, p, f, fps, desde };
};

/** Carimbo que bate (escala 1,6 → 1) quando a ação i chega. */
const Bate: React.FC<{ texto: string; prog: number; rot?: number; size?: number; style?: React.CSSProperties }> = ({ texto, prog, rot = -4, size = 22, style }) =>
  prog <= 0 ? null : (
    <div style={{ fontFamily: MONO, fontSize: size, letterSpacing: 3, color: C.tinta, border: `3px solid ${C.tinta}`, padding: "6px 14px", background: "rgba(255,255,255,0.9)",
      textTransform: "uppercase", whiteSpace: "nowrap", transform: `scale(${interpolate(prog, [0, 1], [1.7, 1])}) rotate(${rot}deg)`, opacity: Math.min(1, prog * 2), ...style }}>{texto}</div>
  );

/* ------------------------------------------------------------------ TEXTO: título, pergunta, citação */
// 1 sublinha · 2 carimbo · 3 marca-texto atrás · 4 colchete na margem · 5+ o marca-texto troca de linha a cada ação
export const AcoesTexto: React.FC<{ children: React.ReactNode; carimbo: string; largura?: number }> = ({ children, carimbo, largura = 520 }) => {
  const { n, p } = useAcoes();
  const alt = n >= 5 ? (n - 5) % 2 : -1;
  return (
    <div style={{ position: "relative", display: "flex", flexDirection: "column", alignItems: "center" }}>
      {n >= 3 && <div style={{ position: "absolute", left: -12, right: -12, top: alt === 1 ? "50%" : "-4%", height: alt === -1 ? "108%" : "54%", background: C.apoio,
        opacity: 0.55, transformOrigin: "left center", transform: `scaleX(${p(3)})`, zIndex: 0, transition: "none" }} />}
      <div style={{ position: "relative", zIndex: 1 }}>{children}</div>
      <div style={{ height: 6, width: largura * p(1), background: C.tinta, marginTop: 18, alignSelf: "center", zIndex: 1 }} />
      {n >= 4 && <div style={{ position: "absolute", left: -40, top: 0, bottom: 0, width: 14, borderLeft: `4px solid ${C.tinta}`, borderTop: `4px solid ${C.tinta}`,
        borderBottom: `4px solid ${C.tinta}`, transformOrigin: "top", transform: `scaleY(${p(4)})` }} />}
      <div style={{ position: "absolute", right: -60, top: -64, zIndex: 2 }}><Bate texto={carimbo} prog={p(2)} rot={6} /></div>
    </div>
  );
};

export const TituloA: React.FC<P> = ({ c, trecho }) => {
  const size = c.grande ? (c.texto.length <= 5 ? 230 : 104) : c.texto.length > 26 ? 66 : 82;
  const k = useEntra(10, 14);
  return (
    <Faixa>
      <AcoesTexto carimbo={c.carimbo ?? `ARQUIVO ${String((trecho?.id ?? "n00").slice(1, 3)).padStart(2, "0")}`} largura={c.grande ? 360 : 480}>
        <Kinetic texto={c.texto} size={size} />
      </AcoesTexto>
      {c.sub && <Mono size={20} style={{ marginTop: 26, opacity: k }}>{c.sub}</Mono>}
    </Faixa>
  );
};

export const PerguntaA: React.FC<P> = ({ c }) => (
  <Faixa>
    <div style={{ marginBottom: 34 }}><Carimbo texto={c.rotulo} delay={4} /></div>
    <AcoesTexto carimbo="?" largura={460}><Kinetic texto={c.texto} size={c.texto.length > 30 ? 60 : 96} delay={8} /></AcoesTexto>
  </Faixa>
);

export const CitacaoA: React.FC<P> = ({ c }) => {
  const k = useEntra(16, 14);
  return (
    <Faixa>
      <AcoesTexto carimbo="CITAÇÃO" largura={480}><Kinetic texto={c.texto} size={c.texto.length > 50 ? 50 : 62} peso={700} passo={2} /></AcoesTexto>
      <Mono size={18} cor={C.tinta} style={{ marginTop: 30, opacity: k }}>{c.credito}</Mono>
      {c.nota && <div style={{ fontFamily: FONT, fontSize: 19, color: C.secundario, marginTop: 18, opacity: k, maxWidth: 560 }}>{c.nota}</div>}
    </Faixa>
  );
};

/* ------------------------------------------------------------------ ENVELOPE */
// sem porta (1997): 1 a aba abre · 2 o DVD desliza para fora · 3 o envelope sai, o disco vai ao centro e gira · 4 o ano é carimbado no disco
//                   5 o rótulo é carimbado · 6+ o disco dá meia-volta a cada ação (gira mais rápido por um instante)
// porta (2025):     o envelope cresce como uma porta · 1 a aba abre · 2 luz por dentro · 3 uma pessoa entra · 4 o rótulo é carimbado
export const EnvelopeA: React.FC<P> = ({ c, dur }) => {
  const { n, p, f, fps, desde } = useAcoes();
  const k = useMola(4, 15);
  const aba = p(1);
  const abaY = interpolate(aba, [0, 1], [170, -120]);
  if (c.porta) {
    const porta = interpolate(f, [0, dur * fps], [1, 1.6], { easing: ease });
    const luz = p(2), pessoa = p(3);
    return (
      <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
        <div style={{ position: "absolute", fontFamily: FONT, fontWeight: 800, fontSize: 420, color: "#F1F1F1", letterSpacing: -10 }}>{c.ano}</div>
        <div style={{ transform: `scale(${k * porta})`, filter: "drop-shadow(18px 18px 22px rgba(0,0,0,0.22))" }}>
          <svg width="460" height="300" viewBox="0 -130 460 430" style={{ overflow: "visible" }}>
            <rect x="0" y="0" width="460" height="300" rx="10" fill={C.netflixEscuro} />
            <rect x="150" y="90" width="160" height="210" fill="#FFFFFF" opacity={luz * 0.9} />
            {pessoa > 0 && <g transform={`translate(${interpolate(pessoa, [0, 1], [-60, 190])} ${interpolate(desde(3), [0, 40], [190, 150], cl)}) scale(0.9)`}
              opacity={interpolate(desde(3), [30, 60], [1, 0], cl)}>
              <circle cx="40" cy="0" r="16" fill={C.tinta} /><rect x="24" y="20" width="32" height="70" rx="14" fill={C.tinta} /></g>}
            <path d="M 0 300 L 0 10 L 230 170 L 460 10 L 460 300 Z" fill={C.netflix} opacity={1 - luz * 0.35} />
            <path d={`M 0 10 L 230 ${abaY} L 460 10 Z`} fill={aba > 0.5 ? C.netflixEscuro : C.netflix} stroke={C.netflixEscuro} strokeWidth="6" />
          </svg>
        </div>
        <div style={{ position: "absolute", bottom: 190, left: FAIXA.x, width: FAIXA.w, display: "flex", justifyContent: "center" }}>
          {n >= 4 ? <Bate texto={c.rotulo} prog={p(4)} rot={-2} size={20} /> : <Mono size={22} cor={C.tinta} style={{ opacity: k }}>{c.rotulo}</Mono>}
        </div>
      </AbsoluteFill>
    );
  }
  const sai = p(2);                       // disco sai do envelope
  const fora = p(3);                      // envelope sai de cena, disco ao centro
  const discoY = interpolate(sai, [0, 1], [150, -40]) + interpolate(fora, [0, 1], [0, 120]);
  const discoS = interpolate(fora, [0, 1], [1, 1.55]);
  const giro = n >= 3 ? desde(3) * 3 + (n >= 6 ? Array.from({ length: n - 5 }, (_, i) => interpolate(desde(6 + i), [0, 14], [0, 180], { ...cl, easing: ease })).reduce((a, b) => a + b, 0) : 0) : 0;
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", fontFamily: FONT, fontWeight: 800, fontSize: 420, color: "#F1F1F1", letterSpacing: -10 }}>{c.ano}</div>
      <div style={{ transform: `scale(${k})`, filter: "drop-shadow(18px 18px 22px rgba(0,0,0,0.22))" }}>
        <svg width="460" height="300" viewBox="0 0 460 300" style={{ overflow: "visible" }}>
          <g transform={`translate(0 ${fora * 760})`} opacity={1 - fora * 0.2}>
            <rect x="0" y="0" width="460" height="300" rx="10" fill={C.netflixEscuro} />
            {aba > 0.5 && <path d={`M 0 10 L 230 ${abaY} L 460 10 Z`} fill={C.netflixEscuro} stroke={C.netflixEscuro} strokeWidth="6" strokeLinejoin="round" />}
          </g>
          <g transform={`translate(230 ${discoY}) scale(${discoS}) rotate(${giro})`}>
            <circle r="118" fill="#DADADA" stroke="#BDBDBD" strokeWidth="3" />
            <circle r="96" fill="none" stroke="#EFEFEF" strokeWidth="10" opacity="0.8" />
            <path d="M -70 -70 A 99 99 0 0 1 40 -90" stroke="#FFFFFF" strokeWidth="14" fill="none" opacity="0.7" />
            <circle r="44" fill="#F6F6F6" stroke="#BDBDBD" strokeWidth="2" />
            <circle r="13" fill={C.branco} stroke="#9E9E9E" strokeWidth="2" />
            {n >= 4 && <text y="78" textAnchor="middle" fontFamily={MONO} fontSize="26" fontWeight="700" fill={C.tinta}
              transform={`scale(${interpolate(p(4), [0, 1], [1.6, 1])})`} opacity={p(4)}>{c.ano}</text>}
          </g>
          <g transform={`translate(0 ${fora * 760})`} opacity={1 - fora * 0.2}>
            <path d="M 0 300 L 0 10 L 230 170 L 460 10 L 460 300 Z" fill={C.netflix} />
            <rect x="300" y="200" width="120" height="60" fill="none" stroke="#FFFFFF" strokeWidth="4" opacity="0.8" />
            {aba <= 0.5 && <path d={`M 0 10 L 230 ${abaY} L 460 10 Z`} fill={C.netflix} stroke={C.netflixEscuro} strokeWidth="6" strokeLinejoin="round" />}
          </g>
        </svg>
      </div>
      <div style={{ position: "absolute", bottom: 190, left: FAIXA.x, width: FAIXA.w, display: "flex", justifyContent: "center" }}>
        {n >= 5 ? <Bate texto={c.rotulo} prog={p(5)} rot={-3} size={24} /> : <Mono size={22} cor={C.tinta} style={{ opacity: k * (1 - fora) }}>{c.rotulo}</Mono>}
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ DADOS */
// medidor: o ponteiro sobe em degraus, um por ação (3 degraus até o valor), depois oscila como contador Geiger a cada ação
export const MedidorA: React.FC<P> = ({ c }) => {
  const { n, p } = useAcoes();
  const deg = Math.min(3, n);
  const prog = (deg === 0 ? 0.25 : (Math.min(3, n - 1) + p(n)) / 3) * 1;
  const geiger = n > 3 ? Math.sin(p(n) * Math.PI) * 0.06 : 0;
  return (
    <Faixa>
      <Medidor rotulo={c.rotulo} marcas={c.marcas} de={c.de} ate={c.ate} prog={Math.min(1, prog) + geiger} />
      <div style={{ display: "flex", gap: 8, marginTop: 22 }}>
        {Array.from({ length: 8 }, (_, i) => <div key={i} style={{ width: 34, height: 10, background: i < n ? C.tinta : C.apoio }} />)}
      </div>
    </Faixa>
  );
};

// contador: entra em 55%, sobe a 80% na 1ª ação e ao valor na 2ª; 3 o rótulo é carimbado; 4+ a régua embaixo enche um segmento por ação
export const ContadorA: React.FC<P> = ({ c }) => {
  const { n, p, f } = useAcoes();
  const k = useEntra(4, 12);
  const digitos = c.valor.replace(/\D/g, "");
  const num = parseInt(digitos || "0", 10);
  const ent = interpolate(f, [0, 20], [0, 0.55], { ...cl, easing: ease });
  const prog = n === 0 ? ent : n === 1 ? 0.55 + 0.25 * p(1) : 0.8 + 0.2 * p(2);
  let mostra = c.valor;
  if (/^[\d.]+$/.test(c.valor) && num > 0) mostra = Math.round(num * prog).toLocaleString("pt-BR");
  else mostra = c.valor.slice(0, Math.max(1, Math.ceil(c.valor.length * Math.min(1, prog / 0.8))));
  const pulo = n >= 1 && n <= 2 ? interpolate(p(n), [0, 0.4, 1], [1, 1.06, 1]) : 1;
  const size = c.valor.length > 9 ? 92 : c.valor.length > 6 ? 118 : 170;
  return (
    <Faixa>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: size, color: C.tinta, letterSpacing: -2, lineHeight: 1, fontVariantNumeric: "tabular-nums", transform: `scale(${pulo})` }}>{mostra}</div>
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 34, color: C.tinta, marginTop: 16, opacity: k }}>{c.sufixo}</div>
      <div style={{ marginTop: 20, minHeight: 40, display: "flex", justifyContent: "center" }}>
        {n >= 3 ? <Bate texto={c.rotulo} prog={p(3)} rot={-2} size={17} /> : <Mono size={18} style={{ opacity: k }}>{c.rotulo}</Mono>}
      </div>
      {c.nota && <Mono size={16} cor={C.tinta} style={{ marginTop: 12, opacity: k }}>{c.nota}</Mono>}
      <div style={{ display: "flex", gap: 6, marginTop: 26 }}>
        {Array.from({ length: 10 }, (_, i) => <div key={i} style={{ width: 30, height: 8, background: i < n - 3 ? C.tinta : C.apoio, transform: `scaleY(${i === n - 4 ? 1 + (1 - p(n)) : 1})` }} />)}
      </div>
    </Faixa>
  );
};

// barras: 1 barra A cresce · 2 barra B cresce · 3 colchete com a diferença · 4 carimbo · 5+ a barra maior pisca a borda
export const BarrasA: React.FC<P> = ({ c }) => {
  const { n, p, f } = useAcoes();
  const ent = interpolate(f, [4, 20], [0, 0.15], cl);
  const bar = (lab: string, v: number, kk: number, cor: string, marca: boolean) => (
    <div style={{ width: 560, marginBottom: 34, textAlign: "left" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontFamily: FONT, fontWeight: 700, fontSize: 34, color: C.tinta }}>
        <span>{lab}</span><span style={{ fontVariantNumeric: "tabular-nums" }}>{(v * kk).toFixed(1).replace(".", ",")}%</span>
      </div>
      <div style={{ height: 34, background: "#F0F0F0", marginTop: 10, outline: marca ? `3px solid ${C.tinta}` : "none", outlineOffset: 4 }}>
        <div style={{ height: "100%", width: `${v * kk}%`, background: cor }} /></div>
    </div>
  );
  const kA = Math.max(ent, p(1)), kB = Math.max(ent, p(2));
  const dif = Math.abs(c.b[1] - c.a[1]);
  return (
    <Faixa>
      <Mono size={20} cor={C.tinta} style={{ marginBottom: 36 }}>{c.titulo}</Mono>
      {bar(c.a[0], c.a[1], kA, C.secundario, false)}
      {bar(c.b[0], c.b[1], kB, C.tinta, n >= 5 && n % 2 === 1)}
      <div style={{ height: 50, display: "flex", alignItems: "center", gap: 16, opacity: p(3) }}>
        <div style={{ width: 120 * p(3), height: 4, background: C.tinta }} />
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 38, color: C.tinta }}>+{dif.toFixed(1).replace(".", ",")} P.P.</div>
      </div>
      <div style={{ marginTop: 8, display: "flex", justifyContent: "center", minHeight: 44 }}>
        {n >= 4 ? <Bate texto="NOV. 2019 – JAN. 2020" prog={p(4)} size={17} /> : <Mono size={16}>NOV. 2019 – JAN. 2020</Mono>}
      </div>
    </Faixa>
  );
};

// mapa: cada ação acende um grupo de pontos com anel que se expande; os países da lista entram um por ação
export const MapaA: React.FC<P> = ({ c }) => {
  const { n, p, desde } = useAcoes();
  const pts = Array.from({ length: 46 }, (_, i) => ({ x: 120 + ((i * 397) % 1680), y: 220 + ((i * 251) % 620) }));
  const k = useEntra(0, 20);
  const acesos = Math.min(46, 8 + n * 6);
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <svg width="1920" height="1080" style={{ position: "absolute" }}>
        {pts.map((q, i) => i > 0 && i % 3 !== 0 && i < acesos ? <line key={"l" + i} x1={pts[i - 1].x} y1={pts[i - 1].y} x2={q.x} y2={q.y} stroke={C.apoio} strokeWidth={1.5} opacity={k} /> : null)}
        {pts.map((q, i) => {
          const grupo = i < 8 ? 0 : Math.floor((i - 8) / 6) + 1;
          const aceso = i < acesos;
          const anel = grupo >= 1 && grupo <= n ? interpolate(desde(grupo), [0, 24], [0, 1], cl) : 1;
          return (
            <g key={i}>
              <circle cx={q.x} cy={q.y} r={aceso ? 6 : 3} fill={aceso ? (i % 5 === 0 ? C.tinta : C.secundario) : C.apoio} />
              {aceso && anel < 1 && <circle cx={q.x} cy={q.y} r={6 + anel * 34} fill="none" stroke={C.tinta} strokeWidth={2} opacity={1 - anel} />}
            </g>
          );
        })}
      </svg>
      <Faixa>
        <div style={{ background: C.branco, padding: "30px 20px" }}>
          <Kinetic texto={c.titulo} size={62} />
          {c.pontos?.length > 0 && <Mono size={22} cor={C.tinta} style={{ marginTop: 22 }}>{c.pontos.slice(0, Math.max(1, n)).join(" · ")}</Mono>}
          <Mono size={18} style={{ marginTop: 14 }}>{c.sub}</Mono>
          <Mono size={16} cor={C.tinta} style={{ marginTop: 14 }}>PONTOS ACESOS · {String(acesos).padStart(2, "0")}</Mono>
        </div>
      </Faixa>
    </AbsoluteFill>
  );
};

// cheque: 1 o valor é datilografado · 2 a assinatura é traçada · 3 carimbo · 4+ o cheque inclina e volta (é entregue) a cada ação
export const ChequeA: React.FC<P> = ({ c }) => {
  const { n, p } = useAcoes();
  const k = useMola(0, 16);
  const val = c.valor.slice(0, Math.ceil(c.valor.length * Math.max(0.15, p(1))));
  const ass = p(2);
  const inc = n >= 4 ? Math.sin(p(n) * Math.PI) * (n % 2 ? 4 : -4) : 0;
  return (
    <Faixa>
      <div style={{ width: 580, height: 270, border: `4px solid ${C.tinta}`, background: C.branco, position: "relative", transform: `scale(${k}) rotate(${inc}deg)`, boxShadow: SOMBRA,
        display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
        <Mono size={16} cor={C.tinta} style={{ position: "absolute", top: 18, left: 22 }}>PAGUE A QUEM MELHORAR O ALGORITMO</Mono>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 62, color: C.tinta, whiteSpace: "nowrap" }}>{val}</div>
        <svg width="220" height="60" viewBox="0 0 220 60" style={{ position: "absolute", left: 30, bottom: 18 }}>
          <path d="M 5 40 C 25 5, 35 55, 55 30 S 85 10, 95 38 S 125 50, 140 22 S 170 30, 215 28" fill="none" stroke={C.tinta} strokeWidth="3" strokeDasharray="320" strokeDashoffset={320 * (1 - ass)} />
          <line x1="0" y1="52" x2="220" y2="52" stroke={C.secundario} strokeWidth="1.5" />
        </svg>
        <div style={{ position: "absolute", right: -30, bottom: -26 }}>{n >= 3 && <Bate texto={c.carimbo} prog={p(3)} size={40} />}</div>
      </div>
      <Mono size={20} cor={C.tinta} style={{ marginTop: 50 }}>{c.rotulo}</Mono>
    </Faixa>
  );
};

// fluxo: o 1º item entra com a cena, cada ação acrescenta o próximo; depois cada ação acende um item (o cursor percorre o fluxo)
export const FluxoA: React.FC<P> = ({ c }) => {
  const { n, p } = useAcoes();
  const m = c.itens.length;
  const cursor = n >= m ? (n - m) % m : -1;
  return (
    <Faixa>
      <Mono size={20} cor={C.tinta} style={{ marginBottom: 28 }}>{c.rotulo}</Mono>
      {c.itens.map((it: string, i: number) => {
        const kk = i === 0 ? 1 : p(i);
        const ativo = i === cursor || (cursor === -1 && i === 2 && n >= 3);
        return (
          <React.Fragment key={i}>
            {i > 0 && <div style={{ width: 3, height: 34 * kk, background: C.tinta }} />}
            <div style={{ border: `3px solid ${C.tinta}`, padding: "16px 26px", width: 460, fontFamily: MONO, fontSize: 24, letterSpacing: 2,
              opacity: kk, transform: `translateY(${(1 - kk) * 18}px) scale(${ativo ? 1.05 : 1})`, background: ativo ? C.tinta : C.branco, color: ativo ? C.branco : C.tinta }}>{it}</div>
          </React.Fragment>
        );
      })}
    </Faixa>
  );
};

// lista: dois itens com a cena, um a mais por ação; riscados entram depois de todos
export const ListaA: React.FC<P> = ({ c }) => {
  const { n, p } = useAcoes();
  const m = c.itens.length;
  return (
    <Faixa>
      {c.titulo && <Mono size={20} cor={C.tinta} style={{ marginBottom: 24 }}>{c.titulo}</Mono>}
      {c.itens.map((it: string, i: number) => {
        const kk = i < 2 ? 1 : p(i - 1);
        return <div key={i} style={{ fontFamily: FONT, fontWeight: 800, fontSize: m > 5 ? 50 : 70, lineHeight: 1.08, color: C.tinta, opacity: kk, transform: `translateY(${(1 - kk) * 30}px)` }}>{it}</div>;
      })}
      {(c.riscados ?? []).map((it: string, i: number) => {
        const a = Math.max(0, m - 2) + 1 + i;
        return (
          <div key={"r" + i} style={{ position: "relative", fontFamily: FONT, fontWeight: 800, fontSize: 70, lineHeight: 1.08, color: C.apoio, opacity: p(a) }}>
            {it}<div style={{ position: "absolute", left: 0, top: "52%", height: 6, width: `${(n > a ? 1 : 0) * 100 * p(a + 1)}%`, background: C.tinta }} />
          </div>
        );
      })}
    </Faixa>
  );
};

// pessoas: o corte acontece em 4 levas, uma por ação; 5 "E FIZERAM MAIS" sobe
export const PessoasA: React.FC<P> = ({ c }) => {
  const { n, p } = useAcoes();
  const leva = Math.min(4, n);
  const corta = (leva === 0 ? 0 : (leva - 1 + p(leva)) / 4) * 40;
  return (
    <Faixa>
      <Mono size={20} cor={C.tinta} style={{ marginBottom: 20 }}>{c.ano} · DEMISSÃO DE UM TERÇO</Mono>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 44px)", gap: 4 }}>
        {Array.from({ length: c.de }, (_, i) => <Picto key={i} nome="PESSOA" size={44} cor={i >= c.de - corta ? C.apoio : C.tinta} />)}
      </div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 92, color: C.tinta, marginTop: 24 }}>{c.de} → {Math.round(c.de - corta)}</div>
      <Mono size={20} cor={C.tinta} style={{ opacity: p(5), marginTop: 6, transform: `translateY(${(1 - p(5)) * 20}px)` }}>E FIZERAM MAIS ↑</Mono>
    </Faixa>
  );
};

// anzol: entra a linha · 1 o peixe nada até o anzol · 2 belisca · 3 fisgada (sobe) · 4+ o peixe se debate a cada ação
export const AnzolA: React.FC<P> = ({ c }) => {
  const { n, p, f } = useAcoes();
  const sw = interpolate(f, [0, 20], [0, 1], cl);
  const px = interpolate(p(1), [0, 1], [-60, 40]) + (n >= 2 ? Math.sin(p(2) * Math.PI * 2) * 10 : 0);
  const sobe = p(3) * 70;
  const debate = n >= 4 ? Math.sin(p(n) * Math.PI * 3) * 12 : 0;
  return (
    <Faixa>
      <svg width="360" height="300" viewBox="0 0 360 300" style={{ overflow: "visible" }}>
        <g transform={`translate(0 ${-sobe})`}>
          <line x1="180" y1="-200" x2="180" y2={120 * sw} stroke={C.tinta} strokeWidth="3" />
          <path d="M 180 120 L 180 170 Q 180 205 150 205 Q 125 205 125 182" fill="none" stroke={C.tinta} strokeWidth="5" strokeLinecap="round" opacity={sw} />
        </g>
        <g transform={`translate(${70 + px} ${240 - sobe}) rotate(${debate} 70 0)`} opacity={sw}>
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

// logo: o N fica intocado (guia de marca). As ações acontecem em volta: 1 cantos de enquadramento · 2 cota de altura · 3 área de proteção tracejada
export const LogoNA: React.FC<P> = ({ c }) => {
  const { n, p } = useAcoes();
  const k = useEntra(c.silencio ? 20 : 0, 18);
  const kl = useEntra(26, 14);
  const H = 380, Wl = 214;
  return (
    <Faixa>
      <div style={{ position: "relative", opacity: k }}>
        <NLogo altura={H} />
        <svg width={Wl + 240} height={H + 240} style={{ position: "absolute", left: -120, top: -120, overflow: "visible", pointerEvents: "none" }}>
          {[[0, 0, 1, 1], [1, 0, -1, 1], [0, 1, 1, -1], [1, 1, -1, -1]].map(([x, y, sx, sy], i) => {
            const X = 100 + x * (Wl + 40), Y = 100 + y * (H + 40);
            return <path key={i} d={`M ${X} ${Y + sy * 30 * p(1)} L ${X} ${Y} L ${X + sx * 30 * p(1)} ${Y}`} fill="none" stroke={C.tinta} strokeWidth="3" />;
          })}
          <g opacity={p(2)}>
            <line x1={Wl + 175} y1={120} x2={Wl + 175} y2={120 + H * p(2)} stroke={C.secundario} strokeWidth="2" />
            <text x={Wl + 188} y={120 + H / 2} fontFamily={MONO} fontSize="15" fill={C.secundario} letterSpacing="2">ALTURA N</text>
          </g>
          <rect x={60} y={60} width={(Wl + 120) * p(3)} height={H + 120} fill="none" stroke={C.secundario} strokeWidth="2" strokeDasharray="10 8" opacity={p(3)} />
          {n >= 4 && <g>
            <line x1={100} y1={H + 205} x2={100 + (Wl + 40) * Math.min(1, (n - 3) / 5)} y2={H + 205} stroke={C.tinta} strokeWidth="3" />
            {Array.from({ length: Math.min(6, n - 3) }, (_, i) => <line key={i} x1={100 + i * (Wl + 40) / 5} y1={H + 196} x2={100 + i * (Wl + 40) / 5} y2={H + 214} stroke={C.tinta} strokeWidth="2" />)}
            <text x={100} y={H + 236} fontFamily={MONO} fontSize="14" fill={C.secundario} letterSpacing="2">RESPIRO · {String(n - 3).padStart(2, "0")}</text>
          </g>}
        </svg>
      </div>
      {c.legenda && <div style={{ marginTop: 90, opacity: kl }}><Kinetic texto={c.legenda} size={40} peso={700} delay={26} passo={2} /></div>}
    </Faixa>
  );
};

// cores: o N limpo; 1 amostra vermelha · 2 amostra escura · 3 carimbo "OFICIAL" · 4 a cota mede a amostra
export const CoresA: React.FC<P> = () => {
  const { n, p, f } = useAcoes();
  const k = interpolate(f, [0, 14], [0, 1], cl);
  const sw = (cor: string, hex: string, pms: string, kk: number) => (
    <div style={{ display: "flex", alignItems: "center", gap: 20, opacity: kk, transform: `translateX(${(1 - kk) * -40}px)` }}>
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
      <div style={{ display: "flex", flexDirection: "column", gap: 26, position: "relative" }}>
        <div style={{ outline: n >= 5 && n % 2 === 1 ? `3px solid ${C.tinta}` : "none", outlineOffset: 8 }}>{sw(C.netflix, "#E50914", "NETFLIX RED · PMS 1795 C", Math.max(0.0, p(1)))}</div>
        <div style={{ outline: n >= 5 && n % 2 === 0 ? `3px solid ${C.tinta}` : "none", outlineOffset: 8 }}>{sw(C.netflixEscuro, "#B20710", "SYMBOL DARK RED · PMS 7627 C", p(2))}</div>
        <div style={{ position: "absolute", right: -70, top: -40 }}><Bate texto="OFICIAL" prog={p(3)} rot={8} /></div>
        <div style={{ position: "absolute", left: 0, top: -22, width: 90 * p(4), height: 2, background: C.tinta }} />
      </div>
    </Faixa>
  );
};

// proibições: os 8 quadros entram com a cena; cada ação risca um (o X é traçado); depois de todos, carimbo
export const ProibicoesA: React.FC<P> = ({ c }) => {
  const { n, p, f } = useAcoes();
  const tf = ["scaleX(1.6)", "rotate(25deg)", "none", "none", "none", "none", "perspective(200px) rotateX(55deg)", "none"];
  const m = c.itens.length;
  return (
    <Faixa>
      <Mono size={20} cor={C.tinta} style={{ marginBottom: 26 }}>O QUE O GUIA PROÍBE</Mono>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 140px)", gap: "26px 14px" }}>
        {c.itens.map((it: string, i: number) => {
          const k = interpolate(f - i * 4, [0, 10], [0, 1], { ...cl, easing: ease });
          const bg = i === 2 ? C.tinta : i === 4 ? "repeating-linear-gradient(45deg,#BBB 0 6px,#EEE 6px 12px)" : i === 5 ? C.secundario : i === 7 ? C.branco : C.apoio;
          const x = p(i + 1);
          const foco = n === i + 1;
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", opacity: k, transform: `scale(${foco ? 1 + 0.12 * Math.sin(x * Math.PI) : 1})` }}>
              <div style={{ width: 120, height: 120, position: "relative", display: "flex", alignItems: "center", justifyContent: "center", background: i === 4 || i === 5 ? bg : "transparent" }}>
                <div style={{ width: 54, height: 54, background: i === 4 || i === 5 ? C.apoio : bg, transform: tf[i], boxShadow: i === 3 ? "0 0 22px 8px #999" : "none",
                  border: i === 7 ? `3px dashed ${C.tinta}` : "none", borderRadius: i === 7 ? 27 : 0 }} />
                <svg width="120" height="120" style={{ position: "absolute" }}>
                  <line x1="14" y1="14" x2={14 + 92 * Math.min(1, x * 2)} y2={14 + 92 * Math.min(1, x * 2)} stroke={C.tinta} strokeWidth="5" />
                  <line x1="106" y1="14" x2={106 - 92 * Math.max(0, x * 2 - 1)} y2={14 + 92 * Math.max(0, x * 2 - 1)} stroke={C.tinta} strokeWidth="5" />
                </svg>
              </div>
              <Mono size={14} cor={C.tinta} style={{ marginTop: 8, fontWeight: foco ? 700 : 400 }}>{it}</Mono>
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 22, minHeight: 50, display: "flex", justifyContent: "center", alignItems: "center" }}>
        {n > m ? <Bate texto="PROIBIDO PELO GUIA" prog={p(m + 1)} size={20} /> : <div style={{ fontFamily: FONT, fontSize: 18, color: C.secundario }}>Demonstração genérica: o logo verdadeiro nunca é distorcido.</div>}
      </div>
    </Faixa>
  );
};

// pôsteres: entram com a cena; cada ação põe um em destaque (sobe e aproxima, os outros recuam); com 1 pôster, 1 aproxima · 2 carimbo do rótulo
export const PostersA: React.FC<P> = ({ c }) => {
  const { n, p, f } = useAcoes();
  const m = c.imgs.length;
  const w = m === 1 ? 430 : 330;
  const foco = n === 0 ? -1 : (n - 1) % m;
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", gap: 40, alignItems: "flex-end" }}>
        {c.imgs.map((src: string, i: number) => {
          const k = interpolate(f - i * 10, [0, 16], [0, 1], { ...cl, easing: ease });
          const pb = c.pb?.[i];
          const em = m > 1 && i === foco ? p(n) : m === 1 && n >= 1 ? (n >= 3 ? (n % 2 ? p(n) : 1 - p(n) * 0.7) : p(1)) : 0;
          const recua = m > 1 && foco >= 0 && i !== foco ? 1 : 0;
          return (
            <div key={i} style={{ width: pb ? w * 0.82 : w, opacity: k * (1 - recua * 0.35), transform: `translateY(${(1 - k) * 60 - em * 26}px) scale(${1 + em * 0.07})`,
              display: "flex", flexDirection: "column", alignItems: "center", position: "relative", zIndex: i === foco ? 2 : 1 }}>
              <Img src={staticFile(src)} style={{ width: "100%", boxShadow: SOMBRA, border: "8px solid white", filter: pb ? "grayscale(1) contrast(1.1)" : "none" }} />
              <Mono size={17} cor={C.tinta} style={{ marginTop: 18, fontWeight: i === foco ? 700 : 400 }}>{c.rotulos?.[i]}</Mono>
              {(m === 1 ? n >= 2 : i === foco) && c.rotulos?.[i] && <div style={{ position: "absolute", top: 20, right: -30 }}><Bate texto={c.rotulos[i].split("·")[0].trim()} prog={m === 1 ? p(2) : p(n)} rot={7} size={18} /></div>}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// botão: aperta de novo a cada ação; o contador sobe em quatro levas
export const BotaoA: React.FC<P> = ({ c }) => {
  const { n, p, f } = useAcoes();
  const aperta = (fr: number) => interpolate(fr, [0, 3, 7], [1, 0.9, 1], cl);
  const press = n >= 1 ? aperta(p(n) * 9) : aperta(f - 8);
  const k = useEntra(18, 12);
  const prog = Math.min(1, (n === 0 ? interpolate(f, [18, 40], [0, 0.25], cl) : 0.25 + 0.25 * (n - 1) + 0.25 * p(n)));
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

// colunas: 1 estrelas da esquerda acendem · 2 a barra da direita sobe · 3 carimbo "O QUE ASSISTEM"
export const ColunasA: React.FC<P> = ({ c }) => {
  const { p } = useAcoes();
  return (
    <Faixa style={{ flexDirection: "row", gap: 40 }}>
      <div style={{ width: 270, display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
        <Mono size={18} cor={C.tinta}>{c.esquerda}</Mono>
        <div style={{ display: "flex" }}>{[0, 1, 2, 3, 4].map((i) => (
          <svg key={i} width={46} height={46} viewBox="0 0 24 24" style={{ opacity: p(1) * 5 > i ? 1 : 0.15 }}><path d="M12 2l3 7h7l-5.5 4.5L18.5 21 12 16.8 5.5 21l2-7.5L2 9h7z" fill={C.tinta} /></svg>
        ))}</div>
        <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 26, color: C.tinta }}>A LISTA DE SCHINDLER</div>
      </div>
      <div style={{ width: 3, height: 340, background: C.apoio }} />
      <div style={{ width: 270, display: "flex", flexDirection: "column", alignItems: "center", gap: 20, position: "relative" }}>
        <Mono size={18} cor={C.tinta}>{c.direita}</Mono>
        <div style={{ width: 70, height: 220, border: `3px solid ${C.tinta}`, display: "flex", alignItems: "flex-end" }}>
          <div style={{ width: "100%", height: `${p(2) * 100}%`, background: C.tinta }} />
        </div>
        <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 26, color: C.tinta }}>ADAM SANDLER</div>
        <div style={{ position: "absolute", top: 90, right: -40 }}><Bate texto="O QUE ASSISTEM" prog={p(3)} rot={8} size={16} /></div>
      </div>
    </Faixa>
  );
};

// fim: o átomo gira devagar; 1 a marca é carimbada · 2 a assinatura sobe · 3 carimbo ARQUIVO 10/10 · 4 ENCERRADO · 5+ recarimba (ENCERRADO/ARQUIVADO) e o átomo dá um salto de giro a cada ação
export const FimA: React.FC<P> = ({ c, dur }) => {
  const { n, p, f, fps } = useAcoes();
  const k = useEntra(0, 18);
  const off = interpolate(f, [dur * fps - 40, dur * fps - 20], [1, 0], cl);
  const salto = n >= 3 ? Array.from({ length: n - 2 }, (_, i) => p(i + 3) * 60).reduce((a, b) => a + b, 0) : 0;
  return (
    <Faixa style={{ opacity: off }}>
      <div style={{ opacity: k, transform: `rotate(${f * 0.5 + salto}deg)` }}><Picto nome="ATOMO" size={110} /></div>
      <div style={{ marginTop: 26, minHeight: 90, display: "flex", alignItems: "center" }}>
        {n >= 1 ? <Bate texto={c.marca} prog={p(1)} rot={-2} size={46} /> : <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.tinta, opacity: k, letterSpacing: 2 }}>{c.marca}</div>}
      </div>
      <Mono size={20} style={{ marginTop: 18, opacity: k * (n >= 2 ? p(2) : 0), transform: `translateY(${(1 - p(2)) * 50}px)` }}>{c.sub}</Mono>
      <div style={{ marginTop: 30, minHeight: 70, display: "flex", gap: 28, alignItems: "center" }}>
        {n >= 3 && <Bate texto="ARQUIVO 10/10" prog={p(3)} rot={3} size={30} />}
        {n >= 4 && <Bate texto={n >= 5 && n % 2 ? "ARQUIVADO" : "ENCERRADO"} prog={n >= 5 ? p(n) : p(4)} rot={-3} size={30} />}
      </div>
    </Faixa>
  );
};

// ao vivo: a TV acende; 1 a 1ª linha é datilografada · 2 a 2ª · 3+ o relógio "AO VIVO" avança e a tela dá um pulo de sinal a cada ação
export const AoVivoA: React.FC<P> = ({ c }) => {
  const { n, p, f } = useAcoes();
  const k = useMola(0, 16);
  const l1 = c.linha1.slice(0, Math.ceil(c.linha1.length * Math.max(0.2, p(1))));
  const l2 = (c.linha2 ?? "").slice(0, Math.ceil((c.linha2 ?? "").length * p(2)));
  const pulo = n >= 3 ? (1 - p(n)) * 14 : 0;
  const seg = Math.floor(f / 30);
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco, alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: C.tinta, padding: "30px 30px 60px", borderRadius: 30, boxShadow: SOMBRA, transform: `scale(${k})` }}>
        <div style={{ width: 580, height: 400, background: "#111", borderRadius: 22, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", position: "relative", overflow: "hidden" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14, transform: `translateY(${pulo}px)` }}>
            <div style={{ width: 22, height: 22, borderRadius: 11, background: C.ambar, opacity: Math.floor(f / 12) % 2 ? 1 : 0.25 }} />
            <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 80, color: "#EEE" }}>{l1}</div>
          </div>
          <Mono size={18} cor="#CCC" style={{ marginTop: 18, maxWidth: 480, minHeight: 50 }}>{l2}</Mono>
          <Mono size={16} cor="#999" style={{ position: "absolute", top: 18, right: 22 }}>{`00:${String(seg).padStart(2, "0")}`}</Mono>
          <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0px, rgba(0,0,0,0.25) 1px, transparent 1px, transparent 3px)" }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
