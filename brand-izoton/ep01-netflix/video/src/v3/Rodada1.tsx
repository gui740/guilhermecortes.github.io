// FIXES rodada 1 · cold open curto. A frase-chave entra no quadro 0; ficha, TED no CRT e painel são camadas sobre a narração.
// Duas vozes: "gacrux" (provisória, linhas cortadas l01c/l02c) e "gui" (narração do Guilherme, blocos 01 e 02).
// Todos os tempos (s) caem na palavra, pelo Whisper.
import React from "react";
import { AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, FAIXA, FONT, MONO } from "../theme";
import { Camada, Camera, Card, Carimbo3, Destaque, Grao, PaginaEditorial, Papel, Recorte, useEntrada, useS } from "./kit";
import { Mascara, Painel, TelaCRT } from "./transicoes";
import { FalaCtx, ListaCard, Narr, Sfx, Trilha, clamp } from "./Amostra";

type Voz = "gacrux" | "gui";
type Tempos = {
  fim: number; n2: number; painel: number; carimbo: number; falas: [number, number][]; a1: string; a2: string;
  ano: number; ceo: number; netflix: number; disse: number; empresa: number; lista: number[]; sono: number;
  hbo: number; risca: number; fora: number; acende: number; jogadas: number; pelo: number; conta?: number;
};
// gacrux: l01c (6,13 s) + l02c em 6,25 s ("Neste episódio..." até "tempo")
const T_GACRUX: Tempos = {
  fim: 13.7, n2: 6.25, painel: 6.25, carimbo: 11.9, falas: [[0, 6.14], [6.25, 11.71]], a1: "media/v3audio/l01c_107.wav", a2: "media/v3audio/l02c_107.wav",
  ano: 0.6, ceo: 1.1, netflix: 1.7, disse: 2.36, empresa: 2.92, lista: [3.4, 3.62, 3.86, 4.08], sono: 5.46,
  hbo: 4.5, risca: 4.8, fora: 5.2, acende: 6.61, jogadas: 7.67, pelo: 10.97,
};
// gui: bloco 01 (4,85 s) + bloco 02 em 5,0 s (9,81 s). Palavras do bloco 02 (+5,0): HBO 1,16 · lista 2,08 · Neste 2,86 ·
// episódio 3,08 · jogadas 3,98 · pelo 5,46 · conta 7,0 · fim 8,44
const N2G = 5.0;
const T_GUI: Tempos = {
  fim: 15.0, n2: N2G, painel: N2G + 2.86, carimbo: 13.5, falas: [[0, 4.85], [N2G, N2G + 9.81]], a1: "media/narr_gui/b01.wav", a2: "media/narr_gui/b02.wav",
  ano: 0.72, ceo: 1.76, netflix: 2.0, disse: 2.48, empresa: 3.0, lista: [3.24, 3.5, 3.75, 4.0], sono: 4.28,
  hbo: N2G + 1.16, risca: N2G + 2.08, fora: N2G + 2.3, acende: N2G + 3.08, jogadas: N2G + 3.98, pelo: N2G + 5.46, conta: N2G + 7.0,
};
export const COLD_OPEN_V2_DUR = T_GACRUX.fim;
export const COLD_OPEN_GUI_DUR = T_GUI.fim;

const Recibo: React.FC = () => (
  <div style={{ padding: "26px 28px", fontFamily: MONO, fontSize: 21, color: C.tinta, letterSpacing: 1.5, lineHeight: 1.8 }}>
    <div style={{ fontWeight: 600, fontSize: 26, letterSpacing: 4 }}>A CONTA</div>
    <div style={{ borderTop: `2px dashed ${C.apoio}`, margin: "10px 0" }} />
    <div>SENHA COMPARTILHADA ...... ?</div>
    <div>PLANO COM ANÚNCIOS ....... ?</div>
    <div>REAJUSTE ................. ?</div>
    <div style={{ borderTop: `2px dashed ${C.apoio}`, margin: "10px 0" }} />
    <div style={{ fontWeight: 600 }}>CAPÍTULO 09 .............. →</div>
  </div>
);

export const ColdOpenV2: React.FC<{ voz?: Voz }> = ({ voz = "gacrux" }) => {
  const T = voz === "gui" ? T_GUI : T_GACRUX;
  const S = useS();
  const f = useCurrentFrame();
  const PB = T.painel, D = T.carimbo, FIM = T.fim;
  const kTopo = useEntrada(0, 4), kFrase = useEntrada(0, 5);
  const pulso = 1 + 0.12 * Math.max(0, 1 - Math.abs(f - S(T.sono + 0.04)) / 6); // "sono": o destaque dá um pulso
  const sobeFrase = Math.floor(interpolate(f, [0, S(PB)], [0, -40], clamp) / 4) * 4; // deriva em degraus
  const r = (s: number) => s - PB; // tempo relativo à cena do painel
  return (
    <FalaCtx.Provider value={T.falas}>
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      {/* ---------------- A · frase + camadas (0 → painel) */}
      <Sequence from={0} durationInFrames={S(PB + 0.5)}>
        <AbsoluteFill>
          <Papel />
          <Camera dur={S(PB)} de={1.0} ate={1.09} dx={-40} dy={-10}>
            <Camada vel={0.3} dur={S(PB)}>
              <div style={{ position: "absolute", left: -60, top: 140, fontFamily: FONT, fontWeight: 800, fontSize: 470, color: "#EDEDED", letterSpacing: -14 }}>2017</div>
            </Camada>
            {/* lateral esquerda: Hastings + ficha da entrevista */}
            <Camada vel={0.8} dur={S(PB)}>
              <Recorte src="media/v3img/rec_hastings_2015.png" x={150} y={90} w={400} inicio={S(0.1)} rot={-3} seed="h15" de="esq" />
              <Carimbo3 texto="17 ABR. 2017" inicio={S(T.ano)} x={170} y={470} rot={4} size={40} />
              <Carimbo3 texto="CEO · REED HASTINGS" inicio={S(T.ceo)} x={330} y={540} rot={-3} size={24} />
              <Card x={80} y={590} w={520} h={320} inicio={S(T.netflix)} rotY={12} rotZ={-3} seed="ficha">
                <Img src={staticFile("media/stills/web_sleep.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 30%" }} />
              </Card>
              <Carimbo3 texto="ENTREVISTA Q1 2017 · 17 ABR." inicio={S(T.disse)} x={100} y={900} rot={-5} />
            </Camada>
            {/* lateral direita: TED no CRT + a lista acendendo + HBO riscada */}
            <Camada vel={1.2} dur={S(PB)}>
              <Card x={1300} y={130} w={540} h={330} inicio={S(T.empresa)} rotY={-12} rotZ={2} seed="crt" fundo="black">
                <Sequence from={S(T.empresa)} layout="none">
                  <TelaCRT clip="media/arquivo/HOOK.mp4" inicioClip={0} dur={S(PB - T.empresa + 0.5)} desliga={false} />
                </Sequence>
                <div style={{ position: "absolute", left: 14, bottom: 10, fontFamily: MONO, fontSize: 15, letterSpacing: 2, color: C.branco, background: "rgba(0,0,0,0.55)", padding: "3px 8px" }}>
                  TED 2018 · REED HASTINGS</div>
              </Card>
              <ListaCard x={1330} y={500} itens={[{ t: "TV LINEAR", s: T.lista[0] }, { t: "VIDEOGAME", s: T.lista[1] }, { t: "YOUTUBE", s: T.lista[2] }, { t: "NETFLIX", s: T.lista[3], tom: "netflix" }]} />
              {f >= S(T.hbo) && (
                <div style={{ position: "absolute", left: 1700, top: 505, transform: "rotate(-4deg)" }}>
                  <Destaque texto="HBO" inicio={S(T.hbo)} size={64} style={{ background: C.apoio, color: C.tinta }} />
                  <div style={{ position: "absolute", left: -8, top: 38, height: 8, background: C.tinta, width: `${interpolate(f - S(T.risca), [0, 8], [0, 170], clamp)}px` }} />
                </div>
              )}
              <Carimbo3 texto="FORA DA LISTA" inicio={S(T.fora)} x={1640} y={630} rot={-7} />
            </Camada>
          </Camera>
          {/* faixa central: a frase-chave desde o quadro 0 */}
          <div style={{ position: "absolute", left: FAIXA.x + 10, width: FAIXA.w - 20, top: 330 + sobeFrase, textAlign: "center" }}>
            <div style={{ fontFamily: MONO, fontSize: 24, letterSpacing: 3, color: C.secundario, opacity: kTopo, lineHeight: 1.5 }}>
              EM 2017, O CEO DA NETFLIX<br />DISSE QUE A EMPRESA</div>
            <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 80, lineHeight: 1.0, color: C.tinta, marginTop: 26, opacity: kFrase,
              transform: `translateY(${(1 - kFrase) * 20}px)` }}>COMPETE COM<br />O SEU</div>
            <div style={{ marginTop: 16, display: "inline-block", transform: `scale(${pulso})` }}><Destaque texto="SONO." inicio={2} size={130} /></div>
          </div>
          <PaginaEditorial capitulo="00 · HOOK" arquivo="ARQUIVO 00/10" />
          <Grao />
        </AbsoluteFill>
      </Sequence>

      {/* ---------------- B · promessa sobre o painel, carimbo do canal no fim */}
      <Sequence from={S(PB)} durationInFrames={S(FIM - PB)}>
        <Mascara inicio={0} direcao="circulo">
          <AbsoluteFill>
            <Painel de={0} para={0} dur={S(FIM - PB)} preenchidos={0} visaoGeral pan={320} acende={{ inicio: S(r(T.acende)), passo: S(0.42) }} />
            {f < S(D) && (
              <div style={{ position: "absolute", left: FAIXA.x + 10, width: FAIXA.w - 20, top: 380, display: "flex", flexDirection: "column", gap: 18, alignItems: "center" }}>
                <Destaque texto="AS JOGADAS" inicio={S(r(T.jogadas))} size={110} />
                <Destaque texto="PELO SEU TEMPO" inicio={S(r(T.pelo))} size={76} tom="ambar" />
              </div>
            )}
            {T.conta !== undefined && <Card x={1330} y={300} w={460} inicio={S(r(T.conta))} fim={S(r(D)) + 4} rotY={-12} rotZ={3} seed="recibo"><Recibo /></Card>}
            <Sequence from={S(D - PB)} layout="none">
              <Carimbo3 texto="BRAND BY IZOTON · EP01 · NETFLIX" inicio={2} x={FAIXA.x - 70} y={500} rot={-3} size={34} />
            </Sequence>
            <Grao />
          </AbsoluteFill>
        </Mascara>
      </Sequence>

      {/* ---------------- som */}
      <Narr s={0} arq={T.a1} />
      <Narr s={T.n2} arq={T.a2} />
      <Sequence from={S(PB)} layout="none"><Trilha de={40} vol={0.06} /></Sequence>
      <Sfx s={0.1} nome="papel_1" vol={0.35} /><Sfx s={T.ano} nome="carimbo_0" vol={0.3} /><Sfx s={T.ceo} nome="click_0" vol={0.25} /><Sfx s={T.netflix} nome="papel_2" /><Sfx s={T.disse} nome="carimbo_1" vol={0.35} />
      <Sfx s={T.empresa - 0.02} nome="crt_on_0" vol={0.35} /><Sfx s={T.lista[3]} nome="bip_0" vol={0.25} /><Sfx s={T.hbo} nome="papel_3" vol={0.35} /><Sfx s={T.fora} nome="carimbo_2" vol={0.35} />
      <Sfx s={T.sono} nome="bip_1" vol={0.25} /><Sfx s={PB} nome="sweep_0" vol={0.3} /><Sfx s={T.jogadas} nome="bip_2" vol={0.22} />
      {[0, 0.84, 1.68, 2.52, 3.36].map((t) => <Sfx key={t} s={T.acende + t} nome="click_0" vol={0.15} />)}
      {T.conta !== undefined && <Sfx s={T.conta} nome="papel_0" vol={0.3} />}
      <Sfx s={D + 0.07} nome="carimbo_3" />
    </AbsoluteFill>
    </FalaCtx.Provider>
  );
};
