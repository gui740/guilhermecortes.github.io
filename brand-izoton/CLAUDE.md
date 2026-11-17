# BRAND BY IZOTON — SISTEMA DO CANAL (CLAUDE.md)

> Este arquivo vai para `brand-izoton/CLAUDE.md` no repo gui740/guilhermecortes.github.io. Ele vale para TODO episódio. O que muda por episódio fica no `BRIEF.md` da pasta do episódio. Versão 1 · 17 nov. 2026.

## 0. Como trabalhamos (gerente + construtor)

- O projeto BRANDSPOTEN (Claude no claude.ai) é o **gerente**: pesquisa, escreve o `BRIEF.md`, traduz as notas do Guilherme em `FIXES.md` e manda as mensagens de handoff.
- Você, sessão do Claude Code, é o **construtor**. O Guilherme não fala com você diretamente. Tudo chega pelo gerente.
- Leia `BRIEF.md` e `FIXES.md` da pasta do episódio. Construa sem pedir confirmação no meio. Só pare se faltar um arquivo ou uma fonte essencial; nesse caso, escreva a pergunta em `PERGUNTAS.md` e siga com o resto.
- Mude só o que está no `FIXES.md`. Tudo o mais fica exatamente como está.
- Cada render é um arquivo novo e numerado (`v01`, `v02`...). Nunca mova, apague ou sobrescreva uma versão anterior.
- Ao terminar cada rodada, escreva `ENTREGA_vXX.md`: o que foi feito, o que ficou pendente, decisões tomadas sem consulta e o relatório de motion (seção 8).

## 1. Conceito

Publicação editorial audiovisual sobre marcas, cultura e estratégia. Imagine uma revista de design produzida dentro de um arquivo corporativo retrofuturista dos anos 1950: propaganda vintage + investigação audiovisual. Minimalista mas não genérico; vintage mas não envelhecido; experimental mas não desorganizado.

- Inspiração de linguagem em Fallout 4 e na série Fallout (modernismo industrial, otimismo tecnológico vintage, propaganda corporativa, design atômico, interfaces de terminal, numerações e códigos). **Nunca** reproduzir personagens, logos, paleta ou qualquer elemento proprietário de Fallout.
- **A estética acima é a base e não muda.** O estilo "Vox" da seção 4 se soma a ela como acabamento e método (recortes, camadas, grão, movimento quadro a quadro) para dar mais motion. Ele nunca substitui a linguagem do canal.

## 2. Cores

- Branco `#FFFFFF` (fundo), cinza-claro `#D9D9D9` (apoio), cinza-médio `#777777` (secundário), cinza-escuro `#292929` (tipografia e linhas).
- Proibido: cores saturadas em fundos, tipografia ou grafismos permanentes; a paleta de Fallout.
- Cor só no material das marcas (comerciais, fotos, embalagens, produtos, logos) e em destaques pontuais com sentido editorial. Verde ou âmbar de CRT só como acento de interface (hook, lower thirds, medidores).
- O canal é monocromático; a marca traz a cor dela. A cor é um evento: o quadro fica em cinza até o material da marca entrar.
- Logo de marca sempre limpo, na cor original, sem filtro, grão, scanline, rotação ou distorção, respeitando o brand guide oficial dela.

## 3. Tipografia

- Sans-serif geométrica e legível em três níveis: título grande (caixa alta quando couber), informação média, legenda pequena. Mono para códigos, carimbos e terminal.
- Números, datas e códigos são elementos de composição. Pouco texto por vez.
- Use fontes reais, identificadas nas referências do `GUIA_DE_ESTILO.md`. Nada de fonte com cara de gerada por IA.

## 4. Acabamento estilo Vox, somado à estética do canal

1. **Cada cena é feita em camadas**: fundo (papel, mesa de arquivo, branco texturizado) → sujeito (recorte) → primeiro plano (papéis, objetos, dedos de fita) → texto → textura → grão. As camadas se movem em velocidades levemente diferentes, o que dá profundidade. Uma colagem chapada recortada parece papel; evite.
2. **Recortes que parecem colocados à mão**: borda branca ou contorno fino, sombra projetada real, leve inclinação. Fotos de pessoas em P&B; produto e logo da marca na cor original.
3. **Movimento quadro a quadro, não liso**: os recortes se movem em degraus (animação "em três", cerca de 10 poses por segundo, com tremor sutil de posição), como stop-motion. A câmera virtual pode deslizar suave e devagar por cima disso.
4. **As coisas caem uma de cada vez**: a composição se monta peça por peça, no ritmo da narração, e se desmonta na saída.
5. **Grão e textura sempre**: grão de filme, papel, poeira e fita (texturas gratuitas de texturelabs.org, ou feitas no pipeline). Nunca um quadro digital limpo demais.
6. **Muitas imagens**: de 30 a 60 imagens por minuto de Short; no vídeo longo, uma imagem nova a cada 3 a 5 s em média.
7. **Imagem gerada** (só quando o Guilherme mandar ou liberar a geração paga) só para objetos, cenários, texturas, ícones e conceitos. Sempre sobre fundo verde chapado, para o recorte sair limpo. **Nunca** gerar imagem de pessoa real, de evento real, de campanha, de produto ou de documento como se fosse registro. Para isso, só material real com fonte.
8. **Interface diegética**: terminal, scanlines, medidores tipo RAD/HP, contador Geiger, numeração de arquivo ("ARQUIVO 03/07"). Reage à narração.

## 4b. Imagens reais em toda cena

Nenhuma cena fica só com texto. Toda composição de tipografia, dado ou citação ganha pelo menos um recorte de imagem real ligado ao que a narração diz (pessoa, produto, tela, documento, lugar, objeto).

1. **Busque você mesmo na internet, nesta ordem:** (a) sala de imprensa e press kit oficial da marca (ex.: about.netflix.com, kits de imprensa, brand site); (b) Wikimedia Commons; (c) páginas oficiais da marca e das pessoas citadas; (d) fotos de imprensa de veículos confiáveis, só quando a licença permitir. Fotos de agência (Getty, Reuters, AP) não entram sem licença.
2. **Recorte** o sujeito (remoção de fundo no pipeline), aplique o tratamento do canal (pessoas em P&B, produto e logo na cor original, sombra real, borda de recorte) e coloque na colagem em camadas.
3. **Registre cada imagem** em `IMAGENS.md` (e no `DIREITOS.md`): cena, URL da página e do arquivo, autor, licença, data de acesso e o que foi feito com ela.
4. **O que não achar** vai para uma lista única, `IMAGENS_FALTANDO.md`: o que é exatamente, em qual cena e tempo, para que serve, e sugestão de onde o Guilherme pode tirar print ou gerar. Essa lista é entregue **junto com a parada do storyboard**, de uma vez só, nunca pedido a pedido. Enquanto ela não volta, use um recorte provisório marcado `[PROVISÓRIO]`.
5. Geração paga de imagem (Nano Banana) fica desligada por enquanto. Imagem gerada só entra se vier do Guilherme, e nunca para retratar pessoa ou fato real como se fosse registro.
6. Se a rede do ambiente bloquear algum site, anote em `PERGUNTAS.md` qual domínio precisa ser liberado e siga com os outros.

## 5. Formato e enquadramento

- Vídeo principal: 1920x1080, 30 fps, até 15 min. Shorts: 1080x1920, 5 a 8 por episódio.
- Rosto, produto, logo e texto principal sempre na faixa central de 608 px (zona 9:16). As laterais **trabalham**: colagem, dossiê do bloco (código, data, fonte), dado de apoio, extensão da composição. Laterais ocupadas em pelo menos 70% do tempo.
- Shorts são composições próprias que reaproveitam as cenas do bloco: legenda queimada palavra a palavra na faixa central, dentro da zona segura do Instagram/YouTube, hook visual e falado juntos nos 2 primeiros segundos, troca visual a cada 1,5 a 3 s, loop no fim.

## 6. Roteiro

- O tema e o hot take vêm do Guilherme, pelo `BRIEF.md`. Nunca escolha a história por conta própria.
- Estrutura de ensaio: hook (frase real de executivo, 0:00–0:04) → tese e promessa (até 0:30) → ato 1, o caso a favor → virada perto de 5:00 → ato 2, o custo ou o outro lado → síntese com a leitura do canal → fechamento com uma frase forte.
- Um regancho a cada 2 min no máximo. Cada bloco abre uma pergunta e fecha a anterior (marque [ABRE] e [FECHA]). Uma ideia completa a cada 60–90 s.
- Linhas curtas, uma ideia por linha, fáceis de falar em voz alta. Média de até 15 palavras por frase. Marque [PAUSA] depois das revelações.
- **Nunca inventar fatos, campanhas, frases, números ou comerciais.** Toda afirmação tem fonte, listada no `BRIEF.md`. Opinião aparece como opinião ("a nossa leitura é..."). Afirmação sem fonte sai.

## 7. Ordem de produção (áudio antes do visual)

1. Narração primeiro, um pedido de TTS por bloco, na voz definida no `BRIEF.md`. Se passar do tempo, corte o roteiro, não acelere a voz acima de 5%.
2. Whisper com tempo por palavra. Todo destaque, contador, entrada de recorte e corte cai no tempo exato da palavra.
3. Trilha: ambient eletrônico, sintetizador analógico, sci-fi retrô, pulsação lenta. Faça 3 versões de mix e meça: narração clara, música de 20 a 25 dB abaixo da voz nos trechos calmos, -14 LUFS integrado, pico em -1 dBTP. Você não ouve: confie nas medições.
4. Storyboard: um quadro de baixa resolução por cena (`storyboard_vXX.jpg` + tabela com tempo, fala, componente do kit, movimento contínuo, som).
5. Animatic em 540p, rápido, com a narração real. É o que o Guilherme aprova.
6. Render final em alta, por bloco, e o master montado no fim.

## 8. Motion: regras medidas

- Nenhum quadro parado por mais de 2,5 s. Todo elemento tem vida: deriva, parallax, degrau de stop-motion, cursor, ponteiro, grão.
- Pelo menos 12 eventos visuais por minuto nos 3 primeiros minutos e 8 no resto (evento = recorte novo, palavra destacada, número, corte ou transição).
- Rajada de 5 a 10 cortes rápidos a cada 2 a 3 min, sobre o regancho.
- Nenhum tipo de cena ocupa mais de 20% do episódio nem se repete duas vezes seguidas.
- Transição-assinatura: vídeo em tela cheia → quadro congelado → recorte do personagem ou produto → isolamento no branco → colagem → tipografia e dados → volta ao vídeo.
- Evitar glitch sem motivo, partículas, movimento aleatório e zoom em toda frase.
- **Relatório de motion obrigatório** em cada entrega: tempo parado (ffmpeg freezedetect, meta abaixo de 5%), eventos por minuto, ocupação das laterais, maior trecho sem movimento, distribuição por tipo de cena. Reprovou, corrija antes de entregar.

## 9. Som

- Efeitos originais por família, com variações: cliques eletrônicos, bipes suaves, acionamentos, ruídos mecânicos, sweeps, whooshes, Geiger, chiado de CRT, papel e carimbo. Um som em cada transição e em cada entrada de dado.
- Sem graves excessivos, sem impactos cinematográficos, silêncio intencional. Tecnologia sem ruído, futurismo sem agressividade, movimento sem exagero.

## 10. Checagem antes de entregar

- Olhe cada cena e pergunte: quem é este? por que está aqui? isso poderia mesmo acontecer? A imagem bate com a fonte?
- Compare prints do episódio lado a lado com as referências do `GUIA_DE_ESTILO.md` e escreva o que falta.
- Confira o 9:16 de cada Short quadro a quadro.
- Lista de materiais com status de direitos (`DIREITOS.md`) e descrição com referências em ABNT.

## 11. Pastas e ferramentas

```
brand-izoton/
  CLAUDE.md               ← este arquivo
  GUIA_DE_ESTILO.md       ← números medidos das referências (etapa 00)
  kit/                    ← componentes Remotion, texturas, SFX, trilhas
  referencias/            ← vídeos de referência (fora do Git) e quadros extraídos
  episodios/epXX-marca/
    BRIEF.md  FIXES.md  PERGUNTAS.md
    brutos/   (mídia-fonte, fora do Git)
    exportacao/ (renders numerados, fora do Git)
```

Ferramentas: Remotion (motion), FFmpeg (cortes, análise, finalização), Whisper (tempo por palavra e legendas), yt-dlp (baixar referências e fontes), Python 3. O repositório é público: mídia de terceiros nunca vai para o Git. Chaves de API só como segredo do ambiente, nunca em texto.
