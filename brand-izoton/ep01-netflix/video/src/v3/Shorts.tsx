// Shorts v3a (Parada 2): composições próprias em 9:16, com a voz do Guilherme.
// Hook falado e visual no 1º segundo, legenda palavra a palavra na faixa de baixo, troca visual a cada 1,5–3 s, loop no fim.
// Os hooks S01 e S02 não foram gravados: o SHORT01 abre com o bloco 01 e o SHORT02 com o bloco 15 (mesmo fato, quase as mesmas palavras).
import React from "react";
import { AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import PAL from "./palavras_gui.json";
import { C, FONT, MONO } from "../theme";
import { Camera, Card, Carimbo3, Contador, Cursor, Destaque, Grao, Papel, Recorte, Terminal, useEntrada, useS } from "./kit";
import { Mascara, TelaCRT } from "./transicoes";
import { FalaCtx, LegendaPalavra, Narr, Sfx, Trilha, clamp } from "./Amostra";

type W = [number, number, string];
const P = PAL as unknown as Record<string, { dur: number; palavras: W[] }>;
/** palavras de um bloco deslocadas para o tempo do Short (opcionalmente só até `ate` s do bloco) */
const pal = (b: string, desloc: number, ate = 1e9): W[] => P[b].palavras.filter((w) => w[0] < ate).map((w) => [w[0] + desloc, w[1] + desloc, w[2]] as W);
const t = (b: string, desloc: number, palavra: string, n = 0) => {
  const ws = P[b].palavras.filter((w) => w[2].toLowerCase().replace(/[.,?%!]/g, "").startsWith(palavra.toLowerCase()));
  return (ws[Math.min(n, ws.length - 1)]?.[0] ?? 0) + desloc;
};

/** janela de um plano: monta só entre `de` e `ate` (em s) e passa o quadro relativo */
const Plano: React.FC<{ de: number; ate: number; children: React.ReactNode }> = ({ de, ate, children }) => {
  const S = useS();
  return <Sequence from={S(de)} durationInFrames={Math.max(1, S(ate) - S(de))} layout="none"><Empurra n={Math.max(1, S(ate) - S(de))}>{children}</Empurra></Sequence>;
};
// cada plano se aproxima devagar em degraus de 3 quadros (stop-motion), para nenhum plano ficar parado
const Empurra: React.FC<{ n: number; children: React.ReactNode }> = ({ n, children }) => {
  const f = Math.floor(useCurrentFrame() / 3) * 3;
  const k = Math.min(1, f / n);
  return <AbsoluteFill style={{ transform: `scale(${1 + 0.1 * k}) translateY(${-30 * k}px)`, transformOrigin: "50% 45%" }}>{children}</AbsoluteFill>;
};
const Topo: React.FC<{ texto: string }> = ({ texto }) => (
  <div style={{ position: "absolute", left: 60, top: 70, display: "flex", alignItems: "center", gap: 12, fontFamily: MONO, fontSize: 26, letterSpacing: 3, color: C.tinta }}>
    <span style={{ width: 12, height: 12, borderRadius: 6, background: C.ambar, display: "inline-block" }} />{texto}
  </div>
);
const Botao: React.FC<{ clique: number; escuro?: boolean }> = ({ clique }) => {
  const f = useCurrentFrame();
  const on = f > clique;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 600, display: "flex", justifyContent: "center" }}>
      <div style={{ border: `5px solid ${C.tinta}`, borderRadius: 10, padding: "30px 46px", display: "flex", alignItems: "center", gap: 24,
        background: on ? C.tinta : C.branco, color: on ? C.branco : C.tinta, fontFamily: FONT, fontWeight: 800, fontSize: 76, whiteSpace: "nowrap",
        transform: `scale(${interpolate(f, [clique - 1, clique + 2, clique + 6], [1, 0.92, 1], clamp)})` }}>
        <svg width="66" height="66" viewBox="0 0 24 24"><path d="M3 5l8 7-8 7zM12 5l8 7-8 7z" fill="currentColor" /></svg>PULAR ABERTURA
      </div>
    </div>
  );
};
const Relogio: React.FC<{ inicio: number }> = ({ inicio }) => {
  const f = useCurrentFrame();
  const a = Math.max(0, f - inicio) * 24;
  return (
    <svg width="260" height="260" viewBox="0 0 100 100" style={{ position: "absolute", left: 410, top: 300 }}>
      <circle cx="50" cy="50" r="44" fill="none" stroke={C.tinta} strokeWidth="5" />
      {Array.from({ length: 12 }, (_, i) => <line key={i} x1="50" y1="9" x2="50" y2="15" stroke={C.tinta} strokeWidth="3" transform={`rotate(${i * 30} 50 50)`} />)}
      <line x1="50" y1="50" x2="50" y2="18" stroke={C.ambar} strokeWidth="4" strokeLinecap="round" transform={`rotate(${a} 50 50)`} />
      <line x1="50" y1="50" x2="50" y2="28" stroke={C.tinta} strokeWidth="5" strokeLinecap="round" transform={`rotate(${a / 12} 50 50)`} />
    </svg>
  );
};
const Evid: React.FC<{ img: string; inicio: number; rotulo: string; pos?: string; inteira?: boolean }> = ({ img, inicio, rotulo, pos = "50% 0%", inteira = false }) => (
  <>
    <Card x={90} y={330} w={900} h={760} inicio={inicio} rotY={-6} rotZ={-2} seed={img}>
      <Img src={staticFile(`media/stills/${img}`)} style={{ width: "100%", height: "100%", objectFit: inteira ? "contain" : "cover", objectPosition: pos, background: C.branco }} />
    </Card>
    <Carimbo3 texto={rotulo} inicio={inicio + 8} x={120} y={1120} rot={-4} size={28} />
  </>
);

/* ================================================================== SHORT 02 · Pular abertura (39,6 s) */
const B15 = 0, B16 = 5.5, B17 = 22.6, B18 = 35.0;
export const SHORT02_DUR = B18 + P["18"].dur + 0.8;
export const Short02V3: React.FC = () => {
  const S = useS();
  const palavras = [...pal("15", B15), ...pal("16", B16), ...pal("17", B17), ...pal("18", B18)];
  const T = {
    n136: t("15", B15, "136"), dia: t("15", B15, "dia"), pesquisa: t("16", B16, "pesquisa"), p15: t("16", B16, "15"), adiant: t("16", B16, "adiantavam"),
    min5: t("16", B16, "5"), n250: t("16", B16, "250"), eua: t("16", B16, "estados"), reino: t("16", B16, "reino"), canada: t("16", B16, "canad"),
    web: t("16", B16, "primeiro"), agosto: t("16", B16, "agosto"), y2022: t("17", B17, "2022"), n195: t("17", B17, "195"), eng: t("17", B17, "engenheiro"),
    cupcake: t("17", B17, "cupcake"), botao2: t("18", B18, "um"), esperar: t("18", B18, "esperar"),
  };
  return (
    <FalaCtx.Provider value={[[0, SHORT02_DUR]]}>
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <Papel />
      <Camera dur={S(SHORT02_DUR)} de={1.0} ate={1.08}>
        {/* 1 · o botão clicado no quadro 1 */}
        <Plano de={0} ate={T.n136}><Botao clique={10} /><Cursor de={[900, 1020]} para={[700, 690]} inicio={0} clique={10} /></Plano>
        {/* 2 · contador */}
        <Plano de={T.n136} ate={B16}>
          <Mascara inicio={0} direcao="baixo">
            <div style={{ position: "absolute", left: 0, right: 0, top: 520, display: "flex", flexDirection: "column", alignItems: "center" }}>
              <Contador valor={136000000} inicio={0} dur={36} size={150} />
              <div style={{ fontFamily: MONO, fontSize: 30, letterSpacing: 4, color: C.secundario, marginTop: 14 }}>CLIQUES · PULAR ABERTURA</div>
              <div style={{ marginTop: 40 }}><Destaque texto="NUM DIA TÍPICO" inicio={S(T.dia - T.n136)} size={74} tom="ambar" /></div>
            </div>
          </Mascara>
          <Carimbo3 texto="DADO DE 2022 · NETFLIX" inicio={S(0.8)} x={300} y={380} rot={-4} size={26} />
        </Plano>
        {/* 3 · a origem: o texto oficial */}
        <Plano de={B16} ate={T.p15}><Evid img="web_skipintro.png" inicio={0} rotulo="NETFLIX · ORIGEM DO SKIP INTRO · 2022" inteira /></Plano>
        {/* 4 · 15% */}
        <Plano de={T.p15} ate={T.adiant}>
          <div style={{ position: "absolute", left: 0, right: 0, top: 480, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Contador valor={15} inicio={0} dur={18} size={260} sufixo="%" />
            <div style={{ marginTop: 10 }}><Destaque texto="DAS VEZES" inicio={S(0.6)} size={70} /></div>
          </div>
        </Plano>
        {/* 5 · adiantando na mão */}
        <Plano de={T.adiant} ate={T.n250 - 0.9}>
          <div style={{ position: "absolute", left: 120, top: 520, width: 840 }}>
            <Terminal texto=">> AVANÇAR… AVANÇAR… AVANÇAR" inicio={0} cps={22} w={840} size={44} />
            <div style={{ marginTop: 60, height: 14, background: C.apoio, borderRadius: 7, position: "relative" }}>
              <ProgressoScrub />
            </div>
            <div style={{ marginTop: 30 }}><Destaque texto="PRIMEIROS 5 MINUTOS" inicio={S(T.min5 - T.adiant)} size={58} tom="ambar" /></div>
          </div>
        </Plano>
        {/* 6 · 250 séries */}
        <Plano de={T.n250 - 0.9} ate={T.eua}>
          <Recorte src="media/stills/poster_houseofcards.jpg" x={120} y={330} w={300} inicio={0} rot={-6} seed="p1" />
          <Recorte src="media/stills/poster_strangerthings.jpg" x={400} y={300} w={300} inicio={4} rot={3} seed="p2" />
          <Recorte src="media/stills/poster_wednesday.jpg" x={670} y={340} w={300} inicio={8} rot={-2} seed="p3" />
          <div style={{ position: "absolute", left: 0, right: 0, top: 900, display: "flex", justifyContent: "center" }}>
            <Destaque texto="250 SÉRIES NO TESTE" inicio={S(0.9)} size={78} />
          </div>
        </Plano>
        {/* 7 · três países */}
        <Plano de={T.eua} ate={T.web}>
          <div style={{ position: "absolute", left: 0, right: 0, top: 460, display: "flex", flexDirection: "column", alignItems: "center", gap: 26 }}>
            <Destaque texto="EUA" inicio={0} size={110} />
            <Destaque texto="REINO UNIDO" inicio={S(T.reino - T.eua)} size={110} />
            <Destaque texto="CANADÁ" inicio={S(T.canada - T.eua)} size={110} />
          </div>
        </Plano>
        {/* 8 · web primeiro, TV em agosto de 2017 */}
        <Plano de={T.web} ate={B17}>
          <Evid img="web_skipintro_tv.png" inicio={0} rotulo="NETFLIX · TV EM AGO. 2017" inteira />
          <Carimbo3 texto="AGO. 2017" inicio={S(T.agosto - T.web)} x={560} y={260} rot={6} size={56} />
        </Plano>
        {/* 9 · 2022 */}
        <Plano de={B17} ate={T.n195}>
          <div style={{ position: "absolute", left: -40, top: 360, fontFamily: FONT, fontWeight: 800, fontSize: 420, color: "#E6E6E6", letterSpacing: -12 }}>2022</div>
          <Carimbo3 texto="A NETFLIX FEZ A CONTA" inicio={S(0.4)} x={180} y={900} rot={-5} size={44} />
        </Plano>
        {/* 10 · 195 anos (recompensa) */}
        <Plano de={T.n195} ate={T.eng}>
          <Relogio inicio={0} />
          <div style={{ position: "absolute", left: 0, right: 0, top: 640, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Contador valor={195} inicio={0} dur={30} size={240} />
            <div style={{ marginTop: 6 }}><Destaque texto="ANOS ECONOMIZADOS" inicio={S(0.8)} size={66} tom="ambar" /></div>
            <div style={{ fontFamily: MONO, fontSize: 26, letterSpacing: 3, color: C.secundario, marginTop: 22 }}>SOMANDO O TEMPO DE TODO MUNDO</div>
          </div>
        </Plano>
        {/* 11 · cupcake grátis */}
        <Plano de={T.eng} ate={B18}>
          <Card x={110} y={480} w={860} inicio={0} rotY={-8} rotZ={-2} seed="cup">
            <div style={{ padding: "48px 50px" }}>
              <div style={{ fontFamily: MONO, fontSize: 24, letterSpacing: 3, color: C.secundario }}>ENGENHEIRO DA NETFLIX · 2022</div>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 66, lineHeight: 1.08, color: C.tinta, marginTop: 20 }}>“NEM UM BOTÃO ESCRITO</div>
              <div style={{ marginTop: 14 }}><Destaque texto="CUPCAKE GRÁTIS" inicio={S(T.cupcake - T.eng)} size={76} tom="ambar" /></div>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 66, lineHeight: 1.08, color: C.tinta, marginTop: 14 }}>TERIA MAIS CLIQUES.”</div>
            </div>
          </Card>
        </Plano>
        {/* 12 · volta ao botão (loop com o quadro 1) */}
        <Plano de={B18} ate={SHORT02_DUR}>
          <Botao clique={Math.round((T.esperar - B18) * 30)} />
          <Cursor de={[900, 1020]} para={[700, 690]} inicio={0} clique={Math.round((T.esperar - B18) * 30)} />
          <div style={{ position: "absolute", left: 0, right: 0, top: 880, display: "flex", justifyContent: "center" }}>
            <Destaque texto="NÃO DEIXAR VOCÊ ESPERAR." inicio={S(T.esperar - B18 - 0.6)} size={60} />
          </div>
        </Plano>
      </Camera>
      <Topo texto="PRODUTO · NETFLIX" />
      <LegendaPalavra palavras={palavras} chave={{ "136": "tinta", "MILHÕES": "tinta", "TÍPICO": "ambar", "15": "tinta", "250": "tinta", "195": "ambar", "ANOS": "ambar", "CUPCAKE": "ambar", "ESPERAR": "tinta" }} />
      <Grao />
      <Narr s={B15} arq="media/narr_gui/b15.wav" /><Narr s={B16} arq="media/narr_gui/b16.wav" /><Narr s={B17} arq="media/narr_gui/b17.wav" /><Narr s={B18} arq="media/narr_gui/b18.wav" />
      <Trilha de={260} vol={0.06} />
      <Sfx s={0.33} nome="click_0" vol={0.5} /><Sfx s={T.n136} nome="sweep_0" vol={0.3} /><Sfx s={T.dia} nome="bip_0" vol={0.3} /><Sfx s={B16} nome="papel_1" />
      <Sfx s={T.p15} nome="tecla_1" vol={0.3} /><Sfx s={T.adiant} nome="tecla_2" vol={0.25} /><Sfx s={T.n250 - 0.9} nome="papel_2" /><Sfx s={T.eua} nome="bip_1" vol={0.3} />
      <Sfx s={T.web} nome="papel_3" /><Sfx s={T.agosto} nome="carimbo_1" vol={0.35} /><Sfx s={B17 + 0.4} nome="carimbo_2" vol={0.35} /><Sfx s={T.n195} nome="sweep_1" vol={0.3} />
      <Sfx s={T.eng} nome="papel_0" /><Sfx s={T.esperar} nome="click_1" vol={0.5} />
    </AbsoluteFill>
    </FalaCtx.Provider>
  );
};
const ProgressoScrub: React.FC = () => {
  const f = useCurrentFrame();
  const k = (Math.floor(f / 6) % 8) / 8;
  return <div style={{ position: "absolute", left: 0, top: -9, width: `${8 + k * 60}%`, height: 32 }}>
    <div style={{ position: "absolute", left: 0, top: 9, right: 0, height: 14, background: C.netflix, borderRadius: 7 }} />
    <div style={{ position: "absolute", right: -16, top: 0, width: 32, height: 32, borderRadius: 16, background: C.netflix }} />
  </div>;
};

/* ================================================================== SHORT 01 · Sono (30,5 s) */
const A1 = 0, ARQ = 5.0, A2 = 10.1, A49 = 12.9;
const HOOK_DUR = 4.82;
export const SHORT01_DUR = A49 + P["49"].dur + 2.2;
export const Short01V3: React.FC = () => {
  const S = useS();
  const f = useCurrentFrame();
  const palavras = [...pal("01", A1), ...pal("02", A2, 2.5), ...pal("49", A49)];
  const T = { y2017: t("01", A1, "2017"), ceo: t("01", A1, "ceo"), sono: t("01", A1, "sono"), hbo: t("02", A2, "hbo"), lista: t("02", A2, "lista"),
    y2019: t("49", A49, "2019"), fort: t("49", A49, "fortnite"), perd: t("49", A49, "perdemos"), hbo2: t("49", A49, "hbo"),
    yt: t("49", A49, "youtube"), aud: t("49", A49, "audi"), fim: A49 + P["49"].dur };
  const ARQ_LEG: [number, string][] = [[0, "Você pode ver TV linear,"], [1.6, "jogar videogame,"], [2.9, "ver YouTube…"], [4.2, "ou ver Netflix."]];
  return (
    <FalaCtx.Provider value={[[0, 12.6], [A49, T.fim]]}>
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      <Papel />
      {/* 1 · frase literal sobre a tela CRT, no quadro 0; em "CEO", troca para o recorte e a ficha da entrevista */}
      <Plano de={T.ceo} ate={ARQ}>
        <Recorte src="media/v3img/rec_hastings_2015.png" x={80} y={240} w={440} inicio={0} rot={-3} seed="s1h" de="esq" />
        <Card x={480} y={330} w={520} h={420} inicio={S(0.6)} rotY={-10} rotZ={2} seed="s1f">
          <Img src={staticFile("media/stills/web_sleep.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 30%" }} />
        </Card>
        <Carimbo3 texto="ENTREVISTA Q1 · 17 ABR. 2017" inicio={S(1.0)} x={420} y={780} rot={-4} size={30} />
        <div style={{ position: "absolute", left: 60, right: 60, top: 860, textAlign: "center" }}>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 92, lineHeight: 1.0, color: C.tinta }}>COMPETE COM<br />O SEU</div>
          <div style={{ marginTop: 18, display: "inline-block", transform: `scale(${1 + 0.12 * Math.max(0, 1 - Math.abs(f - S(T.sono)) / 6)})` }}><Destaque texto="SONO." inicio={2} size={150} /></div>
        </div>
      </Plano>
      <Plano de={0} ate={T.ceo}>
        <div style={{ position: "absolute", left: 90, right: 90, top: 260, height: 520, borderRadius: 18, overflow: "hidden", boxShadow: "0 30px 60px rgba(0,0,0,0.25)" }}>
          <TelaCRT clip="media/arquivo/HOOK.mp4" inicioClip={0} dur={S(ARQ)} desliga={false} />
        </div>
        <Carimbo3 texto="WALL STREET · 2017" inicio={S(T.y2017)} x={130} y={210} rot={-4} size={34} />
        <div style={{ position: "absolute", left: 60, right: 60, top: 840, textAlign: "center" }}>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 92, lineHeight: 1.0, color: C.tinta, opacity: useEntrada(0, 4) }}>COMPETE COM<br />O SEU</div>
          <div style={{ marginTop: 18, display: "inline-block", transform: `scale(${1 + 0.12 * Math.max(0, 1 - Math.abs(f - S(T.sono)) / 6)})` }}><Destaque texto="SONO." inicio={2} size={150} /></div>
        </div>
      </Plano>
      {/* 2 · a fala do TED: a lista */}
      <Plano de={ARQ} ate={A2}>
        <div style={{ position: "absolute", left: 0, right: 0, top: 200, height: 640 }}>
          <TelaCRT clip="media/arquivo/HOOK.mp4" inicioClip={0} dur={S(A2 - ARQ)} desliga />
        </div>
        <div style={{ position: "absolute", left: 90, top: 900, display: "flex", flexDirection: "column", gap: 16, alignItems: "flex-start" }}>
          <Destaque texto="TV LINEAR" inicio={S(0.62)} size={70} /><Destaque texto="VIDEOGAME" inicio={S(1.88)} size={70} />
          <Destaque texto="YOUTUBE" inicio={S(3.1)} size={70} /><Destaque texto="NETFLIX" inicio={S(4.58)} size={70} tom="netflix" />
        </div>
        <div style={{ position: "absolute", right: 70, top: 870, fontFamily: MONO, fontSize: 24, letterSpacing: 3, color: C.secundario, textAlign: "right" }}>REED HASTINGS<br />TED · ABR. 2018</div>
      </Plano>
      {/* 3 · a HBO não está na lista */}
      <Plano de={A2} ate={A49}>
        <div style={{ position: "absolute", left: 90, top: 520, display: "flex", flexDirection: "column", gap: 16, alignItems: "flex-start" }}>
          {["TV LINEAR", "VIDEOGAME", "YOUTUBE"].map((x) => <Destaque key={x} texto={x} inicio={0} size={70} />)}<Destaque texto="NETFLIX" inicio={0} size={70} tom="netflix" />
        </div>
        <div style={{ position: "absolute", left: 600, top: 640, transform: "rotate(-5deg)" }}>
          <Destaque texto="HBO" inicio={S(T.hbo - A2)} size={110} style={{ background: C.apoio, color: C.tinta }} />
          <div style={{ position: "absolute", left: -10, top: 62, height: 12, background: C.tinta, width: `${interpolate(f - S(T.lista), [0, 8], [0, 290], clamp)}px` }} />
        </div>
        <Carimbo3 texto="FORA DA LISTA" inicio={S(T.lista - A2 + 0.2)} x={560} y={820} rot={-7} size={40} />
      </Plano>
      {/* 4 · e a concorrência? */}
      <Plano de={A49} ate={T.y2019}>
        <div style={{ position: "absolute", left: 0, right: 0, top: 640, display: "flex", justifyContent: "center" }}><Destaque texto="E A CONCORRÊNCIA?" inicio={0} size={88} /></div>
      </Plano>
      {/* 5 · a carta aos acionistas */}
      <Plano de={T.y2019} ate={(T.y2019 + T.fort) / 2}><Evid img="carta_q4_18-05.png" inicio={0} rotulo="CARTA AOS ACIONISTAS · JAN. 2019" pos="50% 30%" /></Plano>
      <Plano de={(T.y2019 + T.fort) / 2} ate={T.fort}>
        <Card x={60} y={420} w={960} h={520} inicio={0} rotY={6} rotZ={1} seed="s1z">
          <Img src={staticFile("media/stills/carta_q4_18-05.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 62%", transform: "scale(1.5)" }} />
        </Card>
        <Carimbo3 texto="“COMPETITION”" inicio={S(0.3)} x={140} y={360} rot={-5} size={40} />
      </Plano>
      {/* 6 · Fortnite */}
      <Plano de={T.fort} ate={T.hbo2 - 0.3}>
        <div style={{ position: "absolute", left: 0, right: 0, top: 520, display: "flex", flexDirection: "column", alignItems: "center", gap: 26 }}>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 70, color: C.tinta }}>“COMPETIMOS COM O</div>
          <Destaque texto="FORTNITE" inicio={0} size={130} />
          <Destaque texto="E PERDEMOS PARA ELE”" inicio={S(T.perd - T.fort)} size={64} tom="ambar" />
        </div>
      </Plano>
      {/* 7 · mais do que para a HBO */}
      <Plano de={T.hbo2 - 0.3} ate={T.yt - 0.2}>
        <div style={{ position: "absolute", left: 0, right: 0, top: 560, display: "flex", flexDirection: "column", alignItems: "center", gap: 30 }}>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 70, color: C.tinta }}>MAIS DO QUE PARA A</div>
          <div style={{ position: "relative", transform: "rotate(-3deg)" }}>
            <Destaque texto="HBO" inicio={S(0.3)} size={150} style={{ background: C.apoio, color: C.tinta }} />
          </div>
        </div>
      </Plano>
      {/* 8 · o YouTube caiu */}
      <Plano de={T.yt - 0.2} ate={T.aud}>
        <div style={{ position: "absolute", left: 0, right: 0, top: 560, display: "flex", flexDirection: "column", alignItems: "center", gap: 26 }}>
          <Destaque texto="YOUTUBE" inicio={0} size={130} />
          <Carimbo3 texto="FORA DO AR · ALGUNS MINUTOS" inicio={S(0.5)} x={170} y={760} rot={-5} size={40} />
        </div>
      </Plano>
      {/* 9 · audiência e cadastros sobem */}
      <Plano de={T.aud} ate={T.fim}>
        <svg width="900" height="420" viewBox="0 0 900 420" style={{ position: "absolute", left: 90, top: 460 }}>
          <polyline points="20,380 220,340 400,300 560,190 720,110 880,30" fill="none" stroke={C.netflix} strokeWidth="14" strokeLinecap="round" strokeLinejoin="round"
            pathLength={1} strokeDasharray={1} strokeDashoffset={interpolate(f - S(T.aud), [0, 30], [1, 0], clamp)} />
        </svg>
        <div style={{ position: "absolute", left: 0, right: 0, top: 950, display: "flex", justifyContent: "center" }}><Destaque texto="A NETFLIX SUBIU" inicio={S(0.6)} size={78} tom="ambar" /></div>
      </Plano>
      {/* 10 · loop: volta à frase do começo */}
      <Plano de={T.fim} ate={SHORT01_DUR}>
        <div style={{ position: "absolute", left: 60, right: 60, top: 640, textAlign: "center" }}>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 92, lineHeight: 1.0, color: C.tinta }}>A BRIGA É PELO SEU</div>
          <div style={{ marginTop: 18 }}><Destaque texto="TEMPO." inicio={4} size={150} /></div>
        </div>
      </Plano>
      <Topo texto="ARQUIVO NETFLIX · O SONO" />
      {/* legenda: palavra a palavra na voz dele; na fala do TED, legenda da tradução */}
      <LegendaPalavra palavras={palavras} chave={{ "SONO": "tinta", "HBO": "tinta", "FORTNITE": "tinta", "YOUTUBE": "tinta", "SUBIRAM": "ambar" }} />
      <Plano de={ARQ} ate={A2}>
        {ARQ_LEG.map(([s, l], i) => f >= S(ARQ + s) && f < S(ARQ + (ARQ_LEG[i + 1]?.[0] ?? HOOK_DUR + 0.2)) && (
          <div key={i} style={{ position: "absolute", left: 60, right: 60, top: 1400, textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 70, color: C.tinta }}>{l.toUpperCase()}</div>
        ))}
      </Plano>
      <Grao />
      <Narr s={A1} arq="media/narr_gui/b01.wav" />
      <Narr s={ARQ} arq="media/arquivo/HOOK.mp4" vol={0.95} />
      <Narr s={A2} arq="media/narr_gui/b02.wav" dur={2.5} />
      <Narr s={A49} arq="media/narr_gui/b49.wav" />
      <Trilha de={40} vol={0.06} />
      <Sfx s={T.y2017} nome="carimbo_0" vol={0.35} /><Sfx s={ARQ - 0.05} nome="crt_on_0" vol={0.35} /><Sfx s={A2 - 0.2} nome="crt_off_1" vol={0.35} />
      <Sfx s={T.hbo} nome="papel_3" vol={0.35} /><Sfx s={T.lista + 0.2} nome="carimbo_2" vol={0.35} /><Sfx s={A49} nome="bip_0" vol={0.3} /><Sfx s={T.y2019} nome="papel_1" />
      <Sfx s={T.fort} nome="bip_1" vol={0.3} /><Sfx s={T.hbo2} nome="papel_2" /><Sfx s={T.yt} nome="carimbo_1" vol={0.35} /><Sfx s={T.aud} nome="sweep_0" vol={0.3} /><Sfx s={T.fim} nome="carimbo_3" />
    </AbsoluteFill>
    </FalaCtx.Provider>
  );
};
