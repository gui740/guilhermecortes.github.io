# ENTREGA v3a · Parada 2 · EP01 Netflix

O Guilherme aprovou a Parada 1 com a rodada 1. Esta parada segue o prompt v3, com a voz dele e no tempo dele, sem aceleração. **Parei aqui, aguardando o `FIXES.md`.**

**Artifact privado:** https://claude.ai/artifact/8Kk6oFik6obRCd2pWHzBEd. Tem:
- o animatic 0–3 min;
- o SHORT01 e o SHORT02;
- o storyboard com 110 quadros reais;
- a folha lado a lado com as referências;
- o relatório.

## O que foi feito
1. **Narração dele no episódio inteiro.** `pipeline/montar_timeline_v3.py` gera `video/src/timeline_v3.json`.
   - Cada fala da Gacrux virou o bloco correspondente dele (`mapa-blocos.md`).
   - As cenas foram reposicionadas pelas palavras dele: as palavras da voz antiga foram alinhadas com as dele.
   - Total: **13,1 min** (a v2 tinha 14,9). Ele lê cerca de 15% mais rápido que a Gacrux acelerada.
2. **Montagem v3** em `video/src/v3/EpisodioV3.tsx`:
   - cold open, colagem 01:09 e fala TED 03:33 com camadas são cenas v3;
   - os respiros viraram viagem pelo painel, com os reganchos 19, 23 e 43 falados (o 11 não foi gravado);
   - as cenas da v2 entram numa casca v3 (grão, câmera em deriva, página editorial do capítulo);
   - o áudio é feito dentro do Remotion: voz, arquivo, efeitos suavizados com ducking e trilha baixa.
3. **[REGRAVAR]:**
   - Bloco 09: silêncio estimado de 4,3 s, com etiqueta na tela.
   - Bloco 11: o painel fica só com o texto na tela.
4. **Correção da narração:** os blocos 18, 30 e 36 terminavam com o começo de uma leitura abortada do bloco seguinte ("E pra que escolher?", "Mas…", "No Brasil."). Cortei essas sobras.
5. **Storyboard:** 110 quadros renderizados do EpisodioV3 (um por cena, mais três por cena v3), com tempo, fala, componente, transição e imagens. `video/storyboard.mjs`.
6. **Imagens:** `IMAGENS_FALTANDO.md` tem 30 cenas sem imagem real, com candidatas livres que já achei no Commons (Ted Sarandos, Chris Anderson, sede em Los Gatos, debate da CNN 2015, Netflix House, VHS, controle remoto, box de DVD, figurino de Round 6) e os prints que só o Guilherme consegue. As candidatas entram na Parada 3.
7. **Shorts v3a** (`video/src/v3/Shorts.tsx`), composições próprias em 9:16:
   - **SHORT01** (29,9 s): hook do bloco 01 sobre a tela CRT, a lista do TED, a HBO riscada, a carta de 2019 (Fortnite, HBO, YouTube fora do ar) e o loop "a briga é pelo seu tempo".
   - **SHORT02** (40,3 s): hook do bloco 15 com o cursor clicando PULAR ABERTURA no quadro 1, o contador 136.000.000, 15%, 250 séries, 3 países, a TV em ago. 2017, 195 anos com relógio, "cupcake grátis" e a volta ao botão.
8. **Correções feitas no caminho:**
   - a legenda palavra a palavra some 0,7 s depois da fala (antes ficava sobre a fala do TED e misturava blocos);
   - o print da Netflix no SHORT02 aparece inteiro, sem cortar a faixa "Company News";
   - as texturas de grão são pré-carregadas, o que acaba com os quadros que piscavam.

## Relatório de motion (sem grão: 160 px, desfoque, n=0,004)
| Trecho | Parado | Maior trecho parado | Trocas fortes/min |
|---|---|---|---|
| Episódio 0:00–3:00 · v2 | 55% | 13,4 s | 11,7 |
| Episódio 0:00–3:00 · v3a | **35%** | **7,1 s** | 13,3 |
| SHORT01 · v2 → v3a | 53% → **8%** | 7,6 s → **1,3 s** | 7,5 → 4,0 |
| SHORT02 · v2 → v3a | 80% → **16%** | 10,5 s → **2,1 s** | 1,3 → 1,5 |

- **O animatic reprova.** Todos os trechos parados estão em cenas v2 ainda não reconstruídas:
  - envelope (0:18, 6,0 s);
  - linha da TV e evidência do Jenner (0:50–1:03);
  - títulos 2005, "Como ter certeza?" e "Quem é dono…";
  - medidor (2:25, 7,1 s);
  - "Todos os episódios" (2:44, 5,4 s).
- As cenas v3 ficam abaixo de 2,5 s parados.
- Os Shorts passam nos 2,5 s, mas ainda ficam acima de 5% parado:
  - SHORT01: 8%;
  - SHORT02: 16%, nos planos de número grande, que ganham deriva na próxima rodada.
- A medida de "trocas fortes" (limiar de cena 0,3) conta pouco as trocas sobre o branco.
- Transições usadas: painel, CRT liga e desliga, máscara, empurrão e corte com som.

## Folha lado a lado
`lado_a_lado_v3a_referencias.jpg` no artifact: 6 quadros v3a e 6 das referências.

**Falta:**
- **Escala:** nas referências, rosto ou objeto ocupa 50–70% da altura. Nas cenas v2 (cheque, proibições, títulos), 20–30%.
- **Imagem real em toda frase.**
- **Troca forte a cada 1,2–2,8 s.**

É o Passo 3 (correções cena a cena), previsto para a Parada 3.

## Decisões tomadas sem consulta
1. Hooks dos Shorts: o S01 e o S02 não foram gravados. Usei os blocos 01 e 15, que dizem o mesmo fato. A diferença é que o 15 diz "num dia típico", e o hook do prompt dizia "por dia".
2. O bloco 02 entra inteiro no cold open, como na rodada 1 aprovada.
3. Os reganchos sem voz (bloco 11) ficam só com o texto na tela.
4. Os respiros curtos (capítulos sem regancho) viraram painel de 2,6 s, sem fala.
5. O efeito de rádio ou CRT na voz ainda não foi aplicado. Entra na Parada 3, nas falas que citam documento.
6. As cenas v2 foram mantidas na casca v3 nesta parada, em vez de reconstruídas, para o Guilherme aprovar a estrutura e o tempo antes do Passo 3.
