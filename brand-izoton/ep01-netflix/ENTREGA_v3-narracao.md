# ENTREGA v3 · narração do Guilherme + rodada 1

**Artifact privado:** https://claude.ai/artifact/9JtkHHrzRCPfwp4CiPpmnF. Tem a cobertura, o antes e depois da limpeza, os 3 clipes em 540p a -14 LUFS, os prints e os relatórios.

## O que foi feito
1. **Transcrição e alinhamento:** 13 gravações (cerca de 12 min) transcritas com Whisper medium e alinhadas bloco a bloco, ficando sempre com a última leitura. Detalhes em `COBERTURA_NARRACAO.md`.
   - **Gravados:** 53 de 55 blocos.
   - **Faltam:** os blocos 09 e 11 e os hooks S01–S08.
   - **Nenhum fato mudou.** Não há bloco para regravar por fato.
   - **Conferir de ouvido:** blocos 22, 28 e 30.
   - **Fora do roteiro:** gravacao-02 e gravacao-03 (texto de apresentação do canal) e gravacao-04 (leitura antiga do bloco 01). Não usei nenhuma delas.
2. **Limpeza e tratamento:**
   - high-pass em 80 Hz e redução de ruído;
   - EQ: corpo em 140 Hz, menos abafado em 350 Hz, presença em 4,2 kHz;
   - de-esser e compressão 2,5:1;
   - gate suave nas pausas;
   - sala pequena bem leve;
   - -16 LUFS por arquivo.
   - **Resultado:** a distância entre voz e ruído passou de 29–33 dB para 36–44 dB.
   - O efeito de rádio ou CRT fica para as falas de documento, na montagem completa.
3. **Cortes:** última leitura de cada bloco, com pausas longas apertadas (saiu 1,3 s no total). **Sem acelerar.** Tempos por palavra novos em `video/src/v3/palavras_gui.json`.
4. **Ressincronização:**
   - **Cold open:** tempos dos blocos 01 e 02.
   - **Colagem:** mapa de tempo `WarpCtx` (`kit.tsx`), que leva cada palavra da voz antiga para a palavra correspondente na voz dele.
   - **Transição:** bloco 12; o regancho (bloco 11) ficou só na tela.

## Relatório
| Clipe | Duração | Parado (sem grão) | Maior trecho parado | Efeitos abaixo do pico da voz |
|---|---|---|---|---|
| Cold open (blocos 01+02) | 15,0 s | 0% | 0 s | 21,8 dB sob a fala; 17,3 dB no pior efeito fora dela |
| Colagem 01:09 (bloco 04) | 11,9 s | 0% | 0 s | 22,2 dB; 17,8 dB |
| Transição 2 → 3 (bloco 12) | 10,5 s | 12% (imagem igual) | 1,3 s | 21,8 dB; 17,3 dB |

## Decisões tomadas sem consulta
1. **Cold open com o bloco 02 inteiro**, incluindo "Repara: a HBO não está na lista" e "e a conta…".
   - Para caber em 15 s, as pausas foram limitadas a 0,42 s e o carimbo do canal (1,5 s) entra sobre "pra você no fim".
   - O recibo "A CONTA" voltou, em "conta", e sai quando o carimbo entra.
2. **Transição sem o regancho falado** até o bloco 11 ser gravado. O texto continua na tela.
3. **Correção de render:** as texturas de grão agora são pré-carregadas (`Grao` em `kit.tsx`). Antes, um quadro às vezes saía claro. Todos os clipes foram checados quadro a quadro com `glitch.py`.

**Parei aqui.** Nada da Parada 2.
