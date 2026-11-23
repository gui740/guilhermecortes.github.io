import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import raw from "../../data/copa-do-brasil.json";
import { CameraMove, pop, Shots } from "../../cartoon/Base";
import {
  Arquibancada,
  Bandeirinha,
  Carimbo,
  centroEstado,
  Escudo,
  Faixa,
  Gramado,
  Jornal,
  MapaBrasil,
  Mesa,
  Nuvens,
  PlacaMadeira,
  ROUND,
  SalaVintage,
  Sepia,
  Trofeu,
  TVTubo,
  Vareta,
  Zebra,
} from "../../cartoon/Cenarios";
import { Estadio3D } from "../../cartoon/Estadio3D";
import { Expressao, Personagem } from "../../cartoon/Personagem";

const D = raw;
const ES = raw.escudos as Record<string, string>;
const LOGO = raw.logos as Record<string, string>;
const OUT = "#2A1A12";

/* ------------------------------- elenco ------------------------------- */
const Cartola: React.FC<{ e: Expressao; alt?: number; braco?: boolean; espelhar?: boolean }> = ({ e, alt = 560, braco, espelhar }) => (
  <Personagem altura={alt} expressao={e} oculos cabelo="lados" corCabelo="#4A3020" terno="#4E5560" gravata="#9B2D20" bracoErguido={braco} espelhar={espelhar} fase={0.3} />
);
const Dirigente: React.FC<{ e: Expressao; alt?: number; terno?: string; fase?: number; espelhar?: boolean }> = ({ e, alt = 500, terno = "#6B4A2E", fase = 1, espelhar }) => (
  <Personagem altura={alt} expressao={e} chapeu bigode terno={terno} gravata="#2E4A6B" fase={fase} espelhar={espelhar} />
);
const Narrador: React.FC<{ e: Expressao; alt?: number; braco?: boolean }> = ({ e, alt = 560, braco }) => (
  <Personagem altura={alt} expressao={e} bigode cabelo="topete" corCabelo="#2B1B10" terno="#2F5E9E" gravata="#F2B705" bracoErguido={braco} fase={2} />
);
const Torcedor: React.FC<{ e: Expressao; cor: string; alt?: number; fase?: number; pulo?: number; espelhar?: boolean; braco?: boolean }> = ({ e, cor, alt = 520, fase = 3, pulo = 0, espelhar, braco }) => (
  <Personagem altura={alt} expressao={e} cachecol={cor} terno="#3D3D45" gravata={cor} fase={fase} pulo={pulo} espelhar={espelhar} bracoErguido={braco} cabelo={fase % 2 ? "topete" : "careca"} />
);

const useSec = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { s: f / fps, f, fps };
};

const Abs: React.FC<{ x: number; y: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ x, y, children, style }) => (
  <div style={{ position: "absolute", left: x, top: y, ...style }}>{children}</div>
);

const Placar: React.FC<{ a: { src?: string; selo?: { nome: string; cor1: string; cor2: string } }; b: { src?: string; selo?: { nome: string; cor1: string; cor2: string } }; ga?: number; gb?: number; titulo: string; k?: number }> = ({ a, b, ga, gb, titulo, k = 1 }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", scale: `${k}` }}>
    <div style={{ background: "#0B6E3A", border: `5px solid ${OUT}`, color: "#FEDD00", fontFamily: ROUND, fontWeight: 800, fontSize: 40, padding: "4px 26px", borderRadius: 12, marginBottom: 10 }}>{titulo}</div>
    <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
      <Escudo {...a} tam={170} />
      <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 130, color: "#FFF4DD", WebkitTextStroke: "10px #2A1A12", paintOrder: "stroke fill" }}>
        {ga === undefined ? "×" : `${ga}×${gb}`}
      </div>
      <Escudo {...b} tam={170} />
    </div>
  </div>
);

/* -------------------------------- CENAS -------------------------------- */

/** 1 — Gancho: sobrevoo 3D da torcida até o estádio inteiro. */
export const C01Gancho: React.FC = () => {
  const { s } = useSec();
  const texto = interpolate(s, [0.6, 1.0], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Estadio3D
        faixa={["R$ 78 MILHÕES", "PRO CAMPEÃO DA COPA DO BRASIL"]}
        keys={[
          { pos: [34, 9, -24], look: [44, 9, -40] },
          { pos: [14, 10, -14], look: [6, 9, -46] },
          { pos: [0, 16, 26], look: [0, 6, -30] },
          { pos: [0, 120, 150], look: [0, 0, 0] },
        ]}
      />
      <Abs x={0} y={250} style={{ width: 1080, display: "flex", justifyContent: "center", opacity: texto }}>
        <div style={{ background: "#FEDD00", border: `6px solid ${OUT}`, borderRadius: 20, padding: "10px 30px", fontFamily: ROUND, fontWeight: 800, fontSize: 64, color: OUT, rotate: "-3deg", boxShadow: "8px 10px 0 rgba(0,0,0,0.35)" }}>
          A HISTÓRIA DA COPA DO BRASIL
        </div>
      </Abs>
    </AbsoluteFill>
  );
};

/** 2 — Ameaça de punição. */
export const C02Ameaca: React.FC = () => (
  <Sepia>
    <Shots
      planos={[
        {
          dur: 1.8,
          el: (
            <CameraMove tipo="zoom">
              <SalaVintage>
                <Abs x={110} y={430}><PlacaMadeira largura={300}><div style={{ fontSize: 92 }}>CBF</div></PlacaMadeira></Abs>
                <Abs x={290} y={1000}><Cartola e="dentes" braco /></Abs>
                <Abs x={110} y={1360}><Mesa /></Abs>
              </SalaVintage>
            </CameraMove>
          ),
        },
        {
          dur: 1.6,
          el: (
            <CameraMove tipo="zoom" forca={1.0} origem="50% 40%">
              <SalaVintage lustre={false}>
                <Abs x={240} y={520}><Cartola e="dentes" alt={760} braco /></Abs>
                <StampIn texto="PUNIDO!" y={260} />
              </SalaVintage>
            </CameraMove>
          ),
        },
        {
          dur: 1.6,
          el: (
            <CameraMove tipo="panDir">
              <SalaVintage>
                <Abs x={120} y={1060}><Dirigente e="espanto" alt={560} /></Abs>
                <Abs x={560} y={1080}><Dirigente e="espanto" alt={520} terno="#4F5B3A" fase={2.2} espelhar /></Abs>
                <Abs x={0} y={300} style={{ width: 1080, textAlign: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 70, color: "#5A1E14" }}>“QUEM NÃO JOGAR...”</Abs>
              </SalaVintage>
            </CameraMove>
          ),
        },
      ]}
    />
  </Sepia>
);

const StampIn: React.FC<{ texto: string; y: number; delay?: number }> = ({ texto, y, delay = 6 }) => {
  const f = useCurrentFrame();
  const k = pop(f, delay, 8);
  return (
    <Abs x={0} y={y} style={{ width: 1080, textAlign: "center" }}>
      <Carimbo texto={texto} k={k} size={120} rot={-6} />
    </Abs>
  );
};

/** 3 — "Fica até o final que eu explico." */
export const C03Fica: React.FC = () => (
  <Sepia forca={0.45}>
    <Shots
      planos={[
        {
          dur: 1,
          el: (
            <CameraMove tipo="zoom">
              <SalaVintage>
                <Abs x={420} y={330}>
                  <TVTubo largura={560}>
                    <Img src={staticFile(LOGO.copaDoBrasil)} style={{ height: 230, objectFit: "contain" }} />
                  </TVTubo>
                </Abs>
                <Abs x={70} y={1060}><Narrador e="sorriso" /></Abs>
              </SalaVintage>
            </CameraMove>
          ),
        },
        {
          dur: 1,
          el: (
            <CameraMove tipo="zoom" forca={1.5} origem="30% 70%">
              <SalaVintage lustre={false}>
                <Abs x={190} y={1000}><Narrador e="dentes" alt={760} braco /></Abs>
              </SalaVintage>
            </CameraMove>
          ),
        },
      ]}
    />
  </Sepia>
);

/** 4 — "Tudo começou em 1989." */
export const C04Comecou: React.FC = () => {
  const Spin: React.FC = () => {
    const f = useCurrentFrame();
    const r = interpolate(f, [0, 14], [720, -4], { extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
    const sc = interpolate(f, [0, 14], [0.2, 1], { extrapolateRight: "clamp" });
    return (
      <Abs x={160} y={260} style={{ rotate: `${r}deg`, scale: `${sc}` }}>
        <Jornal manchete="1989" sub="CBF anuncia um novo torneio nacional" largura={760} />
      </Abs>
    );
  };
  return (
    <Sepia>
      <Shots
        planos={[
          { dur: 1.4, el: <CameraMove tipo="zoom"><SalaVintage><Spin /></SalaVintage></CameraMove> },
          {
            dur: 1.4,
            el: (
              <CameraMove tipo="panEsq">
                <SalaVintage>
                  <Abs x={300} y={300}>
                    <PlacaMadeira largura={480}>
                      <div style={{ fontSize: 48 }}>CALENDÁRIO</div>
                      <div style={{ fontSize: 170, lineHeight: 1 }}>1989</div>
                    </PlacaMadeira>
                  </Abs>
                  <Abs x={110} y={1080}><Dirigente e="sorriso" /></Abs>
                </SalaVintage>
              </CameraMove>
            ),
          },
        ]}
      />
    </Sepia>
  );
};

/** 5 — Ricardo Teixeira assume a CBF. */
export const C05Teixeira: React.FC = () => (
  <Sepia>
    <Shots
      planos={[
        {
          dur: 1.5,
          el: (
            <CameraMove tipo="zoom">
              <SalaVintage>
                <Abs x={340} y={320}><PlacaMadeira largura={400}><div style={{ fontSize: 110 }}>CBF</div></PlacaMadeira></Abs>
                <Abs x={290} y={1000}><Cartola e="sorriso" /></Abs>
                <Abs x={110} y={1360}><Mesa /></Abs>
              </SalaVintage>
            </CameraMove>
          ),
        },
        {
          dur: 1.5,
          el: (
            <CameraMove tipo="panDir" origem="50% 60%">
              <SalaVintage lustre={false}>
                <Abs x={150} y={1080}>
                  <PlacaMadeira largura={780}>
                    <div style={{ fontSize: 40 }}>PRESIDENTE DA CBF · JAN/1989</div>
                    <div style={{ fontSize: 76 }}>RICARDO TEIXEIRA</div>
                  </PlacaMadeira>
                </Abs>
                <Abs x={330} y={300}><Cartola e="sorriso" alt={540} /></Abs>
              </SalaVintage>
            </CameraMove>
          ),
        },
      ]}
    />
  </Sepia>
);

const NORTE_NE = ["AC", "AM", "RR", "AP", "PA", "RO", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "MT", "MS"];

/** 6 — Estados menores bravos. */
export const C06Estados: React.FC = () => (
  <Sepia>
    <Shots
      planos={[
        { dur: 2.4, el: <CameraMove tipo="zoom"><SalaVintage lustre={false}><Abs x={110} y={150}><MapaBrasil largura={860} destaque={NORTE_NE} piscar /></Abs></SalaVintage></CameraMove> },
        {
          dur: 2.4,
          el: (
            <CameraMove tipo="panEsq">
              <SalaVintage>
                <Abs x={40} y={1060}><Dirigente e="desconfiado" alt={520} /></Abs>
                <Abs x={380} y={1040}><Dirigente e="dentes" alt={540} terno="#4F5B3A" fase={2} /></Abs>
                <Abs x={720} y={1070}><Dirigente e="desconfiado" alt={500} terno="#5B3A4F" fase={3} espelhar /></Abs>
                <Abs x={220} y={330}><PlacaMadeira largura={640}><div style={{ fontSize: 80 }}>E A GENTE?</div><div style={{ fontSize: 40 }}>FORA DA ELITE DO BRASILEIRÃO</div></PlacaMadeira></Abs>
              </SalaVintage>
            </CameraMove>
          ),
        },
      ]}
    />
  </Sepia>
);

const SIGLAS = ["AC", "AM", "RR", "AP", "PA", "RO", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA", "MT", "MS", "GO", "DF", "MG", "ES", "RJ", "SP", "PR", "SC", "RS"];
const CORES = ["#C0392B", "#2E86C1", "#1E8449", "#B7950B", "#7D3C98", "#CA6F1E", "#17202A"];

/** 7 — Mata-mata com campeões de todos os estados. */
export const C07MataMata: React.FC = () => {
  const Mapa: React.FC = () => {
    const f = useCurrentFrame();
    const W = 860;
    const idx = Math.min(SIGLAS.length - 1, Math.floor(f / 2.5));
    const alvo = centroEstado(SIGLAS[idx]);
    return (
      <Abs x={110} y={150}>
        <MapaBrasil largura={W}>
          {SIGLAS.map((sg, i) => {
            const c = centroEstado(sg);
            return <Bandeirinha key={sg} x={c.x} y={c.y} largura={W} cor={CORES[i % CORES.length]} k={pop(f, i * 2.5, 6)} />;
          })}
          <Vareta x={alvo.x} y={alvo.y} largura={W} ang={-30} />
        </MapaBrasil>
      </Abs>
    );
  };
  return (
    <Sepia>
      <Shots
        planos={[
          { dur: 2.2, el: <CameraMove tipo="zoom"><SalaVintage lustre={false}><Mapa /></SalaVintage></CameraMove> },
          {
            dur: 1.4,
            el: (
              <CameraMove tipo="zoom" forca={1.4}>
                <SalaVintage>
                  <Abs x={230} y={300}><PlacaMadeira largura={620}><div style={{ fontSize: 96 }}>MATA-MATA</div><div style={{ fontSize: 40 }}>CAMPEÕES DE TODOS OS ESTADOS</div></PlacaMadeira></Abs>
                  <Abs x={290} y={1060}><Cartola e="sorriso" /></Abs>
                </SalaVintage>
              </CameraMove>
            ),
          },
        ]}
      />
    </Sepia>
  );
};

/** 8 — 32 times, 46 dias, vaga na Libertadores. */
export const C08Numeros: React.FC = () => {
  const Contador: React.FC<{ alvo: number; rotulo: string }> = ({ alvo, rotulo }) => {
    const f = useCurrentFrame();
    const n = Math.round(interpolate(f, [2, 22], [0, alvo], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
    return (
      <Abs x={190} y={250}>
        <PlacaMadeira largura={700}>
          <div style={{ fontSize: 260, lineHeight: 1 }}>{n}</div>
          <div style={{ fontSize: 72 }}>{rotulo}</div>
        </PlacaMadeira>
      </Abs>
    );
  };
  return (
    <Sepia forca={0.5}>
      <Shots
        planos={[
          { dur: 1.9, el: <CameraMove tipo="zoom"><SalaVintage><Contador alvo={32} rotulo="TIMES" /><Abs x={110} y={1080}><Dirigente e="espanto" /></Abs></SalaVintage></CameraMove> },
          { dur: 1.9, el: <CameraMove tipo="panDir"><SalaVintage><Contador alvo={46} rotulo="DIAS DE TORNEIO" /><Abs x={600} y={1080}><Cartola e="sorriso" alt={520} espelhar /></Abs></SalaVintage></CameraMove> },
          {
            dur: 2,
            el: (
              <CameraMove tipo="zoom" forca={1.3}>
                <SalaVintage>
                  <Abs x={240} y={290}>
                    <div style={{ width: 600, background: "#F4E9D0", border: `14px solid #8A5A30`, outline: `5px solid ${OUT}`, padding: 30, display: "flex", flexDirection: "column", alignItems: "center", boxShadow: "12px 14px 0 rgba(0,0,0,0.35)" }}>
                      <Img src={staticFile(LOGO.libertadores)} style={{ height: 300, objectFit: "contain" }} />
                      <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 56, color: OUT }}>VAGA PRO CAMPEÃO</div>
                    </div>
                  </Abs>
                  <Abs x={330} y={1080}><Dirigente e="espanto" alt={540} terno="#4F5B3A" /></Abs>
                </SalaVintage>
              </CameraMove>
            ),
          },
        ]}
      />
    </Sepia>
  );
};

/** 9 — Primeiro campeão: Grêmio x Sport. */
export const C09Primeiro: React.FC = () => {
  const TV: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <Abs x={170} y={300}>
        <TVTubo largura={760}>
          <div style={{ scale: "0.62" }}>
            <Placar a={{ src: ES.gremio }} b={{ src: ES.sport }} ga={2} gb={1} titulo="FINAL 1989 · VOLTA" k={pop(f, 4, 10)} />
          </div>
        </TVTubo>
      </Abs>
    );
  };
  return (
    <Sepia forca={0.35}>
      <Shots
        planos={[
          { dur: 1.9, el: <CameraMove tipo="zoom"><SalaVintage><TV /><Abs x={330} y={1100}><PlacaMadeira largura={420}><div style={{ fontSize: 60 }}>1º CAMPEÃO</div></PlacaMadeira></Abs></SalaVintage></CameraMove> },
          {
            dur: 1.9,
            el: (
              <CameraMove tipo="zoom" forca={1.5} origem="50% 70%">
                <SalaVintage>
                  <Abs x={250} y={330}><Escudo src={ES.gremio} tam={420} /></Abs>
                  <Abs x={250} y={1000}><Torcedor e="dentes" cor="#1E88E5" alt={620} pulo={18} braco /></Abs>
                </SalaVintage>
              </CameraMove>
            ),
          },
        ]}
      />
    </Sepia>
  );
};

/** 10 — A chance dos pequenos. */
export const C10Pequenos: React.FC = () => {
  const Mapa: React.FC = () => {
    const f = useCurrentFrame();
    const W = 860;
    const tour = ["AC", "RR", "AP", "PI", "SE", "AL", "TO", "RO"];
    const i = Math.min(tour.length - 1, Math.floor(f / 8));
    const c = centroEstado(tour[i]);
    return (
      <Abs x={110} y={150}>
        <MapaBrasil largura={W} destaque={[tour[i]]} corDestaque="#F4D03F">
          {SIGLAS.map((sg, j) => {
            const cc = centroEstado(sg);
            return <Bandeirinha key={sg} x={cc.x} y={cc.y} largura={W} cor={CORES[j % CORES.length]} />;
          })}
          <Vareta x={c.x} y={c.y} largura={W} ang={-25} />
        </MapaBrasil>
      </Abs>
    );
  };
  return (
    <Sepia>
      <Shots
        planos={[
          { dur: 1.4, el: <CameraMove tipo="panEsq"><SalaVintage lustre={false}><Mapa /></SalaVintage></CameraMove> },
          { dur: 1.2, el: <CameraMove tipo="zoom" forca={1.4}><SalaVintage><Abs x={290} y={1000}><Torcedor e="sorriso" cor="#F4D03F" alt={600} pulo={14} /></Abs><Abs x={250} y={330}><PlacaMadeira largura={580}><div style={{ fontSize: 78 }}>VEZ DOS PEQUENOS</div></PlacaMadeira></Abs></SalaVintage></CameraMove> },
        ]}
      />
    </Sepia>
  );
};

/** 11 — Criciúma 1991. */
export const C11Criciuma: React.FC = () => {
  const P: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <Abs x={110} y={300}>
        <PlacaMadeira largura={860}>
          <div style={{ fontSize: 46, marginBottom: 10 }}>FINAL 1991 · CAMPEÃO NO GOL FORA</div>
          <div style={{ scale: `${pop(f, 3, 10)}` }}>
            <Placar a={{ src: ES.criciuma }} b={{ src: ES.gremio }} ga={0} gb={0} titulo="CRICIÚMA x GRÊMIO" />
          </div>
        </PlacaMadeira>
      </Abs>
    );
  };
  return (
    <Sepia forca={0.3}>
      <Shots
        planos={[
          { dur: 1.8, el: <CameraMove tipo="zoom"><SalaVintage lustre={false}><P /></SalaVintage></CameraMove> },
          {
            dur: 1.8,
            el: (
              <CameraMove tipo="panDir">
                <SalaVintage>
                  <Abs x={60} y={1040}><Torcedor e="dentes" cor="#F4D03F" alt={580} pulo={22} braco /></Abs>
                  <Abs x={560} y={1060}><Torcedor e="triste" cor="#1E88E5" alt={540} fase={4} espelhar /></Abs>
                  <Abs x={340} y={330}><Escudo src={ES.criciuma} tam={400} /></Abs>
                </SalaVintage>
              </CameraMove>
            ),
          },
        ]}
      />
    </Sepia>
  );
};

/* -------------------------------- PRESENTE -------------------------------- */

const Estadio2D: React.FC<{ cores: string[]; faixa?: React.ReactNode; silencio?: boolean; children?: React.ReactNode }> = ({ cores, faixa, silencio, children }) => (
  <Gramado horizonte={1060}>
    <Nuvens />
    <Arquibancada cores={cores} linhas={6} tam={66} top={360} faixa={faixa} />
    {silencio ? <AbsoluteFill style={{ background: "rgba(20,30,60,0.25)" }} /> : null}
    {children}
  </Gramado>
);

const SANTO_ANDRE = { nome: "SANTO ANDRÉ", cor1: "#1D4E9E", cor2: "#FFFFFF" };
const PAULISTA = { nome: "PAULISTA", cor1: "#C62828", cor2: "#FFFFFF" };

/** 12 — Santo André cala o Maracanã (2004). */
export const C12SantoAndre: React.FC = () => {
  const P: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <Abs x={110} y={150} style={{ width: 860, display: "flex", justifyContent: "center", scale: `${pop(f, 3, 10)}` }}>
        <Placar a={{ selo: SANTO_ANDRE }} b={{ src: ES.flamengo }} ga={2} gb={0} titulo="FINAL 2004 · MARACANÃ" />
      </Abs>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 2.1, el: <CameraMove tipo="zoom"><Estadio2D cores={["#C62828", "#111111"]} silencio><P /><Abs x={0} y={1230} style={{ width: 1080, textAlign: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 80, color: "#fff", WebkitTextStroke: "8px #2A1A12", paintOrder: "stroke fill" }}>SILÊNCIO...</Abs></Estadio2D></CameraMove> },
        { dur: 2.1, el: <CameraMove tipo="zoom" forca={1.4} origem="50% 75%"><Estadio2D cores={["#C62828", "#111111"]} silencio><Abs x={260} y={1100}><Torcedor e="espanto" cor="#C62828" alt={620} /></Abs></Estadio2D></CameraMove> },
      ]}
    />
  );
};

/** 13 — Paulista bate o Fluminense (2005). */
export const C13Paulista: React.FC = () => (
  <Shots
    planos={[
      {
        dur: 2.1,
        el: (
          <CameraMove tipo="panEsq">
            <Estadio2D cores={["#C62828", "#FFFFFF", "#111111"]} faixa={<Faixa texto="PAULISTA CAMPEÃO 2005" cor="#C62828" corTexto="#fff" largura={900} />}>
              <Abs x={110} y={160} style={{ width: 860, display: "flex", justifyContent: "center" }}>
                <Placar a={{ selo: PAULISTA }} b={{ src: ES.fluminense }} titulo="FINAL 2005 · CAMPEÃO: PAULISTA" />
              </Abs>
            </Estadio2D>
          </CameraMove>
        ),
      },
      {
        dur: 2.1,
        el: (
          <CameraMove tipo="zoom" forca={1.4} origem="50% 75%">
            <Estadio2D cores={["#7B1E3A", "#1E7B4A", "#FFFFFF"]}>
              <Abs x={260} y={1100}><Torcedor e="desconfiado" cor="#7B1E3A" alt={620} fase={5} /></Abs>
              <Abs x={340} y={180}><Escudo src={ES.fluminense} tam={400} /></Abs>
            </Estadio2D>
          </CameraMove>
        ),
      },
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
        <Abs x={140} y={260}>
          <div style={{ width: 800, height: 700, background: "repeating-linear-gradient(90deg,#6E7B8B 0 20px, transparent 20px 90px)", border: `10px solid ${OUT}`, borderRadius: "40px 40px 0 0", position: "relative" }}>
            <div style={{ position: "absolute", left: 120, right: 120, top: 220, background: "#B3261E", border: `6px solid ${OUT}`, borderRadius: 16, color: "#fff", fontFamily: ROUND, fontWeight: 800, fontSize: 58, textAlign: "center", padding: 14, rotate: "-3deg" }}>
              QUEM JOGA A LIBERTADORES<br />NÃO ENTRA!
            </div>
          </div>
        </Abs>
        <Abs x={60} y={1060} style={{ display: "flex", gap: 16, flexWrap: "wrap", width: 960, justifyContent: "center" }}>
          {GRANDES.map((g, i) => (
            <div key={g} style={{ scale: `${pop(f, 4 + i * 3, 8)}` }}>
              <Escudo src={ES[g]} tam={140} />
            </div>
          ))}
        </Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 2, el: <CameraMove tipo="zoom"><Gramado horizonte={1000}><Nuvens /><Portao /></Gramado></CameraMove> },
        { dur: 1.8, el: <CameraMove tipo="panDir"><Gramado horizonte={1000}><Nuvens /><Abs x={240} y={330}><PlacaMadeira largura={600}><div style={{ fontSize: 64 }}>2001 → 2012</div><div style={{ fontSize: 44 }}>SÓ 64 TIMES, SEM OS DA LIBERTA</div></PlacaMadeira></Abs><Abs x={290} y={1040}><Torcedor e="desconfiado" cor="#1E88E5" alt={600} /></Abs></Gramado></CameraMove> },
      ]}
    />
  );
};

/** 15 — 2013: grandes entram nas oitavas e as zebras somem. */
export const C15Oitavas: React.FC = () => {
  const Chave: React.FC = () => {
    const f = useCurrentFrame();
    return (
      <Abs x={90} y={220}>
        <PlacaMadeira largura={900} style={{ background: "linear-gradient(180deg,#0B6E3A,#075029)" }}>
          <div style={{ fontSize: 70 }}>OITAVAS DE FINAL · 2013</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 18, marginTop: 16, justifyItems: "center" }}>
            {GRANDES.map((g, i) => (
              <div key={g} style={{ scale: `${pop(f, 3 + i * 3, 8)}` }}>
                <Escudo src={ES[g]} tam={150} />
              </div>
            ))}
          </div>
        </PlacaMadeira>
      </Abs>
    );
  };
  const Puf: React.FC = () => {
    const f = useCurrentFrame();
    const sumiu = interpolate(f, [14, 22], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const nuvem = interpolate(f, [14, 20, 34], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <>
        <Abs x={300} y={360} style={{ scale: `${sumiu}`, opacity: sumiu }}><Zebra tam={480} /></Abs>
        <Abs x={240} y={330} style={{ opacity: nuvem, scale: `${0.6 + nuvem * 0.6}` }}>
          <svg width="600" height="500" viewBox="0 0 600 500">
            {[[300, 250, 140], [180, 220, 90], [420, 220, 100], [240, 340, 90], [380, 340, 90]].map(([x, y, r], i) => (
              <circle key={i} cx={x} cy={y} r={r} fill="#fff" stroke={OUT} strokeWidth="6" />
            ))}
          </svg>
        </Abs>
        <Abs x={0} y={420} style={{ width: 1080, textAlign: "center", opacity: nuvem, fontFamily: ROUND, fontWeight: 800, fontSize: 130, color: OUT }}>PUF!</Abs>
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 2, el: <CameraMove tipo="zoom"><Gramado horizonte={1100}><Nuvens /><Chave /></Gramado></CameraMove> },
        { dur: 1.9, el: <CameraMove tipo="zoom" forca={1.3}><Gramado horizonte={1100}><Nuvens /><Puf /><Abs x={290} y={1060}><Torcedor e="espanto" cor="#43A047" alt={600} /></Abs></Gramado></CameraMove> },
        { dur: 1.8, el: <CameraMove tipo="panEsq"><Estadio2D cores={["#1E88E5", "#C62828", "#111111", "#43A047"]} faixa={<Faixa texto="SÓ DÁ GIGANTE" largura={760} />} /></CameraMove> },
      ]}
    />
  );
};

/** 16 — Maiores campeões. */
export const C16Maiores: React.FC = () => {
  const Podio: React.FC = () => {
    const f = useCurrentFrame();
    const col = (src: string, n: number, h: number, x: number, d: number) => (
      <div style={{ position: "absolute", left: x, bottom: 0, width: 280, display: "flex", flexDirection: "column", alignItems: "center", scale: `${pop(f, d, 10)}`, transformOrigin: "50% 100%" }}>
        <Escudo src={src} tam={200} />
        <div style={{ width: 260, height: h, marginTop: 14, background: "linear-gradient(180deg,#F4D03F,#B7950B)", border: `6px solid ${OUT}`, borderRadius: 12, display: "flex", alignItems: "flex-start", justifyContent: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 120, color: OUT }}>{n}</div>
      </div>
    );
    return (
      <Abs x={70} y={180} style={{ width: 940, height: 800 }}>
        {col(ES.gremio, 5, 300, 0, 10)}
        {col(ES.cruzeiro, 6, 420, 330, 2)}
        {col(ES.flamengo, 5, 300, 660, 16)}
      </Abs>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 2.6, el: <CameraMove tipo="zoom"><Gramado horizonte={980}><Nuvens /><Podio /><Arquibancada cores={["#1E3A8A", "#1E88E5", "#C62828", "#111111"]} linhas={4} tam={64} top={1340} /></Gramado></CameraMove> },
        { dur: 1.4, el: <CameraMove tipo="zoom" forca={1.5} origem="50% 30%"><Gramado horizonte={980}><Nuvens /><Abs x={290} y={240}><Escudo src={ES.cruzeiro} tam={500} /></Abs><Abs x={290} y={1060}><Torcedor e="dentes" cor="#1E3A8A" alt={600} pulo={20} braco /></Abs></Gramado></CameraMove> },
        { dur: 1.4, el: <CameraMove tipo="panDir"><Estadio2D cores={["#1E88E5", "#C62828", "#111111"]} faixa={<Faixa texto="GRÊMIO 5 · FLAMENGO 5" largura={880} />} /></CameraMove> },
      ]}
    />
  );
};

/** 17 — Hoje: 126 clubes e final única em Brasília. */
export const C17Hoje: React.FC = () => {
  const Pontos: React.FC = () => {
    const f = useCurrentFrame();
    const W = 860;
    const n = Math.min(126, Math.floor(interpolate(f, [2, 50], [0, 126], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })));
    const pts = Array.from({ length: 126 }).map((_, i) => {
      const sg = SIGLAS[i % SIGLAS.length];
      const c = centroEstado(sg);
      const a = i * 2.39996;
      const r = 8 + ((i * 37) % 40);
      return { x: c.x + Math.cos(a) * r, y: c.y + Math.sin(a) * r };
    });
    return (
      <Abs x={110} y={150}>
        <MapaBrasil largura={W} antigo={false}>
          <svg width={W} height={W} viewBox="0 0 1000 1000" style={{ position: "absolute", inset: 0 }}>
            {pts.slice(0, n).map((p, i) => (
              <circle key={i} cx={p.x} cy={p.y} r={9} fill="#FEDD00" stroke="#2A1A12" strokeWidth="2.5" />
            ))}
          </svg>
        </MapaBrasil>
        <Abs x={0} y={-60} style={{ width: W, textAlign: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 90, color: "#fff", WebkitTextStroke: "8px #2A1A12", paintOrder: "stroke fill" }}>{n} CLUBES</Abs>
      </Abs>
    );
  };
  const Brasilia: React.FC = () => {
    const f = useCurrentFrame();
    const df = centroEstado("DF");
    const W = 860;
    return (
      <Abs x={110} y={150}>
        <MapaBrasil largura={W} antigo={false} destaque={["DF"]} corDestaque="#FEDD00" piscar>
          <Abs x={(df.x * W) / 1000 - 120} y={(df.y * W) / 1000 - 400} style={{ scale: `${pop(f, 6, 12)}` }}>
            <Trofeu altura={380} />
          </Abs>
        </MapaBrasil>
        <Abs x={0} y={900} style={{ width: W, display: "flex", justifyContent: "center" }}>
          <PlacaMadeira largura={720} style={{ background: "linear-gradient(180deg,#0B6E3A,#075029)" }}>
            <div style={{ fontSize: 50 }}>FINAL 2026 · JOGO ÚNICO</div>
            <div style={{ fontSize: 70 }}>BRASÍLIA · 06/12</div>
          </PlacaMadeira>
        </Abs>
      </Abs>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 3, el: <CameraMove tipo="zoom"><Gramado horizonte={1500}><Nuvens /><Pontos /></Gramado></CameraMove> },
        { dur: 3.1, el: <CameraMove tipo="zoom" forca={1.3} origem="50% 40%"><Gramado horizonte={1500}><Nuvens /><Brasilia /></Gramado></CameraMove> },
      ]}
    />
  );
};

/** 18 — Frase de impacto: o carimbo vira troféu. */
export const C18Impacto: React.FC = () => {
  const Vira: React.FC = () => {
    const { s } = useSec();
    const flip = interpolate(s, [1.2, 1.7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <>
        <Abs x={0} y={320} style={{ width: 1080, textAlign: "center", opacity: 1 - flip, scale: `${1 - flip * 0.6}` }}>
          <Carimbo texto="PUNIDO!" k={1} size={170} />
        </Abs>
        <Abs x={540 - 186} y={200} style={{ opacity: flip, scale: `${0.4 + flip * 0.6}` }}>
          <Trofeu altura={600} brilho={1.4} />
        </Abs>
        {flip > 0
          ? Array.from({ length: 40 }).map((_, i) => {
              const x = (i * 97) % 1080;
              const y = ((s - 1.5) * (300 + (i % 7) * 60) + (i * 53) % 400) - 200;
              return <div key={i} style={{ position: "absolute", left: x, top: y, width: 22, height: 12, background: ["#FEDD00", "#0B6E3A", "#1E88E5", "#fff"][i % 4], border: `2px solid ${OUT}`, rotate: `${s * 300 + i * 40}deg` }} />;
            })
          : null}
      </>
    );
  };
  return (
    <Shots
      planos={[
        { dur: 1.9, el: <CameraMove tipo="zoom"><Sepia forca={0.3}><SalaVintage><Vira /></SalaVintage></Sepia></CameraMove> },
        {
          dur: 2,
          el: (
            <AbsoluteFill>
              <Estadio3D faixa={["A TAÇA QUE VALE", "UMA FORTUNA"]} keys={[{ pos: [0, 10, 40], look: [0, 6, 0] }, { pos: [30, 14, 28], look: [0, 6, 0] }]} />
            </AbsoluteFill>
          ),
        },
      ]}
    />
  );
};

/** 19 — CTA. */
export const C19Cta: React.FC = () => {
  const { s } = useSec();
  const k = interpolate(s, [0.3, 0.7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Estadio3D faixa={["SEGUE O", "@FUTEXPLICANDO"]} trofeu keys={[{ pos: [-30, 30, 90], look: [0, 4, 0] }, { pos: [30, 26, 80], look: [0, 4, 0] }]} />
      <Abs x={190} y={1040}><Narrador e="sorriso" alt={580} braco /></Abs>
      <Abs x={0} y={260} style={{ width: 1080, display: "flex", justifyContent: "center", scale: `${k}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, background: "#fff", border: `7px solid ${OUT}`, borderRadius: 999, padding: "14px 36px 14px 18px", boxShadow: "10px 12px 0 rgba(0,0,0,0.35)" }}>
          <div style={{ width: 90, height: 90, borderRadius: "50%", background: "#0B6E3A", border: `5px solid ${OUT}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ROUND, fontWeight: 800, fontSize: 44, color: "#FEDD00" }}>FE</div>
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 66, color: OUT }}>@futexplicando</div>
          <div style={{ background: "#E53935", color: "#fff", border: `5px solid ${OUT}`, borderRadius: 18, fontFamily: ROUND, fontWeight: 800, fontSize: 46, padding: "4px 20px" }}>SEGUIR</div>
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
