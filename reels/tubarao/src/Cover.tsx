import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {Ocean} from './components/Ocean';
import {Tag} from './components/bits';
import {BODY, C, HEAD, textShadow} from './theme';

/** Capa 1080x1920. Texto concentrado no recorte 3:4 do grid (y 240–1680). */
export const Cover: React.FC = () => {
  const posters = ['tubarao.jpg', 'meg.jpg', 'sena.jpg'];
  return (
    <AbsoluteFill style={{background: C.abyss}}>
      <Ocean />
      <AbsoluteFill style={{alignItems: 'center'}}>
        <div style={{position: 'absolute', top: 300, left: 70, right: 70, textAlign: 'center'}}>
          <Tag style={{fontSize: 34}}>TEM NO STREAMING · BRASIL</Tag>
          <div style={{fontFamily: HEAD, fontSize: 200, lineHeight: 1.24, color: C.white, marginTop: 22, textShadow}}>
            <span style={{color: C.bloodBright}}>3</span> FILMES
            <br />
            DE TUBARÃO
          </div>
          <div style={{fontFamily: BODY, fontWeight: 900, fontSize: 62, lineHeight: 1.1, color: C.white, marginTop: 18, textShadow}}>
            pra você nunca mais
            <br />
            entrar no mar <span style={{color: C.bloodBright}}>tranquilo</span> 🩸
          </div>
        </div>
        <div style={{position: 'absolute', top: 1040, left: 0, right: 0, height: 560}}>
          {posters.map((p, i) => {
            const rot = (i - 1) * 9;
            const x = 540 - 170 + (i - 1) * 270;
            return (
              <div
                key={p}
                style={{
                  position: 'absolute',
                  left: x,
                  top: i === 1 ? 0 : 50,
                  width: 340,
                  height: 485,
                  transform: `rotate(${rot}deg)`,
                  borderRadius: 14,
                  overflow: 'hidden',
                  zIndex: i === 1 ? 2 : 1,
                  boxShadow: `0 30px 70px rgba(0,0,0,0.8), 0 0 0 5px ${C.white}`,
                }}
              >
                <Img src={staticFile(p)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
              </div>
            );
          })}
        </div>
        <div
          style={{
            position: 'absolute',
            top: 1760,
            left: 0,
            right: 0,
            textAlign: 'center',
            fontFamily: BODY,
            fontWeight: 800,
            fontSize: 36,
            color: C.foam,
          }}
        >
          @talking_horror
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
