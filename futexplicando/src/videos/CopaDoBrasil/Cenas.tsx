import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import raw from "../../data/copa-do-brasil.json";
import { CameraMove, pop, Shots } from "../../cartoon/Base";
import { Arquibancada, Bandeirinha, Carimbo, centroEstado, Escudo, Faixa, Gramado, Jornal, MapaBrasil, Nuvens, PlacaMadeira, ROUND, Trofeu, Zebra } from "../../cartoon/Cenarios";
import { LuzQuente, MesaReuniao, PlacaEscudo, Porta, QuadroTexto, Radio, SalaRica, VaretaPOV } from "../../cartoon/Cenarios2";
import { Estadio3D } from "../../cartoon/Estadio3D";
import { Expressao, Personagem, PersonagemProps } from "../../cartoon/Personagem";

const D = raw;
const ES = raw.escudos as Record<string, string>;
const LOGO = raw.logos as Record<string, string>;
const OUT = "#1A110C";

/* ------------------------------- elenco ------------------------------- */
type P = Partial<PersonagemProps>;
const CARTOLA: P = { oculos: true, cabelo: "lados", corCabelo: "#4A3020", terno: "#4E5560", gravata: "#9B2D20", pele: "#F2C29B" };
const VELHO: P = { bigode: true, cabelo: "grisalho", terno: "#5A5F68", gravata: "#7A4A22", pele: "#F4E6DC" };
const CHAPEU: P = { chapeu: true, oculos: true, bigode: true, terno: "#2E3A5A", gravata: "#6B2A4A", pele: "#F8F2EC" };
const NARRADOR: P = { bigode: true, cabelo: "capacete", corCabelo: "#2B1B10", terno: "#7A7F88", gravata: "#2E8B57", pele: "#E8A877" };
const fan = (cor: string, pele = "#F2C29B", cabelo: PersonagemProps["cabelo"] = "capacete"): P => ({ cachecol: cor, gravata: cor, terno: "#2E2E36", pele, cabelo, corCabelo: "#1E140E" });

/** Personagem posicionado; enquadramentos: "close" (cabeça enche a tela), "medio", "corpo". */
const Ator: React.FC<{ p: P; e: Expressao; plano?: "close" | "medio" | "corpo"; x?: number; y?: number; fase?: number; espelhar?: boolean; braco?: boolean; pulo?: number; alt?: number }> = ({ p, e, plano = "medio", x = 540, y, fase = 0, espelhar, braco, pulo, alt }) => {
  const h = alt ?? (plano === "close" ? 1850 : plano === "medio" ? 1180 : 720);
  const s = h / 520;
  const top = y ?? (plano === "close" ? 700 - 150 * s : plano === "medio" ? 980 - 150 * s : 1720 - h);
  return (
    <div style={{ position: "absolute", left: x - 150 * s, top, filter: "drop-shadow(24px 18px 22px rgba(20,8,0,0.45))" }}>
      <Personagem {...p} altura={h} expressao={e} fase={fase} espelhar={espelhar} bracoErguido={braco} pulo={pulo} />
    </div>
  );
};

const Abs: React.FC<{ x: number; y: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ x, y, children, style }) => (
  <div style={{ position: "absolute", left: x, top: y, ...style }}>{children}</div>
);
const useSec = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { s: f / fps, f, fps };
};

type Lado = { src?: string; selo?: { nome: string; cor1: string; cor2: string } };
const Placar: React.FC<{ a: Lado; b: Lado; ga?: number; gb?: number; titulo: string; k?: number }> = ({ a, b, ga, gb, titulo, k = 1 }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", scale: `${k}` }}>
    <div style={{ background: "#0B6E3A", border: `6px solid ${OUT}`, color: "#FEDD00", fontFamily: ROUND, fontWeight: 800, fontSize: 44, padding: "4px 28px", borderRadius: 14, marginBottom: 12 }}>{titulo}</div>
    <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
      <Escudo {...a} tam={210} />
      <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 150, color: "#FFF4DD", WebkitTextStroke: `12px ${OUT}`, paintOrder: "stroke fill" }}>{ga === undefined ? "×" : `${ga}×${gb}`}</div>
      <Escudo {...b} tam={210} />
    </div>
  </div>
);

const Sala: React.FC<{ children?: React.ReactNode; tipo?: CameraMoveProps["tipo"]; forca?: number; origem?: string; opts?: React.ComponentProps<typeof SalaRica> }> = ({ children, tipo = "zoom", forca = 1, origem, opts }) => (
  <CameraMove tipo={tipo} forca={forca} origem={origem}>
    <SalaRica {...opts}>{children}</SalaRica>
  </CameraMove>
);
type CameraMoveProps = React.ComponentProps<typeof CameraMove>;

/** Sala de reunião com três dirigentes atrás da mesa (como na referência). */
const Reuniao: React.FC<{ es: [Expressao, Expressao, Expressao]; quadro?: string[]; tipo?: CameraMoveProps["tipo"]; forca?: number; quadroEl?: React.ReactNode }> = ({ es, quadro = ["CONFEDERAÇÃO", "BRASILEIRA DE", "FUTEBOL"], tipo = "zoom", forca = 1, quadroEl }) => (
  <Sala tipo={tipo} forca={forca} opts={{ cortina: false, janela: false, tapete: false, quadros: false }}>
    <Abs x={540 - 290} y={280}>{quadroEl ?? <QuadroTexto linhas={quadro} largura={580} />}</Abs>
    <Ator p={VELHO} e={es[0]} plano="medio" x={190} y={760} fase={1} />
    <Ator p={CHAPEU} e={es[2]} plano="medio" x={900} y={790} fase={2} espelhar />
    <Ator p={CARTOLA} e={es[1]} plano="medio" x={545} y={720} fase={0} />
    <MesaReuniao top={1330} />
  </Sala>
);

const Mapa: React.FC<{ alvo: string[]; ritmo?: number; destaque?: string[]; antigo?: boolean; bandeiras?: string[]; corDest?: string; zoom?: number }> = ({ alvo, ritmo = 8, destaque = [], antigo = true, bandeiras = [], corDest = "#C0392B", zoom = 1.25 }) => {
  const f = useCurrentFrame();
  const i = Math.min(alvo.length - 1, Math.floor(f / ritmo));
  const W = 1100;
  const c = centroEstado(alvo[i]);
  const ox = -10;
  const oy = 300;
  return (
    <AbsoluteFill style={{ background: "#5A6E62" }}>
      <AbsoluteFill style={{ background: "repeating-linear-gradient(0deg, rgba(255,255,255,0.06) 0 2px, transparent 2px 80px), repeating-linear-gradient(90deg, rgba(255,255,255,0.06) 0 2px, transparent 2px 80px)" }} />
      <AbsoluteFill style={{ scale: `${zoom}`, transformOrigin: `${((ox + (c.x * W) / 1000) / 1080) * 100}% ${((oy + (c.y * W) / 1000) / 1920) * 100}%` }}>
        <Abs x={ox} y={oy}>
          <MapaBrasil largura={W} antigo={antigo} destaque={destaque} corDestaque={corDest} piscar={destaque.length > 0}>
            {bandeiras.map((sg, j) => {
              const cc = centroEstado(sg);
              return <Bandeirinha key={sg} x={cc.x} y={cc.y} largura={W} cor={["#C0392B", "#2E86C1", "#1E8449", "#B7950B", "#7D3C98"][j % 5]} k={pop(f, j * 2.2, 6)} />;
            })}
          </MapaBrasil>
        </Abs>
        <VaretaPOV x={ox + (c.x * W) / 1000} y={oy + (c.y * W) / 1000} />
      </AbsoluteFill>
      <LuzQuente forca={0.6} />
    </AbsoluteFill>
  );
};

const SIGLAS = ["AC", "AM", "RR", "AP", "PA", "RO", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA", "MT", "MS", "GO", "DF", "MG", "ES", "RJ", "SP", "PR", "SC", "RS"];
const NORTE_NE = ["AC", "AM", "RR", "AP", "PA", "RO", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "MT", "MS"];

/* -------------------------------- CENAS -------------------------------- */

/** Torcida 2D em close (mini-personagens grandes) com faixa. */
const TorcidaClose: React.FC<{ faixa?: React.ReactNode; cores: string[]; tam?: number }> = ({ faixa, cores, tam = 150 }) => (
  <Gramado horizonte={1500}>
    <Arquibancada cores={cores} linhas={8} tam={tam} top={-60} faixa={faixa} />
  </Gramado>
);

/** 1 — Gancho: torcida → close nos torcedores → sobrevoo 3D até o estádio inteiro. */
export const C01Gancho: React.FC = () => (
  <Shots
    planos={[
      { dur: 0.9, el: <CameraMove tipo="zoom" forca={1.4}><TorcidaClose cores={["#0B6E3A", "#FFFFFF", "#FEDD00", "#1E88E5"]} tam={120} faixa={<Faixa texto="COPA DO BRASIL" largura={860} cor="#0B6E3A" corTexto="#FEDD00" />} /></CameraMove> },
      {
        dur: 1.1,
        el: (
          <CameraMove tipo="panDir" forca={1.2}>
            <TorcidaClose cores={["#C62828", "#1E3A8A", "#111111", "#FFFFFF"]} tam={170} />
            <Ator p={fan("#C62828", "#F8F2EC", "careca")} e="dentes" plano="medio" x={170} y={820} fase={1} braco />
            <Ator p={fan("#1E88E5", "#A86F4C")} e="sorriso" plano="medio" x={900} y={860} fase={2} espelhar />
            <Ator p={fan("#111111", "#F2C29B")} e="espanto" plano="medio" x={540} y={740} fase={0} pulo={20} />
          </CameraMove>
        ),
      },
      {
        dur: 3.06,
        el: (
          <Estadio3D
            faixa={["R$ 78 MILHÕES", "PRO CAMPEÃO DA COPA DO BRASIL"]}
            trofeu={false}
            keys={[
              { pos: [0, 6, -28], look: [0, 5, -46] },
              { pos: [26, 16, -6], look: [0, 4, -36] },
              { pos: [10, 26, 40], look: [0, 0, -12] },
              { pos: [0, 34, 74], look: [0, 0, -6] },
            ]}
          />
        ),
      },
    ]}
  />
);

/** 2 — Ameaça de punição. */
export const C02Ameaca: React.FC = () => (
  <Shots
    planos={[
      { dur: 1.1, el: <Sala tipo="zoom" forca={1.5} opts={{ cortina: false, janela: false, quadros: false, tapete: false }}><Abs x={260} y={260}><Porta placa="CBF" /></Abs></Sala> },
      { dur: 1.2, el: <Reuniao es={["desconfiado", "dentes", "espanto"]} /> },
      {
        dur: 1.4,
        el: (
          <Sala tipo="zoom" forca={0.8} opts={{ cortina: false }}>
            <Ator p={CARTOLA} e="dentes" plano="close" />
            <CarimboIn texto="PUNIDO!" y={230} />
          </Sala>
        ),
      },
      { dur: 1.3, el: <Sala tipo="panEsq" opts={{ janela: false }}><Ator p={CHAPEU} e="espanto" plano="close" x={520} /></Sala> },
    ]}
  />
);

const CarimboIn: React.FC<{ texto: string; y: number }> = ({ texto, y }) => {
  const f = useCurrentFrame();
  return (
    <Abs x={0} y={y} style={{ width: 1080, textAlign: "center" }}>
      <Carimbo texto={texto} k={pop(f, 5, 8)} size={130} rot={-7} />
    </Abs>
  );
};

/** 3 — "Fica até o final que eu explico." */
export const C03Fica: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 1,
        el: (
          <Sala tipo="zoom" forca={1.2}>
            <Abs x={-30} y={760}><Radio largura={430} /></Abs>
            <Ator p={NARRADOR} e="sorriso" plano="medio" x={680} y={720} />
          </Sala>
        ),
      },
      {
        dur: 0.94,
        el: (
          <CameraMove tipo="zoom" forca={1.8}>
            <AbsoluteFill style={{ background: "#2A1408" }}>
              <Abs x={-90} y={300}><Radio largura={1260}><Img src={staticFile(LOGO.copaDoBrasil)} style={{ height: 300, objectFit: "contain", filter: "drop-shadow(0 0 20px #fff)" }} /></Radio></Abs>
              <LuzQuente />
            </AbsoluteFill>
          </CameraMove>
        ),
      },
    ]}
  />
);

/** 4 — "Tudo começou em 1989." */
export const C04Comecou: React.FC = () => {
  const Spin: React.FC = () => {
    const f = useCurrentFrame();
    const r = interpolate(f, [0, 14], [720, -4], { extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
    const sc = interpolate(f, [0, 14], [0.2, 1.15], { extrapolateRight: "clamp" });
    return (
      <Abs x={100} y={330} style={{ rotate: `${r}deg`, scale: `${sc}` }}>
        <Jornal manchete="1989" sub="CBF anuncia um novo torneio nacional" largura={880} />
      </Abs>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.3, el: <Sala tipo="zoom" opts={{ cortina: false, quadros: false }}><Spin /></Sala> },
        {
          dur: 1.48,
          el: (
            <Sala tipo="panDir">
              <Abs x={110} y={320}><Radio largura={300} /></Abs>
              <Ator p={VELHO} e="espanto" plano="medio" x={600} y={700} />
            </Sala>
          ),
        },
      ]}
    />
  );
};

/** 5 — Ricardo Teixeira assume a CBF. */
export const C05Teixeira: React.FC = () => (
  <Shots
    planos={[
      { dur: 1.4, el: <Reuniao es={["sorriso", "sorriso", "desconfiado"]} quadroEl={<QuadroTexto linhas={["PRESIDENTE", "DA CBF · 1989"]} largura={580} />} tipo="zoom" forca={1.3} /> },
      {
        dur: 1.62,
        el: (
          <Sala tipo="zoom" forca={0.9} opts={{ janela: false }}>
            <Ator p={CARTOLA} e="sorriso" plano="close" />
            <Abs x={140} y={1300}>
              <PlacaMadeira largura={800}>
                <div style={{ fontSize: 40 }}>PRESIDENTE DA CBF · JAN/1989</div>
                <div style={{ fontSize: 74 }}>RICARDO TEIXEIRA</div>
              </PlacaMadeira>
            </Abs>
          </Sala>
        ),
      },
    ]}
  />
);

/** 6 — Estados menores bravos. */
export const C06Estados: React.FC = () => (
  <Shots
    planos={[
      { dur: 1.7, el: <Mapa alvo={["AM", "PA", "MA", "PI", "RN", "AL"]} destaque={NORTE_NE} ritmo={9} /> },
      { dur: 1.6, el: <Reuniao es={["dentes", "desconfiado", "dentes"]} quadro={["E A GENTE?", "FORA DA ELITE", "DO BRASILEIRÃO"]} tipo="panEsq" /> },
      { dur: 1.58, el: <Sala tipo="zoom" opts={{ cortina: false }}><Ator p={VELHO} e="dentes" plano="close" x={560} /></Sala> },
    ]}
  />
);

/** 7 — Mata-mata com campeões de todos os estados. */
export const C07MataMata: React.FC = () => (
  <Shots
    planos={[
      { dur: 2, el: <Mapa alvo={SIGLAS} ritmo={2.2} bandeiras={SIGLAS} zoom={1.05} /> },
      {
        dur: 1.64,
        el: (
          <Sala tipo="zoom" forca={1.2} opts={{ janela: false, cortina: false }}>
            <Abs x={240} y={260}><QuadroTexto linhas={["MATA-MATA", "CAMPEÕES DE", "TODOS OS ESTADOS"]} largura={600} /></Abs>
            <Ator p={CARTOLA} e="dentes" plano="medio" x={540} y={820} braco />
          </Sala>
        ),
      },
    ]}
  />
);

/** 8 — 32 times, 46 dias, vaga na Libertadores. */
export const C08Numeros: React.FC = () => {
  const Contador: React.FC<{ alvo: number; rotulo: string }> = ({ alvo, rotulo }) => {
    const f = useCurrentFrame();
    const n = Math.round(interpolate(f, [2, 20], [0, alvo], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
    return (
      <Abs x={140} y={250}>
        <QuadroTexto linhas={[]} largura={800}>
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 300, lineHeight: 1, color: "#F0B23C" }}>{n}</div>
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 80, color: "#F0B23C" }}>{rotulo}</div>
        </QuadroTexto>
      </Abs>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.4, el: <Sala tipo="zoom" opts={{ janela: false, cortina: false, quadros: false }}><Contador alvo={32} rotulo="TIMES" /><Ator p={CHAPEU} e="espanto" plano="medio" x={540} y={1050} /></Sala> },
        { dur: 1.4, el: <Sala tipo="panDir" opts={{ janela: false, cortina: false, quadros: false }}><Contador alvo={46} rotulo="DIAS" /><Ator p={VELHO} e="desconfiado" plano="medio" x={540} y={1050} /></Sala> },
        {
          dur: 1.5,
          el: (
            <Sala tipo="zoom" forca={1.3} opts={{ janela: false, cortina: false, quadros: false }}>
              <Abs x={190} y={260}>
                <div style={{ width: 700, background: "#F4E9D0", border: `20px solid #8A5A30`, outline: `5px solid ${OUT}`, padding: 30, display: "flex", flexDirection: "column", alignItems: "center", boxShadow: "14px 16px 22px rgba(0,0,0,0.45)" }}>
                  <Img src={staticFile(LOGO.libertadores)} style={{ height: 360, objectFit: "contain" }} />
                  <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 62, color: OUT }}>VAGA PRO CAMPEÃO</div>
                </div>
              </Abs>
            </Sala>
          ),
        },
        { dur: 1.56, el: <Sala tipo="zoom" opts={{ cortina: false }}><Ator p={CARTOLA} e="espanto" plano="close" /></Sala> },
      ]}
    />
  );
};

/** 9 — Primeiro campeão: Grêmio x Sport. */
export const C09Primeiro: React.FC = () => {
  const P1: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <Abs x={30} y={380} style={{ width: 1020, display: "flex", justifyContent: "center" }}>
        <Placar a={{ src: ES.gremio }} b={{ src: ES.sport }} ga={2} gb={1} titulo="FINAL 1989 · VOLTA" k={pop(f, 3, 10)} />
      </Abs>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.3, el: <Sala tipo="zoom" opts={{ janela: false, cortina: false, quadros: false }}><P1 /><Ator p={VELHO} e="espanto" plano="medio" x={540} y={1100} /></Sala> },
        { dur: 1.2, el: <Sala tipo="zoom" forca={1.4} opts={{ cortina: false }}><Abs x={270} y={330}><PlacaEscudo src={ES.gremio} tam={540} /></Abs></Sala> },
        { dur: 1.32, el: <Sala tipo="panDir" opts={{ janela: false }}><Ator p={fan("#1E88E5")} e="dentes" plano="close" pulo={12} /></Sala> },
      ]}
    />
  );
};

/** 10 — A chance dos pequenos. */
export const C10Pequenos: React.FC = () => (
  <Shots
    planos={[
      { dur: 1.3, el: <Mapa alvo={["AC", "RR", "AP", "PI", "SE", "AL"]} destaque={["AC", "RR", "AP", "PI", "SE", "AL"]} corDest="#F4D03F" bandeiras={SIGLAS} ritmo={6} /> },
      { dur: 1.3, el: <Sala tipo="zoom" opts={{ cortina: false }}><Ator p={fan("#F4D03F", "#A86F4C", "topete")} e="sorriso" plano="close" pulo={10} /></Sala> },
    ]}
  />
);

/** 11 — Criciúma 1991. */
export const C11Criciuma: React.FC = () => {
  const P1: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <Abs x={30} y={330} style={{ width: 1020, display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
        <Placar a={{ src: ES.criciuma }} b={{ src: ES.gremio }} ga={0} gb={0} titulo="FINAL 1991" k={pop(f, 3, 10)} />
        <PlacaMadeira largura={700}><div style={{ fontSize: 52 }}>CAMPEÃO NO GOL FORA</div></PlacaMadeira>
      </Abs>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.2, el: <Sala tipo="zoom" opts={{ janela: false, cortina: false, quadros: false }}><P1 /></Sala> },
        { dur: 1.2, el: <Sala tipo="zoom" forca={1.2}><Ator p={fan("#F4D03F", "#F2C29B", "careca")} e="dentes" plano="close" pulo={16} /></Sala> },
        { dur: 1.14, el: <Sala tipo="panEsq" opts={{ janela: false }}><Ator p={fan("#1E88E5", "#F8F2EC")} e="triste" plano="close" /></Sala> },
      ]}
    />
  );
};

/* -------------------------------- PRESENTE -------------------------------- */

const Estadio2D: React.FC<{ cores: string[]; faixa?: React.ReactNode; silencio?: boolean; children?: React.ReactNode; tam?: number }> = ({ cores, faixa, silencio, children, tam = 80 }) => (
  <Gramado horizonte={1060}>
    <Nuvens />
    <Arquibancada cores={cores} linhas={6} tam={tam} top={300} faixa={faixa} />
    {silencio ? <AbsoluteFill style={{ background: "rgba(20,30,60,0.28)" }} /> : null}
    {children}
  </Gramado>
);
const SANTO_ANDRE = { nome: "SANTO ANDRÉ", cor1: "#1D4E9E", cor2: "#FFFFFF" };
const PAULISTA = { nome: "PAULISTA", cor1: "#C62828", cor2: "#FFFFFF" };

/** 12 — Santo André cala o Maracanã (2004). */
export const C12SantoAndre: React.FC = () => {
  const P1: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <Abs x={30} y={1270} style={{ width: 1020, display: "flex", justifyContent: "center" }}>
        <Placar a={{ selo: SANTO_ANDRE }} b={{ src: ES.flamengo }} ga={2} gb={0} titulo="FINAL 2004 · MARACANÃ" k={pop(f, 3, 10)} />
      </Abs>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.4, el: <CameraMove tipo="zoom"><Estadio2D cores={["#C62828", "#111111"]} silencio><P1 /></Estadio2D></CameraMove> },
        { dur: 1.4, el: <CameraMove tipo="zoom" forca={1.3}><Estadio2D cores={["#C62828", "#111111"]} silencio><Ator p={fan("#C62828", "#A86F4C")} e="espanto" plano="close" /></Estadio2D></CameraMove> },
        { dur: 1.4, el: <CameraMove tipo="panDir"><TorcidaClose cores={["#C62828", "#111111"]} tam={170} /><AbsoluteFill style={{ background: "rgba(20,30,60,0.3)" }} /><Ator p={fan("#111111", "#F8F2EC")} e="triste" plano="medio" x={540} y={760} /></CameraMove> },
      ]}
    />
  );
};

/** 13 — Paulista bate o Fluminense (2005). */
export const C13Paulista: React.FC = () => (
  <Shots
    planos={[
      { dur: 1.4, el: <CameraMove tipo="panEsq"><TorcidaClose cores={["#C62828", "#FFFFFF", "#111111"]} tam={150} faixa={<Faixa texto="PAULISTA CAMPEÃO 2005" cor="#C62828" corTexto="#fff" largura={920} />} /></CameraMove> },
      { dur: 1.4, el: <CameraMove tipo="zoom"><Estadio2D cores={["#C62828", "#FFFFFF"]}><Abs x={30} y={1270} style={{ width: 1020, display: "flex", justifyContent: "center" }}><Placar a={{ selo: PAULISTA }} b={{ src: ES.fluminense }} titulo="FINAL 2005 · CAMPEÃO: PAULISTA" /></Abs></Estadio2D></CameraMove> },
      { dur: 1.46, el: <CameraMove tipo="zoom" forca={1.2}><Estadio2D cores={["#7B1E3A", "#1E7B4A", "#FFFFFF"]}><Ator p={fan("#7B1E3A", "#F2C29B", "topete")} e="desconfiado" plano="close" /></Estadio2D></CameraMove> },
    ]}
  />
);

const GRANDES = ["flamengo", "palmeiras", "corinthians", "cruzeiro", "gremio", "saoPaulo"];

/** 14 — Até 2012, quem jogava a Libertadores não participava. */
export const C14SemLibertadores: React.FC = () => {
  const Portao: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <>
        <Abs x={90} y={220}>
          <div style={{ width: 900, height: 820, background: "repeating-linear-gradient(90deg,#4E5B6B 0 26px, transparent 26px 100px)", border: `12px solid ${OUT}`, borderRadius: "50px 50px 0 0", position: "relative" }}>
            <div style={{ position: "absolute", left: 90, right: 90, top: 250, background: "#B3261E", border: `7px solid ${OUT}`, borderRadius: 18, color: "#fff", fontFamily: ROUND, fontWeight: 800, fontSize: 64, textAlign: "center", padding: 16, rotate: "-3deg" }}>
              QUEM JOGA A LIBERTADORES<br />NÃO ENTRA!
            </div>
          </div>
        </Abs>
        <Abs x={40} y={1090} style={{ display: "flex", gap: 14, flexWrap: "wrap", width: 1000, justifyContent: "center" }}>
          {GRANDES.map((g, i) => (
            <div key={g} style={{ scale: `${pop(f, 3 + i * 2, 8)}` }}>
              <Escudo src={ES[g]} tam={150} />
            </div>
          ))}
        </Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.3, el: <CameraMove tipo="zoom"><Gramado horizonte={1040}><Nuvens /><Portao /></Gramado></CameraMove> },
        { dur: 1.2, el: <CameraMove tipo="panDir"><Gramado horizonte={1040}><Nuvens /><Abs x={170} y={300}><PlacaMadeira largura={740}><div style={{ fontSize: 76 }}>2001 → 2012</div><div style={{ fontSize: 46 }}>SÓ 64 TIMES, SEM OS DA LIBERTA</div></PlacaMadeira></Abs><Ator p={fan("#C62828")} e="desconfiado" plano="medio" x={540} y={760} /></Gramado></CameraMove> },
        { dur: 1.24, el: <CameraMove tipo="zoom"><Gramado horizonte={1040}><Nuvens /><Ator p={fan("#43A047", "#F8F2EC", "careca")} e="desconfiado" plano="close" /></Gramado></CameraMove> },
      ]}
    />
  );
};

/** 15 — 2013: grandes nas oitavas, zebras somem. */
export const C15Oitavas: React.FC = () => {
  const Chave: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <Abs x={60} y={240}>
        <PlacaMadeira largura={960} style={{ background: "linear-gradient(180deg,#0B6E3A,#075029)" }}>
          <div style={{ fontSize: 76 }}>OITAVAS · 2013</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, marginTop: 18, justifyItems: "center" }}>
            {GRANDES.map((g, i) => (
              <div key={g} style={{ scale: `${pop(f, 2 + i * 2.5, 8)}` }}>
                <Escudo src={ES[g]} tam={190} />
              </div>
            ))}
          </div>
        </PlacaMadeira>
      </Abs>
    );
  };
  const Puf: React.FC = () => {
    const f = useCurrentFrame();
    const sumiu = interpolate(f, [16, 24], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const nuvem = interpolate(f, [16, 22, 40], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <>
        <Abs x={190} y={300} style={{ scale: `${sumiu}`, opacity: sumiu }}><Zebra tam={700} /></Abs>
        <Abs x={140} y={260} style={{ opacity: nuvem, scale: `${0.6 + nuvem * 0.7}` }}>
          <svg width="800" height="700" viewBox="0 0 600 500">
            {[[300, 250, 140], [180, 220, 90], [420, 220, 100], [240, 340, 90], [380, 340, 90]].map(([x, y, r], i) => (
              <circle key={i} cx={x} cy={y} r={r} fill="#fff" stroke={OUT} strokeWidth="6" />
            ))}
          </svg>
        </Abs>
        <Abs x={0} y={500} style={{ width: 1080, textAlign: "center", opacity: nuvem, fontFamily: ROUND, fontWeight: 800, fontSize: 170, color: OUT }}>PUF!</Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.5, el: <CameraMove tipo="zoom"><Gramado horizonte={1180}><Nuvens /><Chave /></Gramado></CameraMove> },
        { dur: 1.6, el: <CameraMove tipo="zoom" forca={1.2}><Gramado horizonte={1180}><Nuvens /><Puf /></Gramado></CameraMove> },
        { dur: 1.2, el: <CameraMove tipo="zoom"><Gramado horizonte={1180}><Nuvens /><Ator p={fan("#FFFFFF", "#7A4B30", "capacete")} e="espanto" plano="close" /></Gramado></CameraMove> },
        { dur: 1.42, el: <CameraMove tipo="panEsq"><TorcidaClose cores={["#1E88E5", "#C62828", "#111111", "#43A047"]} tam={150} faixa={<Faixa texto="SÓ DÁ GIGANTE" largura={800} />} /></CameraMove> },
      ]}
    />
  );
};

/** 16 — Maiores campeões. */
export const C16Maiores: React.FC = () => {
  const Podio: React.FC = () => {
    const f = useCurrentFrame();
    const col = (src: string, n: number, h: number, x: number, d: number) => (
      <div style={{ position: "absolute", left: x, bottom: 0, width: 320, display: "flex", flexDirection: "column", alignItems: "center", scale: `${pop(f, d, 10)}`, transformOrigin: "50% 100%" }}>
        <Escudo src={src} tam={230} />
        <div style={{ width: 300, height: h, marginTop: 16, background: "linear-gradient(180deg,#F4D03F,#B7950B)", border: `7px solid ${OUT}`, borderRadius: 14, display: "flex", alignItems: "flex-start", justifyContent: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 140, color: OUT }}>{n}</div>
      </div>
    );
    return (
      <Abs x={20} y={200} style={{ width: 1040, height: 900 }}>
        {col(ES.gremio, 5, 330, 0, 8)}
        {col(ES.cruzeiro, 6, 470, 360, 2)}
        {col(ES.flamengo, 5, 330, 720, 14)}
      </Abs>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.8, el: <CameraMove tipo="zoom"><Gramado horizonte={1100}><Nuvens /><Podio /></Gramado></CameraMove> },
        { dur: 1.2, el: <CameraMove tipo="zoom" forca={1.5}><Gramado horizonte={1100}><Nuvens /><Abs x={240} y={260}><PlacaEscudo src={ES.cruzeiro} tam={600} /></Abs></Gramado></CameraMove> },
        { dur: 1.2, el: <CameraMove tipo="zoom"><Estadio2D cores={["#1E3A8A", "#FFFFFF"]}><Ator p={fan("#1E3A8A", "#F2C29B")} e="dentes" plano="close" pulo={14} /></Estadio2D></CameraMove> },
        { dur: 1.22, el: <CameraMove tipo="panDir"><TorcidaClose cores={["#1E88E5", "#C62828", "#111111"]} tam={150} faixa={<Faixa texto="GRÊMIO 5 · FLAMENGO 5" largura={920} />} /></CameraMove> },
      ]}
    />
  );
};

/** 17 — Hoje: 126 clubes e final única em Brasília (troféu inteiro em quadro). */
export const C17Hoje: React.FC = () => {
  const Pontos: React.FC = () => {
    const f = useCurrentFrame();
    const W = 1000;
    const n = Math.min(126, Math.floor(interpolate(f, [2, 46], [0, 126], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })));
    const pts = Array.from({ length: 126 }).map((_, i) => {
      const c = centroEstado(SIGLAS[i % SIGLAS.length]);
      const a = i * 2.39996;
      const r = 8 + ((i * 37) % 40);
      return { x: c.x + Math.cos(a) * r, y: c.y + Math.sin(a) * r };
    });
    return (
      <Abs x={40} y={330}>
        <MapaBrasil largura={W} antigo={false}>
          <svg width={W} height={W} viewBox="0 0 1000 1000" style={{ position: "absolute", inset: 0 }}>
            {pts.slice(0, n).map((p, i) => (
              <circle key={i} cx={p.x} cy={p.y} r={10} fill="#FEDD00" stroke={OUT} strokeWidth="3" />
            ))}
          </svg>
        </MapaBrasil>
        <Abs x={0} y={-150} style={{ width: W, textAlign: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 110, color: "#fff", WebkitTextStroke: `10px ${OUT}`, paintOrder: "stroke fill" }}>{n} CLUBES</Abs>
      </Abs>
    );
  };
  const TrofeuBrasilia: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <>
        <Abs x={540 - 248} y={230} style={{ scale: `${pop(f, 3, 12)}` }}>
          <Trofeu altura={800} brilho={1.3} />
        </Abs>
        <Abs x={140} y={1180}>
          <PlacaMadeira largura={800} style={{ background: "linear-gradient(180deg,#0B6E3A,#075029)" }}>
            <div style={{ fontSize: 50 }}>FINAL 2026 · JOGO ÚNICO</div>
            <div style={{ fontSize: 76 }}>BRASÍLIA · 06/12</div>
          </PlacaMadeira>
        </Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 2.2, el: <CameraMove tipo="zoom"><Gramado horizonte={1600}><Nuvens /><Pontos /></Gramado></CameraMove> },
        { dur: 2.0, el: <CameraMove tipo="zoom" forca={0.6}><Gramado horizonte={1150}><Nuvens /><TrofeuBrasilia /></Gramado></CameraMove> },
        { dur: 1.9, el: <CameraMove tipo="panEsq"><TorcidaClose cores={["#0B6E3A", "#FEDD00", "#1E88E5", "#FFFFFF"]} tam={150} faixa={<Faixa texto="126 CLUBES · 2026" largura={820} cor="#0B6E3A" corTexto="#FEDD00" />} /></CameraMove> },
      ]}
    />
  );
};

/** 18 — Frase de impacto: carimbo vira troféu; depois o troféu 3D girando, inteiro no quadro. */
export const C18Impacto: React.FC = () => {
  const Vira: React.FC = () => {
    const { s } = useSec();
    const flip = interpolate(s, [0.5, 0.9], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <>
        <Abs x={0} y={420} style={{ width: 1080, textAlign: "center", opacity: 1 - flip, scale: `${1 - flip * 0.6}` }}>
          <Carimbo texto="PUNIDO!" k={1} size={150} />
        </Abs>
        <Abs x={540 - 248} y={230} style={{ opacity: flip, scale: `${0.4 + flip * 0.6}` }}>
          <Trofeu altura={800} brilho={1.4} />
        </Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.5, el: <Sala tipo="zoom" forca={0.6} opts={{ cortina: false, janela: false, quadros: false }}><Vira /></Sala> },
        {
          dur: 2.38,
          el: (
            <AbsoluteFill>
              <Estadio3D faixa={["A TAÇA QUE VALE", "UMA FORTUNA"]} trofeuFoco keys={[{ pos: [0, 8, 36], look: [0, 7.5, 0] }, { pos: [13, 9, 33], look: [0, 7.5, 0] }]} />
              <Confete />
            </AbsoluteFill>
          ),
        },
      ]}
    />
  );
};

const Confete: React.FC = () => {
  const { s } = useSec();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: 46 }).map((_, i) => {
        const x = (i * 97) % 1080;
        const y = s * (380 + (i % 7) * 70) + ((i * 53) % 500) - 520;
        return <div key={i} style={{ position: "absolute", left: x + Math.sin(s * 3 + i) * 30, top: y, width: 26, height: 14, background: ["#FEDD00", "#0B6E3A", "#1E88E5", "#fff"][i % 4], border: `2px solid ${OUT}`, rotate: `${s * 300 + i * 40}deg` }} />;
      })}
    </AbsoluteFill>
  );
};

/** 19 — CTA. */
export const C19Cta: React.FC = () => {
  const { s } = useSec();
  const k = interpolate(s, [0.25, 0.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Estadio3D faixa={["SEGUE O", "@FUTEXPLICANDO"]} trofeu={false} keys={[{ pos: [-30, 24, 70], look: [0, 4, -20] }, { pos: [30, 22, 64], look: [0, 4, -20] }]} />
      <Ator p={NARRADOR} e="sorriso" plano="medio" x={540} y={820} braco />
      <Abs x={0} y={250} style={{ width: 1080, display: "flex", justifyContent: "center", scale: `${k}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, background: "#fff", border: `8px solid ${OUT}`, borderRadius: 999, padding: "16px 38px 16px 18px", boxShadow: "10px 12px 0 rgba(0,0,0,0.35)" }}>
          <div style={{ width: 96, height: 96, borderRadius: "50%", background: "#0B6E3A", border: `5px solid ${OUT}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 46, color: "#FEDD00" }}>FE</div>
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 68, color: OUT }}>@futexplicando</div>
          <div style={{ background: "#E53935", color: "#fff", border: `5px solid ${OUT}`, borderRadius: 18, fontFamily: ROUND, fontWeight: 800, fontSize: 48, padding: "4px 22px" }}>SEGUIR</div>
        </div>
      </Abs>
    </AbsoluteFill>
  );
};

export const CENAS: Record<string, React.FC> = {
  gancho: C01Gancho,
  ameaca: C02Ameaca,
  fica: C03Fica,
  comecou: C04Comecou,
  teixeira: C05Teixeira,
  estados: C06Estados,
  matamata: C07MataMata,
  numeros: C08Numeros,
  primeiro: C09Primeiro,
  pequenos: C10Pequenos,
  criciuma: C11Criciuma,
  santoandre: C12SantoAndre,
  paulista: C13Paulista,
  semlibertadores: C14SemLibertadores,
  oitavas: C15Oitavas,
  maiores: C16Maiores,
  hoje: C17Hoje,
  impacto: C18Impacto,
  cta: C19Cta,
};
export { D };
