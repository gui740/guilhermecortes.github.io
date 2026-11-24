import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { useAudioData, visualizeAudio } from "@remotion/media-utils";
import { noise2D } from "@remotion/noise";
import { fundo } from "../cenarios/Fundos";
import { LuzFrente } from "../cenarios/EstadioNoite";
import { Boca, Chibi, ELENCO, Expressao, Olhos, Pose, PRESETS } from "../personagens/Chibi";
import { easeInOut, Palavra, quando } from "./tempo";
import * as Ob from "./Objetos";

/* eslint-disable @typescript-eslint/no-explicit-any */
export type Camada = Record<string, any> & { tipo: string };
export type PlanoCfg = { de?: string; fundo: string; camera?: { zoom?: [number, number]; pan?: [number, number]; punch?: boolean }; camadas: Camada[] };

const FPS = 30;

/** Fala do personagem: abre/fecha a boca pela amplitude da narração da cena. */
const useAmplitude = (audio: string | undefined, frameCena: number) => {
  const data = useAudioData(audio ? staticFile(audio) : staticFile("lusa2013/cena_01.wav"));
  if (!data || !audio) return 0;
  const v = visualizeAudio({ fps: FPS, frame: Math.max(0, frameCena - Math.round(0.15 * FPS)), audioData: data, numberOfSamples: 16 });
  return v.slice(0, 8).reduce((a, b) => a + b, 0) / 8;
};

const hash = (s: string) => s.split("").reduce((a, c) => a + c.charCodeAt(0), 0);

const Personagem: React.FC<{ c: Camada; u: number; t: number; amp: number }> = ({ c, u, t, amp }) => {
  if (u < 0 && c.entra !== "nenhum") return null;
  const uu = c.entra === "nenhum" ? Math.max(u, 2) : u;
  const larg = c.alt * (500 / 900);
  let dx = 0;
  let dy = 0;
  let sx = 1;
  let sy = 1;
  let rot = 0;
  if (c.entra === "queda") {
    const q = 0.34;
    dy = uu < q ? -1300 * Math.pow(1 - uu / q, 2) : 0;
    const v = uu - q;
    const sq = v > 0 ? 0.2 * Math.exp(-v * 7) * Math.cos(v * 22) : 0;
    sx = 1 + sq;
    sy = 1 - sq;
  } else if (c.entra === "lado") {
    const p = Ob.mola(uu, 2.2, 0.5);
    dx = (1 - p) * (c.espelhar ? 900 : -900);
  }
  // respiração e reações
  sy *= 1 + 0.015 * Math.sin((2 * Math.PI * t) / 1.7 + hash(c.quem));
  if (c.reacao === "pulo") dy -= Math.abs(Math.sin(t * 7)) * 34;
  if (c.reacao === "tremor") dx += Math.sin(t * 46) * 3.5;
  if (c.reacao === "balanco") rot = Math.sin(t * 1.4) * 2.2;
  let cair = 0;
  if (c.cai) {
    const v = Math.max(0, t - 0.45);
    cair = v * v * 2600;
  }
  // piscada a cada 2,5–4 s (4 quadros)
  const per = 2.5 + (hash(c.quem) % 15) / 10;
  const pisca = (t + (hash(c.quem) % 7) * 0.3) % per < 4 / FPS;
  const pr = PRESETS[c.expr as Expressao];
  const olhosBase: Olhos = pr.olhos;
  const olhos: Olhos | undefined = pisca && olhosBase !== "fechado" && olhosBase !== "feliz" ? "fechado" : undefined;
  let boca: Boca | undefined = c.boca;
  if (c.fala) boca = amp > 0.12 ? (Math.floor(t * 8) % 3 === 0 ? "o" : "aberta") : pr.boca === "dentes" ? "dentes" : "neutra";
  const ficha = ELENCO[c.quem];
  let objeto: React.ReactNode = null;
  if (c.objeto === "regulamento") objeto = <Ob.Regulamento />;
  if (c.objeto === "maleta") objeto = <Ob.Maleta />;
  if (c.pose === "telefone") objeto = <Ob.Telefone />;
  if (c.pose === "suor") objeto = <Ob.Suor t={t} />;
  const chibi = <Chibi {...ficha} expressao={c.expr} olhos={olhos} boca={boca} pose={c.pose as Pose | undefined} altura={c.alt} espelhar={c.espelhar} objeto={objeto} cabeca={Math.sin(t * 1.3) * 0.25} />;
  const corpo = (
    <div style={{ position: "absolute", left: c.x - larg / 2 + dx, top: c.pe - c.alt + dy + cair, width: larg, height: c.alt, transform: `rotate(${rot}deg) scale(${sx}, ${sy})`, transformOrigin: "50% 100%", filter: cair > 40 ? `blur(${Math.min(8, cair / 120)}px)` : undefined }}>
      {chibi}
    </div>
  );
  const sombra = !c.cai && (
    <div style={{ position: "absolute", left: c.x - larg * 0.32 + dx, top: c.pe - c.alt * 0.02, width: larg * 0.64, height: c.alt * 0.05, borderRadius: "50%", background: "rgba(0,0,0,0.38)", filter: "blur(6px)", transform: `scale(${1 - Math.min(0.6, -dy / 1300)})` }} />
  );
  if (c.cai) return <div style={{ position: "absolute", inset: 0, clipPath: "inset(0 0 330px 0)" }}>{corpo}</div>;
  return (
    <>
      {sombra}
      {corpo}
    </>
  );
};

/** Impactos (tempo local) que geram punch-in e tremida de câmera. */
const impactos = (camadas: Camada[], t0: (c: Camada) => number) => {
  const out: number[] = [];
  camadas.forEach((c) => {
    const s = t0(c);
    if (c.tipo === "titulo" || c.tipo === "carimbo") out.push(s + 0.16);
    if (c.tipo === "martelo") out.push(...Ob.impactosMartelo(s, c.batidas ?? 1));
    if (c.tipo === "bloco") out.push(Ob.impactoBloco(s));
    if (c.tipo === "personagem" && c.entra === "queda") out.push(s + 0.34);
  });
  return out;
};

export const Plano: React.FC<{ p: PlanoCfg; pal: Palavra[]; tIni: number; tFim: number; t: number; audio?: string }> = ({ p, pal, tIni, tFim, t, audio }) => {
  const dur = Math.max(0.5, tFim - tIni);
  const tc = tIni + t; // tempo na cena
  const t0 = (c: Camada) => quando(pal, c.em, tIni, tIni) - tIni;
  const imps = impactos(p.camadas, t0);
  const temFala = p.camadas.some((c) => c.fala);
  const amp = useAmplitude(temFala ? audio : undefined, Math.round(tc * FPS));
  // câmera
  const [z0, z1] = p.camera?.zoom ?? [1, 1.05];
  let z = z0 + (z1 - z0) * easeInOut(t / dur);
  let sx = 0;
  let sy = 0;
  imps.forEach((ti) => {
    const v = t - ti;
    if (v >= 0 && v < 0.6) {
      if (p.camera?.punch) z += 0.08 * Math.exp(-v * 6);
      const e = 18 * Math.exp(-v * 7.5);
      sx += e * Math.sin(v * 90);
      sy += e * Math.cos(v * 70);
    }
  });
  sx += noise2D("mx", t * 0.6, 0) * 1.6;
  sy += noise2D("my", t * 0.6, 0) * 1.6;
  const pan = p.camera?.pan ?? [0, 0];
  const px = pan[0] * (easeInOut(t / dur) - 0.5) * 2;
  const py = pan[1] * (easeInOut(t / dur) - 0.5) * 2;
  const L = (f: number, filtro?: string): React.CSSProperties => ({
    transform: `translate(${(px + sx) * f}px, ${(py + sy) * f}px) scale(${1 + (z - 1) * f})`,
    transformOrigin: "50% 50%",
    filter: filtro,
  });
  const F = fundo(p.fundo);
  const frente = ["confete", "poeira", "faiscas", "chuva", "flashes"];
  const render = (c: Camada, i: number) => {
    const u = t - t0(c);
    switch (c.tipo) {
      case "personagem":
        return <Personagem key={i} c={c} u={u} t={t} amp={amp} />;
      case "titulo":
        return <Ob.Titulo key={i} linhas={c.linhas} y={c.y} u={u} />;
      case "carimbo":
        return <Ob.Carimbo key={i} texto={c.texto} sub={c.sub} cor={c.cor} x={c.x} y={c.y} rot={c.rot} u={u} />;
      case "banner":
        return <Ob.Banner key={i} texto={c.texto} cor={c.cor} u={u} />;
      case "pulsa":
        return <Ob.Pulsa key={i} texto={c.texto} x={c.x} y={c.y} u={u} />;
      case "logo":
        return <Ob.Logo key={i} x={c.x} y={c.y} u={u} />;
      case "relogio":
        return <Ob.Relogio key={i} x={c.x} y={c.y} tam={c.tam} minuto={c.minuto} u={u} />;
      case "relogioParede":
        return <Ob.RelogioParede key={i} x={c.x} y={c.y} u={u} />;
      case "placar":
        return <Ob.Placar key={i} {...(c as any)} u={u} />;
      case "jornal":
        return <Ob.Jornal key={i} manchete={c.manchete} linha={c.linha} x={c.x} y={c.y} u={u} />;
      case "placaSubst":
        return <Ob.PlacaSubst key={i} texto={c.texto} x={c.x} y={c.y} u={u} />;
      case "martelo":
        return <Ob.Martelo key={i} x={c.x} y={c.y} batidas={c.batidas ?? 1} u={u} />;
      case "bloco":
        return <Ob.Bloco key={i} texto={c.texto} x={c.x} y={c.y} u={u} />;
      case "tabela":
        return <Ob.Tabela key={i} antes={c.antes} depois={c.depois} y={c.y} u={u} tLusa={quando(pal, c.trocaLusa, tIni) - tIni - t0(c)} tFlu={quando(pal, c.trocaFlu, tIni) - tIni - t0(c)} />;
      case "buraco":
        return <Ob.Buraco key={i} texto={c.texto} x={c.x} y={c.y} u={u} />;
      case "gordura":
        return <Ob.Gordura key={i} y={c.y} u={u} />;
      case "papel":
        return <Ob.Papel key={i} texto={c.texto} x={c.x} y={c.y} u={u} uRasga={t - (quando(pal, c.rasga, tIni) - tIni)} />;
      case "placa":
        return <Ob.Placa key={i} texto={c.texto} x={c.x} y={c.y} u={u} />;
      case "silhueta":
        return (
          <Ob.Silhueta key={i} x={c.x} pe={c.pe} alt={c.alt} u={u}>
            <Chibi {...ELENCO.LUSA} uniforme={{ ...ELENCO.LUSA.uniforme, escudo: undefined }} expressao="neutro" pose="baixo" altura={c.alt} />
          </Ob.Silhueta>
        );
      default:
        return null;
    }
  };
  const renderFrente = (c: Camada, i: number) => {
    const u = t - t0(c);
    switch (c.tipo) {
      case "confete":
        return <Ob.Confete key={i} u={u} />;
      case "poeira":
        return <Ob.Poeira key={i} u={u} />;
      case "faiscas":
        return <Ob.Faiscas key={i} x={c.x} y={c.y} u={u} />;
      case "chuva":
        return <Ob.Chuva key={i} t={t} />;
      case "flashes":
        return <Ob.Flashes key={i} t={t} />;
      default:
        return null;
    }
  };
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#0B1433" }}>
      <AbsoluteFill style={L(0.3, "blur(2px)")}>{F.longe}</AbsoluteFill>
      {F.meio && <AbsoluteFill style={L(0.6)}>{F.meio}</AbsoluteFill>}
      {F.chao && <AbsoluteFill style={L(0.85)}>{F.chao}</AbsoluteFill>}
      {/* flashes ficam na torcida (meio) */}
      <AbsoluteFill style={L(0.6)}>{p.camadas.filter((c) => c.tipo === "flashes").map(renderFrente)}</AbsoluteFill>
      <AbsoluteFill style={L(1)}>{p.camadas.filter((c) => !frente.includes(c.tipo)).map(render)}</AbsoluteFill>
      <AbsoluteFill style={L(1.3)}>{p.camadas.filter((c) => frente.includes(c.tipo) && c.tipo !== "flashes").map(renderFrente)}</AbsoluteFill>
      <LuzFrente />
    </AbsoluteFill>
  );
};
