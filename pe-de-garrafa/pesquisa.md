# Pesquisa — Lenda do Pé de Garrafa (MT)

## O que a tradição diz
| Elemento | Detalhe | Fonte |
|---|---|---|
| Nome | "Pé de garrafa": pé maciço e redondo como fundo de garrafa, deixa pegadas redondas e fundas | Cascudo, *Dicionário do folclore brasileiro*; Wikipedia |
| Corpo | Uma perna só, peludo, com casco/pé redondo (informante Sebastião Alves Correia, Jacobina-MT, a Alípio de Miranda Ribeiro) | Wikipedia (citando Miranda Ribeiro); ANPUH 2019 |
| Tamanho | Gigante, "a cabeça batia nas folhas das árvores mais altas", um olho só (Manuel Ambrósio, 1912) | Wikipedia |
| Grito/assobio | Grito fino que imita um companheiro perdido pedindo socorro; quem segue se perde, entra em delírio/loucura. Grito "multiplicado em todas as direções" | Wikipedia; Correio do Estado; Cryptid Archives |
| Pegada | Redonda, sem ponta nem calcanhar: não dá pra saber pra que lado ele foi — faz o poaieiro se perder | Wikipedia; Cryptid Archives |
| Ponto fraco | O UMBIGO BRANCO, único lugar sem pelo; só escapa quem acerta ali | Todamateria; Melhor Escola; livro Turma do Folclore (AL-MS) |
| Comer gente? | Cascudo: não há testemunho de que coma gente — o terror é sumir/enlouquecer | Cascudo via Wikipedia |
| Parentesco | Variante do Mapinguari/Capelobo (Cascudo); "espécie de Caapora" (Barroso, 1932) | Wikipedia |

## Versões juntadas
1. **Poaieiros de MT (pós-Guerra do Paraguai)** — relatos mais antigos de MT ligados à extração da poaia (ipecacuanha) na região de Cáceres, Barra do Bugres, Tangará da Serra, Vila Bela e Cuiabá; estudo de Maria Cristina de Aguiar Campos (Cefet/IFMT) sobre a Baixada Cuiabana.
2. **Caçador e o assobio** — o bicho assobia/grita quando ouve caçador; o caçador acha que é o companheiro, vai ao encontro e não volta.
3. **Gigante de um olho (Ambrósio)** + **umbigo branco** (versão escolar/MS).

## Elementos escolhidos para o vídeo (mais assustadores e visuais)
- Assobio/grito com a **voz de um companheiro** ("Ô, compadre!") → terror psicológico, ótimo pro gancho.
- **Pegada redonda** que não mostra direção → contador de pegadas na HUD; pegadas que "dão volta" no personagem.
- **Uma perna só, peludo, altíssimo, um olho** → aparição em silhueta na névoa, olho vermelho.
- **Umbigo branco** → "ponto fraco" estilo boss de videogame.
- Ambientação: **poaieiro velho, beira do Rio Paraguai perto de Cáceres**, fogueira, lamparina, piúva (ipê-roxo), cerrado/pantanal.
- Toque cuiabano na fala: "compadre", "ixi", "tchá por Deus", "lá pras bandas de".

Descartadas (já usadas): Minhocão, Casarão dos Bandeirantes, Sesc Arsenal.

## Referências visuais e de ritmo
- Pixel art horror 8/16-bit: paletas limitadas (estilo NES/Game Boy/SNES), sprites pequenos ampliados com nearest-neighbor, parallax de camadas, scanlines CRT, flicker de luz, tela de GAME OVER/CONTINUE com contagem.
- Retenção em short-form: gancho em 1–2 s (pergunta/ameaça aberta + imagem forte), abrir um "loop" no início e só fechar no fim, texto na tela (muita gente assiste sem som), final que volta ao começo para rever.

## Narração (TTS)
- Gemini API, modelo `gemini-3.8-flash-tts` (atual, mais expressivo), 30 vozes pré-prontas; candidatas para narrador noturno: **Algenib** (gravelly), **Charon**, **Gacrux** (mature), **Enceladus** (breathy, para sussurros). Controle de estilo via `speech_metadata.style` + tags `<whisper>`, `<long pause>`, `<breath>`. Saída WAV 24 kHz mono.

## Fontes
- Wikipedia — Pé de garrafa: https://en.wikipedia.org/wiki/P%C3%A9_de_garrafa
- Campos, M. C. A. — artigo Profiscientia (IFMT): https://profiscientia.ifmt.edu.br/profiscientia/article/download/136/134/264
- ANPUH 2019 (poaia, Barra do Bugres, Miranda Ribeiro): https://anpuh.org.br/uploads/anais-simposios/pdf/2019-01/1548206369_57396124ffe12384928bb89244ee7b68.pdf
- Toda Matéria — Lendas do Centro-Oeste: https://www.todamateria.com.br/lendas-da-regiao-centro-oeste/
- Correio do Estado — lendas sul-mato-grossenses: https://correiodoestado.com.br/cidades/lendas-urbanas-povoam-imaginario-dos-sul-mato-grossenses/130153/
- Melhor Escola — criaturas pouco conhecidas: https://www.melhorescola.com.br/artigos/3-personagens-do-folclore-brasileiro-que-voce-provavelmente-nunca-ouviu-falar
- AL-MS — livro Turma do Folclore: https://al.ms.gov.br/upload/Pdf/2025_07_17_09_16_18_livro-digital-turma-do-folclore.pdf
- Cryptid Archives: https://cryptidarchives.fandom.com/wiki/P%C3%A9_de_garrafa
- Gemini speech generation docs: https://aistudio.google.com/docs/speech-generation
- Hooks/retensão: https://www.gofaceless.ai/en/blog/mastering-first-impressions-two-second-rule , https://dev.to/bulkdl/hook-engineering-the-science-of-the-first-3-seconds-in-short-form-video-2026-2jp9
