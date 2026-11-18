# ENTREGA v3b · FIXES rodada 2 · status

Atualizado a cada etapa concluída.

## Etapa 1: correções aplicadas (código no Git; mídia fora)
1. **Passo 3 nas cenas v2** (`video/src/v3/EpisodioV3.tsx` e `pipeline/montar_timeline_v3.py`):
   - imagem real presa à palavra em toda fala das cenas estreitas (67 entradas), que sai com a sua cena;
   - etiqueta com palavra-chave dita nas outras marcas: algo novo a cada ~1,2 s (287 etiquetas);
   - câmera em degraus a cada marca (389 passos);
   - escala de 1,15 a 1,5 nas cenas de tipografia e dado;
   - parallax nas laterais (esquerda 0,6; direita 1,1);
   - transição de entrada em rodízio (máscara para a direita, círculo, máscara para baixo, deslize com desfoque), nunca a mesma duas vezes seguidas;
   - título com imagem principal ao lado (página editorial).
2. **Imagens:**
   - 8 imagens novas do Commons (Sarandos, sede em Los Gatos, VHS, controle remoto, Netflix House, guarda de Round 6, box de DVD, cosplay);
   - 5 imagens de conceito (relógio, cupcake, truta, sala de estar, mapa-múndi);
   - tudo registrado em `IMAGENS.md` e `DIREITOS.md`.
   - O Pixabay bloqueia acesso automático (desafio do Cloudflare) e a API pede chave, então usei o Commons. O cadeado não teve imagem livre adequada; a cena das senhas usa o print oficial "An update on sharing".
3. **Painéis sem fala:** o título do capítulo é digitado num terminal sob o cartão, com teclado baixo.
4. **Narração:**
   - bloco 10: saiu o "que" a mais;
   - bloco 32: o "é a mais" era um falso começo ("O guia lista, o guia…" + "Bloco 32"), e o início foi cortado até a leitura boa;
   - bloco 41: a transcrição nova não acha o "que", que sai colado em "4", então não houve corte.
5. **Legendas:** tempos por palavra corrigidos (Hastings, guia de marca oficial, cor assinatura, Meio & Mensagem, Senna, Guaraná Antarctica, keeper test, Brand by Izoton, "quanto").
6. **Shorts:**
   - SHORT01 com troca a cada 2 s no máximo (abertura dividida em CRT → recorte e ficha; carta dividida em página → trecho);
   - SHORT05 abre com o bloco 30;
   - os demais já abrem com a frase do longo que diz o mesmo fato (03: bloco 20; 04: 27; 06: 34; 07: 44; 08: 50), com o hook em texto no 1º quadro.
7. **Duração:** 13,0 min.

## Etapa 1b: ajuste do pulso de câmera (pedido do gerente)
- **Pulso:** até 1,5% de escala, com easing, no começo das palavras da fala (ritmo dele, não metrônomo). Fica desligado em documento, foto, cores, proibições e logo.
- **Conteúdo preso à fala a cada ~0,85 s:** 67 imagens reais e 391 etiquetas com a palavra-chave dita. O bloco 09, que não foi gravado, mostra o texto do roteiro em pedaços.
- **Chave `semPulso`** no EpisodioV3, para a medida de controle.
- **Medida rápida (1:00–3:00, sem pulso):** 12% parado (antes, 35%) e maior trecho de 4,0 s. Esse trecho era o bloco 09, já corrigido com o texto na tela.

## Etapa 2: montagem completa 540p
**Render com pulso (ep540c) terminou às 07:27Z** (não travou, só foi mais lento que o previsto). Medida sem grão: **18% parado**, maior trecho 4,3 s, 4 trechos acima de 2,5 s. Reprovado (meta 5% / 2,5 s).

Diagnóstico pelos quadros congelados:
- laterais vazias na maior parte do tempo (as imagens só entravam até o número de imagens do bloco, em geral 1 a 3);
- as etiquetas de palavra eram pequenas demais para contar como mudança (em 160 px viram uma faixa de 25x6 px no mesmo lugar);
- documentos ficavam 8 a 10 s parados com um zoom de 12%;
- alguns elementos centrais pequenos (medidor, proibições, pôsteres);
- a medida usa janela de 1 s: qualquer segundo sem mudança grande conta como parado.

Reforço de conteúdo (rodada v3b-d):
1. **Fichas de dossiê nas laterais livres**: a palavra-chave que ele diz entra num cartão de papel com o código do arquivo ("ARQ 06 · Nº 07"), deslizando da borda em degraus, lados alternados, no máximo uma por 0,9 s. Onde a lateral tem imagem real, fica a etiqueta pequena embaixo. Nas cenas de documento a ficha é menor e colada na borda para não cobrir o texto.
2. **Imagens reais em rodízio nas laterais**: a cada ~2,4 s durante as cenas estreitas, lados alternados, nunca a mesma imagem dos dois lados ao mesmo tempo (95 entradas, antes 67).
3. **Leitura de documento em degraus ("lupa")**: a cada ~2,1 s a câmera vai para outro pedaço do trecho citado e volta ao todo no fim; o grifo e o sublinhado acompanham.
4. **Elementos centrais maiores**: medidor 1,7x, proibições 1,45x, pôsteres 1,2x.
5. **Deriva de câmera**: órbita lenta e contínua (26 px a cada 7 s, ~23 px/s, sem paradas, não sincronizada) + zoom de 0,5%/s. Não é o pulso: tem chave própria.
6. O pulso continua como pedido: no máximo 1,5%, preso ao começo das palavras, desligado em documento, pôster, cores, proibições e logo.

Teste no trecho mais difícil (7:40–8:20, proibições + barras + documento): normal 8% parado (antes 40%), pulso desligado 11%.

(O render ep540d foi interrompido a pedido do gerente para a rodada de ações abaixo.)

## Etapa 3: "parado na narrativa" (nota do Guilherme: envelope de 0:15 a 0:27)

### O envelope (0:15–0:27)
Agora ele faz uma ação nova a cada 1–2 s, presa às palavras da narração:
1. a aba abre;
2. o DVD desliza para fora (o bolso do envelope fica por cima do disco);
3. o envelope sai de quadro e o disco vai ao centro girando;
4. o ano é carimbado no disco;
5. a etiqueta é carimbada;
6. em diante, o disco dá meio giro a cada ação.

Na cena da porta (2025), o envelope cresce como uma porta, a aba abre, sai luz de dentro, uma pessoa entra e a etiqueta é carimbada.

### Sistema de ações (para todo o episódio)
- **Quando:** cada cena recebe uma lista de tempos de ação, tirada das palavras dele (no mínimo 1,25 s entre ações, a partir de 0,9 s). Pausa de narração maior que 2,2 s ganha uma ação a cada 1,5 s.
- **O quê:** cada objeto principal tem a sua sequência de ações (tabela abaixo).
- **Pose:** além disso, a cada ação o objeto se reposiciona num degrau de stop-motion (desloca cerca de 14 px e, quando pode, gira cerca de 1°). Logo, cores e proibições da marca só deslocam, sem rotação. Documento e pôsteres não fazem pose: eles têm a lupa e o holofote.

| Objeto | Ações em sequência |
|---|---|
| Título, pergunta, citação | sublinha → carimbo → marca-texto atrás → colchete na margem → o marca-texto troca de linha |
| Envelope / porta | ver acima |
| Medidor | o ponteiro sobe em 3 degraus → oscila como Geiger; barra de 8 segmentos acende |
| Contador | 55% → 80% → valor final; rótulo carimbado; régua de 10 marcas enche |
| Barras | barra A cresce → barra B cresce → colchete "+X P.P." → carimbo → contorno pisca |
| Mapa | grupos de pontos acendem com anel → lista de pontos cresce → contador "PONTOS ACESOS" |
| Cheque | valor datilografado → assinatura desenhada → carimbo → inclina |
| Fluxo, lista | um item por ação → cursor percorre os itens |
| Pessoas | o corte acontece em 4 lotes |
| Anzol | o peixe nada até o anzol → belisca → fisga → se debate |
| Logo N | o N fica intocado; em volta: marcas de canto → cota da altura → caixa de respiro tracejada → régua "RESPIRO NN" |
| Cores | amostra vermelha → amostra escura → carimbo "OFICIAL" → cota → contorno passa de amostra em amostra |
| Proibições | um X por ação → carimbo "PROIBIDO PELO GUIA" |
| Pôsteres | holofote passa de pôster em pôster (sobe e cresce, os outros apagam); pôster único alterna zoom |
| Botão | aperta de novo a cada ação; contador sobe em lotes |
| Colunas | estrelas → barra → carimbo "O QUE ASSISTEM" |
| Ao vivo | linhas datilografadas uma por ação; relógio 00:SS; pulo de sinal |
| Fim | átomo gira; marca carimbada → assinatura sobe → "ARQUIVO 10/10" → "ENCERRADO"/"ARQUIVADO" recarimbado |
| Documento | lupa vai a outro pedaço do trecho a cada ação (≥ 1,5 s), até o fim da cena; a frase final ganha marca-texto, carimbo "CITAÇÃO" e pose (o documento não balança, por leitura) |

### Auditoria
**Como foi medido:** recorte só da faixa do elemento principal (sem laterais, fichas, cabeçalho e etiquetas), medida "só conteúdo" (pulso e deriva desligados), freezedetect sem grão. Lista todo trecho em que o elemento principal fica mais de 2,5 s sem mudança própria.

| Medida | Trechos > 2,5 s | Tempo total parado nesses trechos |
|---|---|---|
| Antes (commit 6e69a31) | 52 | 219,7 s |
| Depois das ações | 18 | 66,0 s |
| Depois das ações + pose | 2 | 8,2 s |
| Final (fim e documento corrigidos, conferido em teste do trecho 11:28–13:01) | 0 | 0 s |

**Lista completa, tempos antes e depois** ("≤ 2,5 s" = não aparece mais na auditoria):

| # | Tempo | Trecho | Cena | Antes | Depois (ações) | Depois (ações + pose) |
|---|---|---|---|---|---|---|
| 1 | 00:18.2 | n01a | envelope | 3.4 s | ≤ 2,5 s | ≤ 2,5 s |
| 2 | 01:05.9 | n02a | titulo | 2.5 s | ≤ 2,5 s | ≤ 2,5 s |
| 3 | 01:25.8 | n02b | titulo | 2.5 s | ≤ 2,5 s | ≤ 2,5 s |
| 4 | 01:46.0 | n02c | titulo | 3.4 s | 2.6 s | ≤ 2,5 s |
| 5 | 01:58.8 | n02d | posters | 3.9 s | ≤ 2,5 s | ≤ 2,5 s |
| 6 | 02:22.0 | n02e | titulo | 3.3 s | 2.8 s | ≤ 2,5 s |
| 7 | 02:25.9 | n02e | medidor | 3.9 s | ≤ 2,5 s | ≤ 2,5 s |
| 8 | 02:43.5 | n03a | titulo | 3.1 s | ≤ 2,5 s | ≤ 2,5 s |
| 9 | 03:17.5 | n03b | fluxo | 4.1 s | ≤ 2,5 s | ≤ 2,5 s |
| 10 | 03:21.6 | n03b | fluxo | 4.4 s | ≤ 2,5 s | ≤ 2,5 s |
| 11 | 03:41.6 | n03e | mapa | 8.9 s | 7.1 s | ≤ 2,5 s |
| 12 | 03:58.2 | n03f | contador | 3.2 s | ≤ 2,5 s | ≤ 2,5 s |
| 13 | 04:03.5 | n03f | citacao | 2.5 s | ≤ 2,5 s | ≤ 2,5 s |
| 14 | 04:06.0 | n03f | citacao | 3.7 s | ≤ 2,5 s | ≤ 2,5 s |
| 15 | 04:21.2 | n04a | cheque | 2.7 s | ≤ 2,5 s | ≤ 2,5 s |
| 16 | 04:24.0 | n04a | cheque | 3.3 s | ≤ 2,5 s | ≤ 2,5 s |
| 17 | 04:50.3 | n04b | colunas | 3.8 s | ≤ 2,5 s | ≤ 2,5 s |
| 18 | 05:04.5 | n04c | medidor | 3.5 s | ≤ 2,5 s | ≤ 2,5 s |
| 19 | 05:20.5 | n05a | titulo | 2.7 s | ≤ 2,5 s | ≤ 2,5 s |
| 20 | 06:22.8 | n05d | titulo | 3.1 s | ≤ 2,5 s | ≤ 2,5 s |
| 21 | 07:08.0 | n05e | anzol | 3.2 s | ≤ 2,5 s | ≤ 2,5 s |
| 22 | 07:11.2 | n05e | anzol | 2.7 s | 2.7 s | ≤ 2,5 s |
| 23 | 07:17.6 | n06a | logoN | 6.2 s | 4.6 s | ≤ 2,5 s |
| 24 | 07:25.4 | n06b | logoN | 3.0 s | ≤ 2,5 s | ≤ 2,5 s |
| 25 | 07:33.8 | n06c | cores | 9.1 s | 5.0 s | ≤ 2,5 s |
| 26 | 07:44.3 | n06d | proibicoes | 13.9 s | 3.0 s | ≤ 2,5 s |
| 27 | 07:59.0 | n06e | barras | 6.3 s | ≤ 2,5 s | ≤ 2,5 s |
| 28 | 08:23.4 | n07a | aovivo | 4.9 s | 3.4 s | ≤ 2,5 s |
| 29 | 08:58.2 | n07b | titulo | 5.0 s | ≤ 2,5 s | ≤ 2,5 s |
| 30 | 09:03.4 | n07b | titulo | 4.7 s | ≤ 2,5 s | ≤ 2,5 s |
| 31 | 09:13.3 | n07c | titulo | 3.5 s | ≤ 2,5 s | ≤ 2,5 s |
| 32 | 09:34.2 | n08a | posters | 5.3 s | ≤ 2,5 s | ≤ 2,5 s |
| 33 | 09:39.9 | n08a | contador | 5.9 s | ≤ 2,5 s | ≤ 2,5 s |
| 34 | 09:46.0 | n08a | contador | 2.6 s | 2.6 s | ≤ 2,5 s |
| 35 | 09:55.2 | n08b | contador | 3.0 s | ≤ 2,5 s | ≤ 2,5 s |
| 36 | 10:02.2 | n08c | posters | 5.0 s | ≤ 2,5 s | ≤ 2,5 s |
| 37 | 10:15.7 | n08d | posters | 7.3 s | ≤ 2,5 s | ≤ 2,5 s |
| 38 | 10:23.3 | n08e | mapa | 3.0 s | 3.5 s | ≤ 2,5 s |
| 39 | 10:26.4 | n08e | mapa | 3.1 s | 3.5 s | ≤ 2,5 s |
| 40 | 10:36.8 | n09a | contador | 3.2 s | ≤ 2,5 s | ≤ 2,5 s |
| 41 | 11:04.0 | n09d | pergunta | 5.7 s | 3.0 s | ≤ 2,5 s |
| 42 | 11:10.1 | n09e | contador | 2.7 s | ≤ 2,5 s | ≤ 2,5 s |
| 43 | 11:12.8 | n09e | contador | 2.6 s | ≤ 2,5 s | ≤ 2,5 s |
| 44 | 11:25.3 | n09e | titulo | 2.9 s | ≤ 2,5 s | ≤ 2,5 s |
| 45 | 11:28.2 | n09e | titulo | 3.2 s | ≤ 2,5 s | ≤ 2,5 s |
| 46 | 11:37.5 | n09f | evidencia | 3.3 s | 2.8 s | 2.8 s |
| 47 | 11:41.4 | n09f | medidor | 5.1 s | ≤ 2,5 s | ≤ 2,5 s |
| 48 | 12:10.3 | n10a | contador | 3.1 s | ≤ 2,5 s | ≤ 2,5 s |
| 49 | 12:16.8 | n10a | titulo | 2.6 s | ≤ 2,5 s | ≤ 2,5 s |
| 50 | 12:38.5 | n10c | titulo | 3.1 s | ≤ 2,5 s | ≤ 2,5 s |
| 51 | 12:47.8 | n10c | logoN | 5.1 s | 5.1 s | ≤ 2,5 s |
| 52 | 12:53.1 | n10d | fim | 7.5 s | 6.7 s | 5.4 s |

Os 2 últimos (documento n09f 11:37,9 e fim n10d 12:55,3) foram corrigidos depois disso. Na conferência do trecho 11:28–13:01 nenhum passa de 2,5 s.

### Medidas (montagem final `video/out/v3a/EP01_v3b4_540.mp4`, 781,9 s)

| Medida | Parado | Maior trecho | Meta | Resultado |
|---|---|---|---|---|
| Normal (episódio inteiro, sem grão) | 4,6% (35,8 s) | 2,1 s · nenhum ≥ 2,2 s · fim sem quadro parado | < 5% e nada > 2,5 s | passou |
| Sem pulso | 5% | 2,1 s | até 5–8% | passou |
| Só conteúdo (informativa) | 21% | 2,6 s, no fim; corrigido depois | informação | 21% aceito |

- Auditoria "parado na narrativa" (recorte da faixa central, d = 2,5 s) na v3b4: **0 trechos**.
- Quadro isolado (glitch): nenhum. O quadro preto de 2:49,2 sumiu (a TV liga a partir do branco: `TelaCRT` em `transicoes.tsx`).
- 8,9 trocas fortes por minuto. Loudness da montagem 540p: −16,4 LUFS (o master 1080p sai em −14 LUFS e −1 dBTP).
- As medidas "sem pulso" e "só conteúdo" foram feitas antes dos três últimos ajustes (fim, painel, documento). Esses ajustes só acrescentam movimento, mas as duas medidas não foram refeitas.
- Na primeira montagem (v3b3) a medida normal deu 5,5% (43,0 s), e os últimos 3,2 s ficavam parados. O script arredondava para "5%", e ele também não conta um trecho parado que vai até o fim do arquivo. Correções da v3b4, todas em degraus de stop-motion:
  1. Fim: a pasta do arquivo sobe desde a assinatura, fecha com ENCERRADO, recebe ARQUIVADO e desce para fora do quadro até o último quadro.
  2. Painel de capítulo: a câmera recua e desliza enquanto o traço corre.
  3. Documento: aproximação lenta em degraus de 3 quadros, e o cartão da frase continua a se aproximar entre as ações.
- A v3b4 reaproveita as partes 1–3 já renderizadas, que não têm os ajustes 2 e 3. No 1080p final, todas as cenas saem com o código novo.

### Links
- Montagem completa (vídeo 540p, prints por capítulo, cena de documento, auditoria e medidas): https://claude.ai/artifact/4URkcNdgCGnDVNkDby969o
- Pedidos de imagem para o Gemini (GEMINI_PEDIDOS.md): https://claude.ai/artifact/JYUGvCi7ShrYLzZf4WkrsX
- Os dois são privados: só abrem para quem tiver acesso compartilhado.

### Próximo: Parada 3
Render 1080p final, 8 Shorts, capa, DESCRICAO_YOUTUBE.md, DESCRICAO_SHORTS.md e DIREITOS.md. Os blocos 09, 11 e S01–S08 ficam prontos para trocar (`pipeline/narracao_gui/trocar_audio.py`).
