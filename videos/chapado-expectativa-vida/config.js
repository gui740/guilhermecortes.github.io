// ============================================================================
//  CONFIGURAÇÃO DO VÍDEO — edite aqui
// ============================================================================

// Formato padrão do canal: vertical (Shorts). Troque para FORMATOS.YOUTUBE para 1920x1080.
const FORMATOS = {
  YOUTUBE: { w: 1920, h: 1080 },
  SHORTS: { w: 1080, h: 1920 },
};
const FORMATO = FORMATOS.SHORTS;
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
  { id: "cena1", nome: "GANCHO", dur: 10, legendas: [
    [0.4, "SE VOCÊ NASCESSE"], [1.6, "NO BRASIL DE 1940..."], [3.4, "PROVAVELMENTE NEM CHEGAVA"],
    [5.2, "NO BOLO DE 45 ANOS."], [7.2, "E HOJE?"], [8.2, "QUANTO A GENTE VIVE?"]] },
  { id: "cena2", nome: "VINHETA", dur: 6, legendas: [] },
  { id: "cena3", nome: "RESPOSTA", dur: 16, legendas: [
    [0.4, "A RESPOSTA OFICIAL (IBGE):"], [3, "EM 2010, 74,4 ANOS."], [6.5, "E SÓ FOI SUBINDO..."],
    [11, "HOJE: 76,6 ANOS."], [13.5, "RECORDE DA HISTÓRIA."]] },
  { id: "cena4", nome: "PLOT TWIST", dur: 14, legendas: [
    [0.4, "SÓ QUE TEM UM BURACO..."], [2.6, "EM 2021..."], [4.5, "DESPENCOU PRA 72,8."],
    [7.6, "A PANDEMIA TIROU"], [9.2, "MAIS DE 3 ANOS"], [10.8, "DA MÉDIA DO BRASILEIRO."]] },
  { id: "cena5", nome: "RECUPERAÇÃO", dur: 14, legendas: [
    [0.4, "DEPOIS, VOLTOU A SUBIR:"], [3.2, "76,6 EM 2024."], [5.4, "E NO MUNDO?"],
    [7.4, "73,3 ANOS (2023)."], [10.4, "O BRASIL TÁ ACIMA DA MÉDIA."]] },
  { id: "cena6", nome: "PENSAMENTO CHAPADO", dur: 20, legendas: [
    [0.4, "MAS PERA..."], [2.2, "SE A MÉDIA ERA 45..."], [4.2, "NINGUÉM FICAVA VELHO?"],
    [6.6, "FICAVA SIM!"], [8.2, "É QUE MUITO BEBÊ"], [9.8, "MORRIA CEDO DEMAIS"],
    [11.6, "E PUXAVA A MÉDIA PRA BAIXO."], [15.2, "QUEM PASSAVA DA INFÂNCIA"], [17.4, "IA BEM MAIS LONGE."]] },
  { id: "cena7", nome: "LADO RUIM", dur: 18, legendas: [
    [0.4, "SÓ QUE VIVER MAIS"], [1.8, "TEM SEU PREÇO."], [3.6, "CORAÇÃO E CÉREBRO:"],
    [5.4, "AS DOENÇAS CRÔNICAS"], [7.0, "FORAM DE 58%"], [8.4, "PRA 74% DAS MORTES."],
    [10.8, "E TEM A MEMÓRIA..."], [13.4, "CADÊ A CHAVE?"], [15.4, "TÁ ATRÁS DE VOCÊ, VÔ."]] },
  { id: "cena8", nome: "FECHAMENTO", dur: 12, legendas: [
    [0.4, "A GENTE VIVE MAIS..."], [2.6, "MAS VIVE MELHOR?"], [5.2, "COMENTA SUA PERGUNTA"],
    [8.4, "QUE EU INVESTIGO CHAPADO."]] },
];

// Transição entre cenas (segundos)
const TRANSICAO = 0.9;

if (typeof module !== "undefined") module.exports = { FORMATOS, FORMATO, FPS, PALETA, CENAS, TRANSICAO };
