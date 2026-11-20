import React from "react";
import { AbsoluteFill, Sequence, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { episode, palette } from "../lib/episode";
import { useWordFrame } from "../lib/scene";
import { TITLE, SANS } from "../lib/fonts";
import { Background } from "../components/Background";
import { NameSwap } from "../components/NameSwap";
import { Pitch } from "../components/Pitch";
import { PhotoCard } from "../components/PhotoCard";
import { YearStamp } from "../components/YearStamp";

export const ArrancadaScene: React.FC<{ scene: any }> = ({ scene }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = scene.props;
  const w = p.syncWords;
  const tBorn = useWordFrame(w.born, 0, 1.4);
  const tPitch = useWordFrame(w.pitch, 0, 2.9);
  const tStakes = useWordFrame(w.stakes, 0, 5.2);
  const tAway = useWordFrame(w.away, 1, 6.6);
  const tFlag = useWordFrame(w.flag, 0, 8.5);
  const tScore = useWordFrame(w.score, 0, 9.3);
  const tLeave = useWordFrame(w.leave, 0, 11);
  const tChamp = useWordFrame(w.champion, 0, 13.3);

  const boardOut = spring({ frame: f - tPitch, fps, config: { damping: 16 } });
  const pitchIn = spring({ frame: f - tPitch, fps, config: { damping: 15 } });
  const chip = spring({ frame: f - tStakes, fps, config: { damping: 10, stiffness: 170 } });
  const champ = spring({ frame: f - tChamp, fps, config: { damping: 12 } });

  return (
    <AbsoluteFill>
      <Background color={palette.paper} />
      {boardOut < 0.99 && (
        <div style={{ position: "absolute", top: 560, left: 0, transform: `translateY(${boardOut * -1500}px)` }}>
          <NameSwap
            first={p.names[0]} strikeWord={p.strikeWord} second={p.names[1]} final={p.names[2]} finalSub={p.nameDate}
            strikeAt={-100} swap1At={-100} swap2At={tBorn} startStage={1} crest={p.crest}
            colors={palette} sfx={{ whoosh: episode.audio.whoosh, impact: episode.audio.impact }}
          />
        </div>
      )}
      {f >= tPitch - 1 && (
        <>
          <div style={{ position: "absolute", top: 250, left: 0, right: 0, display: "flex", justifyContent: "center", transform: `translateY(${(1 - pitchIn) * -400}px)` }}>
            <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 40, background: palette.ink, color: palette.paper, padding: "8px 22px", letterSpacing: 2 }}>{p.dateLabel}</div>
          </div>
          <div style={{ position: "absolute", top: 330, left: 90, transform: `translateY(${(1 - pitchIn) * 1800}px) scale(0.86)`, transformOrigin: "50% 0" }}>
            <Sequence from={tPitch} layout="none">
            <Pitch
              homeLabel={p.home} awayLabel={p.away} score={p.score as [number, number]}
              homeColor={palette.primary} awayColor={palette.rival} grass={palette.secondary} grassDark="#27954A" ink={palette.ink} paper={palette.paper} accent={palette.accent}
              enterAwayAt={tAway - tPitch} flagAt={tFlag - tPitch} scoreAt={tScore - tPitch} leaveAt={tLeave - tPitch}
              sfx={{ whoosh: episode.audio.whoosh, crowd: episode.audio.crowd }}
            />
            </Sequence>
          </div>
          {f >= tStakes && f < tFlag && (
            <div style={{ position: "absolute", top: 820, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
              <div style={{ fontFamily: TITLE, fontSize: 96, background: palette.paper, color: palette.ink, border: `8px solid ${palette.ink}`, padding: "0 30px", transform: `scale(${chip}) rotate(-4deg)` }}>{p.stakesText}</div>
            </div>
          )}
        </>
      )}
      {f >= tChamp && (
        <AbsoluteFill style={{ background: `rgba(17,17,17,${champ * 0.55})` }}>
          <div style={{ position: "absolute", top: 380, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
            <PhotoCard src={scene.image?.src} credit={scene.image?.credit} at={tChamp} width={820} height={520} rotate={-3} paper={palette.paper} ink={palette.ink} grayscale from="top" />
          </div>
          <div style={{ position: "absolute", top: 1000, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
            <YearStamp year={p.championText} at={tChamp + 6} color={palette.secondary} size={150} rotate={-6} sound={episode.audio.stamp} />
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
