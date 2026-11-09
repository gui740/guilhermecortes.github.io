# Reel: 3 filmes de terror de tubarão (@talking_horror)

## O que entregar
- `out/reel_tubarao.mp4`: vídeo final, 1080x1920, 30fps, H.264 High, yuv420p, 43s, **sem áudio**
- `out/reel_tubarao_com_sfx.mp4`: o mesmo vídeo com efeitos sonoros sutis (opcional)
- `out/sfx_opcional.wav`: só os efeitos (sonar, água, batida grave), sincronizados, pra mixar por baixo da música
- `out/capa.png`: capa 1080x1920. O texto cabe no recorte 3:4 do grid
- `FONTES.md`: filmes, streamings, data da checagem, links de cada número
- `LEGENDA_E_ROTEIRO.md`: legenda, as 2 opções de CTA e o roteiro

## Como renderizar de novo (Remotion)
Os textos e números ficam em `src/data.ts`.

```bash
npm install
npm run render
npm run cover
python3 tools/sfx.py out/sfx_opcional.wav
```

`npm run studio` abre o editor visual. Os scripts apontam para o Chromium em `/opt/pw-browsers`. Em outra máquina, tire o `--browser-executable`.
