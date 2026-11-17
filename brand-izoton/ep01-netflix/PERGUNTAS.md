# PERGUNTAS · EP01 Netflix (v3, Parada 1)

Dúvidas desta rodada. Segui com a opção indicada em cada uma.

1. **Velocidade da voz:** o `CLAUDE.md` (§7) limita a aceleração a 5%; o prompt v3 (Passo 2b.5) limita a 7%. Mantive 7%, como na v2, para a voz não mudar entre trechos antigos e novos. Confirma 7% ou reduzo para 5% (e corto texto)?
2. **Duração do cold open:** a meta era 0:00–0:25. Com a Gacrux, a primeira linha dura 8,2 s (o prompt previa 3 s), e o cold open fechou em 28,6 s. Para chegar a 25 s, sugiro encurtar a linha 1 para: "Em 2017, o CEO da Netflix disse que ela compete com o seu sono."
3. **Onde fica o guia:** o prompt pede `referencias/GUIA_DE_ESTILO.md`; o `CLAUDE.md` (§11) pede `brand-izoton/GUIA_DE_ESTILO.md`. Segui o `CLAUDE.md`.
4. **Box de DVD da HBO:** no TED, Hastings fala de boxes de séries da HBO. Não achei foto livre de um box da HBO; usei um box genérico (Commons, CC BY-SA), sem dizer que é da HBO. Se houver um print oficial, troco.
5. **Qual medida de "parado" vale para a meta de 5%:** o `freezedetect` padrão (n=0,002) dá 0% na v3, mas o grão animado sozinho já conta como movimento. Com o grão filtrado (imagem reduzida e desfocada), a v3 ainda tem trechos parados (detalhes no relatório). Proponho usar a medida sem grão como oficial.
6. **Cota do Gemini:** o plano gratuito dá 10 pedidos por dia por modelo, e um pedido por linha. O episódio inteiro pede cerca de 15 linhas novas (reganchos, fechamento e 8 hooks de Short), então leva 2 dias ou exige uma chave paga.

## Bancos de imagem (complemento do gerente, Passo 2c item 7)
Testei o acesso do ambiente em 17/11/2026:
- **Texturelabs** (texturelabs.org): abre normalmente.
- **Pixabay** (pixabay.com): o site responde 403 com desafio do Cloudflare. Não é bloqueio da rede do ambiente; o site barra acesso automatizado. A API oficial (pixabay.com/api) responde, mas pede uma chave gratuita de conta Pixabay. **Pergunta:** o Guilherme cria a chave e cadastra no ambiente (como segredo de rede para pixabay.com), ou eu sigo só com Commons + Texturelabs?
- Só referência, sem entrar no vídeo: flim.ai, 60fps.design e insposite.com respondem; curated.supply respondeu 429 (limite de acesso) no teste.
