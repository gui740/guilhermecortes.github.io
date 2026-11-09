import React, {createContext, useContext} from 'react';
import {useCurrentFrame} from 'remotion';
import {prog} from './util';

export type Cam = {x: number; y: number; z: number};
export const CamCtx = createContext<Cam>({x: 0, y: 0, z: 0});
export const useCam = () => useContext(CamCtx);

/** Câmera virtual: drift lento e contínuo de `de` até `ate` ao longo de `dur` frames + flutuação mínima.
 *  Nunca para totalmente. */
export const Camera: React.FC<{de: Cam; ate: Cam; dur: number; children: React.ReactNode}> = ({de, ate, dur, children}) => {
  const f = useCurrentFrame();
  const p = prog(f, 0, dur);
  const flut = {x: Math.sin(f / 47) * 5, y: Math.cos(f / 61) * 4};
  const cam = {
    x: de.x + (ate.x - de.x) * p + flut.x,
    y: de.y + (ate.y - de.y) * p + flut.y,
    z: de.z + (ate.z - de.z) * p,
  };
  return <CamCtx.Provider value={cam}>{children}</CamCtx.Provider>;
};
