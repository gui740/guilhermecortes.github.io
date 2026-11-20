import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { episode, palette } from "../lib/episode";
import { useWordFrame } from "../lib/scene";
import { TITLE, SANS } from "../lib/fonts";
import { Background } from "../components/Background";
import { YearStamp } from "../components/YearStamp";
import { PhotoCard } from "../components/PhotoCard";
import { Icon } from "../components/Icons";
import { Sfx } from "../components/Sfx";

export const FoundationScene: React.FC<{ scene: any }> = ({ scene }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = scene.props;
  const tYear = useWordFrame(p.year, 0, 0.1);
  const tMap = useWordFrame(p.sync?.map, 0, 1.4);
  const tClub = useWordFrame(p.sync?.club, 0, 3.2);
  const tColors = p.colorWords.map((w: string, i: number) => useWordFrame(w, 0, 4.6 + i * 0.4)); // eslint-disable-line
  const red = palette.accent;

  // carimbo encolhe e sobe quando o mapa entra
  const up = spring({ frame: f - tMap, fps, config: { damping: 16 } });
  // mapa
  const mapIn = spring({ frame: f - tMap, fps, config: { damping: 14 } });
  const route = interpolate(f, [tMap + 6, tMap + 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad) });
  const mapOut = spring({ frame: f - tClub, fps, config: { damping: 16 } });
  // faixas tricolor
  const bars = p.flagColors.map((_: string, i: number) => spring({ frame: f - tColors[i], fps, config: { damping: 15, stiffness: 120 } }));
  const photoAside = bars[0];

  return (
    <AbsoluteFill>
      <Background color={palette.paper} />
      {/* faixas da bandeira italiana, entram uma por palavra */}
      <AbsoluteFill style={{ flexDirection: "row" }}>
        {p.flagColors.map((c: string, i: number) => (
          <div key={i} style={{ flex: 1, background: c, transform: `translateY(${(1 - bars[i]) * (i % 2 ? -1 : 1) * 2000}px)`, borderLeft: i ? `6px solid ${palette.ink}` : undefined }}>
            <div style={{ position: "absolute", bottom: 700, width: "100%", textAlign: "center", fontFamily: TITLE, fontSize: 92, color: i === 1 ? palette.ink : palette.paper, transform: "rotate(-90deg)", opacity: 0.9 }}>
              {p.colorWords[i].toUpperCase()}
            </div>
          </div>
        ))}
      </AbsoluteFill>
      <AbsoluteFill style={{ alignItems: "center", top: interpolate(up, [0, 1], [560, 270]) }}>
        <div style={{ transform: `scale(${interpolate(up, [0, 1], [1, 0.55])})`, transformOrigin: "50% 0%" }}>
          <YearStamp year={p.year} sub={p.date} at={tYear} color={red} sound={episode.audio.stamp} />
        </div>
      </AbsoluteFill>
      {/* mapa Itália → São Paulo */}
      {f >= tMap && mapOut < 0.99 && (
        <div style={{ position: "absolute", left: 60, right: 60, top: 640, height: 560, opacity: mapIn * (1 - mapOut), transform: `translateX(${mapOut * -1200}px)` }}>
          <svg width="960" height="560" viewBox="0 0 960 560" style={{ position: "absolute" }}>
            <path d="M820 90 C 640 40, 300 120, 150 450" stroke={palette.ink} strokeWidth={10} fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - route} strokeLinecap="round" />
            <circle cx="820" cy="90" r="26" fill={red} stroke={palette.ink} strokeWidth={6} />
            <circle cx="150" cy="450" r="26" fill={palette.primary} stroke={palette.ink} strokeWidth={6} />
          </svg>
          <div style={{ position: "absolute", left: 600, top: -10, fontFamily: TITLE, fontSize: 76, color: red }}>{p.originLabel}</div>
          <div style={{ position: "absolute", left: 40, top: 480, fontFamily: TITLE, fontSize: 76, color: palette.primary }}>{p.cityLabel}</div>
          <div style={{ position: "absolute", left: 820 - route * 640 - 60, top: 60 + Math.sin(route * Math.PI) * -60 + route * 300, transform: `rotate(${-20 + route * 10}deg)` }}>
            <Icon name="ship" size={130} color={palette.paper} ink={palette.ink} />
          </div>
          <div style={{ position: "absolute", left: 300, top: 300, fontFamily: SANS, fontWeight: 900, fontSize: 44, background: palette.ink, color: palette.paper, padding: "6px 18px", transform: "rotate(-4deg)" }}>IMIGRANTES ITALIANOS</div>
        </div>
      )}
      {/* foto do time + nome */}
      {f >= tClub - 1 && (
        <div style={{ position: "absolute", left: 0, right: 0, top: 560, display: "flex", justifyContent: "center", transform: `translateX(${photoAside * 230}px) rotate(${photoAside * 4}deg) scale(${1 - photoAside * 0.12})` }}>
          <PhotoCard src={scene.image?.src} credit={scene.image?.credit} caption={p.clubName} at={tClub} width={500} height={700} rotate={-4} paper={palette.paper} ink={palette.ink} grayscale objectPosition="50% 20%" />
        </div>
      )}
      <Sfx src={episode.audio.whoosh} at={tMap - 3} volumeDb={-6} />
      {tColors.map((t: number, i: number) => <Sfx key={i} src={episode.audio.whoosh} at={t - 3} volumeDb={-8} />)}
    </AbsoluteFill>
  );
};
