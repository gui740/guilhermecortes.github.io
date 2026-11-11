# CELSO: A VINGANÇA DO PARQUE

Vídeo vertical para o Reels do **@terroremmatogrosso**: terror retrô 8/16-bit em estilo fliperama dos anos 80, com tela CRT (scanlines, curvatura leve, aberração cromática, bloom), glitch e ruído VHS.

- **Entrega:** `output/celso_a_vinganca_do_parque.mp4` (1080x1920, 30 fps, H.264 High + AAC 192k, ~75 s com gancho e narração)
- **Trilha sem narração:** `output/trilha_sem_narracao.wav` (música + SFX, para mixar num editor, se preferir)
- **Frames-chave:** `output/previews/` (`00_contato.png` é a folha com todos)

Tudo é gerado por código (Python + numpy + Pillow + ffmpeg): pixel art, animação, música chiptune e efeitos sonoros. Nenhum asset externo.

## Estrutura

```
celso-vinganca/
├── assets/
│   ├── prompts_imagens.txt      # prompts para gerar os sprites/cenários numa IA de imagem
│   ├── narracao.txt             # roteiro + momento de cada fala no vídeo
│   └── gerados/                 # pixel art feita pelo gerador (mesmo formato dos prompts)
│       ├── celso_sheet.png          6 frames: idle, anda A, anda B, alerta, boca aberta, olhos na água
│       ├── visitantes_sheet.png     2 linhas x 11 frames (visitante A / visitante B)
│       ├── capivara_sheet.png       3 frames
│       ├── celso_jumpscare.png      2 frames de tela cheia
│       ├── bg_dia.png / bg_noite.png  prévia do cenário montado
│       └── camadas_dia/ camadas_noite/  céu, prédios, árvores, lagoa, chão (parallax)
├── src/
│   ├── gerar_assets.py   # gera a pixel art em assets/gerados/
│   ├── fonte.py          # fonte pixel 5x7 feita à mão (acentos PT-BR, ♥)
│   ├── timeline.py       # cenas, falas, eventos e sincronização com a narração
│   ├── audio.py          # trilha chiptune + SFX + ducking da narração
│   └── render.py         # cenas, HUD, CRT/VHS, legendas e encode com ffmpeg
└── output/
```

## Como renderizar

Requisitos: Python 3.10+, `numpy`, `Pillow` e `ffmpeg` no PATH.

```bash
cd celso-vinganca
python3 src/gerar_assets.py        # (opcional) recria a pixel art de assets/gerados/
python3 src/render.py --preview    # frames-chave em output/previews/ (segundos)
python3 src/render.py              # vídeo final em output/ (~6 min com 4 núcleos)
```

## Trocar a arte pelas imagens da IA

Gere as imagens com os prompts de `assets/prompts_imagens.txt` e salve **direto em `assets/`** com estes nomes:

| arquivo | layout esperado |
|---|---|
| `celso_sheet.png` | 1 linha x 6 frames iguais, virado para a direita, fundo `#00FF00` |
| `visitantes_sheet.png` | 2 linhas x 11 frames iguais (ordem nas notas do arquivo de prompts), fundo `#00FF00` |
| `bg_dia.png`, `bg_noite.png` | imagem vertical 9:16; pista mais ou menos entre 57% e 66% da altura |
| `capivara_sheet.png`, `celso_jumpscare.png` | opcionais (veja as notas no arquivo de prompts) |

Quando há um PNG em `assets/`, o render usa ele no lugar do gerado: remove o chroma verde, corta os frames em células iguais e escala **sempre com nearest-neighbor** (sem blur). Os cenários do usuário viram parallax em faixas horizontais. Depois é só rodar `python3 src/render.py` de novo.

## Narração

A narração atual foi gerada com o TTS do Gemini (Google AI Studio), voz **Algenib**, modelo
`gemini-2.5-flash-preview-tts`: `assets/narracao.wav` (roteiro) + `assets/narracao_gancho.wav` (gancho).
Para gerar de novo (outra voz, por exemplo):

```bash
export GEMINI_API_KEY=sua_chave      # nunca coloque a chave em arquivo do repositório
python3 src/gerar_narracao.py --voz Algenib      # outras vozes: Charon, Fenrir, Enceladus, Orus...
python3 src/render.py
```

A narração é acelerada em 1,2x no render (`NARR_SPEED` em `src/timeline.py`, sem mudar o tom). O script faz só 2 pedidos (roteiro inteiro + gancho), porque a cota gratuita é de 10 pedidos por dia por modelo.

Para usar uma gravação sua:

1. Grave o texto de `assets/narracao.txt` (Google AI Studio) e salve como **`assets/narracao.wav`** (qualquer taxa de amostragem, mono ou estéreo).
2. Rode `python3 src/render.py`.

O render detecta as 9 falas pelas pausas de silêncio, coloca cada uma no momento do roteiro e aplica **ducking** na trilha enquanto a voz fala. Se uma fala for mais longa que o espaço dela, as cenas seguintes são empurradas e o vídeo fica um pouco mais longo, sem cortar a voz. O modo usado aparece no terminal (`modo: ...`).
Se a detecção errar, crie `assets/narracao_marcas.txt` com 9 números (um por linha): o segundo em que cada fala começa **dentro do WAV**.

Sem `narracao.wav`, o vídeo usa os tempos do roteiro e mantém as legendas na tela.

## Cenas (tempos do roteiro, contados depois do gancho; com narração as cenas esticam para acompanhar a voz)

| tempo | cena |
|---|---|
| gancho (~5 s) | "E SE O CELSO RESOLVESSE SE VINGAR?" palavra por palavra sobre a lagoa vermelha, com o Celso abrindo a boca e um flash subliminar do jumpscare |
| 0–5 s | Tela de título arcade, "PRESS START", ficha (moeda) |
| 5–15 s | LEVEL 1 – DIA: parallax, Celso respirando, capivara e coraçãozinho, HUD com a paciência em 100% |
| 15–25 s | Visitantes rindo, puxão no rabo, freeze + "!!" + glitch, paciência cai a 0%, "VOCÊ IRRITOU O MORADOR ERRADO.", Celso some na lagoa |
| 25–35 s | LEVEL 2 – A NOITE: transição pixelada, postes acendem, Show das Águas colorido que fica vermelho, neblina, olhos se aproximando |
| 35–52 s | Perseguição side-scroller, contador de DISTÂNCIA, postes apagando um a um, pau partindo em pixels ("CRACK!"), tela tremendo |
| 52–58 s | Jumpscare 8-bit (boca em tela cheia), flash branco de 2 frames, tela preta, "CONTINUE?" |
| 58–63 s | GAME OVER / "NÃO MEXA COM O CELSO", Celso de volta à lagoa com a paciência recarregando |
| 63–70 s | Aviso final + @terroremmatogrosso |

Legendas: fonte pixel com contorno preto, centralizadas um pouco à esquerda e entre y≈1290 e 1480 px. Ficam fora da área do topo, da descrição e dos botões do Reels.

*Obra de ficção. O jacaré Celso é dócil e vive em seu habitat natural. Não toque, não alimente, não provoque. Maus-tratos a animais é crime (Lei 9.605/98).*
