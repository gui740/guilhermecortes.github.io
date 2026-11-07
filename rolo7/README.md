# ROLO 7: A CASA DA ESQUINA

Analog horror em formato de fita de treinamento do novo vigia noturno, gerado por código (vertical 1080x1920, 30 fps, ~78 s).
Inspirado na lenda urbana do "Casarão Assombrado" do bairro Bandeirantes, em Cuiabá-MT.

Estrutura: etiqueta da fita ("você é o novo vigia noturno"), câmera mirando o casarão com marcador de objetivo, 7 regras lidas pela locutora (cada tela dura o tempo da leitura),
cortes curtos de câmera de segurança da casa, fim no corredor e cartão de homenagem/ficção.

## Requisitos

```
pip install -r requirements.txt
apt-get install ffmpeg
```

## Uso

```
python render.py --preview            # 1 PNG por tela em saida/preview/
python render.py --preview --t 12 40  # PNGs de tempos específicos
python render.py                      # saida/rolo7_casa_da_esquina.mp4
```

As falas já estão em cache em `saida/voz/` (Gemini TTS, voz "Kore"), então o render funciona sem
chave. Se mudar algum texto em `config.py` (`FALAS`), a fala nova é gerada com
`GEMINI_API_KEY=... python render.py`. Nunca grave a chave em arquivo do repositório.
Sem chave, o fallback é o espeak-ng (robótico; apt-get install espeak-ng).

Ajustes em `config.py`: textos, `HANDLE`, `INCLUIR_CARTAO_HISTORIA`, `INSERTOS` (quais regras ganham
corte de câmera), intensidade dos efeitos (`FX_AVISO`, `FX_CFTV`, `FX_FINAL`), voz (`TTS_VOZ`).

## Arquivos

- `roteiro.py`: monta a linha do tempo a partir da duração real de cada fala
- `cenas/`: telas de aviso, CFTV e cartão; `cenas/desenhos.py`: casa e corredor procedurais
- `fx_vhs.py`: efeitos de fita; o texto entra numa camada com tratamento leve para continuar legível
- `voz.py`: Gemini TTS com cache e tratamento de locução de época
- `audio.py`: sons sintetizados (tom de alerta, festa distante, goteira, drone, impactos) e mixagem
- `render.py`: glitches sincronizados com o áudio, quadros em paralelo, pipe para o ffmpeg

`saida/rolo7_casa_da_esquina_leve.mp4` é a versão comprimida que cabe no GitHub. A versão em CRF 20
tem ~150 MB; gere com `python render.py`.
