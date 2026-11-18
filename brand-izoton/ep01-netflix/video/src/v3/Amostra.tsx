// Parada 1 · amostra v3 (5 trechos). Cada entrada de elemento cai no tempo exato da palavra (Whisper).
import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FAIXA, FONT, MONO } from "../theme";
import { Legenda, LowerThird, NLogo, Picto } from "../cenas/bits";
import { WarpCtx, Camada, Camera, Card, Carimbo3, Contador, Cursor, Destaque, Dossie, Grao, PaginaEditorial, Papel, Recorte, Terminal, TituloDoisPesos, easeInOut, useEntrada, useS } from "./kit";
import { Empurrao, Mascara, Painel, TelaCRT } from "./transicoes";

export const LT_TED = { nome: "REED HASTINGS", cargo: "CEO DA NETFLIX", fonte: "TED · ABR. 2018" };
export const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

/* ------------------------------------------------------------------ som */
/** Trechos com fala (s) da cena; os efeitos que caem dentro deles levam ducking. Sem provedor, considera que há fala. */
export const FalaCtx = React.createContext<[number, number][] | null>(null);
/** Efeitos de transição (FIXES rodada 1, item 6): -9 dB, arquivos em fx_suave (low-pass 8 kHz, fade-in 30 ms) e -4,4 dB a mais sob fala. */
export const SFX_GANHO = 0.355, SFX_DUCK = 0.6;
export const Sfx: React.FC<{ s: number; nome: string; vol?: number }> = ({ s, nome, vol = 0.45 }) => {
  const S = useS();
  const fala = React.useContext(FalaCtx);
  const sob = fala ? fala.some(([a, b]) => s >= a - 0.1 && s <= b) : true;
  return <Sequence from={S(s)} layout="none"><Audio src={staticFile(`media/som/fx_suave/${nome}.wav`)} volume={vol * SFX_GANHO * (sob ? SFX_DUCK : 1)} /></Sequence>;
};
export const Narr: React.FC<{ s: number; arq: string; vol?: number; inicio?: number; dur?: number }> = ({ s, arq, vol = 1, inicio = 0, dur }) => {
  const S = useS();
  return <Sequence from={S(s)} durationInFrames={dur ? S(dur) : undefined} layout="none"><Audio src={staticFile(arq)} volume={vol} startFrom={S(inicio)} /></Sequence>;
};
export const Trilha: React.FC<{ de: number; vol?: number }> = ({ de, vol = 0.07 }) => {
  const S = useS();
  return <Audio src={staticFile("media/som/trilha.wav")} startFrom={S(de)} volume={vol} />;
};

/* ------------------------------------------------------------------ peças desenhadas */
export const ListaCard: React.FC<{ itens: { t: string; s: number; tom?: "tinta" | "netflix" }[]; x: number; y: number; riscar?: { idx: number; s: number } }> = ({ itens, x, y }) => {
  const S = useS();
  return (
    <div style={{ position: "absolute", left: x, top: y, display: "flex", flexDirection: "column", gap: 14, alignItems: "flex-start" }}>
      {itens.map((it, i) => <Destaque key={i} texto={it.t} inicio={S(it.s)} tom={it.tom ?? "tinta"} size={46} />)}
    </div>
  );
};

const Recibo: React.FC = () => (
  <div style={{ padding: "28px 30px", fontFamily: MONO, fontSize: 22, color: C.tinta, letterSpacing: 1.5, lineHeight: 1.8 }}>
    <div style={{ fontWeight: 600, fontSize: 26, letterSpacing: 4 }}>A CONTA</div>
    <div style={{ borderTop: `2px dashed ${C.apoio}`, margin: "10px 0" }} />
    <div>SENHA COMPARTILHADA ........ ?</div>
    <div>PLANO COM ANÚNCIOS ......... ?</div>
    <div>REAJUSTE ................... ?</div>
    <div style={{ borderTop: `2px dashed ${C.apoio}`, margin: "10px 0" }} />
    <div style={{ fontWeight: 600 }}>CAPÍTULO 09 ................ →</div>
  </div>
);

export const LinhaDVD: React.FC<{ s: number; y: number }> = ({ s, y }) => {
  const S = useS();
  const f = useCurrentFrame();
  const k = interpolate(f - S(s), [0, 30], [0, 1], { ...clamp, easing: easeInOut });
  const itens = ["DVD", "STREAMING"];
  return (
    <div style={{ position: "absolute", left: 150, right: 150, top: y }}>
      <div style={{ height: 3, width: `${k * 100}%`, background: C.tinta }} />
      {itens.map((n, i) => {
        const ki = interpolate(f - S(s) - i * 14, [0, 10], [0, 1], clamp);
        return (
          <div key={n} style={{ position: "absolute", left: `${i === 0 ? 4 : 86}%`, top: -110, opacity: ki, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Picto nome={n} size={92} />
            <div style={{ width: 16, height: 16, borderRadius: 8, background: C.tinta, marginTop: 6 }} />
            <div style={{ fontFamily: MONO, fontSize: 18, letterSpacing: 2, marginTop: 10, color: C.tinta }}>{n}</div>
          </div>
        );
      })}
    </div>
  );
};

const DiscoGirando: React.FC<{ x: number; y: number; s: number; rola?: number }> = ({ x, y, s, rola = 0 }) => {
  const S = useS();
  const f = useCurrentFrame();
  const k = useEntrada(S(s), 10);
  // rola: o disco atravessa `rola` px em degraus de stop-motion (3 quadros por pose) até 2,6 s depois de entrar
  const t = Math.floor((f - S(s)) / 3) * 3;
  const dx = rola ? interpolate(t, [0, S(2.6)], [-rola, 0], { ...clamp, easing: easeInOut }) : 0;
  const dy = rola ? Math.sin(t / 5) * 10 : 0;
  return (
    <div style={{ position: "absolute", left: x + dx, top: y + dy, opacity: k, transform: `rotate(${(rola ? t : f - S(s)) * 4}deg) scale(${0.9 + 0.1 * k})`, filter: "drop-shadow(10px 12px 10px rgba(0,0,0,0.25))" }}>
      <Picto nome="DVD" size={200} />
      {rola > 0 && <div style={{ position: "absolute", left: 128, top: 92, width: 46, height: 16, borderRadius: 3, background: C.tinta }} />}
    </div>
  );
};

/* ================================================================== 1 · COLD OPEN */
export const ColdOpen: React.FC = () => {
  const S = useS();
  const f = useCurrentFrame();
  // linha do tempo (s): A 0–8.6 narração nova · B 8.6–14.4 TED · C 14.4–26.6 narração nova · D 26.6–28.6 carimbo
  const A = 0, B = 8.6, Cc = 14.4, D = 26.6, FIM = 28.6;
  const k2017 = useEntrada(S(0.16), 6), kFrase = useEntrada(S(6.3), 6), kMargem = useEntrada(S(7.7), 6);
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      {/* ---------------- A */}
      <Sequence from={S(A)} durationInFrames={S(B - A)}>
        <AbsoluteFill>
          <Papel />
          <Camera dur={S(B - A)} de={1.0} ate={1.13} dx={-70} dy={-15}>
            <Camada vel={0.3} dur={S(8.6)}>
              <div style={{ position: "absolute", left: -60, top: 120, fontFamily: FONT, fontWeight: 800, fontSize: 470, color: "#EDEDED", letterSpacing: -14,
                opacity: k2017 }}>2017</div>
            </Camada>
            <Camada vel={0.8} dur={S(8.6)}>
              <Recorte src="media/v3img/rec_hastings_2015.png" x={735} y={90} w={450} inicio={S(1.92)} rot={-3} seed="h15" />
            </Camada>
            <Camada vel={1.2} dur={S(8.6)}>
              <Card x={1290} y={230} w={560} h={420} inicio={S(3.92)} rotY={-14} rotZ={2} seed="ficha">
                <Img src={staticFile("media/stills/web_sleep.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 30%" }} />
              </Card>
              <Carimbo3 texto="WALL STREET · 17 ABR. 2017" inicio={S(4.68)} x={1310} y={600} rot={-5} />
              <Dossie linhas={["ENTREVISTA DE RESULTADOS", "Q1 2017 · 17 ABR.", "UBS · STIFEL", "NETFLIX IR"]} lado="esq" inicio={S(0.6)} top={640} />
            </Camada>
          </Camera>
          {/* frase literal na faixa central */}
          {f >= S(6.3) && (
            <div style={{ position: "absolute", left: FAIXA.x + 10, width: FAIXA.w - 20, top: 600, textAlign: "center" }}>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 64, lineHeight: 1.02, color: C.tinta, opacity: kFrase }}>
                “ESTAMOS COMPETINDO COM O</div>
              <div style={{ marginTop: 10 }}><Destaque texto="SONO," inicio={S(7.56)} size={104} /></div>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 64, color: C.tinta, marginTop: 8, opacity: kMargem }}>NA MARGEM.”</div>
            </div>
          )}
          <PaginaEditorial capitulo="00 · HOOK" arquivo="ARQUIVO 00/10" />
          <Grao />
        </AbsoluteFill>
      </Sequence>

      {/* ---------------- B : TED */}
      <Sequence from={S(B)} durationInFrames={S(Cc - B)}>
        <AbsoluteFill>
          <TelaCRT clip="media/arquivo/HOOK.mp4" inicioClip={0} dur={S(Cc - B)} />
          <Sequence from={S(0.2)} layout="none"><LowerThird {...LT_TED} delay={4} /></Sequence>
          <Sequence from={S(0.2)} layout="none"><Legenda linhas={["Você pode ver TV linear, jogar videogame,", "ver YouTube… ou ver Netflix."]} dur={4.8} /></Sequence>
          <ListaCard x={1380} y={300} itens={[{ t: "TV LINEAR", s: 0.62 }, { t: "VIDEOGAME", s: 1.88 }, { t: "YOUTUBE", s: 3.1 }, { t: "NETFLIX", s: 4.58, tom: "netflix" }]} />
          <Dossie linhas={["TED 2018 · VANCOUVER", "FALA 14:21", "A DISPUTA:", "O SEU TEMPO LIVRE"]} lado="esq" inicio={S(0.5)} escuro top={330} />
        </AbsoluteFill>
      </Sequence>

      {/* ---------------- C */}
      <Sequence from={S(Cc)} durationInFrames={S(D - Cc)}>
        <AbsoluteFill>
          <Papel />
          {/* painel do arquivo nasce por baixo, a partir de "Neste episódio" */}
          <Mascara inicio={S(3.76)} direcao="circulo"><Painel de={0} para={0} dur={S(D - Cc)} preenchidos={0} visaoGeral /></Mascara>
          <Camera dur={S(D - Cc)} de={1.1} ate={1.0} dx={50}>
            {f < S(Cc + 3.9) && (
              <>
                <ListaCard x={FAIXA.x + 70} y={260} itens={[{ t: "TV LINEAR", s: 0 }, { t: "VIDEOGAME", s: 0.1 }, { t: "YOUTUBE", s: 0.2 }, { t: "NETFLIX", s: 0.3, tom: "netflix" }]} />
                <Recorte src="media/v3img/rec_hastings_2015.png" x={140} y={260} w={300} inicio={S(0)} rot={4} seed="h15b" de="esq" />
                {f >= S(Cc + 1.18) && (
                  <div style={{ position: "absolute", left: 1330, top: 330, transform: "rotate(-3deg)" }}>
                    <Destaque texto="HBO" inicio={S(1.18)} size={90} style={{ background: C.apoio, color: C.tinta }} />
                    <div style={{ position: "absolute", left: -10, top: 52, height: 9, background: C.tinta, width: `${interpolate(f - S(1.58), [0, 12], [0, 260], clamp)}px` }} />
                  </div>
                )}
                <Carimbo3 texto="FORA DA LISTA" inicio={S(2.66)} x={1320} y={470} rot={-6} />
              </>
            )}
            {f >= S(Cc + 5.0) && (
              <div style={{ position: "absolute", left: FAIXA.x + 10, width: FAIXA.w - 20, top: 380, textAlign: "center", display: "flex", flexDirection: "column", gap: 18, alignItems: "center" }}>
                <Destaque texto="AS JOGADAS" inicio={S(5.26)} size={110} />
                <Destaque texto="PELO SEU TEMPO" inicio={S(8.72)} size={76} tom="ambar" />
              </div>
            )}
            <Card x={1330} y={300} w={460} inicio={S(9.88)} rotY={-12} rotZ={3} seed="recibo"><Recibo /></Card>
          </Camera>
          <PaginaEditorial capitulo="00 · A PROMESSA" arquivo="ARQUIVO 00/10" />
          <Grao />
        </AbsoluteFill>
      </Sequence>

      {/* ---------------- D : carimbo do canal sobre o painel (2 s) */}
      <Sequence from={S(D)} durationInFrames={S(FIM - D)}>
        <AbsoluteFill>
          <Painel de={0} para={0} dur={S(FIM - D)} preenchidos={0} visaoGeral />
          <Carimbo3 texto="BRAND BY IZOTON · EP01 · NETFLIX" inicio={2} x={FAIXA.x - 70} y={500} rot={-3} size={34} />
          <Grao />
        </AbsoluteFill>
      </Sequence>

      {/* ---------------- som */}
      <Narr s={A} arq="media/v3audio/l01_107.wav" />
      <Narr s={B} arq="media/arquivo/HOOK.mp4" vol={0.95} />
      <Narr s={Cc} arq="media/v3audio/l02_107.wav" />
      <Sequence from={S(Cc)} layout="none"><Trilha de={40} vol={0.06} /></Sequence>
      <Sfx s={0.16} nome="carimbo_0" vol={0.35} /><Sfx s={1.92} nome="papel_1" vol={0.35} /><Sfx s={3.92} nome="papel_2" /><Sfx s={4.68} nome="carimbo_1" />
      <Sfx s={7.56} nome="bip_0" vol={0.3} /><Sfx s={B - 0.05} nome="crt_on_0" /><Sfx s={Cc - 0.3} nome="crt_off_1" />
      <Sfx s={Cc + 1.18} nome="papel_3" /><Sfx s={Cc + 2.66} nome="carimbo_2" /><Sfx s={Cc + 3.76} nome="sweep_0" vol={0.3} />
      <Sfx s={Cc + 5.26} nome="bip_1" vol={0.25} /><Sfx s={Cc + 8.72} nome="bip_2" vol={0.25} /><Sfx s={Cc + 9.88} nome="papel_0" /><Sfx s={D + 0.1} nome="carimbo_3" />
    </AbsoluteFill>
  );
};

/* ================================================================== 2 · COLAGEM 01:09 */
const Datilografa: React.FC<{ texto: string; s: number; x: number; y: number }> = ({ texto, s, x, y }) => {
  const S = useS();
  const f = useCurrentFrame();
  const n = Math.max(0, Math.min(texto.length, Math.floor((f - S(s)) / 1.5)));
  if (f < S(s)) return null;
  return <div style={{ position: "absolute", left: x, top: y, fontFamily: MONO, fontSize: 26, letterSpacing: 3, color: C.tinta, background: C.branco, padding: "6px 12px" }}>
    {texto.slice(0, n)}<span style={{ opacity: Math.floor(f / 8) % 2 ? 1 : 0 }}>▌</span></div>;
};

/** v2 = rodada 1 do FIXES: o começo ganha movimento (disco rolando em degraus + ficha datilografada em "formato"). */
// palavras da voz antiga (n01b, Gacrux) → bloco 04 do Guilherme
const WARP_COLAGEM_GUI: [number, number][] = [[0, 0], [1.18, 0.66], [1.82, 1.3], [2.34, 1.74], [3.2, 2.46], [4.28, 3.3], [5.36, 4.0], [5.78, 4.34],
  [7.2, 5.64], [8.56, 6.68], [10.04, 7.92], [11.46, 8.96], [12.12, 9.62], [12.76, 10.28]];
export const COLAGEM_GUI_DUR = 11.9;
export const Colagem: React.FC<{ v2?: boolean; voz?: "gacrux" | "gui" }> = ({ v2 = false, voz = "gacrux" }) => (
  <WarpCtx.Provider value={voz === "gui" ? WARP_COLAGEM_GUI : null}><ColagemCena v2={v2} voz={voz} /></WarpCtx.Provider>
);
const ColagemCena: React.FC<{ v2: boolean; voz: "gacrux" | "gui" }> = ({ v2, voz }) => {
  const S = useS();
  const f = useCurrentFrame();
  const DUR = voz === "gui" ? 12.76 + (COLAGEM_GUI_DUR - 10.28) : 13.9; // em tempo antigo (o mapa leva ao fim da cena)
  return (
    <FalaCtx.Provider value={[[0, 13.48]]}>
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <Papel />
      <Camera dur={S(DUR)} de={1.0} ate={1.13} dx={60} dy={-25}>
        <Camada vel={0.25} dur={S(DUR)}>
          <div style={{ position: "absolute", right: -80, top: 60, fontFamily: FONT, fontWeight: 800, fontSize: 420, color: "#EFEFEF", letterSpacing: -12 }}>1997</div>
        </Camada>
        <Camada vel={0.7} dur={S(DUR)}>
          <Recorte src="media/v3img/rec_envelope.png" x={60} y={170} w={720} inicio={S(0)} rot={-6} seed="env" de="esq" />
          <DiscoGirando x={600} y={130} s={0.2} rola={v2 ? 300 : 0} />
          {v2 && <Datilografa texto="FORMATO: DVD · 1997" s={1.18} x={110} y={520} />}
          <Carimbo3 texto="PRAZO DE VALIDADE" inicio={S(1.82)} x={130} y={600} rot={-8} />
          <Recorte src="media/v3img/rec_hastings_2014.png" x={1290} y={110} w={560} inicio={S(7.2)} rot={3} seed="h14" de="dir" />
        </Camada>
        <Camada vel={1.1} dur={S(DUR)}>
          <Card x={1250} y={640} w={560} inicio={S(8.56)} rotY={-10} rotZ={-2} seed="tedq">
            <div style={{ padding: "24px 28px" }}>
              <div style={{ fontFamily: MONO, fontSize: 16, letterSpacing: 2, color: C.secundario }}>TED 2018 · 5:11</div>
              <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 30, lineHeight: 1.15, color: C.tinta, marginTop: 10 }}>“a lot of paranoia about what’s coming next”</div>
            </div>
          </Card>
          <Carimbo3 texto="FOUNDING ETHOS" inicio={S(12.12)} x={1280} y={830} rot={-4} />
        </Camada>
        {f >= S(9.48) && <LinhaDVD s={9.48} y={960} />}
      </Camera>
      {/* faixa central: destaque → título em dois pesos (empurrão de página) */}
      <AbsoluteFill>
        <Empurrao inicio={S(4.1)}
          antes={<div style={{ position: "absolute", left: FAIXA.x, width: FAIXA.w, top: 400, textAlign: "center" }}><Destaque texto="MÉTODO" inicio={S(3.2)} size={130} /></div>}
          depois={<div style={{ position: "absolute", left: FAIXA.x + 20, width: FAIXA.w - 40, top: 300 }}><TituloDoisPesos a="Desconfiar" b="do próprio sucesso." ta={S(4.28)} tb={S(5.36)} size={112} /></div>} />
      </AbsoluteFill>
      <PaginaEditorial capitulo="01 · DO DVD AO STREAMING" arquivo="ARQUIVO 01/10" />
      <Grao />
      <Narr s={0} arq={voz === "gui" ? "media/narr_gui/b04.wav" : "media/v3audio/n01b.wav"} />
      <Trilha de={70} vol={0.07} />
      <Sfx s={0} nome="papel_0" /><Sfx s={1.82} nome="carimbo_0" />{v2 && <Sfx s={1.18} nome="click_0" vol={0.25} />}<Sfx s={3.2} nome="bip_0" vol={0.25} /><Sfx s={4.1} nome="papel_2" vol={0.35} />
      <Sfx s={7.2} nome="papel_1" /><Sfx s={8.56} nome="papel_3" /><Sfx s={9.48} nome="click_0" vol={0.3} /><Sfx s={12.12} nome="carimbo_1" />
    </AbsoluteFill>
    </FalaCtx.Provider>
  );
};

/* ================================================================== 3 · FALA DE ARQUIVO 03:33 COM CAMADAS */
const Insert: React.FC<{ s: number; d: number; children: React.ReactNode }> = ({ s, d, children }) => {
  const S = useS();
  return (
    <Sequence from={S(s)} durationInFrames={S(d)} layout="none">
      <Mascara inicio={0} direcao="dir"><AbsoluteFill><Papel />{children}<Grao /></AbsoluteFill></Mascara>
    </Sequence>
  );
};
export const FalaT04: React.FC = () => {
  const S = useS();
  const PRE = 0.3, CLIP = 24.56, DUR = PRE + CLIP + 0.5;
  const t = (x: number) => PRE + x; // tempo da palavra no clipe → tempo da cena
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <Sequence from={S(PRE)} durationInFrames={S(CLIP + 0.5)}>
        <TelaCRT clip="media/arquivo/T04.mp4" inicioClip={0} dur={S(CLIP + 0.5)} />
      </Sequence>
      <Sequence from={S(PRE)} layout="none"><LowerThird {...LT_TED} delay={6} /></Sequence>
      <Sequence from={S(PRE)} layout="none"><Legenda linhas={["crescemos enviando DVDs, e tinha as séries em box de DVD.", "Todos nós tivemos a experiência de ver ótimas séries da HBO", "(…) próximo episódio, próximo episódio.", "É muito poderoso ter todos os episódios de uma vez.", "E isso a TV linear não consegue fazer."]} dur={CLIP} /></Sequence>
      <Dossie linhas={["ARQUIVO 03/10", "TED · VANCOUVER", "10 ABR. 2018", "FALA 2:19–2:45"]} lado="esq" inicio={S(0.8)} escuro top={300} />
      <Card x={1370} y={250} w={430} inicio={S(t(3.0))} rotY={-14} rotZ={2} seed="box1" fim={S(t(10.7))}>
        <Img src={staticFile("media/v3img/card_boxset.jpg")} style={{ width: "100%", display: "block" }} />
        <div style={{ fontFamily: MONO, fontSize: 15, letterSpacing: 2, padding: "10px 14px", color: C.tinta }}>BOX DE SÉRIES EM DVD</div>
      </Card>
      <div style={{ position: "absolute", left: 1400, top: 690 }}><Destaque texto="HBO" inicio={S(t(7.9))} size={60} /></div>
      <div style={{ position: "absolute", left: 1380, top: 300 }}><Destaque texto="BINGE" inicio={S(t(19.6))} size={80} tom="ambar" /></div>
      <div style={{ position: "absolute", left: 120, top: 700 }}><Destaque texto="TV LINEAR NÃO FAZ" inicio={S(t(23.18))} size={46} /></div>
      {/* inserts de 2–3 s a cada 5–6 s, sem cortar o áudio */}
      <Insert s={t(4.6)} d={2.5}>
        <Recorte src="media/v3img/card_boxset.jpg" x={FAIXA.x - 60} y={260} w={720} inicio={0} rot={-2} seed="box2" filtro="contrast(1.05)" />
        <div style={{ position: "absolute", left: FAIXA.x, width: FAIXA.w, top: 820, textAlign: "center" }}><Destaque texto="BOX SETS" inicio={6} size={70} /></div>
        <PaginaEditorial capitulo="03 · O BINGE COMO PRODUTO" arquivo="ARQUIVO 03/10" />
      </Insert>
      <Insert s={t(10.6)} d={2.6}>
        <div style={{ position: "absolute", left: 360, top: 360 }}><Terminal texto="PRÓXIMO EPISÓDIO… PRÓXIMO EPISÓDIO" inicio={4} cps={24} w={1200} size={62} /></div>
        <PaginaEditorial capitulo="03 · O BINGE COMO PRODUTO" arquivo="ARQUIVO 03/10" />
      </Insert>
      <Insert s={t(18.9)} d={2.9}>
        <Recorte src="media/stills/poster_houseofcards.jpg" x={FAIXA.x + 104} y={170} w={400} inicio={0} rot={2} seed="hoc" />
        <div style={{ position: "absolute", left: FAIXA.x, width: FAIXA.w, top: 800, textAlign: "center" }}><Destaque texto="TODOS DE UMA VEZ" inicio={S(1.7)} size={56} tom="ambar" /></div>
        <Carimbo3 texto="2013 · 13 EPISÓDIOS" inicio={S(0.6)} x={1280} y={300} rot={-5} />
        <PaginaEditorial capitulo="03 · O BINGE COMO PRODUTO" arquivo="ARQUIVO 03/10" />
      </Insert>
      <Narr s={PRE} arq="media/arquivo/T04.mp4" vol={0.95} />
      <Trilha de={200} vol={0.045} />
      <Sfx s={PRE - 0.05} nome="crt_on_1" /><Sfx s={t(3.0)} nome="papel_1" /><Sfx s={t(4.6)} nome="sweep_1" vol={0.3} /><Sfx s={t(7.9)} nome="bip_0" vol={0.25} />
      <Sfx s={t(10.6)} nome="sweep_2" vol={0.3} /><Sfx s={t(11.0)} nome="tecla_0" vol={0.3} /><Sfx s={t(18.9)} nome="sweep_3" vol={0.3} /><Sfx s={t(19.6)} nome="bip_1" vol={0.25} />
      <Sfx s={t(23.18)} nome="bip_2" vol={0.25} /><Sfx s={DUR - 0.4} nome="crt_off_0" />
    </AbsoluteFill>
  );
};

/* ================================================================== 4 · TRANSIÇÃO DE CAPÍTULO 2 → 3 */
export const TransicaoCap: React.FC<{ voz?: "gacrux" | "gui" }> = ({ voz = "gacrux" }) => {
  const S = useS();
  const f = useCurrentFrame();
  const T06_INI = 3.7, CAUDA = 1.9, PAINEL = 6.0, DEPOIS = 2.6;
  const P0 = CAUDA, P1 = CAUDA + PAINEL;
  const gui = voz === "gui";
  return (
    <FalaCtx.Provider value={gui ? [[0, CAUDA], [P1, P1 + DEPOIS]] : [[0, CAUDA], [P0 + 0.2, P0 + 5.65], [P1, P1 + DEPOIS]]}>
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <Sequence durationInFrames={S(CAUDA)}><TelaCRT clip="media/arquivo/T06.mp4" inicioClip={S(T06_INI)} dur={S(CAUDA)} liga={false} congelaFim /></Sequence>
      <Sequence durationInFrames={S(CAUDA)} layout="none"><LowerThird {...LT_TED} delay={0} /></Sequence>
      <Sequence from={S(P0)} durationInFrames={S(PAINEL)}>
        <AbsoluteFill>
          <Painel de={1} para={2} dur={S(PAINEL)} preenchidos={2} />
          {/* regancho falado, em legenda grande sobre o painel */}
          <div style={{ position: "absolute", left: FAIXA.x + 10, width: FAIXA.w - 20, top: 930, textAlign: "center" }}>
            {f < S(P0 + 2.0) ? <Destaque texto="TER A SÉRIE NÃO BASTAVA." inicio={S(0.2)} size={40} />
              : <Destaque texto="ELA PRECISAVA QUE VOCÊ NÃO PARASSE." inicio={S(2.3)} size={36} tom="ambar" />}
          </div>
          <Grao opacidade={0.4} />
        </AbsoluteFill>
      </Sequence>
      <Sequence from={S(P1)} durationInFrames={S(DEPOIS)}>
        <AbsoluteFill>
          <Papel />
          <Camera dur={S(DEPOIS)} de={1.08} ate={1.0}>
            <Recorte src="media/stills/poster_houseofcards.jpg" x={1340} y={180} w={360} inicio={0} rot={3} seed="hoc2" de="dir" />
            <div style={{ position: "absolute", left: FAIXA.x + 20, width: FAIXA.w - 40, top: 380 }}>
              <TituloDoisPesos a="Todos os episódios" b="de uma vez." ta={S(0.1)} tb={S(1.0)} size={78} />
            </div>
          </Camera>
          <PaginaEditorial capitulo="03 · O BINGE COMO PRODUTO" arquivo="ARQUIVO 03/10" />
          <Grao />
        </AbsoluteFill>
      </Sequence>
      <Narr s={0} arq="media/arquivo/T06.mp4" vol={0.95} inicio={T06_INI} dur={CAUDA} />
      {!gui && <Narr s={P0 + 0.2} arq="media/v3audio/l03a_107.wav" />}
      <Narr s={P1} arq={gui ? "media/narr_gui/b12.wav" : "media/v3audio/n03a.wav"} dur={DEPOIS} />
      <Sequence from={S(P0)} layout="none"><Trilha de={120} vol={0.08} /></Sequence>
      <Sfx s={CAUDA - 0.3} nome="crt_off_2" /><Sfx s={P0 + PAINEL * 0.25} nome="sweep_0" vol={0.35} /><Sfx s={P0 + PAINEL * 0.5} nome="sweep_1" vol={0.35} />
      <Sfx s={P0 + PAINEL * 0.75} nome="click_1" vol={0.35} /><Sfx s={P1} nome="papel_2" />
    </AbsoluteFill>
    </FalaCtx.Provider>
  );
};

/* ================================================================== 5 · SHORT 02 · primeiros 5 s (1080x1920) */
const LegendaPalavra: React.FC<{ palavras: [number, number, string][]; chave: Record<string, "tinta" | "ambar"> }> = ({ palavras, chave }) => {
  const S = useS();
  const f = useCurrentFrame();
  // mostra as últimas 3 palavras já faladas; palavra-chave em caixa
  const ditas = palavras.filter((p) => f >= S(p[0]));
  const vis = ditas.slice(-3);
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: 1330, display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "10px 18px" }}>
      {vis.map((p, i) => {
        const w = p[2].replace(/[.,]/g, "").toUpperCase();
        const tom = chave[w];
        return tom ? <Destaque key={p[0]} texto={w} inicio={S(p[0])} size={92} tom={tom} />
          : <span key={p[0]} style={{ fontFamily: FONT, fontWeight: 800, fontSize: 92, color: C.tinta, lineHeight: 1.1 }}>{w}</span>;
      })}
    </div>
  );
};
const PALAVRAS_L03B: [number, number, string][] = [[0, 0.4, "Esse"], [0.5, 0.9, "botão"], [1.02, 1.1, "é"], [1.16, 1.6, "apertado"], [1.72, 3.0, "136"],
  [3.1, 3.5, "milhões"], [3.62, 3.9, "de"], [4.0, 4.3, "vezes"], [4.36, 4.6, "por"], [4.7, 5.2, "dia."]];
export const Short02Hook: React.FC = () => {
  const S = useS();
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <Papel />
      <Camera dur={S(5.6)} de={1.0} ate={1.06}>
        {/* 0–1.7 s: botão sendo clicado já no quadro 1 */}
        {f < S(1.75) && (
          <div style={{ position: "absolute", left: 0, right: 0, top: 600, display: "flex", justifyContent: "center" }}>
            <div style={{ border: `5px solid ${C.tinta}`, borderRadius: 10, padding: "30px 46px", display: "flex", alignItems: "center", gap: 24,
              background: f > 10 ? C.tinta : C.branco, color: f > 10 ? C.branco : C.tinta, fontFamily: FONT, fontWeight: 800, fontSize: 76, whiteSpace: "nowrap",
              transform: `scale(${interpolate(f, [9, 12, 16], [1, 0.92, 1], clamp)})` }}>
              <svg width="66" height="66" viewBox="0 0 24 24"><path d="M3 5l8 7-8 7zM12 5l8 7-8 7z" fill="currentColor" /></svg>PULAR ABERTURA
            </div>
          </div>
        )}
        {f < S(1.75) && <Cursor de={[900, 1020]} para={[700, 690]} inicio={0} clique={10} />}
        {/* 1.7–4.6 s: contador cabendo na largura */}
        {f >= S(1.72) && (
          <Mascara inicio={S(1.72)} direcao="baixo">
            <div style={{ position: "absolute", left: 0, right: 0, top: 520, display: "flex", flexDirection: "column", alignItems: "center" }}>
              <Contador valor={136000000} inicio={S(1.72)} dur={36} size={150} />
              <div style={{ fontFamily: MONO, fontSize: 30, letterSpacing: 4, color: C.secundario, marginTop: 14 }}>CLIQUES · PULAR ABERTURA</div>
              {f >= S(4.36) && <div style={{ marginTop: 40 }}><Destaque texto="POR DIA" inicio={S(4.36)} size={84} tom="ambar" /></div>}
            </div>
          </Mascara>
        )}
        <Carimbo3 texto="DADO DE 2022 · NETFLIX" inicio={S(2.6)} x={300} y={380} rot={-4} size={26} />
      </Camera>
      <div style={{ position: "absolute", left: 60, top: 70, display: "flex", alignItems: "center", gap: 12, fontFamily: MONO, fontSize: 26, letterSpacing: 3, color: C.tinta }}>
        <span style={{ width: 12, height: 12, borderRadius: 6, background: C.ambar, display: "inline-block" }} />PRODUTO · NETFLIX
      </div>
      <LegendaPalavra palavras={PALAVRAS_L03B} chave={{ "136": "tinta", "MILHÕES": "tinta", "DIA": "ambar" }} />
      <Grao />
      <Narr s={0} arq="media/v3audio/l03b_107.wav" />
      <Trilha de={260} vol={0.07} />
      <Sfx s={0.33} nome="click_0" vol={0.5} /><Sfx s={1.72} nome="sweep_0" vol={0.3} /><Sfx s={1.8} nome="tecla_1" vol={0.3} /><Sfx s={2.6} nome="carimbo_0" vol={0.35} /><Sfx s={4.36} nome="bip_0" vol={0.3} />
    </AbsoluteFill>
  );
};
