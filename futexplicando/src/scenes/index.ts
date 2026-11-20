import React from "react";
import { HookScene } from "./HookScene";
import { FoundationScene } from "./FoundationScene";
import { WarScene } from "./WarScene";
import { ArrancadaScene } from "./ArrancadaScene";
import { TimelineScene } from "./TimelineScene";
import { StatScene } from "./StatScene";
import { CtaScene } from "./CtaScene";

/** Mapa "type" do JSON → componente de cena. Novos tipos entram aqui. */
export const SCENES: Record<string, React.FC<{ scene: any }>> = {
  hook: HookScene,
  foundation: FoundationScene,
  nameswap: WarScene,
  pitch: ArrancadaScene,
  timeline: TimelineScene,
  stat: StatScene,
  cta: CtaScene,
};
