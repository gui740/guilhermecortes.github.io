# Reel: 3 filmes de terror de tubarão (@talking_horror)

## O que entregar
- `out/reel_tubarao_narrado.mp4`: **vídeo final**, 1080x1920, 30fps, H.264 High, 1:10, com narração, trilha e efeitos
- `out/reel_tubarao_sem_audio.mp4`: o mesmo vídeo, mudo
- `out/narracao.wav`, `out/trilha.wav`, `out/sfx.wav`: as três faixas separadas, pra remixar no editor ou trocar a trilha por uma música do Instagram
- `out/capa.png`: capa 1080x1920
- `FONTES.md`: filmes, streamings, data da checagem e fonte de cada número
- `LEGENDA_E_ROTEIRO.md`: legenda, as 2 opções de CTA e o roteiro com a narração

## Como renderizar de novo (Remotion)
Os textos e números ficam em `src/data.ts`.

```bash
npm install
npm run render
npm run cover
bash audio/mixar.sh
```

O `mixar.sh` monta a narração, gera a trilha e os efeitos, mixa tudo e junta com o vídeo.

Os tempos das cenas ficam em `src/timeline.json` e os momentos de cada fala em `cues`, no `src/data.ts`. Para regravar a voz, rode `GOOGLE_API_KEY=... python3 audio/gemini_tts.py`. A cota grátis é de 10 pedidos por dia, e depois disso é preciso atualizar os cortes `in`/`out` em `audio/narracao.json`.

`npm run studio` abre o editor visual. Os scripts apontam para o Chromium em `/opt/pw-browsers`. Em outra máquina, tire o `--browser-executable`.
