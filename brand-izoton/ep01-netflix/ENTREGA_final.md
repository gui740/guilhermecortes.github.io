# ENTREGA final · EP01 Netflix

19 nov. 2026. Arquivos de vídeo em `video/out/v3a/` (fora do Git). Nada foi publicado no YouTube.

## 1. As 10 frases curtas (arquivo frases-curtas-ep01, 77,4 s)

### Como foi feito
- **Rótulos:** antes de cada frase ele diz um número ("um" a "dez"), não o nome do bloco. A frase 1 virou o bloco 09, a 2 o bloco 11 e as frases 3 a 10 viraram os hooks S01 a S08, na ordem da lista do gerente. Os números foram cortados.
- **Tratamento:** o mesmo das outras gravações (`limpar_gui.sh`: ruído, EQ, de-esser, compressão, gate, sala pequena).
  - corte com as mesmas folgas (−0,07 / +0,14 s);
  - pausas internas limitadas a 0,6 s, ou 0,75 s depois de pontuação;
  - sem acelerar.
- **Nível:** casado com os vizinhos. O bloco 09 ficou em −15,5 LUFS (média dos blocos 08 e 10: −15,4). O bloco 11 e os hooks ficaram em −15,9 (mediana dos blocos do episódio).
- **Ferramenta:** `pipeline/narracao_gui/trocar_lote.py`, nova, que faz a troca em lote.

### Transcrição palavra por palavra × roteiro (`roteiro-narracao-ep01-v3.md`)

| Frase | Trecho no arquivo | Bloco | Duração final | Transcrição (Whisper medium, arquivo inteiro) | Roteiro | Diferença |
|---|---|---|---|---|---|---|
| 1 | 5,54–9,48 s | **09** | 4,15 s | O retorno não estava em cada hora assistida, estava em outro lugar. | O retorno não estava em cada hora assistida. [PAUSA] Estava em outro lugar. | nenhuma (só pontuação) |
| 2 | 12,38–16,66 s | **11** | 4,49 s | Ter a série não bastava, ela precisava que você não parasse de assistir. | Ter a série não bastava. [PAUSA] Ela precisava que você não parasse de assistir. | nenhuma |
| 3 | 21,20–24,62 s | **S01** | 3,63 s | O CEO da Netflix disse que ela compete com o seu sono. | igual | nenhuma |
| 4 | 28,22–32,26 s | **S02** | 4,25 s | Esse botão é apertado 136 milhões de vezes por dia. | Esse botão é apertado cento e trinta e seis milhões de vezes por dia. | nenhuma (número por extenso) |
| 5 | 36,62–41,14 s | **S03** | 4,73 s | Você dá cinco estrelas para um filme e assiste outro, a Netflix percebeu. | Você dá cinco estrelas para um filme e assiste outro. [PAUSA] A Netflix percebeu. | nenhuma |
| 6 | 44,48–48,02 s | **S04** | 3,75 s | Todo chefe da Netflix precisa responder uma pergunta sobre você. | igual | a 1ª transcrição ouviu "Todo **o** chefe"; a do trecho cortado, "Todo chefe". Mesmo sentido |
| 7 | 50,76–53,94 s | **S05** | 3,39 s | Em muitos países, a Netflix nem escreve o próprio nome. | igual | nenhuma |
| 8 | 56,72–62,80 s | **S06** | 6,29 s | Em 2015, um candidato fez propaganda no intervalo de um debate **da** CNN. Ele não existe. | … de um debate **na** CNN. [PAUSA] Ele não existe. | "da" no lugar de "na" (as duas transcrições concordam). Não é erro de fato: o debate era da CNN (5º debate republicano, 15 dez. 2015) |
| 9 | 65,78–69,90 s | **S07** | 4,33 s | A Netflix proibiu dividir a senha. Muita gente disse que ia cancelar. | igual | nenhuma |
| 10 | 73,14–76,40 s | **S08** | 3,47 s | A Netflix abriu uma casa onde você entra nas séries. | igual | nenhuma |

- **Resultado:** nada faltando, nada trocado, nenhum erro de fato. Nenhuma frase ficou provisória.
- **Legendas corrigidas à mão:** na transcrição de cada trecho cortado (usada para a legenda palavra a palavra), o Whisper errou duas vezes. No S01 ouviu "O **senhor** da Netflix" e no S03, "**pra** um filme e assiste **o** outro". A legenda foi corrigida para "CEO" e "para … outro", que é o que a transcrição do arquivo inteiro (com os nomes no prompt) e o roteiro dizem.

## 2. Episódio 1080p final

**Master: `video/out/v3a/EP01_v3e_1080.mp4`** (1920x1080, 30 fps, 782,9 s, 23.478 quadros, vídeo a 16 Mb/s, áudio AAC 320 kb/s).

### 2.1 O que mudou desde a montagem aprovada (v3b4)
1. **Bloco 09** (1:58, 4,4 s) e **bloco 11** (narração sobre o painel do capítulo 3) com a voz dele. Antes, eram silêncio com o texto na tela.
   - o episódio passou de 781,6 s para 782,6 s;
   - os capítulos 2 a 10 andaram até 1 s.
2. **Fichas de palavra-chave:** só termos fortes, de uma lista revisada à mão. Não entram stopwords, pronomes nem verbos (lista em `ENTREGA_v3b.md`).
3. **Contadores:** o bloco ocupa de 50 a 70% da altura e fica dentro da faixa de 608 px. O número verdadeiro é datilografado, sem número intermediário falso. A cena diz "MAIS DE 100 MILHÕES", como a fonte.
4. **Legendas** (`legendas/EP01_v3_ptBR.srt`, 312 linhas) refeitas com os blocos 09 e 11.
5. **Capítulos novos** em `DESCRICAO_YOUTUBE.md`.

6. **Prints do guia de marca** (gui_01 Color e gui_02 Clearspace, brand.netflix.com) nas laterais das cenas do guia, de 7:25 a 7:43, em cor e sem distorção.
7. **Mais movimento** (necessário para passar na medida):
   - as ações do objeto principal ficaram mais densas e com pose maior;
   - entre uma ação e outra, o objeto continua a se aproximar em degraus;
   - nos documentos, um marca-texto contínuo desce pelas linhas e o cartão tem um vaivém lento;
   - a frase das citações se aproxima em rampas de 2 s.

### 2.2 Medidas (EP01_v3e_1080.mp4)

| Medida | Resultado | Meta |
|---|---|---|
| Tempo parado (quadro inteiro, sem grão) | **3,5%** (27,3 s de 782,9 s) | abaixo de 5% |
| Maior trecho parado | **1,8 s**; nenhum trecho de 2,2 s ou mais | até 2,5 s |
| Auditoria "parado na narrativa" (faixa central, > 2,5 s) | **0** | 0 |
| Quadros quebrados | **nenhum** (cada parte conferida antes de montar) | nenhum |
| Loudness | **−14,0 LUFS**, LRA 4,7 LU, pico −1,4 | −14 LUFS, −1 dBTP |
| Trocas fortes | 8,8 por minuto | — |

### 2.3 Histórico das versões 1080p de hoje

| Versão | O que é | Resultado |
|---|---|---|
| `EP01_v3b4_1080.mp4` | reserva, código da montagem aprovada | parado 4,8%; **1 quadro quebrado em 0:12,0**; não usar |
| `EP01_v3c_1080.mp4` | 1º render com blocos 09/11, fichas novas e contadores | **parado 6,2%** (as fichas mais fortes e os contadores sem contagem tiraram movimento); reprovado |
| `EP01_v3d_1080.mp4` | partes 1 e 3 re-renderizadas e emendadas na v3c | **defeituosa**: a emenda por cópia de fluxo deixou ~120 quadros a mais (dessincroniza som e imagem) e o parado ficou em 5,5%. **Não usar.** Tentei apagá-la para liberar disco e a regra de não apagar versões numeradas impediu; continua no disco |
| `EP01_v3e_1080.mp4` | render completo com o movimento reforçado | **aprovada** pelas medidas (2.2) |

Uma checagem de quadro quebrado acusou um quadro duas vezes, em partes diferentes: o início do clipe T02 (1:28) e o do T12b (4:55). Nas duas vezes a parte foi renderizada de novo e saiu limpa. Os dois pontos são o liga do efeito de TV.

## 3. Shorts (1080x1920)

| Short | Arquivo final | Duração | Parado | Maior trecho | Loudness | Pico |
|---|---|---|---|---|---|---|
| 01 · Sono | `shorts/SHORT01_v4.mp4` | 28,9 s | 0% | 0 s | −14,0 LUFS | −1,5 |
| 02 · Pular abertura | `shorts/SHORT02_v4b.mp4` | 39,3 s | 0% | 0 s | −13,9 LUFS | −2,1 |
| 03 · Algoritmo | `shorts/SHORT03_v4b.mp4` | 44,3 s | 0% | 0 s | −14,1 LUFS | −1,4 |
| 04 · Keeper test | `shorts/SHORT04_v4.mp4` | 47,0 s | 2% | 1,0 s | −14,0 LUFS | −1,5 |
| 05 · Uma letra | `shorts/SHORT05_v4.mp4` | 46,3 s | 0% | 0 s | −13,9 LUFS | −1,7 |
| 06 · #FU2016 | `shorts/SHORT06_v4.mp4` | 51,6 s | 0% | 0 s | −14,0 LUFS | −1,5 |
| 07 · Senhas | `shorts/SHORT07_v4.mp4` | 40,1 s | 0% | 0 s | −13,9 LUFS | −1,8 |
| 08 · Netflix House | `shorts/SHORT08_v4b.mp4` | 45,2 s | 2% | 1,0 s | −13,9 LUFS | −1,8 |

- Nenhum quadro quebrado. O teto do loudnorm é −1,5 dBTP; os picos da tabela são de amostra.
- Os SHORT02, 03 e 08 saíram de novo (v4b) porque o SHORT03 v4 ficou em 5,2% parado, com a tela do hook parada entre uma linha e outra. A tela do hook agora se aproxima em degraus.
- Conferência 9:16: quadros do hook (0,5, 2 e 4 s) e da passagem para o Short nos 8. Texto do hook, legenda e voz entram juntos, dentro da zona segura.

Cada Short abre com o seu hook na voz do Guilherme, com o texto do hook na tela e legenda palavra a palavra; o resto continua igual.

**Decisão sem consulta (SHORT01 e SHORT02):** os dois já abriam com quase a mesma frase do hook:
- **SHORT01:** bloco 01, "Em 2017, o CEO da Netflix disse que a empresa compete com o seu sono".
- **SHORT02:** bloco 15, "Esse botão é apertado 136 milhões de vezes num dia típico".
- **O que fiz:** nesses dois, o hook gravado substitui essa abertura, para a mesma frase não ser ouvida duas vezes seguidas. O Short começa depois dela e a legenda também tira a frase. Nos Shorts 03 a 08, o hook entra antes e nada sai.


## 4. Imagens do Guilherme (gui_01 a gui_10)

- **gui_01 e gui_02** (Color e Clearspace, brand.netflix.com): em uso no episódio, de 7:25 a 7:43. Registro em `IMAGENS.md` e `DIREITOS.md`: "página oficial, brand.netflix.com, print".
- **gui_03 a gui_10:** fora do vídeo. A origem ainda está em confirmação (Gemini ou internet). Os recortes em P&B estão prontos na área temporária, mas falta terminar dois ajustes:
  - na TV (gui_06), a marca "Philco" ainda aparece;
  - no esquadro (gui_04), parte do texto impresso continua visível.
- **gui_07 (controle):** recomendo deixar fora. Mesmo em P&B, a silhueta é a de um controle de console conhecido.

## 5. Documentos atualizados

- **`DESCRICAO_YOUTUBE.md`:** capítulos novos
  00:00, 00:15, 01:02, 02:38, 04:15, 05:14, 07:15, 08:21, 09:32, 10:30 e 12:00.
- **`DESCRICAO_SHORTS.md`:** cada Short abre com o hook falado.
- **`DIREITOS.md`:**
  - voz do Guilherme em todos os blocos, inclusive 09 e 11, e nos hooks;
  - prints do guia de marca;
  - objetos gui_03 a gui_10 marcados como pendentes.
- **`legendas/EP01_v3_ptBR.srt`:** 312 linhas, com os blocos 09 e 11.
- **`IMAGENS.md`:** as 10 imagens do Guilherme.

## 6. Artifact

Episódio em 4 partes leves, 8 Shorts, capa, prints por capítulo e medidas (privado): https://claude.ai/artifact/6XiiHvN362rDVKE5n9yVhe

## 7. Decisões tomadas sem consulta

- **SHORT01 e SHORT02:** o hook gravado substitui a frase de abertura repetida (ver seção 3 do pedido; detalhes acima).
- **Bitrate do master:** 16 Mb/s, para caber no disco. É o dobro da recomendação do YouTube para 1080p30.
- **Arquivos intermediários apagados para liberar disco** (nenhuma versão numerada foi apagada):
  - partes 1080p, depois de conferir cada master;
  - cópias pré-loudnorm dos Shorts (`_raw`);
  - trechos de teste;
  - caches (modelo do Whisper, pip, uv);
  - o download bruto do Blitzscaling (os clipes já estão cortados no projeto).
- **Legenda corrigida à mão** em duas palavras que o Whisper errou ("CEO" e "para … outro").

## 8. Pendente

- Confirmação da origem de gui_03 a gui_10 (e decisão sobre o controle).
- Nada no YouTube: a publicação fica com o Guilherme.
