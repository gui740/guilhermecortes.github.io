import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Movie} from '../data';
import {BODY, C, HEAD, textShadow} from '../theme';
import {Counter, StreamBadge, Tag, WordsIn} from '../components/bits';
import {WorldMap} from '../components/WorldMap';


export const MovieScene: React.FC<{m: Movie; dur: number}> = ({m, dur}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  // tudo sincronizado com a narração (data.ts → cues, em segundos)
  const cC = Math.round(m.cues.curiosity * fps);
  const cN = Math.round(m.cues.numbers * fps);
  const cP = Math.round(m.cues.platform * fps);
  const SWITCH = cN - 6; // mapa entra quando a voz chega no número
  const head = spring({frame: f - 4, fps, config: {damping: 13, mass: 0.6}});
  const poster = spring({frame: f - 8, fps, config: {damping: 15, mass: 0.8}});
  const out = interpolate(f, [SWITCH - 6, SWITCH + 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });
  const mapIn = spring({frame: f - SWITCH, fps, config: {damping: 16, mass: 0.8}});
  const titleSize = m.subtitle ? 112 : Math.min(150, Math.round(1640 / m.title.length));
  const kenburns = interpolate(f, [0, SWITCH], [1.0, 1.08], {extrapolateRight: 'clamp'});
  const counterOut = interpolate(f, [cP - 10, cP], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  void dur;

  return (
    <AbsoluteFill>
      {/* poster gigante desfocado ao fundo */}
      <AbsoluteFill style={{opacity: 0.22 * (1 - out * 0.6)}}>
        <Img
          src={staticFile(m.poster)}
          style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(28px) saturate(0.7)', transform: `scale(${1.2 * kenburns})`}}
        />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(2,10,13,0.2) 0%, rgba(2,10,13,0.75) 70%)'}} />

      {/* CABEÇALHO */}
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 150,
          top: 262,
          opacity: head,
          transform: `translateY(${(1 - head) * -50}px)`,
        }}
      >
        <Tag>{m.tag}</Tag>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 18, marginTop: 8, whiteSpace: 'nowrap'}}>
          <div style={{fontFamily: HEAD, fontSize: titleSize, lineHeight: 1.02, color: C.white, textShadow}}>
            {m.title}
          </div>
          <div style={{fontFamily: HEAD, fontSize: Math.max(56, titleSize * 0.42), color: C.bloodBright, textShadow}}>
            {m.year}
          </div>
        </div>
        {m.subtitle ? (
          <div style={{fontFamily: HEAD, fontSize: 48, lineHeight: 1, color: C.foam, marginTop: -2, textShadow}}>{m.subtitle}</div>
        ) : null}
      </div>

      {/* FASE 1: pôster + curiosidade */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, transform: `translateX(${-out * 1100}px)`, opacity: 1 - out}}>
        <div
          style={{
            position: 'absolute',
            left: 60,
            top: 530,
            width: 400,
            height: 570,
            transform: `translateY(${(1 - poster) * 300}px) rotate(${interpolate(poster, [0, 1], [-12, -3])}deg) scale(${kenburns})`,
            opacity: poster,
            borderRadius: 14,
            overflow: 'hidden',
            boxShadow: `0 30px 80px rgba(0,0,0,0.75), 0 0 0 5px ${C.white}, 0 0 50px rgba(208,18,27,0.5)`,
          }}
        >
          <Img src={staticFile(m.poster)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </div>
        <div style={{position: 'absolute', left: 500, right: 150, top: 540}}>
          <div
            style={{
              fontFamily: BODY,
              fontWeight: 900,
              fontSize: 28,
              letterSpacing: 4,
              color: C.bloodBright,
              opacity: interpolate(f, [cC - 8, cC - 2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
            }}
          >
            BASTIDOR 💀
          </div>
          <WordsIn
            text={m.curiosity}
            start={cC - 2}
            every={3}
            style={{fontFamily: BODY, fontWeight: 800, fontSize: 46, lineHeight: 1.16, color: C.white, marginTop: 10, textShadow}}
          />
        </div>
      </div>

      {/* FASE 2: mapa + número + onde assistir */}
      {f >= SWITCH - 2 ? (
        <>
          <div
            style={{
              position: 'absolute',
              left: 60,
              top: 500,
              width: 870,
              height: 640,
              borderRadius: 26,
              overflow: 'hidden',
              border: '3px solid rgba(150,225,230,0.35)',
              boxShadow: '0 30px 80px rgba(0,0,0,0.7)',
              transform: `translateX(${(1 - mapIn) * 1100}px)`,
            }}
          >
            <WorldMap
              width={870}
              height={640}
              center={m.map.center}
              scale={m.map.scale}
              pins={m.map.pins}
              start={SWITCH + 2}
              zoomDur={40}
            />
            {/* legenda */}
            <div
              style={{
                position: 'absolute',
                left: 0,
                right: 0,
                bottom: 0,
                padding: '16px 22px',
                background: 'linear-gradient(180deg, rgba(2,10,13,0) 0%, rgba(2,10,13,0.92) 40%)',
                fontFamily: BODY,
                fontSize: 31,
                lineHeight: 1.3,
                color: C.white,
                opacity: interpolate(f, [SWITCH + 40, SWITCH + 50], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
              }}
            >
              <div>
                <span style={{fontWeight: 900, color: C.foam}}>● NA HISTÓRIA:</span>{' '}
                <span style={{fontWeight: 700}}>{m.map.legend.story}</span>
              </div>
              <div>
                <span style={{fontWeight: 900, color: C.bloodBright}}>● FILMADO EM:</span>{' '}
                <span style={{fontWeight: 700}}>{m.map.legend.filmed}</span>
              </div>
            </div>
          </div>
          <div style={{position: 'absolute', left: 60, right: 150, top: 1175, opacity: 1 - counterOut, transform: `translateX(${-counterOut * 900}px)`}}>
          <Counter
            to={m.counter.value}
            decimals={m.counter.decimals}
            prefix={m.counter.prefix}
            suffix={m.counter.suffix}
            start={cN}
            duration={45}
            size={170}
          />
          <div
            style={{
              fontFamily: BODY,
              fontWeight: 800,
              fontSize: 44,
              color: C.white,
              marginTop: 4,
              opacity: interpolate(f, [cN + 10, cN + 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
              textShadow,
            }}
          >
            {m.counterLabel}
          </div>
          <div
            style={{
              fontFamily: BODY,
              fontWeight: 500,
              fontSize: 34,
              color: C.foam,
              marginTop: 8,
              opacity: interpolate(f, [cN + 30, cN + 38], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
            }}
          >
            {m.counterNote}
          </div>
        </div>
          <div style={{position: 'absolute', left: 60, right: 150, top: 1180}}>
            <StreamBadge streams={m.streams} start={cP} />
          </div>
        </>
      ) : null}
    </AbsoluteFill>
  );
};
