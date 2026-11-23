import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import raw from "../../data/vasco.json";
import { CameraMove, pop, Shots } from "../../cartoon/Base";
import { Arquibancada, Carimbo, Faixa, Gramado, Nuvens, PlacaMadeira, ROUND, Sepia } from "../../cartoon/Cenarios";
import { MesaReuniao, PlacaEscudo, QuadroTexto, Radio, SalaRica } from "../../cartoon/Cenarios2";
import { Expressao, MiniTorcedor } from "../../cartoon/Personagem";
import { Estadio3D } from "../../cartoon/Estadio3D";
import { Cutout, Scoreboard, YearStamp, Rays } from "../../components/Graphics";
import { PaperBackground } from "../../components/Paper";
import { ANTON, BEBAS } from "../../theme";
import { Abs, Ator, Barco, Bola, Etiqueta, FotoCheia, Mar, OUT, P, Polaroid, useSec } from "../Flamengo/Elementos";
import { Carta, Caravela, Cruz, CRUZ, Obra, PRETO, Trem } from "./Elementos";

const D = raw;
const ES = raw.escudos as Record<string, string>;
const FT = raw.fotos as Record<string, string>;
const LOGO = raw.logos as Record<string, string>;

/* ------------------------------- elenco ------------------------------- */
const NARRADOR: P = { bigode: true, cabelo: "capacete", corCabelo: "#2B1B10", terno: "#22252B", gravata: CRUZ, pele: "#E8A877" };
const CARTOLA: P = { oculos: true, cabelo: "lados", corCabelo: "#4A3020", terno: "#4E5560", gravata: "#2E4A8B", pele: "#F6DCC6" };
const CARTOLA2: P = { chapeu: true, bigode: true, terno: "#2E3A5A", gravata: "#6B2A4A", pele: "#F8F2EC" };
const CARTOLA3: P = { bigode: true, cabelo: "grisalho", terno: "#5A5F68", gravata: "#1E7B4A", pele: "#F4E6DC" };
const PRESIDENTE: P = { bigode: true, oculos: true, cabelo: "grisalho", terno: "#1C1C22", gravata: CRUZ, pele: "#F2D2B6" };
const PORTUGA: P = { bigode: true, cabelo: "lados", corCabelo: "#2B1B10", terno: "#F1ECE0", gravata: PRETO, pele: "#F2C29B" };
const PORTUGA2: P = { bigode: true, chapeu: true, terno: "#2E2E36", gravata: CRUZ, pele: "#F8E2CC" };
const JOGADOR = (pele: string, cabelo: P["cabelo"] = "capacete"): P => ({ terno: PRETO, gravata: "#fff", pele, cabelo, corCabelo: "#1E140E", cachecol: "#fff" });
const fan = (pele = "#F2C29B", cabelo: P["cabelo"] = "capacete"): P => ({ cachecol: "#fff", gravata: CRUZ, terno: PRETO, pele, cabelo, corCabelo: "#1E140E" });

const CORES_VASCO = [PRETO, "#FFFFFF", PRETO, "#FFFFFF", CRUZ];
const CORES_3D = ["#111111", "#FFFFFF", "#111111", "#FFFFFF", "#111111", "#D7262E"];
const FAIXA_COR: [string, string] = ["#111111", "#FFFFFF"];
const FAIXA_COLINA = ["GIGANTE", "DA COLINA"];
const FAIXA_CTA = ["SEGUE O", "@FUTEXPLICANDO"];
const BARCO_COR: [string, string] = [PRETO, CRUZ];

type CamTipo = React.ComponentProps<typeof CameraMove>["tipo"];

const Sala: React.FC<{ children?: React.ReactNode; tipo?: CamTipo; forca?: number; opts?: React.ComponentProps<typeof SalaRica>; sepia?: boolean }> = ({ children, tipo = "zoom", forca = 1, opts, sepia }) => {
  const el = (
    <CameraMove tipo={tipo} forca={forca}>
      <SalaRica {...opts}>{children}</SalaRica>
    </CameraMove>
  );
  return sepia ? <Sepia forca={0.6}>{el}</Sepia> : el;
};

const Papel: React.FC<{ children?: React.ReactNode; tipo?: CamTipo; forca?: number; raios?: boolean }> = ({ children, tipo = "zoom", forca = 1, raios }) => (
  <CameraMove tipo={tipo} forca={forca}>
    <PaperBackground tint="rgba(17,17,17,0.22)" />
    {raios ? <Rays color={PRETO} opacity={0.12} /> : null}
    {children}
  </CameraMove>
);

const Stamp: React.FC<{ text: string; sub?: string; y: number; at?: number; size?: number; color?: string }> = ({ text, sub, y, at = 4, size = 230, color = CRUZ }) => (
  <Abs x={0} y={y} style={{ width: 1080, display: "flex", justifyContent: "center" }}>
    <YearStamp text={text} sub={sub} startFrame={at} size={size} color={color} />
  </Abs>
);

const CarimboIn: React.FC<{ texto: string; y: number; at?: number; cor?: string; size?: number }> = ({ texto, y, at = 5, cor = CRUZ, size = 130 }) => {
  const f = useCurrentFrame();
  return (
    <Abs x={0} y={y} style={{ width: 1080, textAlign: "center" }}>
      <Carimbo texto={texto} k={pop(f, at, 8)} size={size} rot={-7} cor={cor} />
    </Abs>
  );
};

/** Doze jogadores enfileirados; um X vermelho aparece sobre cada um. */
const Doze: React.FC<{ riscar?: boolean }> = ({ riscar = true }) => {
  const f = useCurrentFrame();
  const peles = ["#7A4B30", "#A86F4C", "#5E3A24", "#D9A27A", "#8C5A3C", "#6B4128"];
  return (
    <Abs x={20} y={300} style={{ width: 1040, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", rowGap: 30, justifyItems: "center" }}>
      {Array.from({ length: 12 }).map((_, i) => (
        <div key={i} style={{ position: "relative", scale: `${pop(f, i * 1.2, 6)}` }}>
          <MiniTorcedor cor={PRETO} pele={peles[i % peles.length]} tam={170} fase={i} bracos={false} />
          {riscar ? (
            <svg width="170" height="238" viewBox="0 0 10 14" style={{ position: "absolute", left: 0, top: 0, opacity: f > 18 + i * 1.5 ? 1 : 0 }}>
              <path d="M1 3 L9 11 M9 3 L1 11" stroke={CRUZ} strokeWidth="1.3" strokeLinecap="round" />
            </svg>
          ) : null}
        </div>
      ))}
    </Abs>
  );
};

/** Sala de reunião com três cartolas. */
const Reuniao: React.FC<{ es: [Expressao, Expressao, Expressao]; quadroEl?: React.ReactNode; tipo?: CamTipo; sepia?: boolean }> = ({ es, quadroEl, tipo = "zoom", sepia }) => (
  <Sala tipo={tipo} sepia={sepia} opts={{ cortina: false, janela: false, tapete: false, quadros: false }}>
    <Abs x={540 - 300} y={260}>{quadroEl}</Abs>
    <Ator p={CARTOLA3} e={es[0]} plano="medio" x={190} y={760} fase={1} />
    <Ator p={CARTOLA2} e={es[2]} plano="medio" x={900} y={790} fase={2} espelhar />
    <Ator p={CARTOLA} e={es[1]} plano="medio" x={545} y={720} braco />
    <MesaReuniao top={1330} />
  </Sala>
);

/* ================================ CENAS ================================ */

/** 1 — "Em 1924, mandaram o Vasco cortar doze jogadores negros e pobres... e o Vasco disse: não!" */
export const C01Gancho: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 1.9,
        el: (
          <Papel tipo="zoom" forca={1.2}>
            <Abs x={110} y={560}><Polaroid src={FT.camisasNegras} largura={820} altura={565} credito="Foto: AFP (reprodução)" rot={-3} /></Abs>
            <Stamp text="1924" y={230} size={230} at={2} />
          </Papel>
        ),
      },
      { dur: 1.7, el: <Reuniao sepia es={["desconfiado", "dentes", "desconfiado"]} quadroEl={<QuadroTexto linhas={["CORTEM", "12 JOGADORES"]} largura={600} />} /> },
      { dur: 1.9, el: <Papel tipo="zoom" forca={1}><Doze /></Papel> },
      {
        dur: 2.83,
        el: (
          <Sala tipo="zoom" forca={1.3} opts={{ janela: false }}>
            <Ator p={PRESIDENTE} e="dentes" plano="close" />
            <CarimboIn texto="NÃO!" y={250} at={30} size={260} />
          </Sala>
        ),
      },
    ]}
  />
);

/** 2 — "Fica até o final que eu explico." */
export const C02Fica: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 1.1,
        el: (
          <Sala tipo="zoom" forca={1.2}>
            <Abs x={-30} y={760}><Radio largura={430} /></Abs>
            <Ator p={NARRADOR} e="sorriso" plano="medio" x={680} y={720} />
          </Sala>
        ),
      },
      { dur: 1.16, el: <Sala tipo="zoom" forca={1.6} opts={{ cortina: false }}><Abs x={260} y={300}><PlacaEscudo src={ES.vasco} tam={560} /></Abs></Sala> },
    ]}
  />
);

/** 3 — "Tudo começou em 1898, quando remadores, a maioria portugueses, fundaram um clube de regatas no Rio." */
export const C03Fundacao: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 1.9,
        el: (
          <Sepia forca={0.55}>
            <CameraMove tipo="zoom" forca={1.1}>
              <Mar horizonte={1100} tarde>
                <Abs x={160} y={980}><Barco largura={760} nome="1898" ritmo={0.8} cores={BARCO_COR} /></Abs>
              </Mar>
              <Stamp text="1898" sub="21 DE AGOSTO" y={330} size={250} />
            </CameraMove>
          </Sepia>
        ),
      },
      {
        dur: 1.8,
        el: (
          <Sepia forca={0.45}>
            <CameraMove tipo="panDir">
              <Mar horizonte={1250} tarde pao={false}>
                <Ator p={PORTUGA} e="sorriso" plano="medio" x={260} y={640} fase={1} />
                <Ator p={PORTUGA2} e="dentes" plano="medio" x={800} y={680} fase={2} espelhar braco />
                <Abs x={0} y={250} style={{ width: 1080, display: "flex", justifyContent: "center" }}><Etiqueta size={70} cor={PRETO}>REMADORES PORTUGUESES</Etiqueta></Abs>
              </Mar>
            </CameraMove>
          </Sepia>
        ),
      },
      {
        dur: 1.72,
        el: (
          <Sepia forca={0.4}>
            <CameraMove tipo="zoom">
              <Mar horizonte={900} tarde>
                <Abs x={200} y={1080}><Barco largura={680} nome="1898" ritmo={0.6} cores={BARCO_COR} /></Abs>
                <Abs x={150} y={330}>
                  <PlacaMadeira largura={780}>
                    <div style={{ fontSize: 44 }}>RIO DE JANEIRO · 1898</div>
                    <div style={{ fontSize: 80 }}>CLUBE DE REGATAS</div>
                  </PlacaMadeira>
                </Abs>
              </Mar>
            </CameraMove>
          </Sepia>
        ),
      },
      {
        dur: 2.0,
        el: (
          <Sala tipo="zoom" forca={1.1} sepia opts={{ cortina: false, janela: false, tapete: false, quadros: false }}>
            <Abs x={540 - 300} y={250}><QuadroTexto linhas={["CLUB DE REGATAS", "VASCO DA GAMA"]} largura={600} /></Abs>
            <Ator p={PORTUGA} e="sorriso" plano="medio" x={200} y={780} fase={1} />
            <Ator p={PORTUGA2} e="sorriso" plano="medio" x={890} y={800} fase={2} espelhar />
            <Ator p={CARTOLA3} e="dentes" plano="medio" x={545} y={730} braco />
            <MesaReuniao top={1330} />
          </Sala>
        ),
      },
    ]}
  />
);

/** 4 — "O nome homenageia Vasco da Gama, que 400 anos antes tinha chegado às Índias." */
export const C04Nome: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 2.2,
        el: (
          <Sepia forca={0.3}>
            <CameraMove tipo="zoom" forca={1}>
              <Mar horizonte={1150} pao={false} tarde>
                <Abs x={130} y={480}><Caravela largura={820} /></Abs>
                <Abs x={0} y={200} style={{ width: 1080, display: "flex", justifyContent: "center" }}><Etiqueta size={78} cor={PRETO}>VASCO DA GAMA</Etiqueta></Abs>
              </Mar>
            </CameraMove>
          </Sepia>
        ),
      },
      {
        dur: 1.6,
        el: (
          <Papel tipo="panDir" forca={1}>
            <Stamp text="1498" sub="CHEGADA ÀS ÍNDIAS" y={260} size={220} at={2} />
            <Abs x={150} y={720} style={{ scale: "0.95" }}><Caravela largura={780} /></Abs>
          </Papel>
        ),
      },
      {
        dur: 1.72,
        el: (
          <Papel tipo="zoom" forca={1.3} raios>
            <Abs x={240} y={270}><PlacaEscudo src={ES.vasco} tam={600} /></Abs>
            <Abs x={0} y={1330} style={{ width: 1080, display: "flex", justifyContent: "center" }}><Etiqueta size={74} cor={CRUZ}>1498 → 1898: 400 ANOS</Etiqueta></Abs>
          </Papel>
        ),
      },
    ]}
  />
);

/** 5 — "No futebol, o Vasco subiu pra elite e, em 1923, já foi campeão carioca, com um time de negros e operários." */
export const C05Camisas: React.FC = () => {
  const Sobe: React.FC = () => {
    const { s } = useSec();
    const y = interpolate(s, [0.1, 1.2], [1100, 420], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
    return (
      <>
        <Abs x={140} y={260}><PlacaMadeira largura={800}><div style={{ fontSize: 90 }}>1ª DIVISÃO</div></PlacaMadeira></Abs>
        <Abs x={390} y={y}><Bola tam={300} /></Abs>
        <Abs x={340} y={y + 300}><svg width="400" height="300" viewBox="0 0 100 75"><path d="M50 0 L90 40 L65 40 L65 75 L35 75 L35 40 L10 40 Z" fill={CRUZ} stroke={OUT} strokeWidth="3" /></svg></Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 2.1, el: <CameraMove tipo="zoom"><Gramado horizonte={1350}><Nuvens /><Sobe /></Gramado></CameraMove> },
        {
          dur: 2.4,
          el: (
            <Papel tipo="zoom" forca={1}>
              <Stamp text="1923" sub="CAMPEÃO CARIOCA" y={220} size={220} at={2} />
              <Abs x={110} y={600}><Polaroid src={FT.camisasNegras} largura={820} altura={565} legenda="CAMISAS NEGRAS" credito="Foto: AFP (reprodução)" rot={2} /></Abs>
            </Papel>
          ),
        },
        {
          dur: 2.0,
          el: (
            <CameraMove tipo="panEsq">
              <Gramado horizonte={1300}>
                <Nuvens />
                <Ator p={JOGADOR("#7A4B30")} e="dentes" plano="medio" x={230} y={720} braco pulo={14} />
                <Ator p={JOGADOR("#D9A27A", "lados")} e="sorriso" plano="medio" x={840} y={740} espelhar pulo={10} fase={2} />
                <Ator p={JOGADOR("#5E3A24", "careca")} e="sorriso" plano="medio" x={540} y={680} fase={1} />
              </Gramado>
            </CameraMove>
          ),
        },
        { dur: 1.64, el: <CameraMove tipo="zoom" forca={1.2}><Gramado horizonte={1500}><Arquibancada cores={CORES_VASCO} linhas={8} tam={120} top={-60} faixa={<Faixa texto="CAMISAS NEGRAS · 1923" largura={940} cor={PRETO} corTexto="#fff" escudo={ES.vasco} />} /></Gramado></CameraMove> },
      ]}
    />
  );
};

/** 6 — "Os grandes clubes criaram uma nova liga e exigiram que o Vasco cortasse doze desses jogadores." */
export const C06Liga: React.FC = () => {
  const Escudos: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <QuadroTexto linhas={[]} largura={600}>
        <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 60, color: "#F0B23C", lineHeight: 1 }}>NOVA LIGA · AMEA</div>
        <div style={{ display: "flex", gap: 18, justifyContent: "center", marginTop: 14 }}>
          {[ES.flamengo, ES.fluminense, ES.botafogo].map((e, i) => (
            <Img key={e} src={staticFile(e)} style={{ height: 120, width: 120, objectFit: "contain", scale: `${pop(f, 4 + i * 3, 8)}` }} />
          ))}
        </div>
      </QuadroTexto>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 2.2, el: <Reuniao sepia es={["sorriso", "dentes", "desconfiado"]} quadroEl={<Escudos />} /> },
        { dur: 1.9, el: <Sala tipo="zoom" forca={1.3} sepia opts={{ cortina: false }}><Ator p={CARTOLA} e="desconfiado" plano="close" /><CarimboIn texto="CORTEM 12!" y={250} at={8} size={140} /></Sala> },
        { dur: 2.24, el: <Papel tipo="zoom" forca={0.8}><Doze /></Papel> },
      ]}
    />
  );
};

/** 7 — "O presidente José Augusto Prestes respondeu por carta: o Vasco ficava com seus atletas. É a Resposta Histórica." */
export const C07Resposta: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 1.9,
        el: (
          <Sala tipo="zoom" forca={1.1} sepia opts={{ cortina: false, janela: false }}>
            <Ator p={PRESIDENTE} e="desconfiado" plano="medio" x={540} y={700} />
            <MesaReuniao top={1330} />
            <Abs x={0} y={1460} style={{ width: 1080, display: "flex", justifyContent: "center" }}>
              <PlacaMadeira largura={820}><div style={{ fontSize: 40 }}>PRESIDENTE DO VASCO</div><div style={{ fontSize: 70 }}>JOSÉ AUGUSTO PRESTES</div></PlacaMadeira>
            </Abs>
          </Sala>
        ),
      },
      {
        dur: 3.5,
        el: (
          <Papel tipo="zoom" forca={0.6}>
            <Abs x={100} y={200}>
              <Carta linhas={["Rio, 7 de abril de 1924 · Ofício nº 261", "O Vasco não", "vai excluir", "seus atletas."]} inicio={4} cps={1.3} assinatura="José Augusto Prestes" />
            </Abs>
          </Papel>
        ),
      },
      {
        dur: 2.44,
        el: (
          <Papel tipo="zoom" forca={1.2} raios>
            <Abs x={390} y={260}><Cruz tam={300} borda={OUT} /></Abs>
            <CarimboIn texto="RESPOSTA HISTÓRICA" y={620} at={4} size={100} />
            <Abs x={0} y={1330} style={{ width: 1080, display: "flex", justifyContent: "center" }}><Etiqueta size={64} cor={PRETO}>O VASCO FICOU FORA DA LIGA EM 1924</Etiqueta></Abs>
          </Papel>
        ),
      },
    ]}
  />
);

/** 8 — "E como diziam que o Vasco não tinha estádio, a torcida construiu um: São Januário, em 1927, o maior da América do Sul na época." */
export const C08SaoJanuario: React.FC = () => {
  const Construindo: React.FC = () => {
    const { s } = useSec();
    return <Obra prog={interpolate(s, [0.1, 2.0], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />;
  };
  return (
    <Shots
      planos={[
        { dur: 1.7, el: <Sala tipo="panDir" sepia opts={{ janela: false }}><Ator p={CARTOLA2} e="desconfiado" plano="close" /><CarimboIn texto="SEM ESTÁDIO?" y={240} at={6} size={120} /></Sala> },
        { dur: 2.3, el: <Sepia forca={0.35}><CameraMove tipo="zoomOut"><Gramado horizonte={1450}><Nuvens /><Construindo /></Gramado></CameraMove></Sepia> },
        {
          dur: 2.6,
          el: (
            <AbsoluteFill>
              <FotoCheia src={FT.saoJanuario} credito="Foto: Marcio Dolzan / Lance!" pos="50% 50%" />
              <Stamp text="1927" sub="SÃO JANUÁRIO" y={240} size={220} at={3} color={CRUZ} />
            </AbsoluteFill>
          ),
        },
        {
          dur: 3.04,
          el: (
            <AbsoluteFill>
              <Estadio3D faixa={FAIXA_COLINA} faixaCor={FAIXA_COR} cores={CORES_3D} trofeu={false} keys={[{ pos: [10, 26, 44], look: [0, 0, -12] }, { pos: [0, 10, 22], look: [0, 9, -46] }]} />
              <Abs x={0} y={1330} style={{ width: 1080, display: "flex", justifyContent: "center" }}><Etiqueta size={66} cor={CRUZ}>MAIOR DA AMÉRICA DO SUL EM 1927</Etiqueta></Abs>
            </AbsoluteFill>
          ),
        },
      ]}
    />
  );
};

/** 9 — "Em 1948, o Expresso da Vitória ganhou o Sul-Americano de Campeões, no Chile: o primeiro campeão continental de clubes." */
export const C09Expresso: React.FC = () => {
  const Passa: React.FC = () => {
    const { s } = useSec();
    const x = interpolate(s, [0, 2.4], [1100, -1600]);
    return <Abs x={x} y={640}><Trem largura={1500} /></Abs>;
  };
  return (
    <Shots
      planos={[
        {
          dur: 2.0,
          el: (
            <Papel tipo="zoom" forca={1}>
              <Stamp text="1948" y={220} size={230} at={2} />
              <Abs x={150} y={600}><Polaroid src={FT.expresso} largura={740} altura={462} legenda="EXPRESSO DA VITÓRIA" credito="Reprodução / Lance!" rot={-2} /></Abs>
            </Papel>
          ),
        },
        {
          dur: 2.4,
          el: (
            <CameraMove tipo="panEsq" forca={0.6}>
              <Gramado horizonte={1060}>
                <Nuvens />
                <div style={{ position: "absolute", left: 0, right: 0, top: 1030, height: 40, background: "repeating-linear-gradient(90deg,#5A341A 0 30px,transparent 30px 70px)" }} />
                <Passa />
                <Abs x={0} y={330} style={{ width: 1080, display: "flex", justifyContent: "center" }}><Etiqueta size={84} cor={PRETO}>EXPRESSO DA VITÓRIA</Etiqueta></Abs>
              </Gramado>
            </CameraMove>
          ),
        },
        {
          dur: 1.8,
          el: (
            <Sala tipo="zoom" forca={1.1} opts={{ cortina: false, janela: false }}>
              <Abs x={140} y={260}><PlacaMadeira largura={800}><div style={{ fontSize: 46 }}>SANTIAGO · CHILE · 1948</div><div style={{ fontSize: 66 }}>SUL-AMERICANO</div><div style={{ fontSize: 66 }}>DE CAMPEÕES</div></PlacaMadeira></Abs>
              <Ator p={fan("#A86F4C")} e="dentes" plano="medio" x={540} y={1060} braco pulo={14} />
            </Sala>
          ),
        },
        {
          dur: 2.36,
          el: (
            <Papel tipo="zoom" forca={1.1} raios>
              <Abs x={290} y={230}><PlacaEscudo src={ES.vasco} tam={500} /></Abs>
              <Abs x={0} y={1330} style={{ width: 1080, display: "flex", justifyContent: "center" }}><Etiqueta size={64} cor={CRUZ}>1º CAMPEÃO CONTINENTAL DE CLUBES</Etiqueta></Abs>
            </Papel>
          ),
        },
      ]}
    />
  );
};

/** 10 — "Depois vieram quatro Brasileiros, com ídolos como Roberto Dinamite, Edmundo e Romário... e a Libertadores de 98, no ano do centenário." */
export const C10Idolos: React.FC = () => {
  const Anos: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <>
        <Abs x={0} y={220} style={{ width: 1080, textAlign: "center", fontFamily: ANTON, fontSize: 420, color: PRETO, lineHeight: 1, scale: `${pop(f, 1, 10)}` }}>4</Abs>
        <Abs x={0} y={680} style={{ width: 1080, textAlign: "center", fontFamily: BEBAS, fontSize: 110, color: PRETO, letterSpacing: 4 }}>BRASILEIROS</Abs>
        <Abs x={40} y={1330} style={{ width: 1000, display: "flex", justifyContent: "center", gap: 18 }}>
          {["1974", "1989", "1997", "2000"].map((a, i) => (
            <div key={a} style={{ scale: `${pop(f, 6 + i * 3, 8)}`, background: i % 2 ? CRUZ : PRETO, color: "#fff", fontFamily: ANTON, fontSize: 70, padding: "6px 22px", border: `5px solid ${OUT}`, rotate: `${i % 2 ? 3 : -3}deg` }}>{a}</div>
          ))}
        </Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.5, el: <Papel tipo="zoom" forca={0.8} raios><Anos /></Papel> },
        {
          dur: 1.4,
          el: (
            <Papel tipo="zoom" forca={1}>
              <Abs x={60} y={260}><Cutout src={FT.dinamite} width={960} startFrame={0} from={{ y: 400, r: -6, s: 0.7 }} /></Abs>
              <Abs x={0} y={1330} style={{ width: 1080, display: "flex", justifyContent: "center" }}><Etiqueta size={76} cor={PRETO}>ROBERTO DINAMITE</Etiqueta></Abs>
              <div style={{ position: "absolute", right: 30, top: 1250, fontFamily: "Inter, Arial", fontSize: 22, color: "#333" }}>Foto: Thiago Ribeiro / AGIF</div>
            </Papel>
          ),
        },
        {
          dur: 1.5,
          el: (
            <Papel tipo="panDir" forca={1}>
              <Abs x={90} y={420}><Cutout src={FT.edmundo} width={900} startFrame={0} from={{ x: 300, r: 8, s: 0.7 }} /></Abs>
              <Abs x={0} y={1330} style={{ width: 1080, display: "flex", justifyContent: "center" }}><Etiqueta size={76} cor={CRUZ}>EDMUNDO · ROMÁRIO</Etiqueta></Abs>
              <div style={{ position: "absolute", right: 30, top: 1250, fontFamily: "Inter, Arial", fontSize: 22, color: "#333" }}>Foto: Lance!Press</div>
            </Papel>
          ),
        },
        {
          dur: 2.0,
          el: (
            <Papel tipo="zoom" forca={0.7} raios>
              <Abs x={60} y={300}>
                <Scoreboard startFrame={3} crestA={ES.vasco} crestB={ES.barcelona} nameA="VASCO" nameB="BARCELONA" a={4} b={1} top="FINAL DA LIBERTADORES" year="1998" bottom="AGREGADO · 2×0 E 2×1" />
              </Abs>
            </Papel>
          ),
        },
        { dur: 2.02, el: <FotoCheia src={FT.lib1998} credito="Foto: Reprodução / Lance!" pos="50% 45%" de={1.12} ate={1.26} /> },
      ]}
    />
  );
};

/** 11 — CTA com a caravela passando no fim (volta ao começo). */
export const C11Cta: React.FC = () => {
  const { s } = useSec();
  const k = interpolate(s, [0.25, 0.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const bx = interpolate(s, [3.2, 5.5], [-800, 1100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Estadio3D faixa={FAIXA_CTA} faixaCor={FAIXA_COR} cores={CORES_3D} trofeu={false} keys={[{ pos: [-30, 24, 70], look: [0, 4, -20] }, { pos: [30, 22, 64], look: [0, 4, -20] }]} />
      <Ator p={NARRADOR} e="sorriso" plano="medio" x={540} y={820} braco />
      <Abs x={0} y={250} style={{ width: 1080, display: "flex", justifyContent: "center", scale: `${k}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, background: "#fff", border: `8px solid ${OUT}`, borderRadius: 999, padding: "16px 38px 16px 18px", boxShadow: "10px 12px 0 rgba(0,0,0,0.35)" }}>
          <div style={{ width: 96, height: 96, borderRadius: "50%", background: PRETO, border: `5px solid ${OUT}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 46, color: "#fff" }}>FE</div>
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 68, color: OUT }}>@futexplicando</div>
          <div style={{ background: CRUZ, color: "#fff", border: `5px solid ${OUT}`, borderRadius: 18, fontFamily: ROUND, fontWeight: 800, fontSize: 48, padding: "4px 22px" }}>SEGUIR</div>
        </div>
      </Abs>
      <Abs x={bx} y={1300}><Caravela largura={560} /></Abs>
    </AbsoluteFill>
  );
};

export const CENAS: Record<string, React.FC> = {
  gancho: C01Gancho,
  fica: C02Fica,
  fundacao: C03Fundacao,
  nome: C04Nome,
  camisas: C05Camisas,
  liga: C06Liga,
  resposta: C07Resposta,
  saojanuario: C08SaoJanuario,
  expresso: C09Expresso,
  idolos: C10Idolos,
  cta: C11Cta,
};
export { D, LOGO };
