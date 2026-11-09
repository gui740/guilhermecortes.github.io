import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {BODY, C, HEAD, textShadow} from '../theme';
import {Counter, Fin, useIn, WordsIn} from '../components/bits';
import {WorldMap} from '../components/WorldMap';

/** Spielberg se arrepende (BBC Desert Island Discs, 2022) */
export const Spielberg: React.FC = () => {
  const p = useIn(2, 12);
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{padding: '400px 150px 0 60px'}}>
      <div style={{fontFamily: HEAD, fontSize: 300, lineHeight: 0.6, color: C.blood, opacity: p}}>“</div>
      <WordsIn
        text="ATÉ O SPIELBERG SE ARREPENDEU."
        start={2}
        every={2}
        highlight={['SPIELBERG']}
        style={{fontFamily: HEAD, fontSize: 130, lineHeight: 1.02, color: C.white, textShadow}}
      />
      <WordsIn
        text="O diretor de Tubarão (1975) diz lamentar a matança de tubarões que veio depois do filme."
        start={18}
        every={2}
        style={{fontFamily: BODY, fontWeight: 800, fontSize: 52, lineHeight: 1.2, color: C.foam, marginTop: 36}}
      />
      <div
        style={{
          fontFamily: BODY,
          fontWeight: 500,
          fontSize: 26,
          color: C.muted,
          marginTop: 30,
          opacity: interpolate(f, [40, 48], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
        }}
      >
        Steven Spielberg à BBC (Desert Island Discs, 2022)
      </div>
    </AbsoluteFill>
  );
};

/** Gancho brasileiro: CEMIT-PE */
export const Brasil: React.FC = () => {
  const f = useCurrentFrame();
  const p = useIn(0, 12);
  return (
    <AbsoluteFill style={{padding: '280px 150px 0 60px'}}>
      <div style={{fontFamily: HEAD, fontSize: 104, color: C.white, lineHeight: 1, opacity: p, textShadow}}>
        E AQUI NO BRASIL?
      </div>
      <div style={{display: 'flex', alignItems: 'center', gap: 26, marginTop: 20}}>
        <Counter to={84} start={40} duration={26} size={230} color={C.bloodBright} />
        <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 40, lineHeight: 1.15, color: C.white}}>
          incidentes com
          <br />
          tubarão em PE
          <br />
          desde 1992
        </div>
      </div>
      <div
        style={{
          marginTop: 22,
          borderRadius: 22,
          overflow: 'hidden',
          border: '3px solid rgba(150,225,230,0.35)',
          height: 420,
          width: 870,
          position: 'relative',
        }}
      >
        <WorldMap
          width={870}
          height={420}
          center={[-38, -8.2]}
          scale={2600}
          pins={[{lon: -34.9, lat: -8.12, label: 'RECIFE E JABOATÃO', kind: 'filmed'}]}
          start={2}
          zoomDur={30}
        />
      </div>
      <WordsIn
        text="Mais da metade em Boa Viagem e Piedade. Raro? Sim. Mas a placa na praia não é enfeite."
        start={34}
        every={2}
        highlight={['placa']}
        style={{fontFamily: BODY, fontWeight: 800, fontSize: 44, lineHeight: 1.2, color: C.white, marginTop: 24, textShadow}}
      />
      <div
        style={{
          position: 'absolute',
          left: 60,
          top: 1520,
          fontFamily: BODY,
          fontWeight: 500,
          fontSize: 22,
          color: C.muted,
          opacity: interpolate(f, [10, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
        }}
      >
        Fonte: CEMIT-PE, dados de jun/2026
      </div>
    </AbsoluteFill>
  );
};

/** CTA final */
export const CTA: React.FC = () => {
  const f = useCurrentFrame();
  const p1 = useIn(2, 11);
  const p2 = useIn(40, 10);
  const finX = interpolate(f, [0, 135], [-380, 1100]);
  const btnPulse = 1 + Math.max(0, Math.sin((f - 50) / 5)) * 0.05 * (f > 50 ? 1 : 0);
  return (
    <AbsoluteFill style={{padding: '360px 150px 0 60px'}}>
      <div
        style={{
          fontFamily: HEAD,
          fontSize: 128,
          lineHeight: 1.02,
          color: C.white,
          textShadow,
          opacity: p1,
          transform: `translateY(${(1 - p1) * 60}px)`,
        }}
      >
        MANDA NO DIRECT
        <br />
        DAQUELE AMIGO
        <br />
        QUE NADA ATÉ
        <br />
        <span style={{whiteSpace: 'nowrap'}}>
          A <span style={{color: C.bloodBright}}>BOIA</span> 🩸
        </span>
      </div>
      <div
        style={{
          marginTop: 70,
          opacity: p2,
          transform: `scale(${interpolate(p2, [0, 1], [0.6, 1]) * btnPulse})`,
          transformOrigin: 'left center',
        }}
      >
        <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 46, color: C.foam, marginBottom: 18}}>
          e segue pra parte 2 💀
        </div>
        <div
          style={{
            display: 'inline-block',
            background: C.blood,
            color: C.white,
            fontFamily: BODY,
            fontWeight: 900,
            fontSize: 64,
            padding: '22px 40px',
            borderRadius: 18,
            boxShadow: '0 12px 50px rgba(255,42,51,0.55)',
          }}
        >
          SEGUIR @talking_horror
        </div>
      </div>
      <div style={{position: 'absolute', left: finX, top: 1330}}>
        <Fin size={230} />
      </div>
    </AbsoluteFill>
  );
};
