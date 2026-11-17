# ENTREGA v3 · Parada 1 (amostra) · EP01 Netflix

Rodada de correção de edição (prompt v3 do gerente), feita até a Parada 1, como pedido. **A v2 não foi tocada.** Tudo novo está em `video/src/v3/` e em `video/out/v3a/` (mídia fora do Git).

## O que foi feito

**Passo 0**
- `brand-izoton/CLAUDE.md` criado com o sistema do canal e lido.

**Passo 1**
- R1 a R4 estudadas quadro a quadro (877 quadros, um a cada 0,25 s). Os números estão em `brand-izoton/GUIA_DE_ESTILO.md`.
- Os 10 itens da gramática do gerente foram confirmados.
- Medida principal: as referências têm movimento em 91–92% dos quadros (R4, 63%), nenhum trecho parado acima de 1 s e uma troca forte a cada 1,2–2,8 s.

**Passo 2: sistema de motion v3**
- `kit.tsx`: grão animado, papel, câmera com deriva, camadas com parallax, recortes em degraus de stop-motion (10 poses/s, tremor de 1,5 px), cards com sombra e perspectiva, palavra-chave em caixa, título em dois pesos, contador, terminal, cursor, página editorial, dossiê lateral e carimbo.
- `transicoes.tsx`: tela CRT com liga e desliga, máscara de revelação, empurrão de página e painel do arquivo (10 cartões, traço âmbar na ligação, câmera voando com desfoque e mergulho).
- **Tempo por palavra (Whisper):** as linhas novas estão em `narr_v3/palavras_v3*.json` e as 52 falas da v2 em `palavras_v2.json`. Toda entrada da amostra cai na palavra.
- **Linhas novas na voz Gacrux** (um pedido por linha, acelerada 7%, como a v2):
  - linha 1 do cold open;
  - linha 2 do cold open (promessa);
  - regancho do capítulo 3;
  - hook do SHORT 02.
- **Imagens reais (Passo 2c):** 4 imagens do Wikimedia Commons (Reed Hastings em 2014 e 2015, envelope de DVD da Netflix, box de DVD), recortadas e tratadas. Estão em `IMAGENS.md` e no `DIREITOS.md`.

**Parada 1: os 5 trechos**

| # | Trecho | Duração | O que entrou |
|---|---|---|---|
| 1 | Cold open novo | 28,6 s | frase literal em tipografia grande, ficha da entrevista caindo, recorte de Hastings, TED na tela CRT com a lista acendendo na palavra, HBO riscada, painel do arquivo nascendo, recibo da "conta", carimbo do canal (2 s) |
| 2 | Colagem 01:09 | 13,9 s | 4 batidas: envelope de DVD + disco girando + carimbo "PRAZO DE VALIDADE" → "MÉTODO" em caixa → título em dois pesos via empurrão de página → recorte de Hastings + ficha da fala do TED + linha DVD → STREAMING + carimbo "FOUNDING ETHOS" |
| 3 | Fala TED 03:33 (25 s) com camadas | 25,4 s | dossiê lateral, card do box de DVD, destaques HBO, BINGE e TV LINEAR NÃO FAZ na palavra, 3 inserts (box sets, terminal "PRÓXIMO EPISÓDIO", pôster de House of Cards com "TODOS DE UMA VEZ"), sem cortar o áudio |
| 4 | Transição cap. 2 → 3 | 10,5 s | fim da fala T06 → CRT desliga → painel: cartão 02, traço âmbar até o 03, câmera voa com desfoque, mergulho → página do capítulo 3, com o regancho falado |
| 5 | SHORT 02, primeiros 5 s | 5,6 s | cursor clicando PULAR ABERTURA no quadro 1, hook falado novo, legenda palavra a palavra com caixa no 136, MILHÕES e DIA, contador 136.000.000 cabendo na largura, "POR DIA" em âmbar |

## Relatório de motion (mesmo trecho na v2 × amostra v3)

Duas medidas com `freezedetect` (d=1 s):

| Trecho | v2: parado (padrão) | v3: parado (padrão) | v2: parado (sem grão) | v3: parado (sem grão) | v2: maior trecho parado | v3: maior trecho parado |
|---|---|---|---|---|---|---|
| Cold open (0–28,6 s) | 59% | 0% | 60% | 47% | 7,6 s | 3,0 s |
| Colagem 01:09 | 95% | 0% | 98% | 32% | 13,6 s | 2,6 s |
| Fala TED 03:33 | 0% | 0% | 0% | 16% | 0 s | 1,9 s |
| Transição cap. 2 → 3 | 68% | 0% | 67% | 12% | 2,9 s | 1,3 s |
| SHORT 02 (0–5,6 s) | 51% | 0% | 52% | 0% | 2,9 s | 0 s |

- **Medida padrão** (n=0,002, vídeo a 480 px): a v3 passa em tudo, mas o grão animado muda a imagem em todo quadro e ajuda a passar.
- **Medida sem grão** (vídeo a 160 px com desfoque, n=0,004): mais rígida, conta só movimento real.

Como ler:
- **Eventos visuais** (contados na definição das cenas: recorte, destaque, número, insert, transição):
  - cold open: cerca de 25 em 28,6 s (cerca de 52/min; a v2 tinha cerca de 8, ou 17/min);
  - colagem: 11 em 13,9 s (cerca de 47/min);
  - fala TED: 14 em 25 s (cerca de 34/min);
  - SHORT 02: 7 em 5,6 s.
- **Laterais ocupadas:** cerca de 90% do tempo nos 5 trechos (dossiê, cards, recortes, painel). Na v2, quase sempre vazias.
- **Ainda reprova na medida sem grão:**
  - O cold open tem um trecho de **3,0 s** (19,9–22,9 s, as palavras-chave sobre o painel) e um de 2,2 s (24,3 s). Estão acima da regra de 2,5 s e da meta de 5% parado.
  - **Correção para a próxima rodada:** os cartões do painel acendem um a um em "as jogadas", o recibo entra mais cedo e a HBO sai com movimento.
  - A colagem tem 2,6 s parados no começo (envelope já pousado, antes do carimbo).

## Desvios e decisões tomadas sem consulta
1. **Cold open com 28,6 s** (meta: 25 s). A Gacrux lê a linha 1 em 8,2 s; o prompt previa 3 s. A sugestão de encurtar a linha está no `PERGUNTAS.md`.
2. **Clipes do cold open (28,6 s) e da fala TED (25,4 s)** passam dos 10–20 s pedidos. Entreguei o trecho inteiro para mostrar começo e fim das transições.
3. **Guia de estilo** em `brand-izoton/GUIA_DE_ESTILO.md`, como no `CLAUDE.md` (o prompt citava `referencias/`).
4. **Box de DVD genérico** (Commons), porque não há foto livre de um box da HBO. Não aparece rotulado como HBO.
5. **Voz acelerada 7%**, igual à v2 (o `CLAUDE.md` fala em 5%). A pergunta está em `PERGUNTAS.md`.
6. **Recibo "A CONTA" do cold open:** é um grafismo desenhado, sem números, que só anuncia o capítulo 9. Não é registro real.

## Arquivos
- **Clipes (540p, -14 LUFS):** `V3ColdOpen_540p.mp4`, `V3Colagem_540p.mp4`, `V3FalaT04_540p.mp4`, `V3TransicaoCap_540p.mp4`, `V3Short02Hook_540p.mp4`.
- **Prints:** 5 a 6 por trecho, em 1920x1080 (o Short em 1080x1920), com tempo e nome da cena.
- **Masters 1080p da amostra:** `video/out/v3a/` (fora do Git).

**Parei aqui.** O resto do episódio só segue depois do `FIXES.md` do gerente com o ok.
