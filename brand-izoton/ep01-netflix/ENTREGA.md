# ENTREGA · EP01 Netflix (Etapa 3)

## Onde estão os arquivos

A mídia **não vai para o Git** (o repositório é público). Ela fica na pasta do episódio desta sessão: `brand-izoton/ep01-netflix/video/out/`.

| Arquivo | O que é |
|---|---|
| `EP01_Netflix_16x9.mp4` | **Master v2, voz Gacrux.** 1920x1080, 30 fps, H.264 + AAC 320k, 14 min 52 s, -14,0 LUFS |
| `EP01_Netflix_previa_720p.mp4` | Prévia leve para ver no celular (56 MB) |
| `shorts/SHORT01.mp4` … `SHORT08.mp4` | 8 Shorts 1080x1920, de 38 s a 80 s, cerca de -14 LUFS, com título-gancho nos 2,5 s iniciais |
| `shorts/checagem_SHORTxx.jpg` | Checagem do enquadramento 9:16 (um quadro a cada 1,5 s) |
| `capa.png` | Capa 1280x720 |
| `folha_de_contato.jpg` | Folha de contato do episódio (um quadro a cada 15 s, com o tempo exato) |
| `mix_v2.wav` | Mix final em WAV 48 kHz, para remixar |
| `v1_voz_provisoria/` | Versão anterior, com a voz provisória (Edge TTS): episódio, Shorts, checagens e mix |

## Shorts

| Short | Tema | Duração |
|---|---|---|
| 01 | A Netflix diz que compete com o seu sono | 1:03 |
| 02 | O botão mais apertado da Netflix (Pular abertura) | 0:45 |
| 03 | Você dá 5 estrelas para Schindler e assiste Adam Sandler | 0:40 |
| 04 | O keeper test | 1:20 |
| 05 | Por que a Netflix lidera com uma letra | 0:55 |
| 06 | #FU2016: a campanha que entrou num debate presidencial | 1:00 |
| 07 | O fim da senha compartilhada foi um acerto? | 0:38 |
| 08 | A Netflix saiu da tela (Netflix House) | 1:01 |

As descrições dos Shorts estão em `DESCRICAO_SHORTS.md`.

## Textos
- `DESCRICAO_YOUTUBE.md`: descrição com capítulos (tempos da v2) e referências em ABNT.
- `DIREITOS.md`: lista de materiais e status de direitos de uso.
- `DECISOES.md`: todas as escolhas feitas sem consulta, para revisão.

## Pendências e pontos de atenção
1. **Uso do TED:** a licença do TED não autoriza uso em canal monetizado nem recortes. Você decidiu usar mesmo assim, e o risco de reivindicação de direitos está registrado em `DIREITOS.md`.
2. **Executivo do vídeo do Netflix House sem nome:** o vídeo não diz quem é. Se você souber, troco o lower third.
3. **Contador "142 MI" (bloco 8):** quebra em duas linhas na v2. É ajuste estético para a próxima rodada.
4. **Chave do AI Studio:** gere uma nova; a atual ficou em texto no chat.

## Como refazer
O passo a passo está nos scripts de `pipeline/` (narração, clipes, trilha, linha do tempo, mix, finalização) e `video/` (Remotion: `node render.mjs episodio | shorts | capa`). As mídias-fonte (vídeos do Drive) ficam fora do repositório.
