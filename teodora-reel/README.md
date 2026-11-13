# Teodora · A moça do Cemitério da Piedade (Reel @terroremmatogrosso)

Reel vertical (1080×1920, 30 fps, ~44 s) em colagem vintage animada, sobre a lenda cuiabana de Teodora.

| Arquivo | O que é |
|---|---|
| `pesquisa.md` | resumo da lenda e do cemitério, com fontes e divergências |
| `creditos.md` | fonte e licença de cada imagem e som (e texto pronto para a legenda) |
| `narracao.txt` | roteiro com marcações de pausa para o Google AI Studio |
| `src/timings.json` | **todos os tempos**: falas/cenas, transições, perda de cor, efeitos sonoros |
| `src/reel.js` | a animação (canvas): cada cena é uma função do tempo |
| `src/index.html` | prévia no navegador (barra de tempo, play com áudio, zonas seguras) |
| `tools/` | scripts: baixar/processar imagens, montar áudio, renderizar |
| `out/frames/` | um quadro PNG por cena (para aprovação) |

## Como usar

```bash
pip install rembg onnxruntime numpy scipy pillow     # recorte e áudio
# (Node 18+ e Playwright com Chromium; ffmpeg)

python3 tools/process_assets.py        # imagens: assets/raw → assets/cut (+ src/assets.json)
python3 tools/build_audio.py           # trilha + efeitos → out/audio_mix.wav (e out/stems/)
node tools/render.js stills            # um PNG por cena → out/frames/
node tools/render.js video --audio out/audio_mix.wav   # MP4 final → out/teodora_reel.mp4
```

Prévia interativa: rode `python3 -m http.server` na pasta `teodora-reel/` e abra
`http://localhost:8000/src/index.html`.

## Sincronizar com a narração

1. Gere a voz no AI Studio a partir de `narracao.txt`.
2. Anote em que segundo começa cada frase e edite `start`/`end` das falas em `src/timings.json`
   (a cena seguinte começa no `end` da anterior). Opcional: `wordsAt` com o instante de cada palavra.
3. Ajuste também o bloco `audio` (chuva, portão, motor, sustos) e `colorDrainStart/End`.
4. `python3 tools/build_audio.py` e renderize de novo. Para juntar a voz:
   `ffmpeg -i out/teodora_reel.mp4 -i voz.wav -filter_complex "[0:a]volume=0.6[m];[m][1:a]amix=inputs=2:duration=first[a]" -map 0:v -map "[a]" -c:v copy -c:a aac out/teodora_final.mp4`

O número da lenda ("LENDA Nº 07") e as frases da prancha final ficam em `timings.json → prancha`.
