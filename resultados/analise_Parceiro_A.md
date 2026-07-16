# Teste A/B de Cashback — Parceiro A

**Período analisado:** 2011-01-01 a 2011-04-02
**Pergunta:** qual variante de cashback devemos escalar pra 100% do tráfego?

## Decisão: escalar **Grupo 1**

Confiança: diferença **não** é estatisticamente significativa (p = 0.1315) — vale considerar estender o teste antes de escalar com confiança total frente ao segundo colocado (Grupo 2).
Atenção: a margem do grupo vencedor caiu bastante entre a 1ª metade do teste (R$ 5.582,50/dia) e a 2ª metade (R$ 3.215,57/dia). Pode ser efeito de novidade — vale acompanhar mais um ciclo antes de escalar de vez.

## Justificativa da decisão

Apesar da falta de significância estatística e da queda na margem entre a 1ª e 2ª metade do teste, o **Grupo 1** ainda é a melhor opção disponível pelos seguintes motivos:

- **Maior margem líquida acumulada:** R$ 404.711,00 — o Grupo 2 tem margem 12% menor (R$ 357.519) e o Grupo 3 tem margem 35% menor (R$ 264.287).
- **Melhor ROI de cashback:** 24,01x — cada R$ 1,00 investido em cashback trouxe R$ 24,01 em vendas.
- **Taxa de cashback mais baixa:** 4,16% — enquanto os grupos 2 e 3 ofereceram 5,77% e 7,42%, respectivamente.

**O custo de oportunidade de manter o teste rodando por mais tempo é maior que o risco de escalar agora.** Recomendamos monitoramento semanal pós-escala para validar a performance em produção.

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