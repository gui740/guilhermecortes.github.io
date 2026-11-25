# O TAMANHO REAL DOS PLANETAS — YouTube Short (v2)

Vídeo 100% gerado por código: 1080x1920, 30 fps, ~59,5 s, narração Gemini TTS, legenda palavra por palavra, loop perfeito.

```
GEMINI_KEY_FILE=/caminho/da/chave ./make.sh   # -> out/tamanho_real_dos_planetas_v2.mp4
```

A linha do tempo inteira sai dos tempos da narração: cada cena começa quando a fala dela começa.
Mudou o texto em `narracao.json`? Apague `out/narr_gemini/` e `out/video_mudo.mp4` e rode de novo.

| arquivo | o que faz |
|---|---|
| `narracao.json` | as 20 falas (e a pausa depois de cada uma) |
| `tts_gemini.py` | narração Gemini TTS (`gemini-2.5-flash-preview-tts`, voz Puck) numa chamada só, cortada nas pausas |
| `tts_provisorio.py` | narração reserva (Edge TTS): `NARR=out/narr ./make.sh` |
| `plan.py` | transforma as falas em linha do tempo |
| `render.py` | cenas, câmera, contagens de Terras, enchimento do Sol, Betelgeuse, legendas (`python render.py preview 0 12.5 40` para frames-chave) |
| `engine.py` | motor: texturas procedurais, esferas 3D, Sol com proeminências, fundo, textos |
| `audio.py` | trilha 110 bpm, whooshes, pops com tom subindo, ticks, risers, booms, enxame, whoosh reverso, ducking sob a voz |
| `fonts/` | Anton e Montserrat Black (SIL OFL) |

## Roteiro
1. Terra + "A TERRA PARECE GRANDE?" (frame 0) → régua medindo 12.742 km
2. Vizinhos: Mercúrio 38%, Marte 53%, Vênus 95% ("quase gêmea")
3. Gigantes, cada um com Terras se enfileirando sobre ele: Netuno 3,9 · Urano 4 · Saturno 9,1 → 21 com anéis · Júpiter 11
4. Zoom na Grande Mancha Vermelha com uma Terra ao lado
5. "AGORA OLHA O SOL..." → riser, o Sol entra pela direita, flash + tremor + BOOM, Sol inteiro com proeminências
6. 109 Terras atravessando o diâmetro (contador 1x → 109x)
7. Enxame de Terras voando para dentro e enchendo o Sol (contador até 1.300.000) → "DENTRO DELE CABEM 1,3 MILHÃO DE TERRAS"
8. Zoom na Terra: "VOCÊ ESTÁ AQUI"
9. Reviravolta: o Sol encolhe até virar um ponto perto de Betelgeuse (~760x o Sol)
10. "QUAL A PRÓXIMA COMPARAÇÃO? COMENTA AÍ!" → zoom de volta até a Terra = frame 0

Área segura respeitada: nada importante nos 300 px de baixo nem nos 120 px da direita.
