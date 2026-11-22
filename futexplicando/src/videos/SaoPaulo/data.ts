import raw from "../../data/sao-paulo.json";

export const D = raw;
export type SceneKey = keyof typeof raw.cenas;
export const A = raw.assets as Record<string, string>;

/** Física da moeda do gancho (compartilhada com o loop final). */
export const COIN = {
  size: 430,
  x: 540,
  apexY: 640,
  floorY: 1050,
  // velocidade angular escolhida para o giro terminar exatamente de frente (múltiplo de 2π) ao parar em pé
  omega: (2 * Math.PI * 3) / 1.92,
};

export const coinAngleAt = (t: number) => {
  const g = D.cenas.gancho.moeda;
  const t0 = g.quiques[0];
  const tEnd = g.emPe;
  const w = COIN.omega;
  if (t <= t0) return w * t;
  if (t >= tEnd) {
    const k = t - tEnd;
    return 0.22 * Math.exp(-k * 9) * Math.sin(k * 38); // pequeno balanço ao parar
  }
  const th1 = w * t0;
  const target = 2 * Math.PI * Math.ceil((th1 + 0.42 * w) / (2 * Math.PI) - 0.01);
  const u = (t - t0) / (tEnd - t0);
  return th1 + (target - th1) * (1 - (1 - u) * (1 - u));
};

export const coinYAt = (t: number) => {
  const g = D.cenas.gancho.moeda;
  const hits = [...g.quiques, g.emPe];
  const heights = [125, 55, 20, 5];
  const t0 = hits[0];
  if (t <= t0) {
    const u = t / t0;
    return COIN.apexY + (COIN.floorY - COIN.apexY) * u * u;
  }
  for (let i = 0; i < hits.length - 1; i++) {
    if (t < hits[i + 1]) {
      const u = (t - hits[i]) / (hits[i + 1] - hits[i]);
      return COIN.floorY - 4 * heights[i] * u * (1 - u);
    }
  }
  return COIN.floorY;
};
