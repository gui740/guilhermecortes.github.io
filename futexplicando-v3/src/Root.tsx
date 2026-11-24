import React from "react";
import { Composition, Still } from "remotion";
import "./estilo/tokens";
import { CenaTeste, Elenco, FichaLusa } from "./estudio/Revisao";
import { ElencoPalmeiras, FichaPal } from "./estudio/RevisaoPalmeiras";
import { Capa, ContatoCena, duracaoTotal, FPS, Historia, Video } from "./motor/Video";
import { TemposCena } from "./motor/tempo";
import lusa from "../historias/lusa2013.json";
import temposLusa from "../videos/lusa2013/tempos.json";
import pal from "../historias/palmeiras1951.json";
import temposPal from "../videos/palmeiras1951/tempos.json";

/** Cada história registra: o vídeo, a folha de contato de cada cena e a capa. */
const HISTORIAS: { comp: string; h: Historia & { capa?: { cena: number; plano: number; t: number } }; t: TemposCena[] }[] = [
  { comp: "Lusa2013", h: lusa as unknown as Historia, t: temposLusa as TemposCena[] },
  { comp: "Palmeiras1951", h: pal as unknown as Historia, t: temposPal as TemposCena[] },
];

export const RemotionRoot: React.FC = () => (
  <>
    {HISTORIAS.map(({ comp, h, t }) => (
      <React.Fragment key={comp}>
        <Composition id={comp} component={Video} defaultProps={{ historia: h, tempos: t, trilha: `${h.id}/mix.wav` }} durationInFrames={duracaoTotal(t)} fps={FPS} width={1080} height={1920} />
        {h.cenas.map((c, i) => (
          <Still key={c.id} id={`${comp}-Contato-${String(i + 1).padStart(2, "0")}-${c.id}`} component={ContatoCena} defaultProps={{ historia: h, tempos: t, cena: i }} width={12 + 3 * 364} height={650} />
        ))}
        <Still id={`Capa-${h.id}`} component={Capa} defaultProps={{ historia: h, tempos: t, cena: h.capa?.cena ?? 0, plano: h.capa?.plano ?? 0, t: h.capa?.t ?? 3 }} width={1080} height={1920} />
      </React.Fragment>
    ))}
    <Still id="FichaPal" component={FichaPal} width={1080} height={1920} />
    <Still id="ElencoPalmeiras" component={ElencoPalmeiras} width={1080} height={1920} />
    <Still id="FichaLusa" component={FichaLusa} width={1080} height={1920} />
    <Still id="Elenco" component={Elenco} width={1080} height={1920} />
    <Still id="CenaTeste" component={CenaTeste} width={1080} height={1920} />
  </>
);
