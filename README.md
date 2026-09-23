# CSAT Pós Med — Coordenação (AMBIENTE DE TESTE)

🧪 **Este NÃO é o dashboard real.** É uma cópia à parte, no seu próprio repositório e link, pra
testar mudanças sem risco de quebrar o site que a coordenação usa. O site publicado mostra uma
faixa vermelha fixa no topo avisando "AMBIENTE DE TESTE" -- nunca dá pra confundir com o real,
mesmo se o link for salvo/compartilhado por engano.

- **Site de teste:** https://pg-med-mandic.github.io/coord_mandic-teste/
- **Site real:** https://pg-med-mandic.github.io/coord_mandic/ (repositório `coord_mandic_pgmed/`
  neste mesmo workspace)

Mesma senha do site real, mesma proteção (`pagina.enc` cifrado, ver `pipeline/protecao.py`).

## Como usar

1. Salve o HTML que você quer testar em `fonte/index_aberto.html`.
2. Dois cliques em **`Atualizar Dashboard.bat`** (ou `python pipeline/publicar.py` na mão).
3. Abra o link de teste acima e confira se ficou do jeito esperado.
4. **Só quando estiver aprovado**, copie o mesmo `fonte/index_aberto.html` pra
   `../coord_mandic_pgmed/fonte/index_aberto.html` e rode o `Atualizar Dashboard.bat` de lá --
   esse sim vai pro site real.

Repita quantas vezes precisar no teste antes de publicar no real; os dois repositórios são
totalmente independentes (remotos diferentes no GitHub), então nada aqui afeta o site real até
o passo 4 ser feito de propósito.
