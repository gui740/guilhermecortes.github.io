// =====================================================================================
//  TIMING DO REEL — todos os tempos num lugar só.
//
//  Como funciona:
//   • A duração de cada cena vem AUTOMATICAMENTE da narração (src/data/narracao.json,
//     gerado por scripts/narracao.py + scripts/ajustar_narracao.py).
//   • Cena = [entrada/transição] + [narração] + [respiro] (+ extra manual) + [saída/transição]
//   • Cenas vizinhas se sobrepõem durante a TRANSICAO (a saída de uma é a entrada da outra).
//
//  Para ajustar à mão, mexa só nas constantes abaixo:
// =====================================================================================

export const FPS = 30;
export const LARGURA = 1080;
export const ALTURA = 1920;

/** Respiro (s) depois da narração de cada cena, antes da transição começar. */
export const RESPIRO_S = 0.5;

/** Duração (frames) das transições: câmera seguindo a seta, papel rasgando, zoom-out do mural. 18 = 0,6s */
export const TRANSICAO = 18;

/** Atraso (s) da primeira fala do gancho (dá tempo da primeira polaroide cair). */
export const INICIO_GANCHO_S = 0.3;

/** Tempo EXTRA (s) por cena, somado ao tempo da narração. Use para segurar uma cena mais tempo. */
export const EXTRA_S: Record<CenaId, number> = {
  gancho: 0,
  possum: 0,
  calvaire: 0,
  hagazussa: 0,
  fechamento: 1.2, // segura o CTA na tela depois da última fala
};

/** Desloca a entrada dos elementos em relação à palavra falada (frames). Negativo = antes da palavra. */
export const ANTECIPA_PALAVRA = -4;

// ------------------------------------------------------------------------------------
export const ORDEM = ['gancho', 'possum', 'calvaire', 'hagazussa', 'fechamento'] as const;
export type CenaId = (typeof ORDEM)[number];

export type Palavra = {w: string; s: number; e: number};
export type Narracao = {voz: string; cenas: Record<string, {dur: number; palavras: Palavra[]}>};

export type CenaTiming = {
  id: CenaId;
  inicio: number;   // frame absoluto onde a cena começa (inclui a transição de entrada)
  duracao: number;  // frames totais da cena (inclui a transição de saída)
  narr0: number;    // frame LOCAL onde a narração começa
  saida: number;    // frame LOCAL onde começa a transição de saída
  palavras: Palavra[];
  narrDur: number;  // s
};

export const montarTiming = (narr: Narracao) => {
  let t = 0;
  const cenas = {} as Record<CenaId, CenaTiming>;
  ORDEM.forEach((id, i) => {
    const n = narr.cenas[id];
    const entrada = i === 0 ? Math.round(INICIO_GANCHO_S * FPS) : TRANSICAO;
    const conteudo = entrada + Math.ceil((n.dur + RESPIRO_S + EXTRA_S[id]) * FPS);
    const ultima = i === ORDEM.length - 1;
    const duracao = conteudo + (ultima ? 0 : TRANSICAO);
    cenas[id] = {id, inicio: t, duracao, narr0: entrada, saida: conteudo, palavras: n.palavras, narrDur: n.dur};
    t += conteudo; // a próxima começa durante a nossa saída
  });
  return {cenas, total: t};
};

const limpa = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');

/** Frame LOCAL (da cena) em que a palavra `alvo` (n-ésima ocorrência) começa a ser falada. */
export const quando = (c: CenaTiming, alvo: string, n = 0, fim = false) => {
  const a = limpa(alvo);
  const hits = c.palavras.filter((p) => limpa(p.w) === a);
  const p = hits[Math.min(n, hits.length - 1)];
  if (!p) return c.narr0;
  return c.narr0 + Math.round((fim ? p.e : p.s) * FPS) + ANTECIPA_PALAVRA;
};
