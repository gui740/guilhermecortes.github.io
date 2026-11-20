import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { TITLE, SANS } from "../lib/fonts";
import { Icon } from "./Icons";
import { PhotoCard } from "./PhotoCard";
import { Sfx } from "./Sfx";

export type TimelineItem = { year: string; label: string; icon: string; at: number; image?: string; credit?: string };

const GAP = 760;

/** Linha do tempo horizontal que rola com spring até o marco atual. */
export const Timeline: React.FC<{
  items: TimelineItem[]; colors: { paper: string; ink: string; primary: string; secondary: string }; whoosh?: string;
}> = ({ items, colors, whoosh }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  // posição da câmera = soma de springs (um por marco)
  const cam = items.reduce((acc, it, i) => (i === 0 ? acc : acc + spring({ frame: f - it.at, fps, config: { damping: 15, stiffness: 90 } })), 0);
  const x0 = 540 - cam * GAP;
  const lineGrow = interpolate(f, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", top: 960, left: x0 - 400, width: (items.length - 1) * GAP + 800, height: 16, background: colors.ink, transformOrigin: "left", transform: `scaleX(${lineGrow})` }} />
      {items.map((it, i) => {
        const x = x0 + i * GAP;
        const on = spring({ frame: f - it.at, fps, config: { damping: 10, stiffness: 170 } });
        const active = f >= it.at && (i === items.length - 1 || f < items[i + 1].at);
        return (
          <div key={i} style={{ position: "absolute", left: x, top: 0 }}>
            <div style={{ position: "absolute", left: -360, top: 360, width: 720, display: "flex", justifyContent: "center", opacity: on }}>
              {it.image && (
                <PhotoCard src={it.image} at={it.at} width={600} height={460} rotate={i % 2 ? 3 : -3} paper={colors.paper} ink={colors.ink} credit={it.credit} grayscale={i < 2} from={i % 2 ? "top" : "bottom"} />
              )}
            </div>
            <div style={{ position: "absolute", left: -60, top: 908, width: 120, height: 120, borderRadius: 999, background: active ? colors.secondary : colors.paper, border: `10px solid ${colors.ink}`, transform: `scale(${0.6 + on * 0.4})`, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Icon name={it.icon} size={74} color={colors.paper} ink={colors.ink} />
            </div>
            <div style={{ position: "absolute", left: -360, width: 720, top: 1050, textAlign: "center", transform: `translateY(${(1 - on) * 60}px)`, opacity: on }}>
              <div style={{ fontFamily: TITLE, fontSize: it.year.length > 5 ? 100 : 130, lineHeight: 1, color: active ? colors.primary : colors.ink }}>{it.year}</div>
              <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 50, color: colors.paper, background: colors.ink, display: "inline-block", padding: "6px 20px", marginTop: 8 }}>{it.label}</div>
            </div>
            {i > 0 && <Sfx src={whoosh} at={it.at - 3} volumeDb={-6} />}
          </div>
        );
      })}
    </div>
  );
};
