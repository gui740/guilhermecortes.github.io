# @futexplicando — vídeo "87 É DE QUEM?!" (continuação)

Projeto vindo de uma conversa no app Claude. O vídeo está pronto (cenas, escudos oficiais, legendas, trilha e efeitos). **Falta só a narração em voz do Gemini.** O ambiente anterior não alcançava a API do Google; aqui no computador do usuário alcança.

## O que já existe
- `render.py`: desenha e anima as 10 cenas (cartoon chibi, 9:16, 30fps). `SCENES` tem o texto de cada cena.
- `audio.py`: sintetiza trilha (100 BPM, Lá menor) e efeitos sincronizados com as cenas (whoosh, pop, carimbo, martelo, ding, torcida). Lê `timings.json`.
- `finalizar.py`: lê `narracao/cena_01.wav … cena_10.wav`, recalcula a duração de cada cena pela voz, re-renderiza o vídeo, regera trilha/efeitos, mixa (voz por cima, trilha abaixando com a voz) e exporta **`fut87_FINAL.mp4`**. Já testado de ponta a ponta.
- `cenas.json`: o texto de cada cena (o que a voz deve falar, palavra por palavra).
- `escudos/`: escudos oficiais em PNG (FLA, SPT, INT, GUA). `fonts/`: Anton e Poppins.
- `fut87_trilha_efeitos.mp4`: versão atual, sem voz.

## Tarefa
1. Instalar dependências se faltar: `pip install pillow numpy scipy google-genai` e ter `ffmpeg` no PATH.
2. Gerar a narração com **Gemini TTS**, **um arquivo por cena**, a partir de `cenas.json`:
   - Antes de codar, ler a doc atual de "speech generation" da Gemini API (o modelo e o formato da chamada mudam com frequência; em nov/2026 a doc citava `gemini-3.8-flash-tts`).
   - Chave: usar a variável de ambiente `GEMINI_API_KEY`. Pedir ao usuário se não existir. **Nunca gravar a chave em arquivo.** A chave colada no chat anterior foi exposta e deve ser revogada; usar uma nova.
   - Voz: **Fenrir** (alternativa: Puck). Português do Brasil.
   - Instrução de estilo (igual em todas as cenas): "Narrador brasileiro de futebol, estilo mesa de bar, voz masculina animada e provocadora. Ritmo rápido, frases curtas, ênfase nas palavras em MAIÚSCULA. Pausa curta onde houver reticências. Tom de quem conta uma fofoca boa. Na última cena, tom de desafio."
   - Salvar como `narracao/cena_01.wav` … `narracao/cena_10.wav` (a API costuma devolver PCM 24 kHz mono, então envolver em WAV).
3. Rodar `python3 finalizar.py`, conferir alguns quadros e ouvir o começo e o fim.
4. Entregar `fut87_FINAL.mp4` + legenda do post:
   "Ganhou a final e não levou o título? 🏆 87 é do Flamengo ou do Sport? Comenta 👇 #futebol #futebolbrasileiro #polemica #flamengo #sport"

## Regras da página
- Vídeos feitos via código; escudos oficiais; nunca numerar como episódio.
- Cada vídeo centrado em um clube (aqui, o ponto de vista do Flamengo; o Sport é o rival).
- Formato da série (skill "futexplicando-polemicas"): título gigante em pergunta "?!", dois lados, narrador não dá veredito, CTA "comenta aí".
- Fatos conferidos em 23/11/2026: STF definiu o Sport como único campeão em 2017, reafirmado em 2024; em ago/2026 o TJ-RJ negou de novo o pedido do Flamengo (caso Taça das Bolinhas).
