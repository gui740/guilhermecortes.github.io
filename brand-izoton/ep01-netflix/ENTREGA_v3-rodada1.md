# ENTREGA v3 · rodada 1 do FIXES · EP01 Netflix

Só os dois trechos do `FIXES.md` foram mexidos. A fala do TED com camadas, a transição 2 → 3 e o começo do SHORT 02 ficaram iguais. A amostra anterior continua intacta: os arquivos novos têm nomes novos.

**Artifact privado:** https://claude.ai/artifact/4WpF1JMsEE92opFs1GbgpK. Tem os 2 clipes em 540p a -14 LUFS, 6 prints de cada um com o tempo e o relatório de motion.

## O que foi feito
**Cold open v2** (`V3ColdOpen-v2`, em `video/src/v3/Rodada1.tsx`): 13,7 s no total, com 1,8 s de carimbo.
- A narração começa no quadro 0. A frase-chave ("COMPETE COM O SEU SONO.") está inteira na tela aos 0,17 s.
- Frase curta tirada do áudio existente da linha 1, cortando "a analistas de Wall Street" e encurtando duas pausas (`l01c_107.wav`). Nenhum áudio novo foi gerado.
- A emenda ficou limpa:
  - o Whisper relê a frase inteira sem erro;
  - o tom não salta (cerca de 212 Hz antes da emenda e 206 Hz depois);
  - não há respiração no meio.
  - Por isso, sem marca [ÁUDIO PROVISÓRIO] por corte. A voz inteira continua provisória até a decisão da clonagem.
- Ficha da entrevista, TED no CRT (mudo), lista acendendo e HBO riscada entram como camadas sobre a narração.
- Na promessa, o painel abre em círculo e os 10 cartões acendem um a um, cada um invertido por um instante. Por cima, entram "AS JOGADAS" e "PELO SEU TEMPO".
- O `Painel` ganhou as opções `acende` e `pan`, desligadas por padrão. A transição 2 → 3 não muda.

**Colagem v2** (`V3Colagem-v2`, prop `v2`):
- O disco atravessa 300 px girando, em degraus de stop-motion (uma pose a cada 3 quadros), com uma marca fora do centro para a rotação aparecer.
- A ficha datilografada "FORMATO: DVD · 1997" entra na palavra "formato" (1,18 s).
- O carimbo continua em "prazo" (1,82 s).

## Relatório de motion
Medida que vale: sem grão (vídeo a 160 px com desfoque, freezedetect n=0,004, d=1 s).

| Trecho | Duração | Parado: antes | Parado: depois | Maior trecho parado: antes → depois | Medida padrão |
|---|---|---|---|---|---|
| Cold open | 28,6 → 13,7 s | 47% | **0%** | 3,0 s → 0 s | 0% → 0% |
| Colagem 01:09 | 13,9 s | 32% | **14%** | 2,6 s (início) → 1,9 s | 0% → 0% |

Eventos no cold open: cerca de 30 em 13,7 s (cerca de 130/min). Laterais ocupadas de 0,1 s até o fim.

- **Ainda acima da meta de 5%:** a colagem tem 1,9 s parados entre 5,4 e 7,3 s, logo depois de "sucesso.", antes do recorte do Hastings.
- Esse trecho passa na regra dos 2,5 s, mas não está no FIXES, então não mexi.
- **Sugestão para a próxima rodada:** o título "Desconfiar do próprio sucesso." sai com empurrão em "Hastings" (7,2 s), e um sublinhado em degraus entra em "sucesso" (5,78 s).

## Desvios e decisões tomadas sem consulta
1. **Frase-chave no áudio aos 4,2 s ("compete") e 5,5 s ("sono"), não até 2 s.** Com a frase curta e sem áudio novo, não há como chegar a 2 s no áudio. Na tela, ela entra no quadro 0.
2. **Promessa cortada do áudio existente**, para caber em 12–15 s. Ficou "Neste episódio, as jogadas que a Netflix montou para ganhar essa briga pelo seu tempo." (`l02c_107.wav`).
   - Saiu "Repara, a HBO não está na lista.": a HBO riscada continua na tela.
   - Saiu "e a conta que ela mandou para você no fim.": o recibo "A CONTA" saiu junto.
3. **TED no CRT mudo**, porque fica sob a narração.
4. **Carimbo "17 ABR. 2017"** e etiqueta "CEO · REED HASTINGS" acrescentados no primeiro segundo. Sem eles, 0,3–1,3 s ficava parado.

## Arquivos
- Código: `video/src/v3/Rodada1.tsx`, `video/src/v3/Amostra.tsx` (helpers exportados e opção v2 da colagem), `video/src/v3/transicoes.tsx` (`acende`, `pan`, cartão invertido) e `video/src/Root.tsx`.
- Áudio cortado (fora do Git): `video/public/media/v3audio/l01c_107.wav` e `l02c_107.wav`.
- Masters 1080p (fora do Git): `video/out/v3a/V3ColdOpen_v2.mp4` e `V3Colagem_v2.mp4`.

**Parei aqui.** Nada da Parada 2.
