# Perguntas que eu me fiz quando estava chapado — Expectativa de vida

Vídeo em colagem de papel + parallax + recortes, 100% desenhado em código (SVG). Vertical 1080x1920, 30 fps, ~110 s,
com faixa de áudio vazia para a narração.

```
node render.js --out chapado_expectativa_de_vida.mp4      # vídeo inteiro
node render.js --cena cena3 --dur 10                      # preview de uma cena
node render.js --cena cena6 --frames 2,8.5,15             # PNGs de frames-chave em out/frames/
```

Stack: HTML + SVG com motor próprio de animação (cada frame é função do tempo), capturado pelo Chromium do Playwright
e montado com ffmpeg. Abra `index.html?cena=cena1` no navegador e chame `setup().then(() => renderFrame(3))` no console para ver um frame.

## Onde mexer
| arquivo | o quê |
|---|---|
| `config.js` | `FORMATO` (SHORTS 1080x1920 / YOUTUBE 1920x1080), `FPS`, `PALETA`, `CENAS` (duração e legendas de cada cena), `TRANSICAO` |
| `scenes/cenaN.js` | uma cena por arquivo (`SCENES.cenaN = function (stage, cfg) {...}`) |
| `lib/components.js` | componentes do canal (abaixo) |
| `lib/art.js`, `lib/art2.js` | ilustrações de gravura: bolo, vela, chama, caveira, mãos, olho, lua, nuvem, bebê, idoso, vírus, globo, balança, cabeça, engrenagem, coração, cérebro, chave, post-it, fita, fumaça, jornal… |
| `lib/props.js` | `CakeWithCandles` (bolo com N velas acendendo) e `StringGraph` (gráfico de barbante com os dados do IBGE) |

## Componentes reutilizáveis
- **`Scene`**: câmera com push-in contínuo (1,0 → 1,08) e drift lateral; `sc.layers([...profundidades])`; `sc.updaters` para a lógica da cena; `sc.shake` para tremida.
- **`ParallaxLayer`**: cada camada se move/escala proporcionalmente à profundidade (0 = fundo, 1 = primeiro plano).
- **`PaperCutout`**: qualquer desenho vira recorte (borda branca irregular, sombra dura, rotação aleatória ±4°, "respira" com pivô na base, entra com pop em stop-motion a 12 fps). `setArt()` troca o desenho (olho piscando, chama tremendo).
- **`RansomText`**: letras de revista recortada (fonte, cor e papel diferentes por letra), entrando uma a uma; `maxW` faz caber na tela.
- **`AnimatedNumber`**: número gigante recortado contando (`from`, `to`, `dec`, `suffix`).
- **`TornTransition`**: papel rasgando e revelando a próxima cena (aplicado automaticamente entre as cenas).
- **`Caption`**: legenda mostarda com contorno preto numa tira de papel preto; encolhe para caber.
- **`PaperBackground`**: papel envelhecido de qualquer cor (granulação, manchas, vincos, vinheta).
- **`Sunburst`**: raios de sol em retícula girando atrás do assunto. **`tornBlob()`**: mancha de papel rasgado para destacar o assunto.

## Narração
As legendas em `config.js` são o roteiro sugerido. Gravou a narração? Ajuste `dur` e os tempos das legendas de cada cena,
renderize de novo e junte o áudio:
```
ffmpeg -i out/chapado_expectativa_de_vida.mp4 -i narracao.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest final.mp4
```

## Dados usados
Expectativa de vida ao nascer no Brasil (IBGE): 74,4 (2010) → 76,4 (2019) → 72,8 (2021) → 76,6 (2024); no mundo,
73,3 anos (ONU, 2023); Brasil de 1940: ~45 anos. Anos intermediários do gráfico são aproximados. "58% → 74%" foi usado
como no roteiro (participação das doenças crônicas nas mortes) — confira a fonte antes de publicar.
