# @futexplicando — estúdio v3

Vídeos verticais (Reels/TikTok/Shorts) sobre polêmicas do futebol em cartoon chibi **vetorial**, animados em **Remotion** a partir de um roteiro em JSON. O próximo vídeo exige só `historias/<id>.json`, a narração e, se precisar, personagens ou objetos novos.

## Por que vetorial (e não IA)
A geração de imagem do Gemini exige faturamento na chave da API (a cota grátis é 0), e geradores grátis não mantêm o personagem igual de um quadro para outro. Por isso os personagens são componentes **SVG riggados** (`src/personagens/Chibi.tsx`):
- Olhos, sobrancelhas, boca e braços são peças trocáveis. A piscada, o lip-sync e as poses trocam sem o personagem "pular".
- O escudo oficial é preso na âncora do peito (`ESCUDO_ANCORA`), então sai sempre perfeito.
- Se um dia houver chave com faturamento, `tools/gimg.py` já gera e edita imagens no Nano Banana. Fundos ilustrados por IA podem entrar como camada `longe` sem mudar o resto.

## Estrutura
```
biblioteca/escudos/   escudos oficiais (SVG washingtonos/escudos-futebol-api → PNG 600 px)
biblioteca/musica/    trilhas CC0 + LICENCAS.md (licença de cada trilha e efeito)
biblioteca/sfx/       efeitos CC0 recortados (boom, whoosh, impacto, martelo, ding, torcida, chuva)
historias/<id>.json   roteiro: cenas → planos → camadas (o Remotion lê daqui)
videos/<id>/          narração (cena_XX.wav + .words.json), tempos.json, FONTES.md, revisão e render
src/estilo/tokens.ts  bíblia de estilo: paleta, contorno, peles, fontes
src/personagens/      Chibi (expressões, poses, uniformes) + ELENCO
src/cenarios/         estádio em camadas, tribunal, mesa, escritório, escuro, chuva, contraluz
src/motor/            Plano (câmera/parallax/camadas), Objetos, Video (transições, legenda), tempo
tools/                preparar.py (tempos), mixar.py (áudio final), sfx_cortar.py, gimg.py
```

## Fluxo de um vídeo novo
1. **Fatos:** checar o status atual de casos em aberto e anotar as fontes em `videos/<id>/FONTES.md`.
2. **Roteiro:** escrever `historias/<id>.json`. Cada cena tem `texto` (exato para o TTS), `transicao` (`whip`|`wipe`|`zoom`), `clima` opcional e `planos`. Cada plano tem `de` (palavra da fala onde o plano começa), `fundo`, `camera {zoom:[a,b], pan, punch}` e `camadas`.
   - **Tipos de camada:** `personagem` (quem, expr, pose, x, pe, alt, entra queda|lado|nenhum, fala, reacao pulo|tremor|balanco, cai, objeto), `titulo`, `carimbo`, `banner`, `pulsa`, `logo`, `relogio`, `relogioParede`, `placar`, `jornal`, `placaSubst`, `martelo`, `bloco`, `tabela`, `buraco`, `gordura`, `papel`, `placa`, `silhueta` e as partículas `confete`, `poeira`, `faiscas`, `chuva`, `flashes`.
   - **`em`:** palavra da fala (string) ou segundos a partir do início do plano (número).
3. **Narração:** Gemini TTS, voz **Fenrir** (alternativa: Puck), pt-BR, um arquivo por cena em `videos/<id>/narracao/cena_XX.wav`, com a instrução de estilo da série. Chave só pela variável `GEMINI_API_KEY`, **nunca gravada em arquivo**. Com cota curta, gerar tudo num pedido e cortar nos silêncios.
4. **Tempos por palavra:** Whisper em cada `cena_XX.wav` → `cena_XX.words.json`. Depois `python3 tools/preparar.py historias/<id>.json` gera `tempos.json` (duração = fala + 0,15 s antes + 0,35 s depois).
5. **Folha de contato:** `npx remotion still Contato-01-<cena> …`. Revisar cada plano: rosto coberto? texto ilegível? escudo errado?
6. **Áudio:** `python3 tools/mixar.py historias/<id>.json` → `public/<id>/mix.wav`, com efeitos nos impactos, ducking de ~10 dB e master em −14 LUFS / −1,5 dBTP.
7. **Prévia e render:**
   - Prévia: `npx remotion render <Id> videos/<id>/render/preview_540.mp4 --scale=0.5`.
   - Final: `npx remotion render <Id> videos/<id>/<id>_FINAL.mp4 --codec=h264 --crf=20 --audio-bitrate=192k`.
   - Capa: `npx remotion still Capa-<id> videos/<id>/capa.png`.

## Padrão de qualidade
- **Formato:** 1080×1920, 30 fps. Corte de plano a cada 1,5–3 s, sempre numa palavra da fala.
- **Câmera:**
  - Push-in contínuo de 4–6%; punch-in de 8% nos impactos.
  - Micro-tremida de mão (`@remotion/noise`, ~1,6 px) e tremida de impacto de 18 px decaindo em 0,4 s.
- **Profundidade:** fundo a 0,3× (com blur de 2 px), arquibancada a 0,6×, chão a 0,85×, personagens a 1× e partículas a 1,3×. Sombra de contato sob os pés.
- **Personagens:**
  - Entrada com mola, queda com squash e respiração (±1,5% em 1,7 s).
  - Piscada a cada 2,5–4 s e lip-sync pela amplitude da voz, só em quem "fala".
  - Reações por clima.
- **Tipografia:** Anton com contorno preto grosso, sombra e itálico leve. Títulos e carimbos batem na tela (escala 2,6→1 em 0,16 s) com tremida e som.
- **Legenda karaokê:**
  - Tempos do Whisper, `createTikTokStyleCaptions`, no máximo 3 palavras por página.
  - Palavra ativa em amarelo #FFD400 com mola 1→1,12.
  - Fica em y≈1330 (69%): fora das zonas de UI (12% de cima, 18% de baixo).
  - Regra de layout: **base da cabeça = pe − 0,54×alt ≤ 1230**, para a legenda nunca cobrir rosto.
- **Transições:** whip-pan com blur, wipe diagonal amarelo/preto ou zoom-through. Nunca corte seco entre cenas.
- **Acabamento:** vinheta, granulação leve, luz quente dos refletores e leve contraste.

## Regras da página
- Escudos oficiais; nunca numerar como episódio; um clube central por vídeo.
- Só fatos verificáveis; checar o status de casos em aberto antes de renderizar.
- Nenhuma pessoa real desenhada: jogadores, juízes e advogados são personagens genéricos. Falas de pessoas reais sempre em paráfrase, nunca entre aspas.
- O narrador não dá veredito; o CTA é sempre "comenta aí".
- Tragédias não entram nesse formato.
