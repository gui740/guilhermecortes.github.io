# Narração do Guilherme: pipeline

Os scripts rodam de dentro de uma pasta de trabalho, fora do Git, que contém:
- `bruto/`: as gravações e o roteiro;
- `wav16/`: as gravações em 16 kHz mono;
- `trans/`: as transcrições.

1. `transcrever_gui.py medium`: Whisper medium com tempo por palavra → `trans/*.medium.json`.
2. `alinhar_gui.py`: lê os blocos do roteiro e acha a última leitura de cada um (busca de trás para frente) → `alinhamento.json`.
3. `bordas_gui.py`: ajusta as bordas, tira sobreposições e lista as diferenças contra o roteiro → `alinhamento_final.json`. Algumas correções manuais (blocos 10, 22 e 54) estão descritas no `COBERTURA_NARRACAO.md`.
4. `limpar_gui.sh entrada saida`, aplicado a cada gravação:
   - high-pass e redução de ruído;
   - EQ;
   - de-esser e compressão;
   - gate suave;
   - sala pequena (`sala_pequena.wav`, sintética);
   - -16 LUFS.
5. `cortar_gui.py <pasta de saída>`: corta a última leitura de cada bloco e aperta as pausas longas, sem acelerar → `bNN.wav`. Depois, o Whisper roda em cada bloco → `video/src/v3/palavras_gui.json`.
6. `glitch.py video.mp4`: acha quadros isolados que destoam dos vizinhos (defeito de render).
