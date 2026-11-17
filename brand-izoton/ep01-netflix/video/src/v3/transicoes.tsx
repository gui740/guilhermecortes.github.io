// Transições e painel de arquivo v3
import React from "react";
import { AbsoluteFill, Freeze, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, FONT, MONO, SOMBRA } from "../theme";
import { CRTOverlay } from "../cenas/bits";
import { easeInOut, easeOut } from "./kit";

const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

/** Tela de arquivo CRT com liga/desliga (usada em todas as falas). */
export const TelaCRT: React.FC<{ clip: string; inicioClip: number; dur: number; liga?: boolean; desliga?: boolean; congelaFim?: boolean }> =
  ({ clip, inicioClip, dur, liga = true, desliga = true, congelaFim = false }) => {
    const f = useCurrentFrame();
    const on = liga ? interpolate(f, [0, 6], [0.004, 1], { ...clamp, easing: easeOut }) : 1;
    const flash = liga ? interpolate(f, [0, 2, 6], [1, 1, 0], clamp) : 0;
    const off = desliga ? interpolate(f, [dur - 10, dur - 4], [1, 0.004], clamp) : 1;
    const offX = desliga ? interpolate(f, [dur - 4, dur], [1, 0.002], clamp) : 1;
    const push = interpolate(f, [0, dur], [1, 1.07], clamp);
    const video = <OffthreadVideo src={staticFile(clip)} muted startFrom={inicioClip} style={{ width: "100%", height: "100%", objectFit: "cover" }} />;
    return (
      <AbsoluteFill style={{ backgroundColor: desliga && f > dur - 10 ? C.branco : "black" }}>
        <AbsoluteFill style={{ transform: `scaleY(${on * off}) scaleX(${offX})`, background: "black" }}>
          <AbsoluteFill style={{ transform: `scale(${push})` }}>
            {congelaFim && f > dur - 12 ? <Freeze frame={dur - 12}>{video}</Freeze> : video}
          </AbsoluteFill>
          <CRTOverlay />
          <AbsoluteFill style={{ background: "white", opacity: flash }} />
        </AbsoluteFill>
      </AbsoluteFill>
    );
  };

/** Máscara de revelação: um retângulo varre a cena em 10 quadros. */
export const Mascara: React.FC<{ inicio: number; children: React.ReactNode; direcao?: "dir" | "baixo" | "circulo" }> = ({ inicio, children, direcao = "dir" }) => {
  const f = useCurrentFrame();
  const k = interpolate(f - inicio, [0, 10], [0, 1], { ...clamp, easing: easeInOut });
  if (f < inicio) return null;
  const clip = direcao === "circulo" ? `circle(${k * 75}% at 50% 50%)` : direcao === "baixo" ? `inset(0 0 ${(1 - k) * 100}% 0)` : `inset(0 ${(1 - k) * 100}% 0 0)`;
  return <AbsoluteFill style={{ clipPath: clip }}>{children}</AbsoluteFill>;
};

/** Empurrão de página: a composição atual sai deslizando, a nova entra pelo lado oposto. */
export const Empurrao: React.FC<{ inicio: number; antes: React.ReactNode; depois: React.ReactNode }> = ({ inicio, antes, depois }) => {
  const f = useCurrentFrame();
  const k = interpolate(f - inicio, [0, 12], [0, 1], { ...clamp, easing: easeInOut });
  return (
    <AbsoluteFill>
      {k < 1 && <AbsoluteFill style={{ transform: `translateX(${-k * 1920}px)` }}>{antes}</AbsoluteFill>}
      {k > 0 && <AbsoluteFill style={{ transform: `translateX(${(1 - k) * 1920}px)` }}>{depois}</AbsoluteFill>}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ painel de arquivo */
export const CAPITULOS = ["DO DVD AO STREAMING", "A APOSTA NO ORIGINAL", "O BINGE COMO PRODUTO", "O ALGORITMO", "A CULTURA",
  "A IDENTIDADE", "A PUBLICIDADE", "OS FENÔMENOS", "A CONTA", "A CASA"];
const CW = 520, CH = 330, GX = 200, GY = 220, X0 = 300, Y0 = 300;
// 5 colunas x 2 linhas, em "serpente" (1→5 na linha de cima, 6→10 voltando embaixo)
export const posCartao = (i: number) => {
  const linha = i < 5 ? 0 : 1;
  const col = linha === 0 ? i : 9 - i;
  return { x: X0 + col * (CW + GX), y: Y0 + linha * (CH + GY) };
};
const PW = X0 * 2 + 5 * CW + 4 * GX, PH = Y0 * 2 + 2 * CH + GY;
const centro = (i: number) => { const p = posCartao(i); return { x: p.x + CW / 2, y: p.y + CH / 2 }; };
const ligacao = (i: number) => {
  // caminho de i até i+1 em ângulos retos (estilo diagrama técnico)
  const a = centro(i), b = centro(i + 1);
  if (i === 4) { const xr = posCartao(4).x + CW + 90; return `M ${posCartao(4).x + CW} ${a.y} H ${xr} V ${b.y} H ${posCartao(5).x + CW}`; }
  if (i < 4) return `M ${posCartao(i).x + CW} ${a.y} H ${posCartao(i + 1).x}`;
  return `M ${posCartao(i).x} ${a.y} H ${posCartao(i + 1).x + CW}`;
};

const Cartao: React.FC<{ i: number; preenchido: boolean; ativo: boolean }> = ({ i, preenchido, ativo }) => {
  const p = posCartao(i);
  return (
    <div style={{ position: "absolute", left: p.x, top: p.y, width: CW, height: CH, background: C.branco, borderRadius: 14,
      border: preenchido ? `2px solid ${C.tinta}` : `2px dashed ${C.apoio}`, boxShadow: ativo ? SOMBRA : "0 8px 20px rgba(0,0,0,0.06)",
      boxSizing: "border-box", padding: "26px 30px" }}>
      <div style={{ fontFamily: MONO, fontSize: 26, letterSpacing: 3, color: ativo ? C.ambar : C.secundario }}>{String(i + 1).padStart(2, "0")}</div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 46, lineHeight: 1.0, color: preenchido ? C.tinta : C.apoio, marginTop: 18, textTransform: "uppercase" }}>
        {CAPITULOS[i]}
      </div>
      <div style={{ position: "absolute", left: 30, right: 30, bottom: 26, height: 2, background: preenchido ? C.tinta : C.apoio }} />
      <div style={{ position: "absolute", right: 30, bottom: 40, fontFamily: MONO, fontSize: 16, letterSpacing: 2, color: C.secundario }}>ARQUIVO {String(i + 1).padStart(2, "0")}/10</div>
    </div>
  );
};

/**
 * Viagem pelo painel. Fases (em quadros): mostra o cartão `de`, traço percorre a ligação, câmera voa até `para` com desfoque
 * e mergulha (zoom-in). `visaoGeral` mostra o painel inteiro (abertura e fechamento).
 */
export const Painel: React.FC<{ de: number; para: number; dur: number; preenchidos: number; visaoGeral?: boolean; mergulho?: boolean }> =
  ({ de, para, dur, preenchidos, visaoGeral = false, mergulho = true }) => {
    const f = useCurrentFrame();
    const t1 = Math.round(dur * 0.25), t2 = Math.round(dur * 0.5), t3 = Math.round(dur * 0.75);
    const zoomCartao = 1920 / (CW * 1.9);
    const zoomGeral = Math.min(1920 / PW, 1080 / PH) * 0.95;
    const A = centro(de), B = centro(para);
    // câmera
    let cx: number, cy: number, z: number, blur = 0;
    if (visaoGeral) {
      cx = PW / 2; cy = PH / 2;
      z = interpolate(f, [0, dur], [zoomGeral * 1.12, zoomGeral * 0.98], clamp);
      cx = PW / 2 + interpolate(f, [0, dur], [-180, 180], clamp);
    } else {
      const sai = interpolate(f, [0, t1], [zoomCartao * 1.6, zoomCartao], { ...clamp, easing: easeOut });
      const voo = interpolate(f, [t2, t3], [0, 1], { ...clamp, easing: easeInOut });
      cx = A.x + (B.x - A.x) * voo; cy = A.y + (B.y - A.y) * voo;
      const recuo = Math.sin(voo * Math.PI) * 0.35;
      z = f < t2 ? sai : zoomCartao * (1 - recuo);
      if (mergulho) z = z * interpolate(f, [t3, dur], [1, 2.6], { ...clamp, easing: Easing2 });
      blur = Math.sin(voo * Math.PI) * 9;
    }
    const trace = interpolate(f, [t1, t2], [0, 1], { ...clamp, easing: easeInOut });
    const branco = mergulho && !visaoGeral ? interpolate(f, [dur - 6, dur], [0, 1], clamp) : 0;
    return (
      <AbsoluteFill style={{ backgroundColor: "#F4F4F2", overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 960, top: 540, width: PW, height: PH, transformOrigin: "0 0",
          transform: `scale(${z}) translate(${-cx}px, ${-cy}px)`, filter: blur > 0.5 ? `blur(${blur}px)` : "none" }}>
          {/* grade técnica de fundo */}
          <div style={{ position: "absolute", inset: 0, backgroundImage: `linear-gradient(${C.apoio}55 1px, transparent 1px), linear-gradient(90deg, ${C.apoio}55 1px, transparent 1px)`,
            backgroundSize: "80px 80px" }} />
          <svg width={PW} height={PH} style={{ position: "absolute", left: 0, top: 0 }}>
            {Array.from({ length: 9 }, (_, i) => (
              <path key={i} d={ligacao(i)} fill="none" stroke={i < preenchidos - 1 ? C.tinta : C.apoio} strokeWidth={4} />
            ))}
            {Array.from({ length: 9 }, (_, i) => (
              <path key={"p" + i} d={ligacao(i)} fill="none" stroke={C.ambar} strokeWidth={6} strokeLinecap="round" pathLength={1}
                strokeDasharray="0.12 0.88" strokeDashoffset={-((f / 40 + i * 0.37) % 1)} opacity={0.75} />
            ))}
            {!visaoGeral && de !== para && (
              <path d={ligacao(Math.min(de, para))} fill="none" stroke={C.ambar} strokeWidth={10} strokeLinecap="round"
                pathLength={1} strokeDasharray="0.22 1" strokeDashoffset={-trace * 1.0 + 0.22} />
            )}
          </svg>
          {Array.from({ length: 10 }, (_, i) => <Cartao key={i} i={i} preenchido={i < preenchidos || (!visaoGeral && i === para && f > t3)} ativo={!visaoGeral && (i === para && f > t2 || i === de && f <= t2)} />)}
          <div style={{ position: "absolute", left: X0, top: 120, fontFamily: MONO, fontSize: 34, letterSpacing: 6, color: C.secundario }}>
            ARQUIVO NETFLIX · EP01 · 10 CAPÍTULOS
          </div>
        </div>
        <AbsoluteFill style={{ background: C.branco, opacity: branco }} />
      </AbsoluteFill>
    );
  };
const Easing2 = (t: number) => t * t * t;
