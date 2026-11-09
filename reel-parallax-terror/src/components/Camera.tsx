import React, {createContext, useContext} from 'react';
import {useCurrentFrame} from 'remotion';
import {prog} from './util';

export type Cam = {x: number; y: number; z: number};
export const CamCtx = createContext<Cam>({x: 0, y: 0, z: 0});
export const useCam = () => useContext(CamCtx);

/** Câmera virtual: drift lento e contínuo de `de` até `ate` ao longo de `dur` frames + flutuação mínima.
 *  Nunca para totalmente. */
export const Camera: React.FC<{de: Cam; ate: Cam; dur: number; punches?: number[]; children: React.ReactNode}> = ({de, ate, dur, punches = [], children}) => {
  const f = useCurrentFrame();
  const p = prog(f, 0, dur);
  const flut = {x: Math.sin(f / 41) * 9, y: Math.cos(f / 53) * 7};
  // "punch": empurrãozinho rápido de câmera (entrada do título do filme)
  const punch = punches.reduce((acc, pf) => {
    const d = f - pf;
    return d < 0 || d > 14 ? acc : acc + Math.sin((d / 14) * Math.PI) * 0.035 * (1 - d / 14);
  }, 0);
  const cam = {
    x: de.x + (ate.x - de.x) * p + flut.x,
    y: de.y + (ate.y - de.y) * p + flut.y,
    z: de.z + (ate.z - de.z) * p + punch,
  };
  return <CamCtx.Provider value={cam}>{children}</CamCtx.Provider>;
};
