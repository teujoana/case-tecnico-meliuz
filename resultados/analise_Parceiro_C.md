# Teste A/B de Cashback — Parceiro C

**Período analisado:** 2011-07-01 a 2011-08-14
**Pergunta:** qual variante de cashback devemos escalar pra 100% do tráfego?

## Decisão: escalar **Grupo 1**

Confiança: diferença estatisticamente significativa (p < 0,001) frente ao segundo colocado (Grupo 2).

## Métricas por grupo

| Grupo   |   Compradores |   Vendas totais (R$) |   Margem líquida (R$) |   % Cashback |   % Take-rate |   ROI Cashback |   Ticket médio (R$) |
|:--------|--------------:|---------------------:|----------------------:|-------------:|--------------:|---------------:|--------------------:|
| Grupo 1 |          4549 |         1,738,460.00 |             34,769.00 |         5.00 |          7.00 |          20.00 |              382.16 |
| Grupo 2 |          4522 |         1,685,235.00 |                  0.00 |         7.00 |          7.00 |          14.29 |              372.67 |

## Leitura

- Grupo 1 teve o melhor equilíbrio entre volume e lucro real: R$ 34,769.00 de margem líquida, com cashback de 5.0%.
- ROI de cashback do vencedor: 20.0x (cada real de cashback trouxe R$ 20.00 em vendas).
- Grupo 2 não dá lucro pro Méliuz: a comissão recebida (R$ 117,967.00) é igual ou menor que o cashback devolvido (R$ 117,967.00). Não deve ser escalado.
