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

*(em render; medidas na seção 2.2)*

### 2.1 O que mudou desde a montagem aprovada (v3b4)
1. **Bloco 09** (1:58, 4,4 s) e **bloco 11** (narração sobre o painel do capítulo 3) com a voz dele. Antes, eram silêncio com o texto na tela.
   - o episódio passou de 781,6 s para 782,6 s;
   - os capítulos 2 a 10 andaram até 1 s.
2. **Fichas de palavra-chave:** só termos fortes, de uma lista revisada à mão. Não entram stopwords, pronomes nem verbos (lista em `ENTREGA_v3b.md`).
3. **Contadores:** o bloco ocupa de 50 a 70% da altura e fica dentro da faixa de 608 px. O número verdadeiro é datilografado, sem número intermediário falso. A cena diz "MAIS DE 100 MILHÕES", como a fonte.
4. **Legendas** (`legendas/EP01_v3_ptBR.srt`, 312 linhas) refeitas com os blocos 09 e 11.
5. **Capítulos novos** em `DESCRICAO_YOUTUBE.md`.

### 2.2 Medidas
*(preenchidas quando o render terminar)*

## 3. Shorts
*(em render, depois do episódio)*

Cada Short abre com o seu hook na voz do Guilherme, com o texto do hook na tela e legenda palavra a palavra; o resto continua igual.

**Decisão sem consulta (SHORT01 e SHORT02):** os dois já abriam com quase a mesma frase do hook:
- **SHORT01:** bloco 01, "Em 2017, o CEO da Netflix disse que a empresa compete com o seu sono".
- **SHORT02:** bloco 15, "Esse botão é apertado 136 milhões de vezes num dia típico".
- **O que fiz:** nesses dois, o hook gravado substitui essa abertura, para a mesma frase não ser ouvida duas vezes seguidas. O Short começa depois dela e a legenda também tira a frase. Nos Shorts 03 a 08, o hook entra antes e nada sai.
