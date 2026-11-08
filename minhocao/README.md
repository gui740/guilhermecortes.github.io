# AVISO AOS PESCADORES: RIO CUIABÁ

Vídeo procedural em estilo *analog horror* (boletim fluvial de TV dos anos 70) sobre
o Minhocão do Pari, lenda do folclore cuiabano. Tudo é desenhado e sintetizado por código.

```bash
pip install numpy Pillow scipy soundfile piper-tts
./assets/baixar_assets.sh     # voz Piper pt_BR (sem ela, usa espeak-ng)
python render.py --preview    # PNGs em saida/preview/
python render.py              # saida/aviso_pescadores_rio_cuiaba.mp4
```

Saída: 1080x1920, 30 fps, H.264 + AAC 48 kHz estéreo, 81 s. Seed fixa 1974.
Textos, tempos e `HANDLE` ficam em `config.py`. Créditos em `assets/CREDITOS.txt`.
