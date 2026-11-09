# Reel — "3 filmes de terror que ninguém te indicou" (@talking_horror)

Vídeo vertical 1080×1920, 30 fps, estilo **parallax 2.5D + colagem recortada / quadro de investigação**, feito em **Remotion** (React + TypeScript).

**Saída:** `out/reel-parallax-terror.mp4` · frames de revisão em `out/frames/` · testes de voz em `out/testes-voz/`

## Refazer do zero

```bash
npm install
pip install rembg onnxruntime opencv-python-headless faster-whisper pillow numpy scipy "av<15"
export GEMINI_API_KEY=...            # nunca coloque a chave no código

python3 scripts/narracao.py Zubenelgenubi        # roteiro inteiro numa chamada (pt-BR) -> 1 wav por cena + timestamps
                                                 #   (2º argumento opcional: modelo, ex. gemini-3.8-flash-tts com billing)
python3 scripts/recortar.py                      # recortes de papel (BiRefNet) + fundos -> assets/<filme>/
                                                 #   se faltar memória: python3 scripts/recortar.py <filme> <nome>
python3 scripts/sfx.py                           # efeitos sonoros sintetizados (a trilha é assets/trilha/hitman.mp3)
python3 scripts/texturas.py                      # quadros de granulação de filme

npm run studio                                   # preview interativo
npm run render                                   # -> out/reel-parallax-terror.mp4 (H.264 CRF 18, AAC 192k)
node --experimental-strip-types scripts/frames.mjs   # 5 frames de amostra -> out/frames/
```

## Onde mexer
- **Durações das cenas:** `src/config/timing.ts` (comentado). As cenas seguem a narração automaticamente.
- **Roteiro/narração:** `config/roteiro.json` → rodar `narracao.py` de novo (evite reticências: viram pausas longas).
- **Quais imagens entram:** `config/imagens.json` → `recortar.py`. Para corrigir um recorte ruim, desenhe
  `assets/raw/<filme>/<arquivo>_mask.png` (branco = manter) e rode `python3 scripts/recortar.py <filme> <nome>`.
- **Layout de cada cena:** `src/scenes/*.tsx` (posições em px no quadro 1080×1920; área segura: y 250–1520).
- **Legendas/palavras-chave em vermelho:** `src/components/Captions.tsx`.
- **Mixagem:** `src/Reel.tsx` (`VOL_TRILHA`/`VOL_DUCK`, trecho inicial da música `TRILHA_INICIO_S`) e `src/sfx.ts`.
- **Crédito obrigatório da música (CC BY):** "Hitman" Kevin MacLeod (incompetech.com), CC BY 4.0 — ver `assets/creditos.txt`.

## Estrutura
```
src/Root.tsx  src/Reel.tsx  src/sfx.ts
src/components/  PaperBackground Cutout ParallaxLayer HandArrow RedString Tape TornReveal
                 Scribble Annotation FilmTag Captions FilmGrain KidnapTitle Camera Cenario
src/scenes/      Hook Possum Calvaire Hagazussa Outro
src/config/      timing.ts (ajustes)  cenas.ts
scripts/         narracao.py recortar.py sfx.py texturas.py commons.py frames.mjs
assets/          possum/ calvaire/ hagazussa/ narracao/ sfx/ trilha/ fonts/ textura/ raw/ creditos.txt
```
Origem de cada arquivo: `assets/creditos.txt`.
