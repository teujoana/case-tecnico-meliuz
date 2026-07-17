# Case Técnico Méliuz - Operações Integradas

Oi pessoal! Este é o meu projeto para a resolução do case técnico de estágio. Desenvolvi uma solução automatizada e flexível em Python para analisar de forma rápida, consistente e padronizada os testes A/B de cashback do time.

## O que desenvolvi:

1. **Script de Automação (`analyze_test.py`):** realiza o ETL dos dados, limpando strings financeiras automaticamente e agregando os resultados dos testes. Ele calcula de forma transparente a Margem Líquida, o Take-rate, o ROI de Cashback e o Ticket Médio de cada variante.
2. **Relatórios de Insights:** o script exporta automaticamente relatórios textuais personalizados com métricas e insights detalhados para cada parceiro na pasta `resultados/`.
3. **Consolidado para Gestão:** um arquivo consolidado (`resumo_geral_testes.csv`) com a decisão tomada de cada teste é gerado para fácil importação e acompanhamento.

---

## Link da planilha de acompanhamento (Google Sheets):

**👉 [Clique aqui para acessar a Planilha de Acompanhamento](https://docs.google.com/spreadsheets/d/13r0QkD7t5rCMBVE6TWNgQAd0vCZ6TdqqRwZz3lRszlA/edit?usp=drivesdk)**

---

## Critério analítico de escolha:

A métrica prioritária de decisão aplicada foi a **Margem Líquida** (Comissão - Cashback), ponderada pelo **ROI do Cashback** (Vendas Totais / Cashback). 

Isso garante que não escolheremos simplesmente a variante com maior volume bruto de vendas (GMV) se ela apresentar uma distribuição de cashback muito agressiva que prejudique o resultado financeiro líquido do Méliuz. Buscamos sempre o ponto ideal de eficiência e lucro real!

---

## Resumo das Decisões:

| Parceiro | Variante Vencedora | Decisão | Justificativa |
|----------|-------------------|---------|---------------|
| **Parceiro A** | Grupo 1 | Escalar para 100% | Apesar da falta de significância estatística (p=0,1315) e da queda na margem entre a 1ª e 2ª metade do teste, o Grupo 1 ainda possui a maior margem líquida acumulada (R$ 404.711) e o maior ROI (24,01x). O Grupo 2 tem margem 12% menor e o Grupo 3 é 35% menor. O custo de oportunidade de manter o teste rodando é maior que o risco de escalar agora. Recomendamos monitoramento semanal pós-escala. |
| **Parceiro B** | Grupo 1 | Escalar para 100% | De longe a melhor performance em margem líquida (mais que o dobro do Grupo 2) e o maior ROI. Diferença estatisticamente significativa (p < 0,001). |
| **Parceiro C** | Grupo 1 | Escalar para 100% | Única variante viável. O Grupo 2 empatou em R$ 0,00 de margem líquida (comissão totalmente consumida por cashback). Diferença estatisticamente significativa (p < 0,001). |

---

## Definições das métricas utilizadas:

Para garantir clareza na interpretação dos relatórios, abaixo estão as definições das principais métricas calculadas:

- **Margem Líquida = Comissão - Cashback** → lucro real do Méliuz por parceiro/variante. É a métrica mais importante para a decisão, pois indica quanto efetivamente sobra para a empresa após distribuir o cashback.
- **Take-rate = Comissão / GMV** → fatia do Méliuz sobre as vendas totais. Representa o percentual de cada venda que o Méliuz recebe do parceiro.
- **ROI do Cashback = GMV / Cashback** → retorno sobre o investimento em cashback. Indica quantos reais em vendas foram gerados para cada real investido em cashback. Quanto maior, mais eficiente é o investimento.

---

## Ferramentas e Processo:

Para a construção deste case, utilizei **Python (Pandas, NumPy, SciPy)** para todo o processamento técnico e análise de dados. Contei com o apoio estratégico de Inteligência Artificial de forma pontual:

- **Manus IA:** utilizado para a estruturação do meu **plano de ação** inicial, organização das etapas do projeto e gestão do tempo para garantir a entrega dentro do prazo.
- **DeepSeek:** utilizado para realizar o **benchmarking cultural**, garantindo que a solução e a comunicação estivessem 100% alinhadas com os valores e a visão de negócio do Méliuz, por além da formatação de alguns textos.

---

## Para executar a solução:

Caso queira reproduzir a análise localmente:

1. Certifique-se de ter os arquivos de dataset (`dataset_01_parceiroA.csv`, `dataset_02_parceiroB.csv` e `dataset_03_parceiroC.csv`) na mesma pasta que o script.
2. Instale as bibliotecas necessárias:
   ```bash
   pip install pandas numpy scipy tabulate
   ```

3. Execute o script:
   ```bash
   python analyze_test.py *.csv
   ```

Os relatórios dinâmicos serão reescritos na pasta /resultados e o arquivo consolidado será gerado.

---

Desenvolvido com carinho por Joana Aghata. Qualquer dúvida, estou totalmente à disposição!
