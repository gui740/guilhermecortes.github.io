# AVISO AOS PESCADORES: RIO CUIABÁ

Vídeo procedural em estilo *analog horror* (boletim fluvial de TV dos anos 70) sobre
o Minhocão do Pari, lenda do folclore cuiabano. Imagens e efeitos sonoros são
desenhados e sintetizados por código; a narração vem do Gemini TTS.

```bash
pip install numpy Pillow scipy soundfile piper-tts
export GEMINI_API_KEY=...       # chave do Google AI Studio (narração)
python render.py --preview      # PNGs em saida/preview/
python render.py                # saida/aviso_pescadores_rio_cuiaba.mp4
```

Sem `GEMINI_API_KEY`, a voz cai para o Piper (`./assets/baixar_assets.sh`) ou espeak-ng.
As falas ficam em cache em `saida/cache_voz/`; o plano gratuito do Gemini permite
~10 falas por dia por modelo, por isso `config.TTS_MODELO_GRUPO` divide os grupos
de falas entre modelos e há troca automática quando a cota diária acaba.

Saída: 1080x1920, 30 fps, H.264 + AAC 48 kHz estéreo, ~95 s. Seed fixa 1974.
Textos, regras, tempos e `HANDLE` ficam em `config.py`. Créditos e fontes da pesquisa
em `assets/CREDITOS.txt`.
