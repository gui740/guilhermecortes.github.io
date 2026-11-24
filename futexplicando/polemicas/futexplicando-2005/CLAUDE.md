# @futexplicando — "2005 FOI DO INTER?!"

Cópia do projeto "87 É DE QUEM?!" adaptada para o Brasileirão de 2005. O clube central é o Internacional e o rival é o Corinthians.

## Como rodar
1. `narracao/cena_01.wav … cena_10.wav` já existem: Gemini TTS, voz Fenrir, instrução de estilo da série. `narracao/palavras_asr.json` guarda o tempo de cada palavra (Whisper), usado na legenda karaokê e para os elementos entrarem no momento da fala.
2. `python3 preview.py` gera a folha de cenas (`sheet.jpg`).
3. `python3 finalizar.py` refaz o tempo das cenas pela voz, renderiza o vídeo, regera trilha e efeitos, mixa e gera **`fut2005_FINAL.mp4`**.

## O que mudou em relação ao 87
- **Estilos misturados:** o chibi da série ganhou textura de grão e vinheta, fotos reais (polaroid com fita e TV de tubo com scanlines), carimbo grunge do ano e etiquetas de papel rasgado.
- **Animação:**
  - Câmera com zoom e pan em toda cena, com paralaxe (fundo a 60%).
  - Molas com overshoot e carimbos que batem e tremem a tela.
  - Slide, drop, cartão vermelho voando e respiração dos personagens.
  - Transições alternando whip pan com borrão e crossfade, no lugar do flash branco.
- **Sincronia:** os elementos entram na palavra falada (`when(...)`), e a legenda acende a palavra do momento.
- **Novos clubes:** COR (camisa branca com detalhes pretos, calção preto), ARB (árbitro), SAN e SAO. Escudos de `washingtonos/escudos-futebol-api`, convertidos para PNG de 600 px.
- **Áudio:** torcida gravada (CC0), whoosh e apito em senoide (sem ruído/chiado).

## Regras da página
- Formato da série: título em pergunta "?!", dois lados, o narrador não dá veredito e o CTA é "comenta aí".
- Falas do Edílson e do Dualib sempre em paráfrase, nunca entre aspas.
- Chave do Gemini só pela variável `GEMINI_API_KEY`; nunca gravar em arquivo.
