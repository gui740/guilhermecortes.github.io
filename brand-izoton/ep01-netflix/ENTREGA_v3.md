# ENTREGA v3 · Parada 3 · EP01 Netflix

18 nov. 2026. Arquivos de vídeo em `video/out/v3a/` (fora do Git). Nada foi publicado no YouTube.

## 1. Episódio 1080p

| Arquivo | Situação |
|---|---|
| `EP01_v3b4_1080.mp4` (1920x1080, 30 fps, 781,9 s, 20 Mb/s) | **reserva**, renderizada com o código da montagem v3b4 aprovada |

Medidas da reserva:
- parado 4,8% (37,5 s), maior trecho 1,8 s, nenhum trecho de 2,2 s ou mais;
- −14,0 LUFS, pico −1,0 dBTP, LRA 4,9 LU.

**Defeito:** um quadro quebrado em 0:12,0 (quadro 360: branco com um pedaço do painel). Não existe na 540p; foi falha de captura do navegador no render 1080p. Não corrigi a reserva porque o próximo 1080p vem hoje à noite, e um arquivo corrigido ocuparia mais 2 GB de disco.

**Próximo 1080p:** junta a troca do bloco 09 com os ajustes do gerente (fichas e escala dos contadores, ver `ENTREGA_v3b.md`). Cada parte passa pela checagem de quadro quebrado antes de ser juntada.
- Se o áudio não chegar hoje, renderizo só com os ajustes.
- O bloco 09 fica em 1:58, então os capítulos da `DESCRICAO_YOUTUBE.md` precisam ser recalculados depois da troca.

## 2. Shorts (1080x1920)

| Short | Arquivo final | Duração | Parado | Maior trecho | Loudness | Pico |
|---|---|---|---|---|---|---|
| 01 · Sono | `shorts/SHORT01_v3f.mp4` | 29,9 s | 0% | 0 s | −14,0 LUFS | −1,5 |
| 02 · Pular abertura | `shorts/SHORT02_v3f.mp4` | 40,3 s | 0% | 0 s | −13,9 LUFS | −2,2 |
| 03 · Algoritmo | `shorts/SHORT03_v3f.mp4` | 39,3 s | 0% | 0 s | −14,1 LUFS | −1,4 |
| 04 · Keeper test | `shorts/SHORT04_v3f.mp4` | 42,9 s | 0% | 0 s | −14,0 LUFS | −1,5 |
| 05 · Uma letra | `shorts/SHORT05_v3f.mp4` | 42,6 s | 0% | 0 s | −13,9 LUFS | −1,7 |
| 06 · #FU2016 | `shorts/SHORT06_v3g.mp4` | 45,0 s | 0% | 0 s | −14,0 LUFS | −1,5 |
| 07 · Senhas | `shorts/SHORT07_v3f.mp4` | 35,5 s | 0% | 0 s | −13,9 LUFS | −1,8 |
| 08 · Netflix House | `shorts/SHORT08_v3f.mp4` | 41,4 s | 2% | 1,0 s | −13,9 LUFS | −2,0 |

Nenhum quadro quebrado em nenhum Short. Os picos estão em dBFS de amostra, com o teto do loudnorm em −1,5 dBTP.

O que mudou até chegar aqui:

| Versão | Problema | Correção |
|---|---|---|
| v3b | 5 de 8 Shorts passavam de 5% parado (até 16%) | — |
| v3c, v3d, v3e | hook em texto parado no começo; quadro final parado; câmera lisa e lenta demais; prints claros | hook e loop se aproximam em degraus; câmera em degraus de 3 quadros com vaivém lateral; vídeo de arquivo se aproxima; marca-texto de leitura nos prints |
| v3c em diante | os contadores contavam de 0 até o valor, mostrando números falsos no caminho (0 → 136.000.000; 15%; 195) | o número verdadeiro é datilografado; as casas que faltam aparecem como traço |
| v3f | palavra "fantasma" na legenda: um "O" ficava na tela até o fim do SHORT06 (duas palavras com o mesmo tempo de início geravam chave repetida no React); a última linha do hook quebrava e saía da zona segura nos Shorts 03–08 | chave única por palavra; tamanho de cada linha calculado para caber em ~900 px |
| v3g (SHORT06) | "PROPRIA" sem acento na legenda (transcrição) | corrigido em `palavras_gui.json` e na SRT do episódio |

Conferência 9:16 quadro a quadro feita nos 8 Shorts (folhas de contato com 8 quadros cada, mais os quadros do hook, do loop e das legendas). Rosto, texto e legenda ficam dentro da zona segura.

**Hooks falados S01–S08:** ainda não gravados. Hoje o hook entra em texto na tela. Quando o áudio chegar:
1. `pipeline/narracao_gui/trocar_audio.py <gravação> S0N`;
2. renderizar só aquele Short de novo (`BITRATE=16M node render.mjs shortsfinal <versão> SHORT0N-v3`).

## 3. Capa

- `video/out/v3a/capa_v3_03.png` (1280x720): recorte de Reed Hastings em P&B com borda e sombra, N limpo na cor original, envelope de DVD em cor e a manchete "ELA COMPETE COM O SEU SONO.".
- A data "ENTREVISTA DE RESULTADOS · 17 ABR. 2017" fica junto da frase. Na v01 ela estava carimbada sobre a foto, que é de 2015 (re:publica), e isso sugeria uma data errada para a imagem.
- Créditos da foto e do envelope em `DIREITOS.md` e `IMAGENS.md`.

## 4. Documentos

- `DESCRICAO_YOUTUBE.md`: capítulos pela timeline v3; fontes em ABNT.
- `DESCRICAO_SHORTS.md`: um texto por Short, com fonte; nota sobre os hooks falados.
- `DIREITOS.md`:
  - narração só com a voz do Guilherme (a TTS saiu);
  - blocos 09 e 11 e hooks S01–S08 ainda por gravar;
  - nenhuma imagem de IA no episódio até agora;
  - geração paga não usada.
- `legendas/EP01_v3_ptBR.srt`: corrigida ("própria").

## 5. Pendente

1. Áudios do Guilherme (blocos 09 e 11, hooks S01–S08). Com eles:
   - `trocar_audio.py`;
   - `montar_timeline_v3.py`;
   - 1080p novo;
   - Shorts com hook falado.
2. `trocar_audio.py` ainda não foi testado com uma gravação real.
3. Imagens do Gemini: nenhuma chegou. Quando chegarem, entram em `IMAGENS.md` e `DIREITOS.md` com a marca "gerada por IA (Gemini), conceito, não é registro".

## 6. Decisões tomadas sem consulta

- **1080p a 20 Mb/s** (Shorts a 16 Mb/s), em vez de qualidade constante. Com o grão de filme, cada parte de 200 s chegava a 3,2 GB e não cabia no disco. 20 Mb/s está acima da recomendação do YouTube para 1080p30.
- **Arquivos intermediários apagados para liberar disco:**
  - as partes 540p (cada conjunto já estava num `EP01_v3b*_540.mp4` numerado);
  - as partes 1080p, depois de conferir a duração do arquivo montado;
  - mixagens antigas e vídeos de medida na área temporária.
  - Nenhuma versão numerada foi apagada.
- **Ceiling de −1,5 dBTP nos Shorts**, porque o SHORT03 v3b ficou com pico de amostra em −0,9.

## 7. Artifact

Shorts, capa e situação do 1080p (privado): https://claude.ai/artifact/DZfyBjmNnpFiEpeLCVCYKN
