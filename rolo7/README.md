# ROLO 7: A CASA DA ESQUINA

Vídeo de analog horror gerado 100% por código (vertical 1080x1920, 30 fps, ~83 s),
inspirado na lenda urbana do "Casarão Assombrado" do bairro Bandeirantes, em Cuiabá-MT.

## Requisitos

```
pip install -r requirements.txt
apt-get install ffmpeg espeak-ng mbrola mbrola-br4
```

## Uso

```
python render.py --preview          # 1 PNG por cena em saida/preview/
python render.py --preview --t 12 61   # PNGs de tempos específicos
python render.py                    # saida/rolo7_casa_da_esquina.mp4
python render.py --sem-audio        # reaproveita saida/audio.wav
```

Ajustes em `config.py`: `HANDLE`, `INCLUIR_CARTAO_HISTORIA`, `SEED`, textos, tempos e motor de voz
(`VOZ_MOTOR = "mbrola"` ou `"espeak"`).

## Estrutura

- `render.py`: eventos de glitch (vídeo e áudio usam a mesma lista), quadros em paralelo, pipe para o ffmpeg
- `cenas/`: uma função por cena, `cena(t, i) -> PIL.Image 360x640`
- `fx_vhs.py`: efeitos de VHS/fita (croma, halo, scanlines, grão, jitter, tracking, head-switch, CRT, drop-outs, glitches, estática)
- `icones.py`: ícones pixel-art 16x16 em texto
- `voz.py`: TTS offline e tratamento de fita de rolo
- `audio.py`: síntese dos SFX e música, mixagem e normalização (-1 dBFS)
- `assets/CREDITOS.txt`: fontes, voz e licenças

`saida/rolo7_casa_da_esquina_leve.mp4` é uma versão comprimida (CRF 30) para caber no GitHub.
O arquivo final em CRF 20 tem cerca de 300 MB por causa do grão de VHS. Gere-o localmente com `python render.py`.
