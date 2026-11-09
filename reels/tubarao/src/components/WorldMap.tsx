import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {geoGraticule10, geoMercator, geoPath} from 'd3-geo';
import {feature} from 'topojson-client';
import world from 'world-atlas/countries-50m.json';
import type {Pin} from '../data';
import {BODY, C} from '../theme';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const countries = feature(world as any, (world as any).objects.countries) as any;
const graticule = geoGraticule10();

export const WorldMap: React.FC<{
  width: number;
  height: number;
  center: [number, number];
  scale: number;
  pins: Pin[];
  start?: number;
  zoomDur?: number;
}> = ({width, height, center, scale, pins, start = 0, zoomDur = 45}) => {
  const f = useCurrentFrame();
  // com 2+ pins, enquadra automaticamente todos eles
  const target = useMemo(() => {
    if (pins.length < 2) return {scale, center};
    const pr = geoMercator().fitExtent(
      [[120, 90], [width - 120, height - 180]],
      {type: 'MultiPoint', coordinates: pins.map((p) => [p.lon, p.lat])} as any,
    );
    const cc = pr.invert!([width / 2, height / 2]) as [number, number];
    return {scale: pr.scale(), center: cc};
  }, [pins, scale, center, width, height]);
  scale = target.scale;
  center = target.center;
  const k = interpolate(f, [start, start + zoomDur], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const s0 = width / (2 * Math.PI) * 1.05;
  const s = Math.exp(Math.log(s0) + (Math.log(scale) - Math.log(s0)) * k);
  const c0: [number, number] = [center[0] * 0.35, 18];
  const c: [number, number] = [c0[0] + (center[0] - c0[0]) * k, c0[1] + (center[1] - c0[1]) * k];

  const projection = useMemo(
    () => geoMercator().scale(s).center(c).translate([width / 2, height / 2]).clipExtent([[-10, -10], [width + 10, height + 10]]),
    [s, c[0], c[1], width, height],
  );
  const path = geoPath(projection);
  const pinIn = interpolate(f, [start + zoomDur * 0.8, start + zoomDur + 6], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const pts = pins.map((p) => projection([p.lon, p.lat]) as [number, number]);
  const lineP = interpolate(f, [start + zoomDur + 4, start + zoomDur + 26], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  // arcos da locação da história (pin 0) até cada locação de filmagem
  const arcs = pts.slice(1).map(([bx, by]) => {
    const [ax, ay] = pts[0];
    const dx = bx - ax;
    const dy = by - ay;
    const d = Math.hypot(dx, dy) || 1;
    const cx = (ax + bx) / 2 - dy * 0.28;
    const cy = (ay + by) / 2 + dx * 0.28;
    return {d: `M${ax},${ay} Q${cx},${cy} ${bx},${by}`, len: d * 1.25};
  });

  return (
    <svg width={width} height={height} style={{display: 'block'}}>
      <defs>
        <radialGradient id="seaG" cx="50%" cy="45%" r="70%">
          <stop offset="0" stopColor="#0d3a43" />
          <stop offset="1" stopColor="#03141a" />
        </radialGradient>
        <filter id="landGlow">
          <feGaussianBlur stdDeviation="3" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <rect width={width} height={height} fill="url(#seaG)" />
      <path d={path(graticule) ?? ''} fill="none" stroke="rgba(140,210,215,0.10)" strokeWidth={1} />
      <g filter="url(#landGlow)">
        {countries.features.map((ft: any, i: number) => (
          <path key={i} d={path(ft) ?? ''} fill="#1f5864" stroke="rgba(170,235,240,0.7)" strokeWidth={1} />
        ))}
      </g>
      {arcs.map((a, i) => (
        <path
          key={i}
          d={a.d}
          fill="none"
          stroke={C.white}
          strokeWidth={4}
          strokeDasharray={`${a.len} ${a.len}`}
          strokeDashoffset={a.len * (1 - lineP)}
          strokeLinecap="round"
          opacity={0.9}
          style={{filter: 'drop-shadow(0 0 6px rgba(255,255,255,0.6))'}}
        />
      ))}
      {pins.map((p, i) => {
        const [x, y] = pts[i];
        const col = p.kind === 'filmed' ? C.bloodBright : C.white;
        const pulse = ((f - start) % 30) / 30;
        const labelLeft = x > width * 0.62;
        return (
          <g key={i} opacity={pinIn} transform={`translate(${x},${y})`}>
            <circle r={14 + pulse * 46} fill="none" stroke={col} strokeWidth={3} opacity={1 - pulse} />
            <circle r={14 + ((pulse + 0.5) % 1) * 46} fill="none" stroke={col} strokeWidth={2} opacity={1 - ((pulse + 0.5) % 1)} />
            <circle r={13} fill={col} stroke="#000" strokeWidth={3} />
            <text
              x={p.labelPos === 'below' || p.labelPos === 'above' ? 0 : labelLeft ? -26 : 26}
              y={p.labelPos === 'below' ? 52 : p.labelPos === 'above' ? -30 : 10}
              textAnchor={p.labelPos === 'below' || p.labelPos === 'above' ? 'middle' : labelLeft ? 'end' : 'start'}
              fontFamily={BODY}
              fontWeight={900}
              fontSize={30}
              fill={col}
              stroke="#000"
              strokeWidth={6}
              paintOrder="stroke"
            >
              {p.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};
