# Roteiro — "A história da Copa do Brasil" (@futexplicando)

Vídeo vertical 1080×1920, 30 fps, ~75 s. Narração frase a frase (Gemini TTS). Cada frase é uma cena; dentro dela há cortes de 1 a 2 s, com crossfade de 6 frames e câmera sempre em movimento.
Fatos conferidos em [pesquisa.md](pesquisa.md).

| # | Frase (narração) | Cena | Época / paleta |
|---|---|---|---|
| 1 | "O torneio que hoje paga setenta e oito milhões de reais pro campeão..." | **Sobrevoo 3D:** começa colado na torcida de mini-personagens, recua até a faixa "R$ 78 MI" e o troféu e termina mostrando o estádio inteiro. Torcida ao fundo. | Presente, cores vivas |
| 2 | "...nasceu com uma ameaça: quem não quisesse jogar, ia ser punido!" | Escritório da CBF anos 80: o cartola de óculos bate na mesa (dentes cerrados) e aparece o carimbo "PUNIDO!". Um dirigente de chapéu-coco faz cara de espanto. | Passado, sépia |
| 3 | "Fica até o final que eu explico." | O narrador de bigode pisca (sorriso) ao lado de uma TV de tubo com o logo da Copa do Brasil. | Passado |
| 4 | "Tudo começou em mil novecentos e oitenta e nove." | Jornal impresso girando até parar com a manchete "1989"; lustre brilhando. | Passado |
| 5 | "Ricardo Teixeira tinha acabado de assumir a CBF." | Cartola de óculos atrás da mesa, com placa "CBF" e quadro na parede; sorriso. | Passado |
| 6 | "E os estados menores estavam bravos: tinham ficado fora da elite do Brasileirão." | Mapa antigo do Brasil: estados do Norte e do Nordeste piscam; dirigentes de chapéu-coco com olhar desconfiado e dentes cerrados. | Passado |
| 7 | "Aí ele inventou um mata-mata com campeões de todos os estados." | Vareta aponta o mapa, e bandeirinhas surgem em todos os estados. Cartola sorri. | Passado |
| 8 | "Trinta e dois times, quarenta e seis dias e uma vaga na Libertadores pro campeão." | Contadores em placas de madeira ("32", "46 dias") e taça da Libertadores em quadro. Espanto. | Passado |
| 9 | "O primeiro campeão? O Grêmio, em cima do Sport." | TV de tubo com placar Grêmio 2 x 1 Sport (escudos em placas); torcedor gremista com dentes cerrados de empolgação. | Passado |
| 10 | "E a Copa virou a chance dos pequenos." | Mapa com bandeirinhas: a vareta passa de estado em estado. Personagem pequeno sorri. | Passado |
| 11 | "Em noventa e um, o Criciúma foi campeão em cima do Grêmio." | Placa com escudo do Criciúma x Grêmio, 1991; personagem gremista de olhos fechados (tristeza) e criciumense pulando. | Passado (anos 90) |
| 12 | "Em dois mil e quatro, o Santo André calou o Maracanã contra o Flamengo." | Estádio cheio em silêncio: placar 2 x 0, escudos do Santo André e do Flamengo em faixas; rubro-negro em espanto. | Transição para cor |
| 13 | "E em dois mil e cinco, o Paulista de Jundiaí bateu o Fluminense." | Faixa da torcida com escudo do Paulista; tricolor desconfiado. | Cor |
| 14 | "Mas até dois mil e doze, quem jogava a Libertadores nem participava." | Portão de estádio com placa "LIBERTADORES: NÃO ENTRA", com os escudos dos grandes do lado de fora. | Presente |
| 15 | "Em dois mil e treze, os grandes passaram a entrar nas oitavas... e as zebras sumiram." | A zebra de pelúcia some com um "puf"; os escudos entram no chaveamento das oitavas. | Presente |
| 16 | "O maior campeão é o Cruzeiro, com seis taças. Grêmio e Flamengo têm cinco." | Pódio no gramado: Cruzeiro (6) no topo, Grêmio (5) e Flamengo (5) ao lado; torcida de mini-personagens. | Presente |
| 17 | "Hoje são cento e vinte e seis clubes, e a final de dois mil e vinte e seis é em jogo único, em Brasília." | Mapa vivo com 126 pontinhos acendendo; zoom em Brasília e troféu. | Presente |
| 18 | "De torneio imposto na marra... a taça que vale uma fortuna." | Frase de impacto: o carimbo "PUNIDO" vira o troféu dourado, com chuva de papel picado. | Presente |
| 19 | "Segue o @futexplicando!" | Narrador acena; botão "SEGUIR" com o selo @futexplicando; estádio ao fundo. | Presente |

**Palavras:** cerca de 185. **Duração estimada:** 70 a 80 s.
**Escudos citados:** Grêmio, Sport, Criciúma, Santo André, Flamengo, Paulista, Fluminense e Cruzeiro.

## Como ficou na produção
- **Narração:** Google Gemini TTS, modelo `gemini-3.1-flash-tts-preview`, voz "Puck", com instrução de estilo "narrador brasileiro empolgado de vídeo curto". A `GOOGLE_API_KEY` não estava definida (veio só o placeholder) e a API Cloud Text-to-Speech recusa chaves de API, por isso foi usado o plano B do briefing. A cota gratuita do primeiro modelo esgotou na frase 11 (10 pedidos/dia), então o roteiro inteiro foi gerado num único pedido e cortado frase a frase pelos timestamps palavra a palavra do Whisper (`faster-whisper`, equivalente ao `openai-whisper` com `word_timestamps`). Duração 77,3 s, pausas de 0,8–1,2 s entre frases.
- **Diferenças de fala:** a frase 1 saiu "para o campeão" (o texto dizia "pro"); a frase 13 saiu sem o "E" inicial. As legendas seguem o áudio.
- **Vídeo:** 1080×1920, 30 fps, 79 s, H.264 veryfast. Arquivo: `out/historia-copa-do-brasil.mp4`.
- **Código:** `src/cartoon/` traz a biblioteca reutilizável (Personagem com expressões, MiniTorcedor, cenários vintage e de hoje, Mapa do Brasil, CameraMove, Shots com crossfade de 6 frames, Legenda e Estadio3D em three.js). As cenas ficam em `src/videos/CopaDoBrasil/Cenas.tsx`.

## Assets
| Item | Origem | Observação |
|---|---|---|
| Escudos de Grêmio, Sport, Fluminense, Cruzeiro (SVG) e Criciúma (PNG 150 px) | ge.globo (s.sde.globo.com) | Marcas registradas, uso informativo |
| Escudos de Flamengo, Palmeiras, São Paulo e Corinthians | ge.globo (reaproveitados dos vídeos anteriores) | idem |
| **Santo André e Paulista** | **sem escudo oficial**: aparecem como selos com nome e cores do clube | Não foram encontrados no ge nem em sites acessíveis daqui (Wikimedia bloqueado). ⚠️ Conferir |
| Logos da Copa do Brasil e da Libertadores | saopaulofc.net | PNG pequeno (~120 px) |
| Troféu, personagens, torcida, mapa estilizado, TV, jornal e zebra | Desenhados em código | O troféu é estilizado, **não é réplica fiel** da taça oficial |
| Mapa dos estados | [click_that_hood – brazil-states.geojson](https://github.com/codeforamerica/click_that_hood) | Simplificado em `scripts/mapa-brasil.py` |
| Trilha "Energizing" | FreePD (domínio público / CC0), espelho archive.org | Volume baixo, abaixa sob a voz |
| SFX (whoosh, torcida, carimbo, placar, contagem, pop, impacto) | Sintetizados em `scripts/sfx.py` | Autoria própria |
| Fontes Baloo 2 ExtraBold e Nunito Black | Google Fonts (OFL), servidas localmente | — |
