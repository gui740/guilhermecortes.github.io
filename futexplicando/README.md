# @futexplicando – template de vídeo (Remotion)

Vídeo vertical 1080x1920, 30 fps. **Todo texto, número, imagem e timing fica no JSON** (`src/data/ep01.json`).

## Comandos
```bash
npm i
npm run dev      # Remotion Studio (preview)
npm run voz      # gera public/voz.mp3 + timing palavra a palavra no JSON
npm run render   # out/ep01-historia-palmeiras.mp4 (H.264, veryfast)
npm run capa     # out/capa.png
```
Voz: com `ELEVENLABS_API_KEY` no ambiente usa ElevenLabs (`voice.elevenVoiceId` no JSON); sem a chave usa Edge TTS (grátis).

## Novo episódio
1. Copie `src/data/ep01.json` → `ep02.json` e troque o import em `src/lib/episode.ts`.
2. Edite `scenes[]`: cada cena tem `type` (hook, foundation, nameswap, pitch, timeline, stat, cta), `narration`, `image` e `props`.
   As animações sincronizam por **palavra falada** (`sync`/`syncWords`/`word`): é só apontar para uma palavra da narração.
3. Troque paleta (`palette`), imagens (`public/img`) e rode `npm run voz` e `npm run render`.
4. Ajuste os nomes de saída nos scripts `render` do `package.json`.

## Estrutura
- `src/scenes/` uma cena por arquivo (`index.ts` mapeia `type` → componente)
- `src/components/` peças reutilizáveis: Hook, YearStamp, NameSwap, Pitch, Timeline, StatSlam, Captions, PhotoCard, Newspaper, Badge, Intro (vinheta 0,5s), PaperGrain…
- `src/data/` JSON do episódio · `public/` fontes, sons, voz, imagens · `docs/fontes.md` checagem e licenças
