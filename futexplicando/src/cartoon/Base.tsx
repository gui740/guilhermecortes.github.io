import React from "react";
import { AbsoluteFill, interpolate, Sequence, useCurrentFrame, useVideoConfig } from "remotion";

/** Câmera nunca parada: push-in lento ou panorâmica durante toda a cena. */
export const CameraMove: React.FC<{
  children: React.ReactNode;
  tipo?: "zoom" | "panEsq" | "panDir" | "sobe" | "zoomOut";
  forca?: number;
  origem?: string;
}> = ({ children, tipo = "zoom", forca = 1, origem = "50% 45%" }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const u = Math.min(1, frame / Math.max(1, durationInFrames));
  const z = interpolate(u, [0, 1], [1.04, 1.04 + 0.12 * forca]);
  let style: React.CSSProperties = {};
  if (tipo === "zoom") style = { scale: `${z}` };
  if (tipo === "zoomOut") style = { scale: `${interpolate(u, [0, 1], [1.04 + 0.14 * forca, 1.04])}` };
  if (tipo === "panEsq") style = { scale: "1.14", translate: `${interpolate(u, [0, 1], [50, -50]) * forca}px 0` };
  if (tipo === "panDir") style = { scale: "1.14", translate: `${interpolate(u, [0, 1], [-50, 50]) * forca}px 0` };
  if (tipo === "sobe") style = { scale: "1.12", translate: `0 ${interpolate(u, [0, 1], [40, -40]) * forca}px` };
  return <AbsoluteFill style={{ transformOrigin: origem, ...style }}>{children}</AbsoluteFill>;
};

/** Cortes internos de uma cena (cada plano com crossfade de ~6 frames). */
export const Shots: React.FC<{ planos: { dur: number; el: React.ReactNode }[] }> = ({ planos }) => {
  const { fps, durationInFrames } = useVideoConfig();
  const total = planos.reduce((a, p) => a + p.dur, 0);
  let acc = 0;
  return (
    <AbsoluteFill>
      {planos.map((p, i) => {
        const from = Math.round((acc / total) * durationInFrames);
        acc += p.dur;
        const to = Math.round((acc / total) * durationInFrames);
        const extra = i < planos.length - 1 ? 6 : 0;
        return (
          <Sequence key={i} from={from} durationInFrames={Math.max(1, to - from + extra)}>
            <FadeIn skip={i === 0}>{p.el}</FadeIn>
          </Sequence>
        );
      })}
      <span style={{ display: "none" }}>{fps}</span>
    </AbsoluteFill>
  );
};

export const FadeIn: React.FC<{ children: React.ReactNode; skip?: boolean; frames?: number }> = ({ children, skip, frames = 6 }) => {
  const frame = useCurrentFrame();
  const o = skip ? 1 : interpolate(frame, [0, frames], [0, 1], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};

/** Pop-in com mola simples (escala). */
export const usePop = (startFrame = 0, dur = 10) => {
  const frame = useCurrentFrame();
  const t = (frame - startFrame) / dur;
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  return 1 + Math.sin(t * Math.PI) * 0.18 - (1 - t) * (1 - t) * 1.0 + (1 - t) * 0.0;
};

export const pop = (frame: number, start: number, dur = 10) => {
  const t = (frame - start) / dur;
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  const e = 1 - Math.pow(1 - t, 3);
  return e + Math.sin(t * Math.PI) * 0.15;
};
