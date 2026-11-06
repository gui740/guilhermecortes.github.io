# FITA 13: O ARSENAL

Vídeo analog horror vertical (1080x1920, 30 fps, ~98 s): imagem, ícones, efeitos VHS e áudio gerados por código, com narração do Zé Canhãozinho e fotos reais do Arsenal (licenças livres).

```
python render.py --preview   # 1 PNG por cena em saida/preview/
python render.py             # vídeo completo em saida/fita13_arsenal.mp4
```

Requisitos: Python 3.10+, numpy, Pillow, ffmpeg no PATH.

Narração: usa o **Gemini TTS** (Google AI Studio) quando há chave em `GEMINI_API_KEY`
(ou o caminho de um arquivo com a chave em `GEMINI_API_KEY_FILE`). As falas geradas ficam em
`assets/narracao_gemini/`; com elas lá, o render não precisa mais da chave. Para regerar uma voz,
apague o arquivo correspondente. Sem Gemini, a reserva é o Piper (`pip install piper-tts`).
Na primeira execução a voz pt-BR do Piper (`pt_BR-faber-medium`, ~60 MB) é baixada para `assets/vozes/`.
Sem Piper/sem internet, o vídeo sai com "blips" de voz no lugar da narração.

- `config.py` — tempos, textos, `HANDLE` do canal (troque ou deixe `""`), seed 1987.
- `eventos.py` — lista de falhas (estática, tracking, drop-outs, glitches) compartilhada entre vídeo e áudio (salva em `saida/eventos.json`).
- `cenas/` — uma função por bloco: `cena(t, frame_idx) -> PIL.Image 360x640`.
- `narracao.py` — roteiro falado: voz do Zé (aguda, pitch-shift WSOLA sem acelerar) e voz de terror nas regras (grave, camada uma oitava abaixo, eco; mais grave a cada regra). Velocidades em `VELOCIDADE_ZE`/`VELOCIDADE_TERROR`.
- `fx_vhs.py` — pipeline VHS; `icones.py` — ícones pixel-art 16x16; `audio.py` — síntese de áudio.
- `assets/fonts/*.ttf` — opcional, fonte estilo VCR OSD (senão usa DejaVu Sans Mono Bold).
- `assets/fotos/` — `fachada.jpg` e `varanda.jpg` são fotos reais do Wikimedia Commons (créditos em `assets/fotos/CREDITOS.txt` e no cartão final). Dá para trocar por fotos próprias, e também adicionar `patio.jpg` e `porao.jpg`.

Obra de ficção. Fatos históricos reais; eventos sobrenaturais inventados. Sem relação com o Sesc.
