# O TAMANHO REAL DOS PLANETAS — YouTube Short

Vídeo 100% gerado por código: 1080x1920, 30 fps, 25 s (750 frames), loop perfeito.

```
./make.sh        # narração -> áudio -> vídeo -> out/tamanho_real_dos_planetas.mp4
```

| arquivo | o que faz |
|---|---|
| `render.py` | planetas 3D procedurais, câmera, textos e cartões (`python render.py preview 0 5.2 15.4` gera frames-chave em `out/preview`) |
| `audio.py` | trilha 110 bpm (Am–F–C–G), whooshes, blips, ticks, riser, boom, whoosh reverso, ducking sob a voz |
| `narracao.json` | falas e o momento (s) em que cada uma entra |
| `tts_provisorio.py` | narração **provisória** (Edge TTS, pt-BR-AntonioNeural) |
| `fonts/` | Anton (números) e Montserrat Black (textos), SIL OFL |

## Trocar pela narração do AI Studio
Gere um arquivo por fala (`n00.wav`, `n01.wav`, … na ordem de `narracao.json`), coloque numa pasta e rode:

```
rm -f out/tamanho_real_dos_planetas.mp4
NARR=pasta_com_falas ./make.sh
```

O vídeo não é renderizado de novo (usa `out/video_mudo.mp4`); só o áudio é remixado. Os silêncios no começo e no fim das falas são cortados automaticamente, e o script avisa se alguma fala invadir a seguinte.

## Linha do tempo
| s | cena |
|---|---|
| 0,0 | Terra + "A TERRA PARECE GRANDE?" (já no frame 0) |
| 1,7 | Mercúrio, Marte e Vênus aparecem — "PERTO DOS VIZINHOS, ATÉ QUE SIM..." |
| 3,9 | "MAS AÍ CHEGAM OS GIGANTES": Netuno 4,9 · Urano 6,9 · Saturno 8,9 · Júpiter 10,9 (cartões) |
| 12,4 | "AGORA OLHA O SOL..." + riser, zoom-out longo, Sol entra pela direita |
| 15,4 | flash + tremor + BOOM, contador 1x → 109x |
| 17,6 | seta "VOCÊ ESTÁ AQUI" |
| 19,8 | "DENTRO DELE CABEM 1,3 MILHÃO DE TERRAS" · 22,4 "QUAL A PRÓXIMA COMPARAÇÃO?" |
| 24,0 | zoom rápido de volta até a Terra, fecha no frame 0 |

Área segura respeitada: nada importante nos 300 px de baixo nem nos 120 px da direita.
