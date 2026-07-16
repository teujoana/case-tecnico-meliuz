# Teste A/B de Cashback — Parceiro A

**Período analisado:** 2011-01-01 a 2011-04-02
**Pergunta:** qual variante de cashback devemos escalar pra 100% do tráfego?

## Decisão: escalar **Grupo 1**

Confiança: diferença **não** é estatisticamente significativa (p = 0.1315) — vale considerar estender o teste antes de escalar com confiança total frente ao segundo colocado (Grupo 2).
Atenção: a vantagem do Grupo 1 sobre os demais diminuiu na 2ª metade do teste (queda geral observada também no Grupo 2), mas ele segue líder mesmo nesse recorte mais recente. Recomendação de escalar com acompanhamento semanal se mantém.

## Métricas por grupo

| Grupo   |   Compradores |   Vendas totais (R$) |   Margem líquida (R$) |   % Cashback |   % Take-rate |   ROI Cashback |   Ticket médio (R$) |
|:--------|--------------:|---------------------:|----------------------:|-------------:|--------------:|---------------:|--------------------:|
| Grupo 1 |          9633 |         5,605,173.00 |            404,711.00 |         4.16 |         11.38 |          24.01 |              581.87 |
| Grupo 2 |         10814 |         6,423,096.00 |            357,519.00 |         5.77 |         11.34 |          17.33 |              593.96 |
| Grupo 3 |         11410 |         6,785,856.00 |            264,287.00 |         7.42 |         11.32 |          13.47 |              594.73 |

## Leitura

- O Grupo 3 vendeu mais (R$ 6,785,856.00), mas o cashback mais alto (7.42%) comeu boa parte da margem.
- Grupo 1 teve o melhor equilíbrio entre volume e lucro real: R$ 404,711.00 de margem líquida, com cashback de 4.16%.
- ROI de cashback do vencedor: 24.01x (cada real de cashback trouxe R$ 24.01 em vendas).
