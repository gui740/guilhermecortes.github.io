import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import "./lib/fonts";
import { db, episode, palette, sec } from "./lib/episode";
import { SceneProvider } from "./lib/scene";
import { SCENES } from "./scenes";
import { PaperGrain } from "./components/PaperGrain";
import { Badge } from "./components/Badge";
import { Intro } from "./components/Intro";
import { Captions } from "./components/Captions";
import { Sfx } from "./components/Sfx";

const OVERLAP = 8; // frames de transição entre cenas

const SceneShell: React.FC<{ children: React.ReactNode; enter: boolean; dir: number }> = ({ children, enter, dir }) => {
  const f = useCurrentFrame();
  if (!enter) return <AbsoluteFill>{children}</AbsoluteFill>;
  const p = interpolate(f, [0, OVERLAP], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  // wipe diagonal
  const a = (1 - p) * 140;
  const clip = dir > 0 ? `polygon(${a}% 0, 100% 0, 100% 100%, ${a - 40}% 100%)` : `polygon(0 0, ${100 - a + 40}% 0, ${100 - a}% 100%, 0 100%)`;
  return <AbsoluteFill style={{ clipPath: p < 1 ? clip : undefined }}>{children}</AbsoluteFill>;
};

/** Trilha com "ducking": abaixa enquanto a voz fala e sobe nas pausas (audio.music.gapBoostDb). */
const musicVolume = (f: number, fps: number, total: number) => {
  const music = episode.audio.music as { volumeDb: number; gapBoostDb?: number };
  const t = f / fps;
  const speaking = episode.timing.words.some((w) => t >= w.start - 0.25 && t <= w.end + 0.35);
  const target = music.volumeDb + (speaking ? 0 : music.gapBoostDb ?? 0);
  const fade = interpolate(f, [0, 8, total - 30, total], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return db(target) * fade;
};

export const Episode: React.FC = () => {
  const { durationInFrames, fps } = useVideoConfig();
  const t = episode.timing;
  const music = episode.audio.music;
  const amb = episode.audio.ambience;
  return (
    <AbsoluteFill style={{ background: palette.paper }}>
      {t.scenes.map((st, i) => {
        const sc = episode.scenes.find((s) => s.id === st.id)!;
        const C = SCENES[sc.type];
        const from = sec(st.start) - (i === 0 ? 0 : OVERLAP);
        const dur = sec(st.end) - from;
        const words = t.words.filter((w) => w.scene === st.id);
        return (
          <Sequence key={st.id} from={from} durationInFrames={dur} name={st.id}>
            <SceneProvider id={st.id} startSec={from / fps} endSec={st.end} words={words}>
              <SceneShell enter={i > 0} dir={i % 2 ? 1 : -1}>
                <C scene={sc} />
              </SceneShell>
            </SceneProvider>
            {i > 0 && <Sfx src={episode.audio.whoosh} at={0} volumeDb={-8} />}
          </Sequence>
        );
      })}

      <Captions words={t.words} highlight={palette.secondary} color={palette.paper} bg={palette.ink} />
      <Badge handle={episode.handle} ink={palette.ink} paper={palette.paper} accent={palette.primary} />
      <PaperGrain />
      <Intro handle={episode.handle} colors={[palette.primary, palette.ink, palette.secondary]} ink={palette.ink} paper={palette.paper} />
      <Sequence from={durationInFrames - 16} durationInFrames={16}>
        <Intro reverse handle={episode.handle} colors={[palette.primary, palette.ink, palette.secondary]} ink={palette.ink} paper={palette.paper} />
      </Sequence>

      <Audio src={staticFile(episode.voice.file)} />
      <Audio src={staticFile(music.file)} volume={(f) => musicVolume(f, fps, durationInFrames)} />
      <Audio src={staticFile(amb.file)} volume={(f) => db(amb.volumeDb) * interpolate(f, [0, 20, durationInFrames - 20, durationInFrames], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
    </AbsoluteFill>
  );
};
