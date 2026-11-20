import React from "react";
import { Audio, Sequence, staticFile } from "remotion";
import { db, episode } from "../lib/episode";

/** Toca um efeito sonoro em `at` (frame relativo ao pai). */
export const Sfx: React.FC<{ src?: string; at: number; volumeDb?: number; durationInFrames?: number }> = ({ src, at, volumeDb = 0, durationInFrames = 90 }) => {
  if (!src) return null;
  return (
    <Sequence from={Math.max(0, at)} durationInFrames={durationInFrames} layout="none">
      <Audio src={staticFile(src)} volume={db(episode.audio.sfxVolumeDb + volumeDb)} />
    </Sequence>
  );
};
