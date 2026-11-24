/** Tempos da história: resolve "em"/"de" (palavra da fala ou segundos) para segundos na cena. */
export type Palavra = { w: string; t: number; f: number };
export type TemposCena = { id: string; fala: number; dur: number; audio: string; palavras: Palavra[] };

export const norm = (s: string) =>
  s
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9º]/g, "");

/** Tempo (s, na cena) da palavra `chave` a partir de `desde`; número = segundos a partir de `base`. */
export const quando = (pal: Palavra[], chave: string | number | undefined, base: number, desde = 0): number => {
  if (chave === undefined) return base;
  if (typeof chave === "number") return base + chave;
  const k = norm(chave);
  const exata = pal.find((p) => p.t >= desde - 0.01 && norm(p.w) === k) ?? pal.find((p) => norm(p.w) === k);
  if (exata) return exata.t;
  const parcial = pal.find((p) => p.t >= desde - 0.01 && norm(p.w).startsWith(k)) ?? pal.find((p) => norm(p.w).startsWith(k));
  return parcial ? parcial.t : base;
};

/** Início de cada plano (s, na cena). */
export const iniciosPlanos = (pal: Palavra[], planos: { de?: string }[]) => {
  const ini: number[] = [];
  planos.forEach((p, i) => {
    if (i === 0) ini.push(0);
    else ini.push(Math.max(ini[i - 1] + 0.3, quando(pal, p.de, ini[i - 1], ini[i - 1]) - 0.05));
  });
  return ini;
};

export const easeInOut = (p: number) => {
  const x = Math.min(1, Math.max(0, p));
  return x * x * (3 - 2 * x);
};
