// Shorts 03–08 (Parada 3): gerador de Short a partir de trechos (blocos do Guilherme e falas de arquivo).
// Os hooks S03–S08 não foram gravados: o hook entra só como texto na tela (sem voz; nunca TTS), e a voz dele começa junto.
// Quando forem gravados, hooks.tsx (ComHook) põe a voz do hook antes do Short e este texto inicial sai.
import React from "react";
import { AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame } from "remotion";
import PAL from "./palavras_gui.json";
import TL from "../timeline_v3.json";
import { C, FONT, MONO } from "../theme";
import { NLogo } from "../cenas/bits";
import { Camera, Card, Carimbo3, Destaque, Grao, Papel, Recorte, useS } from "./kit";
import { TelaCRT } from "./transicoes";
import { FalaCtx, LegendaPalavra, Narr, Sfx, Trilha } from "./Amostra";
import { temHook } from "./hooks";

type W = [number, number, string];
const P = PAL as unknown as Record<string, { dur: number; palavras: W[] }>;
const ARQ = Object.fromEntries((TL as any).trechos.filter((b: any) => b.tipo === "arq").map((b: any) => [b.id, b.cenas[0]])) as Record<string, any>;

type Im = { src: string; tipo?: "rec" | "card" | "print" | "logo" };
type Seg =
  | { tipo: "narr"; bloco: string; imgs: Im[]; destaques?: [string, string, ("tinta" | "ambar" | "netflix")?][]; carimbo?: [string, string] }
  | { tipo: "arq"; id: string; dur?: number; lt: string };
export type ShortCfg = { id: string; topo: string; hook: string[]; segs: Seg[]; trilha: number; loop: string[] };

const durSeg = (s: Seg) => (s.tipo === "narr" ? P[s.bloco].dur : s.dur ?? ARQ[s.id].clipDur);
const GAP = 0.25;
export const duracaoShort = (cfg: ShortCfg) => cfg.segs.reduce((a, s) => a + durSeg(s) + GAP, 0) + 1.4;
const inicios = (cfg: ShortCfg) => { let t = 0; return cfg.segs.map((s) => { const a = t; t += durSeg(s) + GAP; return a; }); };

const Imagem: React.FC<{ im: Im; inicio: number; i: number }> = ({ im, inicio, i }) => {
  const rot = (i % 2 ? 1 : -1) * (2 + (i % 3));
  if (im.tipo === "logo") return <div style={{ position: "absolute", left: 0, right: 0, top: 380, display: "flex", justifyContent: "center" }}><NLogo altura={520} /></div>;
  if (im.tipo === "rec") return <Recorte src={im.src} x={im.src.includes("controle") ? 440 : 170} y={300} w={im.src.includes("controle") ? 200 : 740} inicio={inicio} rot={rot} seed={im.src + i} />;
  const poster = im.src.includes("poster");
  const w = poster ? 560 : 900, h = poster ? 820 : im.tipo === "print" ? 700 : 640;
  return (
    <Card x={(1080 - w) / 2} y={280} w={w} h={h} inicio={inicio} rotY={i % 2 ? -7 : 7} rotZ={rot} seed={im.src + i}>
      <Img src={staticFile(im.src)} style={{ width: "100%", height: "100%", objectFit: im.tipo === "print" ? "contain" : "cover", objectPosition: im.src.includes("guard") ? "50% 0%" : "50% 15%", background: C.branco }} />
    </Card>
  );
};

const SegNarr: React.FC<{ s: Extract<Seg, { tipo: "narr" }> }> = ({ s }) => {
  const S = useS();
  const f = useCurrentFrame();
  const dur = P[s.bloco].dur;
  const passo = Math.max(2.4, dur / Math.max(1, s.imgs.length));
  const k = Math.min(s.imgs.length - 1, Math.floor(f / S(passo)));
  const pal = P[s.bloco].palavras;
  const quando = (p: string) => pal.find((w) => w[2].toLowerCase().replace(/[.,?!%]/g, "").startsWith(p.toLowerCase()))?.[0] ?? 0;
  const ds = (s.destaques ?? []).map(([p, txt, tom]) => ({ t: quando(p), txt, tom })).sort((a, b) => a.t - b.t);
  const atual = ds.filter((d) => f >= S(d.t)).slice(-1)[0];
  return (
    <AbsoluteFill>
      <Camera dur={S(dur)} de={1.0} ate={1.16} dy={-40} degrau>
        {s.imgs.length > 0 && <Sequence key={k} from={S(k * passo)} layout="none"><Imagem im={s.imgs[k]} inicio={0} i={k} /></Sequence>}
      </Camera>
      {s.carimbo && <Carimbo3 texto={s.carimbo[1]} inicio={S(quando(s.carimbo[0]))} x={150} y={1060} rot={-4} size={32} />}
      {atual && <div style={{ position: "absolute", left: 40, right: 40, top: 1150, display: "flex", justifyContent: "center" }}><Destaque key={atual.t} texto={atual.txt} inicio={S(atual.t)} size={72} tom={atual.tom ?? "tinta"} /></div>}
    </AbsoluteFill>
  );
};

const SegArq: React.FC<{ s: Extract<Seg, { tipo: "arq" }> }> = ({ s }) => {
  const S = useS();
  const f = useCurrentFrame();
  const c = ARQ[s.id]; const dur = s.dur ?? c.clipDur;
  const linhas: string[] = c.legenda ?? [];
  const n = Math.min(linhas.length - 1, Math.floor((f / S(dur)) * linhas.length));
  const cor = c.tipo !== "arquivo";
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 0, right: 0, top: 260, height: 760, transformOrigin: "50% 50%",
        transform: `scale(${1 + 0.08 * Math.floor(f / 3) * 3 / S(dur)}) translateX(${18 * (Math.abs(((Math.floor(f / 3) * 3 / 120) % 2) - 1) * 2 - 1)}px)` }}>
        {cor ? <Img src={staticFile("media/v3img/card_house_kop.jpg")} style={{ display: "none" }} /> : null}
        <TelaCRT clip={c.clip} inicioClip={0} dur={S(dur)} />
      </div>
      <div style={{ position: "absolute", left: 60, top: 1050, fontFamily: MONO, fontSize: 26, letterSpacing: 3, color: C.secundario }}>{s.lt}</div>
      <div style={{ position: "absolute", left: 60, right: 60, top: 1330, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 62, lineHeight: 1.12, color: C.tinta }}>
        {(linhas[n] ?? "").toUpperCase()}
      </div>
    </AbsoluteFill>
  );
};

export const ShortGen: React.FC<{ cfg: ShortCfg }> = ({ cfg }) => {
  const S = useS();
  const f = useCurrentFrame();
  const ini = inicios(cfg);
  const total = duracaoShort(cfg);
  const palavras: W[] = cfg.segs.flatMap((s, i) => (s.tipo === "narr" ? P[s.bloco].palavras.map((w) => [w[0] + ini[i], w[1] + ini[i], w[2]] as W) : []));
  const falas: [number, number][] = cfg.segs.map((s, i) => [ini[i], ini[i] + durSeg(s)]);
  const fim = ini[ini.length - 1] + durSeg(cfg.segs[cfg.segs.length - 1]);
  return (
    <FalaCtx.Provider value={falas}>
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <Papel />
      {cfg.segs.map((s, i) => (
        <Sequence key={i} from={S(ini[i])} durationInFrames={S(durSeg(s) + GAP)}>
          {s.tipo === "narr" ? <SegNarr s={s} /> : <SegArq s={s} />}
        </Sequence>
      ))}
      {/* hook em texto, no quadro 0 (sem voz); some quando o hook gravado entra antes (hooks.tsx) */}
      {f < S(2.4) && !temHook(cfg.id) && (
        <AbsoluteFill style={{ background: C.branco }}>
          <div style={{ position: "absolute", left: 60, right: 60, top: 420, display: "flex", flexDirection: "column", alignItems: "center", gap: 18,
            transform: `scale(${1 + 0.16 * Math.floor(f / 3) * 3 / S(2.4)}) translateY(${-40 * Math.floor(f / 3) * 3 / S(2.4)}px)` }}>
            {cfg.hook.map((l, i) => <Destaque key={i} texto={l} inicio={i * 4} size={i === cfg.hook.length - 1 ? 104 : 76} tom={i === cfg.hook.length - 1 ? "tinta" : "tinta"} />)}
          </div>
        </AbsoluteFill>
      )}
      {/* loop: o último quadro retoma o hook */}
      {f >= S(fim) && (
        <AbsoluteFill style={{ background: C.branco }}>
          <div style={{ position: "absolute", left: 60, right: 60, top: 520, display: "flex", flexDirection: "column", alignItems: "center", gap: 18,
            transform: `scale(${1 + 0.14 * Math.floor((f - S(fim)) / 3) * 3 / S(1.4)}) translateY(${-36 * Math.floor((f - S(fim)) / 3) * 3 / S(1.4)}px)` }}>
            {cfg.loop.map((l, i) => <Destaque key={i} texto={l} inicio={S(fim) + i * 4} size={i === cfg.loop.length - 1 ? 110 : 76} tom={i === cfg.loop.length - 1 ? "ambar" : "tinta"} />)}
          </div>
        </AbsoluteFill>
      )}
      <div style={{ position: "absolute", left: 60, top: 70, display: "flex", alignItems: "center", gap: 12, fontFamily: MONO, fontSize: 26, letterSpacing: 3, color: C.tinta }}>
        <span style={{ width: 12, height: 12, borderRadius: 6, background: C.ambar, display: "inline-block" }} />{cfg.topo}
      </div>
      {(f >= S(2.4) || temHook(cfg.id)) && <LegendaPalavra palavras={palavras} chave={{}} />}
      <Grao />
      {cfg.segs.map((s, i) => s.tipo === "narr"
        ? <Narr key={i} s={ini[i]} arq={`media/narr_gui/b${s.bloco}.wav`} />
        : <Narr key={i} s={ini[i]} arq={`media/arquivo/${s.id}.mp4`} vol={0.95} dur={durSeg(s)} />)}
      <Trilha de={cfg.trilha} vol={0.06} />
      <Sfx s={0} nome="carimbo_0" vol={0.3} />
      {cfg.segs.map((s, i) => <Sfx key={"x" + i} s={ini[i]} nome={s.tipo === "arq" ? "crt_on_1" : ["papel_1", "papel_2", "papel_3"][i % 3]} vol={0.3} />)}
      <Sfx s={fim} nome="carimbo_3" />
    </AbsoluteFill>
    </FalaCtx.Provider>
  );
};

const V = "media/v3img/", ST = "media/stills/";
export const SHORTS_CFG: ShortCfg[] = [
  { id: "SHORT03", topo: "ALGORITMO · NETFLIX", trilha: 300, hook: ["VOCÊ DÁ 5 ESTRELAS", "PARA UM FILME", "E ASSISTE OUTRO."], loop: ["O QUE VOCÊ ASSISTE", "É VOCÊ."],
    segs: [
      { tipo: "narr", bloco: "20", imgs: [{ src: V + "rec_hastings_2015.png", tipo: "rec" }, { src: V + "card_losgatos.jpg" }], destaques: [["milhão", "US$ 1 MILHÃO"], ["10", "+10%"], ["nunca", "NUNCA REPETIU", "ambar"]] },
      { tipo: "arq", id: "T12a", lt: "REED HASTINGS · TED · ABR. 2018" },
      { tipo: "arq", id: "T12b", lt: "REED HASTINGS · TED · ABR. 2018" },
      { tipo: "narr", bloco: "21", imgs: [{ src: V + "rec_hastings_2014.png", tipo: "rec" }], destaques: [["ideal", "VERSÃO IDEAL"], ["você", "VOCÊ", "ambar"]] },
    ] },
  { id: "SHORT04", topo: "CULTURA · NETFLIX", trilha: 360, hook: ["TODO CHEFE DA NETFLIX", "PRECISA RESPONDER", "UMA PERGUNTA."], loop: ["VOCÊ LUTARIA", "PARA MANTÊ-LA?"],
    segs: [
      { tipo: "narr", bloco: "27", imgs: [{ src: V + "rec_hastings_2015.png", tipo: "rec" }], destaques: [["densidade", "DENSIDADE DE TALENTO"]] },
      { tipo: "arq", id: "B02", dur: 14.0, lt: "REED HASTINGS · STANFORD · 2015" },
      { tipo: "narr", bloco: "28", imgs: [{ src: ST + "web_keeper.png", tipo: "print" }, { src: V + "rec_hastings_2014.png", tipo: "rec" }], destaques: [["keeper", "KEEPER TEST"], ["justo", "SEPARAR RÁPIDO"], ["pescaria", "PESCARIA", "ambar"], ["fica", "ESSE FICA.", "ambar"]], carimbo: ["memorando", "CULTURE MEMO · NETFLIX"] },
    ] },
  { id: "SHORT05", topo: "IDENTIDADE · NETFLIX", trilha: 420, hook: ["EM MUITOS PAÍSES,", "A NETFLIX NEM ESCREVE", "O PRÓPRIO NOME."], loop: ["DONO DE UMA", "LETRA."],
    segs: [
      { tipo: "narr", bloco: "30", imgs: [{ src: "", tipo: "logo" }], destaques: [["lidera", "LIDERA COM O N"], ["letra", "UMA LETRA DO ALFABETO", "ambar"]] },
      { tipo: "narr", bloco: "29", imgs: [{ src: "", tipo: "logo" }], destaques: [["cor", "SÓ UMA COISA TEM COR"], ["regra", "É REGRA.", "ambar"]] },
      { tipo: "narr", bloco: "31", imgs: [{ src: ST + "n_symbol_card.jpg" }], destaques: [["vermelho", "VERMELHO NETFLIX", "netflix"]] },
      { tipo: "narr", bloco: "32", imgs: [{ src: ST + "web_brand_n.png", tipo: "print" }], destaques: [["esticar", "ESTICAR"], ["girar", "GIRAR"], ["efeitos", "EFEITOS"], ["chão", "NO CHÃO", "ambar"], ["comida", "NA COMIDA", "ambar"]], carimbo: ["guia", "BRAND.NETFLIX.COM"] },
    ] },
  { id: "SHORT06", topo: "PUBLICIDADE · NETFLIX", trilha: 480, hook: ["EM 2015, UM CANDIDATO", "FEZ PROPAGANDA NA CNN.", "ELE NÃO EXISTE."], loop: ["ELE NÃO", "EXISTE."],
    segs: [
      { tipo: "narr", bloco: "34", imgs: [{ src: ST + "web_drum.png", tipo: "print" }], destaques: [["dezembro", "DEZ. 2015"], ["cnn", "AO VIVO · CNN"], ["anúncio", "ANÚNCIO ESPECIAL", "ambar"]], carimbo: ["debate", "5º DEBATE REPUBLICANO"] },
      { tipo: "arq", id: "FU1", dur: 9.5, lt: "COMERCIAL #FU2016 · NETFLIX" },
      { tipo: "narr", bloco: "35", imgs: [{ src: ST + "poster_houseofcards.jpg" }], destaques: [["frank", "FRANK UNDERWOOD", "ambar"], ["hashtag", "#FU2016"], ["março", "4 DE MARÇO"]] },
      { tipo: "arq", id: "FU2", lt: "COMERCIAL #FU2016 · NETFLIX" },
      { tipo: "narr", bloco: "36", imgs: [{ src: ST + "poster_houseofcards.jpg" }], destaques: [["entrou", "ENTROU NELA.", "ambar"]] },
    ] },
  { id: "SHORT07", topo: "A CONTA · NETFLIX", trilha: 540, hook: ["A NETFLIX PROIBIU", "DIVIDIR A SENHA.", "MUITA GENTE IA CANCELAR."], loop: ["A CONTA", "MUDOU."],
    segs: [
      { tipo: "narr", bloco: "44", imgs: [{ src: ST + "web_sharing.png", tipo: "print" }], destaques: [["100", "100 MILHÕES DE CASAS"], ["investir", "MENOS PARA INVESTIR"]], carimbo: ["fevereiro", "NETFLIX · 8 FEV. 2023"] },
      { tipo: "narr", bloco: "45", imgs: [{ src: ST + "carta_q4_22-06.png", tipo: "print" }], destaques: [["cancelamentos", "CANCELAMENTOS", "ambar"]] },
      { tipo: "narr", bloco: "46", imgs: [{ src: ST + "carta_q2_23-01.png", tipo: "print" }], destaques: [["100", "100+ PAÍSES"], ["receita", "RECEITA MAIOR"], ["adesões", "ADESÕES > CANCELAMENTOS"]] },
      { tipo: "narr", bloco: "47", imgs: [{ src: ST + "carta_q2_23-01.png", tipo: "print" }], destaques: [["acerto", "FOI UM ACERTO?"], ["sim", "PELA EMPRESA: SIM"], ["mudou", "A CONTA MUDOU.", "ambar"]] },
    ] },
  { id: "SHORT08", topo: "A CASA · NETFLIX", trilha: 600, hook: ["A NETFLIX ABRIU", "UMA CASA ONDE VOCÊ", "ENTRA NAS SÉRIES."], loop: ["A PORTA DA CASA", "DELA."],
    segs: [
      { tipo: "narr", bloco: "50", imgs: [{ src: V + "card_house_kop.jpg" }, { src: V + "card_house_guard.jpg" }, { src: ST + "house_release-1.png", tipo: "print" }], destaques: [["filad", "FILADÉLFIA · NOV. 2025"], ["dallas", "DALLAS · DEZ. 2025"], ["grátis", "ENTRADA GRÁTIS"], ["vegas", "LAS VEGAS · 2027", "ambar"]] },
      { tipo: "narr", bloco: "51", imgs: [{ src: V + "rec_envelope.png", tipo: "rec" }], destaques: [["envelope", "ENVELOPE VERMELHO", "netflix"]] },
      { tipo: "arq", id: "H02", lt: "NETFLIX · NETFLIX HOUSE · DEZ. 2025" },
      { tipo: "narr", bloco: "52", imgs: [{ src: V + "rec_envelope.png", tipo: "rec" }, { src: V + "card_house_kop.jpg" }], destaques: [["envelope", "O ENVELOPE"], ["porta", "AGORA É A PORTA", "ambar"]] },
    ] },
];
export const ShortN: React.FC<{ id: string }> = ({ id }) => <ShortGen cfg={SHORTS_CFG.find((c) => c.id === id)!} />;
