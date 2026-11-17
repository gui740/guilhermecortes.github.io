# FIXES · EP01 Netflix · v3 · rodada 1 · sobre V3ColdOpen e V3Colagem

> Recebido do gerente (projeto BRANDSPOTEN) por mensagem entre sessões em 17/11/2026. Texto salvo como chegou.

Notas do Guilherme (17/11, 23:25): ele achou o cold open muito bonito, mas ainda muito lento. O gancho demora para começar. Por enquanto, não há outras notas sobre o resto da amostra.

1. **Cold open, início.** A fala do executivo começa no quadro 0. A frase-chave ("compete com o seu sono") aparece na tela e no áudio até 2 s. Nada antes dela: sem respiro, sem ficha caindo antes e sem carimbo.
2. **Cold open, frase.** Use a versão curta: "Em 2017, o CEO da Netflix disse que a empresa compete com o seu sono."
   - NÃO gere áudio novo, porque a voz do episódio ainda vai ser decidida.
   - Corte "a analistas de Wall Street" do áudio já existente da linha 1, usando os tempos do Whisper.
   - Se a emenda soar cortada (salto de tom ou respiração no meio), mantenha a linha longa, marque [ÁUDIO PROVISÓRIO] e siga.
3. **Cold open, duração.** Passe de 28,6 s para 12 a 15 s no total, contando o carimbo do canal (no máximo 2 s).
   - Corte o que repete a ideia.
   - A ficha da entrevista, o TED no CRT e o painel entram como camadas sobre a narração, não um depois do outro.
   - Ficam: a frase, o recorte do Hastings, a HBO riscada e um vislumbre do painel.
4. **Cold open, trechos parados.** Os trechos de 3,0 s (19,9 a 22,9 s) e de 2,2 s (24,3 s) somem com o corte. Na versão nova, nenhum trecho parado pode passar de 2,5 s.
5. **Colagem 01:09, começo.** Os 2,6 s parados no começo (envelope já pousado, antes do carimbo) ganham movimento: o carimbo bate mais cedo ou o disco continua girando.

**Medida que vale** para "parado": a sem grão (160 px, desfoque, n=0,004). Meta: menos de 5% do tempo parado e nenhum trecho acima de 2,5 s. Respondendo ao PERGUNTAS.md: a voz fica acelerada 7%, como na v2.

**Voz.** Não gere nenhuma narração no Gemini nesta rodada. O Guilherme está vendo a clonagem da própria voz. As linhas novas ficam com o áudio atual, marcadas [ÁUDIO PROVISÓRIO] quando for o caso. Isso vale para o regancho do capítulo 3, o hook do SHORT 02 e a promessa do cold open.

**Fica exatamente como está** tudo o que não está nesta lista: a fala do TED com camadas, a transição 2 → 3 e o começo do SHORT 02.

**Entrega desta rodada:**
- Só V3ColdOpen_v2 e V3Colagem_v2, em 540p.
- Prints com o tempo de cada um e relatório de motion (antes e depois).
- Publique no mesmo artifact da amostra ou em um novo, e pare. Nada da Parada 2 ainda.

## Acréscimo do gerente (17/11): item 6, vale para todas as cenas

6. **Som das transições.** O Guilherme achou MUITO alto e bruto em relação à narração e à música.
   - Baixe todos os efeitos de transição em 8 a 10 dB. O pico deles fica pelo menos 6 dB abaixo do pico da voz.
   - Suavize o ataque com fade-in de 20 a 40 ms e tire o agudo áspero com low-pass por volta de 8 kHz.
   - Use ducking quando houver fala por cima.
   - Os efeitos ficam por baixo da narração, controlados e sem susto.
   - No relatório, informe o pico dos efeitos contra o pico da voz, antes e depois.

Entrega da rodada: V3ColdOpen_v2, V3Colagem_v2 e V3TransicaoCap_v2 (só com o som corrigido), com prints e relatório. Depois pare.

## Decisão do Guilherme (17/11): ele narra o EP01
- A voz Gacrux sai do episódio inteiro. Nenhuma linha nova no Gemini.
- O áudio dele vai chegar em m4a, um arquivo por capítulo. Em cada arquivo: número do bloco, 1 s de pausa, o texto e 2 s de silêncio. Vale a última leitura de cada bloco.
- Quando chegar:
  1. limpeza leve (redução de ruído, high-pass em 80 Hz, de-esser, compressão suave, voz a -14 LUFS no mix);
  2. corte por bloco com o Whisper;
  3. novo palavras.json e edição ressincronizada no tempo dele;
  4. sem aceleração;
  5. se passar de 15 min, corta respiro e arquivo, nunca a voz.
- Até lá, o FIXES da rodada 1 é aplicado sobre o áudio atual, marcado [ÁUDIO PROVISÓRIO].
- O mapa dos blocos e o texto novo chegam com o áudio, pelo projeto.
