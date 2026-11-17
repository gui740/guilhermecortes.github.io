# GUIA DE ESTILO · números medidos nas referências

Medido em 17 nov. 2026, um quadro a cada 0,25 s (877 quadros), mais diferença de imagem entre quadros e ataques de áudio.
As referências ficam em `referencias/`, fora do Git:
- **R1** reel editorial "SPOT" (Michelangelo), 63 s, 720x1280
- **R2** reel editorial "SPOT" (Nvidia), 68 s, 720x1280
- **R3** reel sobre edição com Claude, 29 s, 720x1280
- **R4** tutorial de organização da edição, 60 s, 1080x1920

## 1. Ritmo (medido)

| Métrica | R1 | R2 | R3 | R4 | Nossa v2 |
|---|---|---|---|---|---|
| Quadros com movimento (diferença > 1,5) | 91% | 92% | 92% | 63% | cerca de 50% |
| Trechos parados > 1 s | 0 | 0 | 0 | 3 | 68 (> 1,5 s) |
| Troca forte de plano, intervalo médio | 1,28 s | 2,79 s | 1,18 s | 2,38 s | cerca de 7,7 s (116 em 892 s) |
| Ataques de áudio por minuto | 61 | 123 | 86 | 68 | n/d |
| Trocas fortes com ataque a até 0,25 s | 57% | 74% | 62% | 71% | n/d |

O que isso significa:
- **Meta prática:** nada parado por mais de 1 s nos Shorts e por mais de 2,5 s no longo; troca forte a cada 1,2–2,8 s nos Shorts e a cada 3–6 s no longo; um evento menor a cada 0,5–1,5 s.
- **Rajada de cortes:** R1 tem uma rajada de 12 trocas em 2,5 s (29,75–32,25 s), uma foto em tela cheia por palavra (Davi → Pietà → Capela Sistina), com cerca de 0,25–1 s por foto.
- **Som:** a ligação entre som e troca é indicativa, porque os ataques incluem sílabas da fala. Ainda assim, cerca de 2 em cada 3 trocas caem junto de um ataque.

## 2. Gramática observada (confirma os 10 itens do gerente)

1. **Página persistente.** Fundo branco (ou preto) fixo, com uma etiqueta de categoria no canto superior esquerdo: ponto vermelho e caixa alta mínima (`• NOVIDADE`, `• SEGUNDO A IMPRENSA`), cerca de 1,5% da altura. A marca "SPOT" fica no topo central. A etiqueta muda só quando muda o assunto.
2. **Algo novo por palavra.** A legenda entra palavra a palavra, a cada 0,25–0,5 s. Dentro de um plano de 3–6 s, um elemento novo entra a cada 0,5–1,5 s (rótulo, linha, número, card).
3. **Infográficos que crescem.**
   - Linha do tempo (R1 24,25–28,5 s): `1475` entra junto com uma linha que se desenha em cerca de 0,5 s. `1564` entra em fade de 0,25 s, os rótulos NASCE/MORRE logo em seguida, ESCULTOR na palavra (27,0 s) e PINTOR na palavra (27,75 s).
   - Diagrama (R2 15,0–19,25 s): o nó-imagem entra, depois o rótulo; a seta se desenha em cerca de 1 s; o próximo nó e o próximo rótulo vêm a cada 0,75 s, sempre na palavra.
4. **Palavra-chave em caixa chapada.** Caixa vermelha com texto branco, em caixa alta, fazendo fade de cerca de 0,25 s (um quadro rosa, depois o vermelho cheio). Ela aparece exatamente na palavra e fica até o fim da frase. No R3 a caixa é amarela.
5. **Título em dois pesos.** "Fonte / oficial.": a primeira linha em tinta escura e peso médio; a segunda em cinza claro e peso fino. Cada linha entra na sua palavra, cerca de 0,25 s depois da anterior.
6. **Cards com sombra.** Manchete, tela ou documento entra como cartão branco de cantos levemente arredondados, com sombra grande e suave (desfoque de cerca de 4% da largura, opacidade baixa). Entra em cerca de 0,25 s (fade com subida curta) e fica parado ou flutua. Os pills de destaque (vermelhos) entram embaixo, na palavra.
7. **Objetos ao redor do sujeito.** No R3, cards e fotos caem em volta da pessoa um a um, a cada 0,25 s, com profundidade (os de trás desfocados).
8. **Troca de página.** De branco para preto ou para foto em tela cheia, quase sempre em corte seco com fade de 1 quadro, junto de um ataque de áudio. A foto em tela cheia leva título no canto superior esquerdo, com a mesma etiqueta de categoria.
9. **Painel com câmera (R4).**
   - O painel é escuro, com cartões numerados (`01 configuração`, `02 ferramentas`, `03 estilo`, `04 edição`) ligados por linhas finas claras.
   - A câmera viaja entre os cartões em cerca de 0,5 s, com desfoque de movimento forte (2 quadros borrados), enquanto um traço de luz percorre a linha em cerca de 0,75 s.
   - Dentro do cartão, os itens entram um por palavra (cerca de 0,5 s), cada um com um conector que se desenha.
   - A abertura é um mosaico de vídeos que encolhe até um único vídeo (0–3 s).
10. **Legenda palavra a palavra.**
    - R1 e R2: centralizada, logo abaixo do card do apresentador, por volta de 55–70% da altura, sans negrito.
    - R3: grande, no topo, colorida.
    - R4: pequena, embaixo.
    - Nos Shorts do canal: terço inferior, dentro da zona segura, palavra-chave em caixa.

## 3. Adaptação para o Brand by Izoton (sem trocar a estética)

| Referência | No canal |
|---|---|
| Caixa vermelha ou amarela na palavra | `#292929` com texto branco por padrão; âmbar `#FFB000` para dado ou interface; vermelho `#E50914` **só** quando a palavra for da Netflix. Nada de amarelo |
| Página branca ou preta | Página branca do canal; a "página escura" é a tela de arquivo CRT |
| Etiqueta `• CATEGORIA` | `• 03 · O BINGE COMO PRODUTO` (mono, canto superior esquerdo da faixa) + `ARQUIVO 03/10` |
| Painel escuro do R4 | Painel de arquivo **no branco**: 10 cartões numerados, linhas `#292929`, traço que percorre a linha, câmera voando com desfoque |
| Fonte da referência (sans geométrica tipo SF Pro / Inter) | Mantemos Jost (títulos) + IBM Plex Mono (etiquetas), já definidos no canal |

## 4. Curvas e tempos para o kit v3

| Elemento | Duração | Curva |
|---|---|---|
| Entrada de card | 8 quadros (0,27 s), subida de 24 px | ease-out forte |
| Palavra-chave | 6–8 quadros de fade de caixa | linear |
| Linha ou seta se desenhando | 15–30 quadros | ease-in-out |
| Viagem de câmera entre cartões | 15 quadros, com desfoque de movimento nos 6 centrais | ease-in-out |
| Traço de luz na linha | 22 quadros | linear |
| Rajada de fotos | 8–30 quadros por foto | corte seco + som |

Na vida contínua, o card flutua de 3 a 8% ao longo do plano, e o recorte se move em degraus (10 poses por segundo) com tremor de 1–2 px.
