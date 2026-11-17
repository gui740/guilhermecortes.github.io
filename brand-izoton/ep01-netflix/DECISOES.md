# DECISÕES · EP01 Netflix (produção autônoma da Etapa 3)

Escolhas tomadas sem consulta, seguindo o guia do prompt. Revise e me diga o que mudar.

## Narração
1. **Voz provisória nesta versão:** Microsoft Edge TTS, `pt-BR-FranciscaNeural`, levemente mais lenta (-6%) e mais grave (-4 Hz). Motivo: a cota gratuita diária do Gemini acabou, e o filtro de segurança do Gemini bloqueou o grupo dos blocos 5 a 7. Conforme o seu pedido, uso a voz gratuita só nesta versão.
2. **Trechos da Gacrux já prontos (blocos 0 a 4)** ficam guardados fora do repo e **não** entram nesta versão. Uma voz só no vídeo todo deixa a avaliação mais justa.
3. **Para a versão final:** quando a cota renovar, gero os blocos 5 a 10 na Gacrux. Antes, isolo a frase que disparou o filtro, segmento por segmento.
4. **Números falados por extenso** no texto da narração ("cento e trinta e seis milhões"), para a voz não ler dígito por dígito. Na tela, os números aparecem em algarismos.
5. **Códigos de cor (E50914, B20710) ficam só na tela.** Na narração, ficou "o vermelho Netflix, com um vermelho escuro de apoio".

## Arquivo (falas reais)
6. **TED e Blitzscaling:** P&B com tratamento de TV falhada. Reenquadramento automático por plano, com detecção de rosto: Hastings à direita nos planos abertos do TED, à esquerda nos do Blitzscaling. Zoom de 1,15× nos closes e até 2,4× nos planos abertos, com o rosto sempre na faixa 9:16.
7. **Material da própria Netflix** (vídeo do Netflix House, comercial #FU2016): fica **em cor e sem filtro**. A regra do canal manda manter a cor no material da marca, e a regra do logo proíbe efeitos sobre ele.
8. **Executivo do vídeo do Netflix House:** o vídeo não diz o nome dele, e a busca não confirmou. Lower third: "Executivo da Netflix · vídeo oficial · dez. 2025". Não chutei nome.
9. **#FU2016:** o comercial entra dentro de uma TV desenhada. O lower third fala do personagem (Frank Underwood) e não destaca o ator.
10. **T12 (Schindler × Adam Sandler)** dividido em dois trechos (T12a e T12b), com a narração no meio, como no roteiro.

## Logo e marca
11. **Símbolo N:** o PNG oficial do site de marca (`Logos-Readability-N-Symbol.png`, com o degradê original), recortado só nas margens transparentes. Nunca recebe filtro, sombra, caixa, rotação ou distorção.
12. **Proibições do guia (bloco 6):** demonstradas com um quadrado cinza genérico, nunca com o logo verdadeiro distorcido.
13. **Logos de terceiros** (HBO, Amazon, YouTube, Fortnite, marcas parceiras de Senna): aparecem **só como texto**, sem logos.

## Visual
14. **Tipografia:** Jost (geométrica, de traço futurista) para títulos e informação; IBM Plex Mono para carimbos, códigos e lower thirds de terminal. As duas são do Google Fonts.
15. **Acento de interface:** âmbar de terminal `#FFB000`, só nos lower thirds de arquivo e nos medidores. Não usei o verde, para não competir com o vermelho da Netflix.
16. **Fichas de evidência:** prints reais (PDFs oficiais em 160 dpi e capturas das páginas citadas), recortados com sombra projetada sobre o branco.

## Som e mix
17. **Trilha e efeitos 100% sintetizados no pipeline** (sem bibliotecas de terceiros), com famílias de cliques, bipes, Geiger, CRT, sweep, carimbo e papel. Sem "tudum".
18. **Mix:** narração em primeiro plano; trilha abaixada sob a voz (ducking) e mais baixa ainda sob as falas de arquivo; alvo -14 LUFS integrado e pico máximo de -1 dBTP.

## Legendas
19. **Legenda PT-BR só nas falas em inglês**, como pede o briefing. A narração em português não ganha legenda queimada no vídeo longo; o YouTube gera a automática.

## Montagem
21. **Zoom mínimo por plano:** quando o rosto de Hastings está perto da borda (ex.: plano por cima do ombro de Chris Anderson no T12), o zoom sobe até o necessário para centralizar o rosto, com limite de 2,6×. A regra vem da faixa 9:16, que manda.
22. **Scanlines, barra de rolagem e cintilação do CRT são feitas no Remotion** (camada por cima do vídeo). P&B, grão, curvatura e aberração ficam no ffmpeg. Motivo: o filtro de scanline no ffmpeg deixava o processamento 10 vezes mais lento.
23. **Saída das falas de arquivo:** o último quadro congela, encolhe para 60% com sombra e se isola no branco. É a versão enxuta da transição-assinatura. No hook, a saída é o "desligar de TV": a imagem colapsa numa linha.
24. **O hook abre seco**, só com o áudio original de Hastings, sem trilha. A trilha entra com a narração.
25. **Captura da The Drum** refeita só com o título e o primeiro parágrafo (a primeira captura tinha pegado um anúncio).
26. **Referência do vídeo #FU2016:** o arquivo vem do canal "Frank Underwood" no YouTube (não é o canal oficial da Netflix). A descrição cita o canal e informa que é a reprodução do comercial exibido na CNN.

## Shorts
27. **Renderizados do mesmo projeto em 1,5×** (2880x1620) e recortados na faixa central (912x1620), com ampliação final pequena para 1080x1920. Fica bem mais nítido que recortar do master 1080p.
28. **Título-gancho** nos 2,5 s iniciais: cartão branco no topo, mesma tipografia do episódio. O SHORT 01 junta dois trechos (o hook e o bloco do Fortnite e do vício), como previsto na decupagem.

## Capa
29. **Capa 1280x720:** Hastings em P&B com scanlines à esquerda, o N limpo à direita, título "ELA COMPETE COM O SEU SONO." (paráfrase fiel da fala literal "competing with sleep"), assinatura do canal e lower third em âmbar.

## Entrega
20. **Mídia fora do repo:** o repositório é público. Vídeo, áudio e clipes de terceiros não vão para o Git, só código, roteiro e documentos. Os arquivos finais vão para a pasta do episódio na sessão e, se der, para o seu Drive.
