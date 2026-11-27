// ============================================================================
//  CONFIGURAÇÃO DO VÍDEO — edite aqui
// ============================================================================

// Troque para FORMATOS.SHORTS para gerar em 1080x1920.
const FORMATOS = {
  YOUTUBE: { w: 1920, h: 1080 },
  SHORTS: { w: 1080, h: 1920 },
};
const FORMATO = FORMATOS.YOUTUBE;
const FPS = 30;

// Paleta do canal (colagem de papel)
const PALETA = {
  creme: "#efe3c6",
  papel: "#f7f1e1",
  tinta: "#1b1712",      // preto de gravura
  tomate: "#d9452b",
  mostarda: "#e2a72e",
  petroleo: "#1f5f6b",
  rosa: "#e9a598",
  pele: "#f0cfa6",
};

// Cenas: uma por bloco do roteiro. Ajuste "dur" (segundos) para casar com a narração.
// "legendas": [tempo dentro da cena (s), texto]. Cada bloco aparece até o próximo; 3–5 palavras.
const CENAS = [
  {
    id: "cena1", nome: "GANCHO", dur: 12,
    legendas: [
      [0.4, "SE VOCÊ NASCESSE"],
      [1.6, "NO BRASIL DE 1940..."],
      [3.6, "PROVAVELMENTE NEM CHEGAVA"],
      [5.4, "NO SEU BOLO"],
      [6.6, "DE 45 ANOS."],
      [8.6, "E HOJE? QUANTO A GENTE"],
      [10.2, "VIVE DE VERDADE?"],
    ],
  },
  { id: "cena2", nome: "VINHETA", dur: 8, legendas: [] },
  { id: "cena3", nome: "RESPOSTA", dur: 18, legendas: [] },
  { id: "cena4", nome: "PLOT TWIST", dur: 16, legendas: [] },
  { id: "cena5", nome: "RECUPERAÇÃO", dur: 14, legendas: [] },
  { id: "cena6", nome: "PENSAMENTO CHAPADO", dur: 20, legendas: [] },
  { id: "cena7", nome: "LADO RUIM", dur: 18, legendas: [] },
  { id: "cena8", nome: "FECHAMENTO", dur: 12, legendas: [] },
];

// Transição entre cenas (segundos)
const TRANSICAO = 0.9;

if (typeof module !== "undefined") module.exports = { FORMATOS, FORMATO, FPS, PALETA, CENAS, TRANSICAO };
