import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import raw from "../../data/flamengo.json";
import { CameraMove, pop, Shots } from "../../cartoon/Base";
import { Arquibancada, Carimbo, Faixa, Gramado, Jornal, Nuvens, PlacaMadeira, ROUND, Sepia } from "../../cartoon/Cenarios";
import { LuzQuente, MesaReuniao, PlacaEscudo, Porta, QuadroTexto, Radio, SalaRica } from "../../cartoon/Cenarios2";
import { Estadio3D } from "../../cartoon/Estadio3D";
import { Cutout, Scoreboard, StatSlam, YearStamp, Rays } from "../../components/Graphics";
import { PaperBackground } from "../../components/Paper";
import { ANTON, BEBAS } from "../../theme";
import {
  Abs,
  Ator,
  Barco,
  Bola,
  DIRIGENTE,
  Etiqueta,
  fan,
  FotoCheia,
  LADRAO,
  Mar,
  NARRADOR,
  NEGRO,
  OUT,
  Polaroid,
  REMADOR,
  REMADOR2,
  RUBRO,
  TRICOLOR,
  useSec,
} from "./Elementos";

const D = raw;
const ES = raw.escudos as Record<string, string>;
const FT = raw.fotos as Record<string, string>;
const LOGO = raw.logos as Record<string, string>;

const CORES_FLA = [RUBRO, NEGRO, RUBRO, NEGRO, "#FFFFFF"];
const CORES_FLA_3D = ["#C8102E", "#111111", "#C8102E", "#111111", "#C8102E", "#FFFFFF"];
const FAIXA_COR: [string, string] = ["#B00E26", "#FFFFFF"];
const FAIXA_GANCHO = ["MAIOR TORCIDA", "DO BRASIL"];
const FAIXA_NACAO = ["NAÇÃO", "RUBRO-NEGRA"];
const FAIXA_CTA = ["SEGUE O", "@FUTEXPLICANDO"];

type CamTipo = React.ComponentProps<typeof CameraMove>["tipo"];

const Sala: React.FC<{ children?: React.ReactNode; tipo?: CamTipo; forca?: number; opts?: React.ComponentProps<typeof SalaRica>; sepia?: boolean }> = ({ children, tipo = "zoom", forca = 1, opts, sepia }) => {
  const el = (
    <CameraMove tipo={tipo} forca={forca}>
      <SalaRica {...opts}>{children}</SalaRica>
    </CameraMove>
  );
  return sepia ? <Sepia forca={0.6}>{el}</Sepia> : el;
};

/** Fundo de papel (estilo 1) com câmera em movimento. */
const Papel: React.FC<{ children?: React.ReactNode; tipo?: CamTipo; forca?: number; cor?: string; raios?: boolean }> = ({ children, tipo = "zoom", forca = 1, cor, raios }) => (
  <CameraMove tipo={tipo} forca={forca}>
    <PaperBackground color={cor} tint="rgba(200,16,46,0.22)" />
    {raios ? <Rays color={RUBRO} opacity={0.18} /> : null}
    {children}
  </CameraMove>
);

const TorcidaClose: React.FC<{ faixa?: React.ReactNode; tam?: number }> = ({ faixa, tam = 150 }) => (
  <Gramado horizonte={1500}>
    <Arquibancada cores={CORES_FLA} linhas={8} tam={tam} top={-60} faixa={faixa} />
  </Gramado>
);

const CarimboIn: React.FC<{ texto: string; y: number; at?: number; cor?: string; size?: number }> = ({ texto, y, at = 5, cor, size = 130 }) => {
  const f = useCurrentFrame();
  return (
    <Abs x={0} y={y} style={{ width: 1080, textAlign: "center" }}>
      <Carimbo texto={texto} k={pop(f, at, 8)} size={size} rot={-7} cor={cor} />
    </Abs>
  );
};

const Stamp: React.FC<{ text: string; sub?: string; y: number; at?: number; size?: number; color?: string }> = ({ text, sub, y, at = 4, size = 230, color = RUBRO }) => (
  <Abs x={0} y={y} style={{ width: 1080, display: "flex", justifyContent: "center" }}>
    <YearStamp text={text} sub={sub} startFrame={at} size={size} color={color} />
  </Abs>
);

/* ================================ CENAS ================================ */

/** 1 — "O time com a maior torcida do Brasil nasceu sem bola. Nasceu num barco!" */
export const C01Gancho: React.FC = () => {
  const SemBola: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <>
        <Abs x={390} y={380} style={{ scale: `${pop(f, 0, 8)}`, rotate: `${f * 3}deg` }}>
          <Bola tam={300} />
        </Abs>
        <Abs x={300} y={300} style={{ scale: `${pop(f, 8, 6)}` }}>
          <svg width="480" height="480" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="44" fill="none" stroke={RUBRO} strokeWidth="9" />
            <line x1="20" y1="20" x2="80" y2="80" stroke={RUBRO} strokeWidth="9" />
          </svg>
        </Abs>
        <CarimboIn texto="SEM BOLA" y={860} at={10} cor={RUBRO} size={120} />
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.0, el: <CameraMove tipo="zoom" forca={1.4}><TorcidaClose tam={120} faixa={<Faixa texto="MAIOR TORCIDA DO BRASIL" largura={940} cor={RUBRO} corTexto="#fff" escudo={ES.flamengo} />} /></CameraMove> },
        {
          dur: 1.0,
          el: (
            <CameraMove tipo="panDir" forca={1.2}>
              <TorcidaClose tam={170} />
              <Ator p={fan("#F8F2EC", "careca")} e="dentes" plano="medio" x={170} y={820} fase={1} braco />
              <Ator p={fan("#A86F4C")} e="sorriso" plano="medio" x={900} y={860} fase={2} espelhar />
              <Ator p={fan("#F2C29B")} e="espanto" plano="medio" x={540} y={740} fase={0} pulo={20} />
            </CameraMove>
          ),
        },
        {
          dur: 1.5,
          el: (
            <Estadio3D
              faixa={FAIXA_GANCHO}
              faixaCor={FAIXA_COR}
              cores={CORES_FLA_3D}
              trofeu={false}
              keys={[
                { pos: [0, 9, 20], look: [0, 9, -46] },
                { pos: [0, 12, 30], look: [0, 8, -46] },
                { pos: [0, 30, 66], look: [0, 0, -10] },
              ]}
            />
          ),
        },
        { dur: 1.15, el: <Papel tipo="zoom" forca={1.3}><SemBola /></Papel> },
        {
          dur: 1.66,
          el: (
            <CameraMove tipo="zoom" forca={1.2}>
              <Mar horizonte={900}>
                <Abs x={110} y={760}><Barco largura={860} nome="1895" /></Abs>
              </Mar>
              <LuzQuente forca={0.35} />
            </CameraMove>
          ),
        },
      ]}
    />
  );
};

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
      { dur: 1.16, el: <Sala tipo="zoom" forca={1.6} opts={{ cortina: false }}><Abs x={260} y={300}><PlacaEscudo src={ES.flamengo} tam={560} /></Abs></Sala> },
    ]}
  />
);

/** 3 — "Em 1895, um grupo de remadores fundou, na praia do Flamengo, um clube de regatas." */
export const C03Fundacao: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 1.6,
        el: (
          <Sepia forca={0.55}>
            <CameraMove tipo="zoom" forca={1.1}>
              <Mar horizonte={1100} tarde>
                <Abs x={160} y={980}><Barco largura={760} nome="1895" ritmo={0.8} /></Abs>
              </Mar>
              <Stamp text="1895" sub="17 DE NOVEMBRO" y={330} size={250} />
            </CameraMove>
          </Sepia>
        ),
      },
      {
        dur: 1.8,
        el: (
          <Sepia forca={0.45}>
            <CameraMove tipo="panDir" forca={1}>
              <Mar horizonte={1250} tarde pao={false}>
                <Ator p={REMADOR} e="sorriso" plano="medio" x={260} y={640} fase={1} />
                <Ator p={REMADOR2} e="dentes" plano="medio" x={800} y={680} fase={2} espelhar braco />
              </Mar>
            </CameraMove>
          </Sepia>
        ),
      },
      {
        dur: 1.9,
        el: (
          <Sepia forca={0.4}>
            <CameraMove tipo="zoom" forca={1}>
              <Mar horizonte={900} tarde>
                <div style={{ position: "absolute", left: 0, right: 0, top: 1350, bottom: 0, background: "linear-gradient(180deg,#F2D59A,#E2BC72)", borderTop: `6px solid ${OUT}` }} />
                <Abs x={200} y={1080}><Barco largura={680} nome="1895" ritmo={0.6} /></Abs>
                <Abs x={150} y={330}>
                  <PlacaMadeira largura={780}>
                    <div style={{ fontSize: 44 }}>RIO DE JANEIRO</div>
                    <div style={{ fontSize: 86 }}>PRAIA DO FLAMENGO</div>
                  </PlacaMadeira>
                </Abs>
              </Mar>
            </CameraMove>
          </Sepia>
        ),
      },
      {
        dur: 1.98,
        el: (
          <Sala tipo="zoom" forca={1.1} sepia opts={{ cortina: false, janela: false, tapete: false, quadros: false }}>
            <Abs x={540 - 300} y={250}><QuadroTexto linhas={["CLUBE DE", "REGATAS DO", "FLAMENGO"]} largura={600} /></Abs>
            <Ator p={REMADOR} e="sorriso" plano="medio" x={200} y={780} fase={1} />
            <Ator p={REMADOR2} e="sorriso" plano="medio" x={890} y={800} fase={2} espelhar />
            <Ator p={DIRIGENTE} e="dentes" plano="medio" x={545} y={730} braco />
            <MesaReuniao top={1330} />
          </Sala>
        ),
      },
    ]}
  />
);

/** 4 — "O primeiro barco, o Pherusa, virou no mar... e depois ainda foi roubado!" */
export const C04Pherusa: React.FC = () => {
  const Vira: React.FC = () => {
    const { s } = useSec();
    const ang = interpolate(s, [0.9, 1.5], [0, 150], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => x * x });
    const afunda = interpolate(s, [1.3, 2.2], [0, 180], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const splash = interpolate(s, [1.2, 1.5, 2.2], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <>
        <Abs x={110} y={760 + afunda}><Barco largura={860} nome="PHERUSA" inclina={ang} /></Abs>
        <Abs x={140} y={880} style={{ opacity: splash, scale: `${0.5 + splash}` }}>
          <svg width="800" height="400" viewBox="0 0 800 400">
            {[[200, 260, 90], [400, 200, 130], [600, 260, 90], [300, 140, 60], [520, 130, 70]].map(([x, y, r], i) => (
              <circle key={i} cx={x} cy={y} r={r} fill="#fff" stroke={OUT} strokeWidth="6" />
            ))}
          </svg>
        </Abs>
        <Abs x={0} y={300} style={{ width: 1080, textAlign: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 150, color: "#fff", WebkitTextStroke: `12px ${OUT}`, paintOrder: "stroke fill", opacity: splash }}>SPLASH!</Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 2.3, el: <Sepia forca={0.35}><CameraMove tipo="zoom" forca={0.9}><Mar horizonte={900}><Vira /></Mar></CameraMove></Sepia> },
        {
          dur: 1.1,
          el: (
            <Sepia forca={0.3}>
              <CameraMove tipo="zoom" forca={1.4}>
                <Mar horizonte={700} pao={false}>
                  <Ator p={REMADOR} e="espanto" plano="close" y={300} />
                  <div style={{ position: "absolute", left: 0, right: 0, top: 1450, bottom: 0, background: "linear-gradient(180deg,#1E7FB8,#0F5A8A)", borderTop: `6px solid ${OUT}` }} />
                </Mar>
              </CameraMove>
            </Sepia>
          ),
        },
        {
          dur: 1.86,
          el: (
            <Sala tipo="panEsq" sepia opts={{ cortina: false, quadros: false }}>
              <Ator p={LADRAO} e="desconfiado" plano="medio" x={540} y={760} />
              <CarimboIn texto="ROUBADO!" y={300} at={8} cor={RUBRO} size={150} />
            </Sala>
          ),
        },
      ]}
    />
  );
};

/** 5 — "Futebol? Só em 1911, com jogadores que saíram brigados do Fluminense." */
export const C05Futebol: React.FC = () => {
  const Saida: React.FC = () => {
    const { s } = useSec();
    const x = interpolate(s, [0.1, 1.1], [520, 820], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <>
        <Abs x={60} y={230}>
          <Porta placa=" " aberta={interpolate(s, [0, 0.3], [0, 1], { extrapolateRight: "clamp" })} />
          <Abs x={190} y={-6}><Img src={staticFile(ES.fluminense)} style={{ height: 120, objectFit: "contain" }} /></Abs>
        </Abs>
        <Ator p={{ ...REMADOR, terno: "#F1ECE0", gravata: RUBRO }} e="dentes" plano="medio" x={x} y={740} espelhar />
      </>
    );
  };
  return (
    <Shots
      planos={[
        {
          dur: 1.15,
          el: (
            <Sala tipo="zoom" forca={1.5} opts={{ janela: false }}>
              <Ator p={NARRADOR} e="desconfiado" plano="close" />
              <Abs x={700} y={1250}><Bola tam={260} /></Abs>
            </Sala>
          ),
        },
        {
          dur: 1.3,
          el: (
            <Papel tipo="zoom" forca={1.2}>
              <Abs x={100} y={640}><Jornal manchete="FUTEBOL NO FLAMENGO" sub="Dissidentes do Fluminense chegam ao clube" ano="1911" largura={880} /></Abs>
              <Stamp text="1911" y={260} size={220} />
            </Papel>
          ),
        },
        { dur: 1.6, el: <Sala tipo="panDir" forca={1} opts={{ janela: false, cortina: false, quadros: false }}><Saida /></Sala> },
        {
          dur: 1.23,
          el: (
            <Sala tipo="zoom" forca={1.2} opts={{ cortina: false }}>
              <Ator p={TRICOLOR} e="dentes" plano="close" x={560} />
            </Sala>
          ),
        },
      ]}
    />
  );
};

/** 6 — "No ano seguinte, nascia o Fla-Flu." (1º Fla-Flu: 7/7/1912, Fluminense 3 x 2 Flamengo) */
export const C06FlaFlu: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 2.1,
        el: (
          <Papel tipo="zoom" forca={0.8} raios>
            <Stamp text="1912" y={210} size={170} at={2} />
            <Abs x={60} y={470}>
              <Scoreboard startFrame={4} crestA={ES.fluminense} crestB={ES.flamengo} nameA="FLUMINENSE" nameB="FLAMENGO" a={3} b={2} top="1º FLA-FLU" year="1912" bottom="LARANJEIRAS · 7/7/1912" />
            </Abs>
          </Papel>
        ),
      },
      {
        dur: 1.72,
        el: (
          <CameraMove tipo="zoom" forca={1.2}>
            <Gramado horizonte={1300}>
              <Nuvens />
              <Ator p={TRICOLOR} e="dentes" plano="medio" x={250} y={700} />
              <Ator p={fan("#E8A877")} e="dentes" plano="medio" x={830} y={700} espelhar />
              <Abs x={0} y={340} style={{ width: 1080, textAlign: "center", fontFamily: ANTON, fontSize: 170, color: "#fff", WebkitTextStroke: `10px ${OUT}`, paintOrder: "stroke fill" }}>FLA × FLU</Abs>
            </Gramado>
          </CameraMove>
        ),
      },
    ]}
  />
);

/** 7 — "Em 1981, com Zico, o Flamengo conquistou a América... e o mundo: 3 a 0 no Liverpool, em Tóquio." */
export const C07Zico: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 2.2,
        el: (
          <Papel tipo="zoom" forca={1} raios>
            <Stamp text="1981" y={240} size={240} at={2} />
            <Abs x={170} y={600}>
              <Cutout src={FT.zico} width={740} startFrame={8} from={{ y: 500, r: -8, s: 0.6 }} outline />
            </Abs>
          </Papel>
        ),
      },
      {
        dur: 1.1,
        el: (
          <Papel tipo="zoom" forca={1.4} cor="#EFE6D6">
            <Abs x={200} y={250}><Polaroid src={FT.zicoRetrato} largura={640} altura={820} legenda="ZICO" credito="Foto: Sport legends / Flickr (CC BY 2.0)" rot={-4} pos="50% 25%" /></Abs>
          </Papel>
        ),
      },
      {
        dur: 1.6,
        el: (
          <Sala tipo="zoom" forca={1.1} opts={{ cortina: false, janela: false }}>
            <Abs x={150} y={260}>
              <div style={{ width: 780, background: "#F4E9D0", border: `20px solid #8A5A30`, outline: `5px solid ${OUT}`, padding: 26, display: "flex", flexDirection: "column", alignItems: "center", boxShadow: "14px 16px 22px rgba(0,0,0,0.45)" }}>
                <Img src={staticFile(LOGO.libertadores)} style={{ height: 300, objectFit: "contain" }} />
                <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 70, color: OUT, lineHeight: 1 }}>CAMPEÃO DA</div>
                <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 96, color: RUBRO, lineHeight: 1 }}>AMÉRICA · 1981</div>
              </div>
            </Abs>
            <Ator p={fan("#E8A877", "topete")} e="dentes" plano="medio" x={540} y={1100} braco pulo={14} />
          </Sala>
        ),
      },
      {
        dur: 1.2,
        el: (
          <Estadio3D
            faixa={["CAMPEÃO", "DO MUNDO · 1981"]}
            faixaCor={FAIXA_COR}
            cores={CORES_FLA_3D}
            trofeu={false}
            ceu="#FFC98A"
            keys={[
              { pos: [-8, 9, 18], look: [0, 9, -46] },
              { pos: [6, 10, 26], look: [0, 9, -46] },
            ]}
          />
        ),
      },
      {
        dur: 2.98,
        el: (
          <Papel tipo="zoom" forca={0.7} raios>
            <Abs x={60} y={330}>
              <Scoreboard startFrame={3} crestA={ES.flamengo} crestB={ES.liverpool} nameA="FLAMENGO" nameB="LIVERPOOL" a={3} b={0} top="MUNDIAL INTERCLUBES" year="1981" bottom="TÓQUIO · 13/12/1981" />
            </Abs>
            <Abs x={0} y={1330} style={{ width: 1080, display: "flex", justifyContent: "center" }}>
              <Etiqueta size={64} cor={RUBRO}>NUNES 2 · ADÍLIO</Etiqueta>
            </Abs>
          </Papel>
        ),
      },
    ]}
  />
);

/** Contador de anos 1981 → 2019 (a espera). */
const Espera: React.FC = () => {
  const f = useCurrentFrame();
  const n = Math.round(interpolate(f, [4, 44], [1981, 2019], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const anos = n - 1981;
  return (
    <>
      <Abs x={140} y={250}>
        <QuadroTexto linhas={[]} largura={800}>
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 250, lineHeight: 1, color: "#F0B23C" }}>{n}</div>
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 70, color: "#F0B23C" }}>{anos} ANOS SEM A LIBERTA</div>
        </QuadroTexto>
      </Abs>
      <Ator p={fan("#F2C29B", "grisalho")} e="triste" plano="medio" x={540} y={1060} />
    </>
  );
};

/** 8 — "Depois, 38 anos de espera pela Libertadores... até 2019: Gabigol fez dois gols no fim, contra o River, e virou o jogo!" */
export const C08Gabigol: React.FC = () => (
  <Shots
    planos={[
      { dur: 1.9, el: <Sala tipo="zoom" forca={1} opts={{ janela: false, cortina: false, quadros: false }}><Espera /></Sala> },
      { dur: 1.8, el: <Sala tipo="panEsq" forca={1} opts={{ janela: false }}><Ator p={fan("#A86F4C")} e="desconfiado" plano="close" /></Sala> },
      {
        dur: 1.3,
        el: (
          <Papel tipo="zoom" forca={1.2}>
            <Abs x={150} y={560}><Polaroid src={FT.final2019} largura={740} altura={470} credito="Foto: Alexandre Vidal / Flamengo" rot={3} /></Abs>
            <Stamp text="2019" sub="LIMA · PERU" y={230} size={220} at={2} />
          </Papel>
        ),
      },
      {
        dur: 1.8,
        el: (
          <Papel tipo="zoom" forca={1.1} raios>
            <Abs x={30} y={330}><Polaroid src={FT.gabigolTaca} largura={980} altura={612} legenda="GABIGOL" credito="Foto: Alexandre Vidal / CRF" rot={-2} pos="50% 50%" /></Abs>
            <Abs x={0} y={1330} style={{ width: 1080, display: "flex", justifyContent: "center" }}>
              <Etiqueta size={70} cor={RUBRO}>GOLS AOS 43' E 46' DO 2º TEMPO</Etiqueta>
            </Abs>
          </Papel>
        ),
      },
      {
        dur: 1.8,
        el: (
          <Papel tipo="zoom" forca={0.7} raios>
            <Abs x={60} y={330}>
              <Scoreboard startFrame={3} crestA={ES.flamengo} crestB={ES.river} nameA="FLAMENGO" nameB="RIVER PLATE" a={2} b={1} top="FINAL DA LIBERTADORES" year="2019" bottom="LIMA · 23/11/2019" />
            </Abs>
          </Papel>
        ),
      },
      {
        dur: 1.74,
        el: (
          <AbsoluteFill>
            <FotoCheia src={FT.festa2019} credito="Foto: Alexandre Vidal / Flamengo" pos="40% 50%" de={1.15} ate={1.3} />
            <Confete />
          </AbsoluteFill>
        ),
      },
    ]}
  />
);

const Confete: React.FC = () => {
  const { s } = useSec();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: 46 }).map((_, i) => {
        const x = (i * 97) % 1080;
        const y = s * (380 + (i % 7) * 70) + ((i * 53) % 500) - 520;
        return <div key={i} style={{ position: "absolute", left: x + Math.sin(s * 3 + i) * 30, top: y, width: 26, height: 14, background: [RUBRO, NEGRO, "#fff", "#F0B23C"][i % 4], border: `2px solid ${OUT}`, rotate: `${s * 300 + i * 40}deg` }} />;
      })}
    </AbsoluteFill>
  );
};

/** Linha de placar compacta (estilo TV) para 2022 e 2025. */
const Linha: React.FC<{ ano: string; adv: string; local: string; heroi: string; at: number }> = ({ ano, adv, local, heroi, at }) => {
  const f = useCurrentFrame();
  const k = pop(f, at, 10);
  return (
    <div style={{ width: 960, scale: `${k}`, display: "flex", flexDirection: "column", filter: "drop-shadow(14px 14px 0 rgba(200,16,46,0.9))" }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <div style={{ background: RUBRO, color: "#fff", fontFamily: BEBAS, fontSize: 50, padding: "4px 24px", letterSpacing: 3 }}>LIBERTADORES {ano}</div>
        <div style={{ background: "#fff", color: NEGRO, fontFamily: ANTON, fontSize: 44, padding: "4px 22px" }}>{local}</div>
      </div>
      <div style={{ background: `linear-gradient(180deg,#2a2a2a,${NEGRO})`, border: "6px solid #fff", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "20px 34px" }}>
        <Img src={staticFile(ES.flamengo)} style={{ height: 170, width: 170, objectFit: "contain" }} />
        <div style={{ fontFamily: ANTON, fontSize: 170, color: "#fff", lineHeight: 1 }}>1<span style={{ color: RUBRO, fontSize: 100 }}> × </span>0</div>
        <Img src={staticFile(adv)} style={{ height: 170, width: 170, objectFit: "contain" }} />
      </div>
      <div style={{ alignSelf: "center", background: "#fff", color: NEGRO, border: `6px solid ${NEGRO}`, fontFamily: ANTON, fontSize: 50, padding: "4px 30px", marginTop: -2 }}>{heroi}</div>
    </div>
  );
};

/** 9 — "Vieram mais duas: em 2022 e em 2025." */
export const C09TriTetra: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 1.35,
        el: (
          <CameraMove tipo="zoom" forca={1.3}>
            <TorcidaClose tam={160} />
            <Ator p={fan("#7A4B30", "careca")} e="dentes" plano="medio" x={300} y={780} braco pulo={20} />
            <Ator p={fan("#F2C29B", "topete")} e="sorriso" plano="medio" x={800} y={820} espelhar pulo={16} fase={2} />
          </CameraMove>
        ),
      },
      {
        dur: 1.4,
        el: (
          <Papel tipo="zoom" forca={0.8} raios>
            <Abs x={60} y={360}><Linha ano="2022" adv={ES.athletico} local="GUAYAQUIL" heroi="GOL DE GABIGOL" at={2} /></Abs>
          </Papel>
        ),
      },
      {
        dur: 1.81,
        el: (
          <Papel tipo="zoom" forca={0.8} raios>
            <Abs x={60} y={1290}><Linha ano="2025" adv={ES.palmeiras} local="LIMA" heroi="GOL DE DANILO" at={4} /></Abs>
            <Abs x={20} y={200}>
              <Cutout src={FT.danilo} width={1040} startFrame={0} from={{ y: -300, r: 6, s: 0.7 }} />
            </Abs>
            <div style={{ position: "absolute", right: 30, top: 1020, fontFamily: "Inter, Arial", fontSize: 22, color: "#333" }}>Foto: Luis Acosta / AFP</div>
          </Papel>
        ),
      },
    ]}
  />
);

/** 10 — "Hoje são quatro Libertadores, recorde entre os brasileiros, e a maior torcida do país: a Nação rubro-negra." */
export const C10Nacao: React.FC = () => {
  const Quatro: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <>
        <Abs x={0} y={170} style={{ width: 1080, display: "flex", justifyContent: "center" }}>
          <StatSlam value={4} startFrame={2} label="LIBERTADORES" size={560} color={RUBRO} />
        </Abs>
        <Abs x={40} y={1330} style={{ width: 1000, display: "flex", justifyContent: "center", gap: 18 }}>
          {["1981", "2019", "2022", "2025"].map((a, i) => (
            <div key={a} style={{ scale: `${pop(f, 10 + i * 4, 8)}`, background: i % 2 ? NEGRO : RUBRO, color: "#fff", fontFamily: ANTON, fontSize: 70, padding: "6px 22px", border: `5px solid ${OUT}`, rotate: `${(i % 2 ? 3 : -3)}deg` }}>{a}</div>
          ))}
        </Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 2.1, el: <Papel tipo="zoom" forca={0.8} raios><Quatro /></Papel> },
        {
          dur: 1.5,
          el: (
            <Papel tipo="zoom" forca={1.3}>
              <Abs x={240} y={260}><PlacaEscudo src={ES.flamengo} tam={600} /></Abs>
              <Abs x={0} y={1330} style={{ width: 1080, display: "flex", justifyContent: "center" }}>
                <Etiqueta size={74}>RECORDE ENTRE OS BRASILEIROS</Etiqueta>
              </Abs>
            </Papel>
          ),
        },
        { dur: 2.0, el: <FotoCheia src={FT.maracana} credito="Foto: Christian Haugen / Flickr (CC BY 2.0)" pos="45% 50%" de={1.1} ate={1.28} /> },
        {
          dur: 2.48,
          el: (
            <Estadio3D
              faixa={FAIXA_NACAO}
              faixaCor={FAIXA_COR}
              cores={CORES_FLA_3D}
              trofeu={false}
              keys={[
                { pos: [10, 26, 44], look: [0, 0, -12] },
                { pos: [0, 10, 22], look: [0, 9, -46] },
              ]}
            />
          ),
        },
      ]}
    />
  );
};

/** 11 — CTA: narrador acena; termina com o barco (volta ao começo: loop). */
export const C11Cta: React.FC = () => {
  const { s } = useSec();
  const k = interpolate(s, [0.25, 0.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const bx = interpolate(s, [4.2, 6.3], [-900, 1100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Estadio3D faixa={FAIXA_CTA} faixaCor={FAIXA_COR} cores={CORES_FLA_3D} trofeu={false} keys={[{ pos: [-30, 24, 70], look: [0, 4, -20] }, { pos: [30, 22, 64], look: [0, 4, -20] }]} />
      <Ator p={NARRADOR} e="sorriso" plano="medio" x={540} y={820} braco />
      <Abs x={0} y={250} style={{ width: 1080, display: "flex", justifyContent: "center", scale: `${k}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, background: "#fff", border: `8px solid ${OUT}`, borderRadius: 999, padding: "16px 38px 16px 18px", boxShadow: "10px 12px 0 rgba(0,0,0,0.35)" }}>
          <div style={{ width: 96, height: 96, borderRadius: "50%", background: RUBRO, border: `5px solid ${OUT}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 46, color: "#fff" }}>FE</div>
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 68, color: OUT }}>@futexplicando</div>
          <div style={{ background: RUBRO, color: "#fff", border: `5px solid ${OUT}`, borderRadius: 18, fontFamily: ROUND, fontWeight: 800, fontSize: 48, padding: "4px 22px" }}>SEGUIR</div>
        </div>
      </Abs>
      <Abs x={bx} y={1420}><Barco largura={720} nome="CRF" ritmo={1.4} /></Abs>
    </AbsoluteFill>
  );
};

export const CENAS: Record<string, React.FC> = {
  gancho: C01Gancho,
  fica: C02Fica,
  fundacao: C03Fundacao,
  pherusa: C04Pherusa,
  futebol: C05Futebol,
  flaflu: C06FlaFlu,
  zico: C07Zico,
  gabigol: C08Gabigol,
  tri_tetra: C09TriTetra,
  nacao: C10Nacao,
  cta: C11Cta,
};
export { D };
