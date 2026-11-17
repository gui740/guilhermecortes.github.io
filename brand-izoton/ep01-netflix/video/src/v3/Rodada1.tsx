// FIXES rodada 1 · cold open curto (13,7 s). A frase-chave entra no quadro 0; ficha, TED no CRT e painel são camadas sobre a narração.
// Tempos por palavra (Whisper nas linhas cortadas):
//   l01c: Em 0 · 2017 0.16 · CEO 1.70 · Netflix 2.36 · disse 2.92 · compete 4.20 · sono 5.46 · fim 6.13
//   l02c (+6.25): Neste 0 · jogadas 1.42 · Netflix 2.22 · tempo 4.88 · fim 5.46
import React from "react";
import { AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, FAIXA, FONT, MONO } from "../theme";
import { Camada, Camera, Card, Carimbo3, Destaque, Grao, PaginaEditorial, Papel, Recorte, useEntrada, useS } from "./kit";
import { Mascara, Painel, TelaCRT } from "./transicoes";
import { FalaCtx, ListaCard, Narr, Sfx, Trilha, clamp } from "./Amostra";

export const COLD_OPEN_V2_DUR = 13.7;

export const ColdOpenV2: React.FC = () => {
  const S = useS();
  const f = useCurrentFrame();
  const N2 = 6.25, D = 11.9, FIM = COLD_OPEN_V2_DUR;
  const kTopo = useEntrada(0, 4), kFrase = useEntrada(0, 5);
  // "sono" (5.46 s): o destaque dá um pulso
  const pulso = 1 + 0.12 * Math.max(0, 1 - Math.abs(f - S(5.5)) / 6);
  const sobeFrase = Math.floor(interpolate(f, [0, S(N2)], [0, -40], clamp) / 4) * 4; // deriva em degraus
  return (
    <FalaCtx.Provider value={[[0, 6.14], [N2, N2 + 5.46]]}>
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      {/* ---------------- A · frase + camadas (0 → N2) */}
      <Sequence from={0} durationInFrames={S(N2 + 0.5)}>
        <AbsoluteFill>
          <Papel />
          <Camera dur={S(N2)} de={1.0} ate={1.09} dx={-40} dy={-10}>
            <Camada vel={0.3} dur={S(N2)}>
              <div style={{ position: "absolute", left: -60, top: 140, fontFamily: FONT, fontWeight: 800, fontSize: 470, color: "#EDEDED", letterSpacing: -14 }}>2017</div>
            </Camada>
            {/* lateral esquerda: Hastings + ficha da entrevista */}
            <Camada vel={0.8} dur={S(N2)}>
              <Recorte src="media/v3img/rec_hastings_2015.png" x={150} y={90} w={400} inicio={S(0.1)} rot={-3} seed="h15" de="esq" />
              <Carimbo3 texto="17 ABR. 2017" inicio={S(0.6)} x={170} y={470} rot={4} size={40} />
              <Carimbo3 texto="CEO · REED HASTINGS" inicio={S(1.1)} x={330} y={540} rot={-3} size={24} />
              <Card x={80} y={590} w={520} h={320} inicio={S(1.7)} rotY={12} rotZ={-3} seed="ficha">
                <Img src={staticFile("media/stills/web_sleep.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 30%" }} />
              </Card>
              <Carimbo3 texto="ENTREVISTA Q1 2017 · 17 ABR." inicio={S(2.36)} x={100} y={900} rot={-5} />
            </Camada>
            {/* lateral direita: TED no CRT + a lista acendendo + HBO riscada */}
            <Camada vel={1.2} dur={S(N2)}>
              <Card x={1300} y={130} w={540} h={330} inicio={S(2.92)} rotY={-12} rotZ={2} seed="crt" fundo="black">
                <Sequence from={S(2.92)} layout="none">
                  <TelaCRT clip="media/arquivo/HOOK.mp4" inicioClip={0} dur={S(N2 - 2.92 + 0.5)} desliga={false} />
                </Sequence>
                <div style={{ position: "absolute", left: 14, bottom: 10, fontFamily: MONO, fontSize: 15, letterSpacing: 2, color: C.branco, background: "rgba(0,0,0,0.55)", padding: "3px 8px" }}>
                  TED 2018 · REED HASTINGS</div>
              </Card>
              <ListaCard x={1330} y={500} itens={[{ t: "TV LINEAR", s: 3.4 }, { t: "VIDEOGAME", s: 3.62 }, { t: "YOUTUBE", s: 3.86 }, { t: "NETFLIX", s: 4.08, tom: "netflix" }]} />
              {f >= S(4.5) && (
                <div style={{ position: "absolute", left: 1700, top: 505, transform: "rotate(-4deg)" }}>
                  <Destaque texto="HBO" inicio={S(4.5)} size={64} style={{ background: C.apoio, color: C.tinta }} />
                  <div style={{ position: "absolute", left: -8, top: 38, height: 8, background: C.tinta, width: `${interpolate(f - S(4.8), [0, 8], [0, 170], clamp)}px` }} />
                </div>
              )}
              <Carimbo3 texto="FORA DA LISTA" inicio={S(5.2)} x={1640} y={630} rot={-7} />
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

      {/* ---------------- B · promessa sobre o painel (N2 → FIM), carimbo do canal no fim */}
      <Sequence from={S(N2)} durationInFrames={S(FIM - N2)}>
        <Mascara inicio={0} direcao="circulo">
          <AbsoluteFill>
            <Painel de={0} para={0} dur={S(FIM - N2)} preenchidos={0} visaoGeral pan={320} acende={{ inicio: S(0.36), passo: S(0.42) }} />
            {f < S(D) && (
              <div style={{ position: "absolute", left: FAIXA.x + 10, width: FAIXA.w - 20, top: 380, display: "flex", flexDirection: "column", gap: 18, alignItems: "center" }}>
                <Destaque texto="AS JOGADAS" inicio={S(1.42)} size={110} />
                <Destaque texto="PELO SEU TEMPO" inicio={S(4.72)} size={76} tom="ambar" />
              </div>
            )}
            <Sequence from={S(D - N2)} layout="none">
              <Carimbo3 texto="BRAND BY IZOTON · EP01 · NETFLIX" inicio={2} x={FAIXA.x - 70} y={500} rot={-3} size={34} />
            </Sequence>
            <Grao />
          </AbsoluteFill>
        </Mascara>
      </Sequence>

      {/* ---------------- som */}
      <Narr s={0} arq="media/v3audio/l01c_107.wav" />
      <Narr s={N2} arq="media/v3audio/l02c_107.wav" />
      <Sequence from={S(N2)} layout="none"><Trilha de={40} vol={0.06} /></Sequence>
      <Sfx s={0.1} nome="papel_1" vol={0.35} /><Sfx s={0.6} nome="carimbo_0" vol={0.3} /><Sfx s={1.1} nome="click_0" vol={0.25} /><Sfx s={1.7} nome="papel_2" /><Sfx s={2.36} nome="carimbo_1" vol={0.35} />
      <Sfx s={2.9} nome="crt_on_0" vol={0.35} /><Sfx s={4.08} nome="bip_0" vol={0.25} /><Sfx s={4.5} nome="papel_3" vol={0.35} /><Sfx s={5.2} nome="carimbo_2" vol={0.35} />
      <Sfx s={5.46} nome="bip_1" vol={0.25} /><Sfx s={N2} nome="sweep_0" vol={0.3} /><Sfx s={N2 + 1.42} nome="bip_2" vol={0.22} />{[0.36, 1.2, 2.04, 2.88, 3.72].map((t) => <Sfx key={t} s={N2 + t} nome="click_0" vol={0.15} />)}<Sfx s={D + 0.07} nome="carimbo_3" />
    </AbsoluteFill>
    </FalaCtx.Provider>
  );
};
