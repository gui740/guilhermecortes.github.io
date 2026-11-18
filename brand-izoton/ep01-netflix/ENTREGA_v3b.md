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

Em andamento: render 540p completo (ep540d) → medida com pulso desligado → medida só conteúdo (pulso e deriva desligados). As três medidas entram no relatório.
