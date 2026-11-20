import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { episode, palette } from "../lib/episode";
import { useWordFrame } from "../lib/scene";
import { TITLE, SANS } from "../lib/fonts";
import { Background } from "../components/Background";
import { YearStamp } from "../components/YearStamp";
import { NameSwap } from "../components/NameSwap";
import { Newspaper } from "../components/Newspaper";
import { Icon } from "../components/Icons";
import { Sfx } from "../components/Sfx";
import { shake } from "../components/motion";

export const WarScene: React.FC<{ scene: any }> = ({ scene }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = scene.props;
  const w = p.syncWords;
  const tYear = useWordFrame(p.year, 0, 0.1);
  const tNews1 = useWordFrame(w.news1, 0, 1.8);
  const tBoard = useWordFrame(w.board, 0, 3);
  const tStrike = useWordFrame(w.strike, 0, 3.4);
  const tSwap = useWordFrame(w.swap1, 0, 6);
  const tNo = useWordFrame(w.noUse, 0, 7.7);
  const tNews2 = useWordFrame(w.news2, 0, 9);
  const tDanger = useWordFrame(w.danger, 0, 11.6);
  const tD1 = useWordFrame(w.danger1, 0, 12);
  const tD2 = useWordFrame(w.danger2, 0, 12.5);

  const yearUp = spring({ frame: f - tNews1, fps, config: { damping: 16 } });
  const boardIn = spring({ frame: f - tBoard, fps, config: { damping: 13 } });
  const boardOut = spring({ frame: f - tNews2, fps, config: { damping: 16 } });
  const noStamp = spring({ frame: f - tNo, fps, config: { damping: 9, stiffness: 200 } });
  const sk = shake(f, tNo, 16, 10);
  const news2Up = spring({ frame: f - tDanger, fps, config: { damping: 16 } });

  return (
    <AbsoluteFill>
      <Background color={palette.ink} dots="rgba(255,255,255,0.05)" photo={scene.image?.src} photoOpacity={0.12} />
      {/* ano */}
      <AbsoluteFill style={{ alignItems: "center", top: 560 - yearUp * 330, opacity: 1 - news2Up }}>
        <div style={{ transform: `scale(${1 - yearUp * 0.45})`, transformOrigin: "50% 0" }}>
          <YearStamp year={p.year} at={tYear} color={palette.paper} sound={episode.audio.stamp} rotate={6} />
        </div>
      </AbsoluteFill>
      {/* manchete 1 */}
      <AbsoluteFill style={{ alignItems: "center", top: 560 }}>
        <Newspaper at={tNews1} outAt={tBoard} date={p.news1.date} headline={p.news1.headline} paper={palette.paper} ink={palette.ink} />
      </AbsoluteFill>
      {/* placa do nome */}
      {f >= tBoard - 1 && boardOut < 0.99 && (
        <div style={{ position: "absolute", top: 560, left: 0, transform: `translateX(${(1 - boardIn) * 1200 - boardOut * 1300}px) translate(${sk.x}px,${sk.y}px)` }}>
          <NameSwap
            first={p.names[0]} strikeWord={p.strikeWord} second={p.names[1]} final={p.names[2]}
            strikeAt={tStrike} swap1At={tSwap}
            colors={palette} sfx={{ tear: episode.audio.tear, whoosh: episode.audio.whoosh, stamp: episode.audio.stamp, impact: episode.audio.impact }}
          />
          {f >= tNo && (
            <div style={{ position: "absolute", top: 380, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
              <div style={{ fontFamily: TITLE, fontSize: 130, color: palette.paper, background: palette.ink, border: `8px solid ${palette.paper}`, padding: "0 30px", transform: `rotate(-10deg) scale(${2 - noStamp})`, opacity: Math.min(1, noStamp * 1.5) }}>
                {p.noUseText}
              </div>
            </div>
          )}
        </div>
      )}
      {/* manchete 2: guerra */}
      <AbsoluteFill style={{ alignItems: "center", top: 560 - news2Up * 200 }}>
        <div style={{ transform: `scale(${1 - news2Up * 0.25})`, transformOrigin: "50% 0" }}>
          <Newspaper at={tNews2} date={p.news2.date} headline={p.news2.headline} paper={palette.paper} ink={palette.ink} rotate={3} />
        </div>
      </AbsoluteFill>
      {/* o que está em risco */}
      {f >= tDanger && (
        <div style={{ position: "absolute", top: 870, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 50 }}>
          {[{ t: tD1, icon: "stadium", label: p.dangerItems[0] }, { t: tD2, icon: "trophy", label: p.dangerItems[1] }].map((d, i) => {
            const s = spring({ frame: f - d.t, fps, config: { damping: 9, stiffness: 180 } });
            return (
              <div key={i} style={{ width: 420, background: palette.paper, border: `8px solid ${palette.ink}`, padding: "20px 10px 10px", display: "flex", flexDirection: "column", alignItems: "center", transform: `scale(${s}) rotate(${i ? 4 : -4}deg)`, boxShadow: "0 20px 0 rgba(0,0,0,0.4)" }}>
                <Icon name={d.icon} size={170} color={palette.secondary} ink={palette.ink} />
                <div style={{ fontFamily: TITLE, fontSize: 70, color: palette.ink }}>{d.label}</div>
                <div style={{ width: "100%", height: 46, marginTop: 8, background: `repeating-linear-gradient(45deg, ${palette.ink} 0 22px, ${palette.paper} 22px 44px)`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <span style={{ fontFamily: SANS, fontWeight: 900, fontSize: 30, background: palette.ink, color: palette.paper, padding: "0 12px" }}>EM RISCO</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
      <Sfx src={episode.audio.whoosh} at={tNews1 - 3} volumeDb={-4} />
      <Sfx src={episode.audio.whoosh} at={tBoard - 3} volumeDb={-6} />
      <Sfx src={episode.audio.stamp} at={tNo} volumeDb={-2} />
      <Sfx src={episode.audio.impact} at={tNews2 + 4} volumeDb={-8} durationInFrames={60} />
      <Sfx src={episode.audio.stamp} at={tD1} volumeDb={-6} />
      <Sfx src={episode.audio.stamp} at={tD2} volumeDb={-6} />
    </AbsoluteFill>
  );
};
