#!/usr/bin/env python3
"""
analyze_test.py — Análise automática de testes A/B de cashback (Méliuz)

Uso:
    python analyze_test.py caminho/para/dataset.csv
    python analyze_test.py dataset_01_parceiroA.csv dataset_02_parceiroB.csv
    python analyze_test.py *.csv

Pra cada arquivo passado, gera:
    - resultados/analise_<parceiro>.md   (relatório pro gestor)
    - uma linha nova em resumo_geral_testes.csv (formato pra subir no Sheets)

Funciona com qualquer CSV que siga o schema (Data, Grupos de usuários, Parceiro,
compradores, comissão, cashback, vendas totais) — não precisa ser um dos 3
datasets de exemplo, e o script não quebra se o arquivo vier com sujeira comum
(valor com centavos, célula vazia, moeda em outro formato, linha duplicada etc).
"""

import argparse
import csv
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RESULTADOS_DIR = Path("resultados")
RESUMO_PATH = Path("resumo_geral_testes.csv")

# Colunas que o schema espera, e possíveis apelidos/variações que aceitamos
COLUNAS_ESPERADAS = {
    "data": ["data", "date"],
    "grupo": ["grupos de usuarios", "grupo de usuarios", "grupo", "variante", "group"],
    "parceiro": ["parceiro", "partner"],
    "compradores": ["compradores", "buyers", "usuarios"],
    "comissao": ["comissao", "comissão", "commission"],
    "cashback": ["cashback"],
    "vendas": ["vendas totais", "vendas_totais", "gmv", "vendas"],
}


def normalizar(texto):
    """Remove acento, baixa caixa, tira espaço extra — pra casar nomes de coluna com variação."""
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", texto).strip()


def mapear_colunas(df):
    """Acha, pra cada coluna esperada, qual coluna real do CSV corresponde a ela."""
    normalizadas = {normalizar(c): c for c in df.columns}
    mapa = {}
    faltando = []
    for chave, apelidos in COLUNAS_ESPERADAS.items():
        achou = None
        for apelido in apelidos:
            if apelido in normalizadas:
                achou = normalizadas[apelido]
                break
        if achou is None:
            faltando.append(chave)
        else:
            mapa[chave] = achou
    if faltando:
        raise ValueError(
            f"Não achei no CSV as colunas: {faltando}. "
            f"Colunas disponíveis: {list(df.columns)}"
        )
    return mapa


def tratar_grana(valor):
    """
    Converte valor monetário em float, aceitando formatos comuns:
    'R$ 1.234,56' | 'R$ 1234.56' | '1234' | '' | NaN | já numérico.
    Retorna NaN se não der pra interpretar (em vez de quebrar o script).
    """
    if pd.isna(valor):
        return np.nan
    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()
    if texto == "":
        return np.nan

    texto = texto.replace("R$", "").replace("r$", "").strip()

    # Se tem vírgula E ponto, o último separador é o decimal
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        # só vírgula: assume decimal se tiver 1-2 dígitos depois, senão milhar
        partes = texto.split(",")
        if len(partes[-1]) in (1, 2):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "." in texto:
        # só ponto, sem vírgula: padrão BR usa ponto como separador de milhar
        # (ex: "93.390" = noventa e três mil). Só tratamos como decimal se
        # houver um único ponto com exatamente 2 casas depois (ex: "1234.56").
        partes = texto.split(".")
        if not (len(partes) == 2 and len(partes[1]) == 2):
            texto = texto.replace(".", "")

    texto = re.sub(r"[^\d\.\-]", "", texto)
    try:
        return float(texto)
    except ValueError:
        return np.nan


def carregar_dataset(caminho):
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    # tenta utf-8, cai pra latin1 se o arquivo vier de outra origem
    try:
        df = pd.read_csv(caminho, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(caminho, encoding="latin1")

    df.columns = [str(c).strip() for c in df.columns]
    mapa = mapear_colunas(df)

    avisos = []

    linhas_antes = len(df)
    df = df.drop_duplicates()
    if len(df) < linhas_antes:
        avisos.append(f"{linhas_antes - len(df)} linha(s) duplicada(s) removida(s).")

    for chave in ["comissao", "cashback", "vendas"]:
        df[mapa[chave]] = df[mapa[chave]].apply(tratar_grana)

    df[mapa["compradores"]] = pd.to_numeric(df[mapa["compradores"]], errors="coerce")
    df[mapa["data"]] = pd.to_datetime(df[mapa["data"]], errors="coerce")

    colunas_numericas = [mapa["compradores"], mapa["comissao"], mapa["cashback"], mapa["vendas"]]
    linhas_antes = len(df)
    linhas_invalidas = df[colunas_numericas].isna().any(axis=1) | df[mapa["data"]].isna()
    if linhas_invalidas.any():
        avisos.append(
            f"{linhas_invalidas.sum()} linha(s) descartada(s) por dado ilegível "
            f"(valor vazio, texto não numérico ou data inválida)."
        )
    df = df[~linhas_invalidas].copy()

    linhas_antes = len(df)
    negativos = (df[colunas_numericas] < 0).any(axis=1)
    if negativos.any():
        avisos.append(f"{negativos.sum()} linha(s) com valor negativo descartada(s).")
    df = df[~negativos].copy()

    if df.empty:
        raise ValueError("Depois da limpeza não sobrou nenhuma linha válida nesse arquivo.")

    df = df.rename(columns={
        mapa["data"]: "data",
        mapa["grupo"]: "grupo",
        mapa["parceiro"]: "parceiro",
        mapa["compradores"]: "compradores",
        mapa["comissao"]: "comissao",
        mapa["cashback"]: "cashback",
        mapa["vendas"]: "vendas",
    })
    df["margem"] = df["comissao"] - df["cashback"]

    return df, avisos


def analisar(df):
    resumo = df.groupby("grupo").agg(
        compradores=("compradores", "sum"),
        comissao=("comissao", "sum"),
        cashback=("cashback", "sum"),
        vendas=("vendas", "sum"),
        margem=("margem", "sum"),
        dias=("data", "count"),
    ).reset_index()

    resumo["take_rate_%"] = (resumo["comissao"] / resumo["vendas"] * 100).round(2)
    resumo["cashback_rate_%"] = (resumo["cashback"] / resumo["vendas"] * 100).round(2)
    resumo["roi_cashback"] = (resumo["vendas"] / resumo["cashback"]).round(2)
    resumo["ticket_medio"] = (resumo["vendas"] / resumo["compradores"]).round(2)
    resumo = resumo.sort_values("margem", ascending=False).reset_index(drop=True)

    vencedor = resumo.loc[0, "grupo"]
    resultado_estatistico = None

    if len(resumo) >= 2:
        segundo = resumo.loc[1, "grupo"]
        serie_venc = df.loc[df["grupo"] == vencedor, "margem"]
        serie_seg = df.loc[df["grupo"] == segundo, "margem"]
        t_stat, p_valor = stats.ttest_ind(serie_venc, serie_seg, equal_var=False)

        # consistência ao longo do tempo: 1ª metade do teste vs 2ª metade,
        # pra pegar efeito de novidade ou tendência que uma foto única não mostra
        df_venc = df.loc[df["grupo"] == vencedor].sort_values("data")
        meio = len(df_venc) // 2
        margem_1a_metade = df_venc.iloc[:meio]["margem"].mean()
        margem_2a_metade = df_venc.iloc[meio:]["margem"].mean()

        resultado_estatistico = {
            "grupo_comparado": segundo,
            "p_valor": round(p_valor, 4),
            "significativo": bool(p_valor < 0.05),
            "margem_1a_metade": round(margem_1a_metade, 2),
            "margem_2a_metade": round(margem_2a_metade, 2),
            "tendencia_estavel": bool(
                margem_2a_metade >= margem_1a_metade * 0.8
            ),
        }

    return resumo, vencedor, resultado_estatistico


def gerar_relatorio_md(parceiro, resumo, vencedor, stat, avisos, periodo):
    linhas = []
    linhas.append(f"# Teste A/B de Cashback — {parceiro}")
    linhas.append("")
    linhas.append(f"**Período analisado:** {periodo[0]} a {periodo[1]}")
    linhas.append(f"**Pergunta:** qual variante de cashback devemos escalar pra 100% do tráfego?")
    linhas.append("")
    linhas.append(f"## Decisão: escalar **{vencedor}**")
    linhas.append("")

    if stat:
        if pd.isna(stat["p_valor"]):
            confianca = (
                "amostra pequena demais pra calcular significância estatística com confiança — "
                "trate a decisão como preliminar"
            )
        elif stat["significativo"]:
            confianca = f"diferença estatisticamente significativa (p = {stat['p_valor']})"
        else:
            confianca = (
                f"diferença **não** é estatisticamente significativa (p = {stat['p_valor']}) — "
                f"vale considerar estender o teste antes de escalar com confiança total"
            )
        linhas.append(f"Confiança: {confianca} frente ao segundo colocado ({stat['grupo_comparado']}).")

        if not stat["tendencia_estavel"]:
            linhas.append(
                f"Atenção: a margem do grupo vencedor caiu bastante entre a 1ª metade do teste "
                f"(R$ {stat['margem_1a_metade']:.2f}/dia) e a 2ª metade "
                f"(R$ {stat['margem_2a_metade']:.2f}/dia). Pode ser efeito de novidade — "
                f"vale acompanhar mais um ciclo antes de escalar de vez."
            )
        linhas.append("")

    linhas.append("## Métricas por grupo")
    linhas.append("")
    tabela = resumo[[
        "grupo", "compradores", "vendas", "margem",
        "cashback_rate_%", "take_rate_%", "roi_cashback", "ticket_medio",
    ]].copy()
    tabela.columns = [
        "Grupo", "Compradores", "Vendas totais (R$)", "Margem líquida (R$)",
        "% Cashback", "% Take-rate", "ROI Cashback", "Ticket médio (R$)",
    ]
    linhas.append(tabela.to_markdown(index=False, floatfmt=",.2f"))
    linhas.append("")

    linhas.append("## Leitura")
    linhas.append("")
    melhor = resumo.iloc[0]
    pior_margem_maior_venda = resumo.sort_values("vendas", ascending=False).iloc[0]
    if pior_margem_maior_venda["grupo"] != vencedor:
        linhas.append(
            f"- O {pior_margem_maior_venda['grupo']} vendeu mais "
            f"(R$ {pior_margem_maior_venda['vendas']:,.2f}), mas o cashback mais alto "
            f"({pior_margem_maior_venda['cashback_rate_%']}%) comeu boa parte da margem."
        )
    linhas.append(
        f"- {vencedor} teve o melhor equilíbrio entre volume e lucro real: "
        f"R$ {melhor['margem']:,.2f} de margem líquida, com cashback de {melhor['cashback_rate_%']}%."
    )
    linhas.append(
        f"- ROI de cashback do vencedor: {melhor['roi_cashback']}x "
        f"(cada real de cashback trouxe R$ {melhor['roi_cashback']:.2f} em vendas)."
    )
    for _, linha_grupo in resumo.iterrows():
        if linha_grupo["grupo"] == vencedor:
            continue
        if linha_grupo["margem"] <= 0:
            linhas.append(
                f"- {linha_grupo['grupo']} não dá lucro pro Méliuz: a comissão recebida "
                f"(R$ {linha_grupo['comissao']:,.2f}) é igual ou menor que o cashback devolvido "
                f"(R$ {linha_grupo['cashback']:,.2f}). Não deve ser escalado."
            )

    if avisos:
        linhas.append("")
        linhas.append("## Qualidade do dado de entrada")
        linhas.append("")
        for aviso in avisos:
            linhas.append(f"- {aviso}")

    return "\n".join(linhas)


def registrar_no_resumo(parceiro, resumo, vencedor, stat, periodo):
    RESUMO_PATH_EXISTE = RESUMO_PATH.exists()
    melhor = resumo.iloc[0]

    linha = {
        "Nome do teste": f"Cashback {parceiro}",
        "Descrição": (
            f"Teste A/B de % de cashback — {parceiro}, "
            f"{periodo[0]} a {periodo[1]}, {len(resumo)} variantes"
        ),
        "Variante vencedora": vencedor,
        "Margem líquida (R$)": round(melhor["margem"], 2),
        "% Cashback vencedor": melhor["cashback_rate_%"],
        "p-valor": stat["p_valor"] if stat else "",
        "Estatisticamente significativo": (
            "Sim" if stat and stat["significativo"] else "Não" if stat else ""
        ),
        "Decisão": f"Escalar {vencedor} para 100% do tráfego",
        "Data da análise": datetime.now().strftime("%Y-%m-%d"),
    }

    modo = "a" if RESUMO_PATH_EXISTE else "w"
    with open(RESUMO_PATH, modo, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(linha.keys()))
        if not RESUMO_PATH_EXISTE:
            writer.writeheader()
        writer.writerow(linha)


def rodar_um_arquivo(caminho):
    print(f"\n→ Processando {caminho}...")
    df, avisos = carregar_dataset(caminho)
    parceiro = df["parceiro"].iloc[0]
    periodo = (df["data"].min().strftime("%Y-%m-%d"), df["data"].max().strftime("%Y-%m-%d"))

    resumo, vencedor, stat = analisar(df)
    relatorio = gerar_relatorio_md(parceiro, resumo, vencedor, stat, avisos, periodo)

    RESULTADOS_DIR.mkdir(exist_ok=True)
    nome_saida = RESULTADOS_DIR / f"analise_{str(parceiro).replace(' ', '_')}.md"
    nome_saida.write_text(relatorio, encoding="utf-8")

    registrar_no_resumo(parceiro, resumo, vencedor, stat, periodo)

    print(f"  Parceiro: {parceiro} | Vencedor: {vencedor} | Relatório: {nome_saida}")
    if avisos:
        for a in avisos:
            print(f"  Aviso: {a}")


def main():
    parser = argparse.ArgumentParser(description="Analisa teste(s) A/B de cashback.")
    parser.add_argument("arquivos", nargs="+", help="Caminho(s) do(s) CSV(s) do teste A/B")
    args = parser.parse_args()

    erros = []
    # Filtra para processar apenas arquivos .csv e ignora o próprio arquivo de resumo
    arquivos_para_processar = [
        f for f in args.arquivos 
        if f.lower().endswith(".csv") and Path(f).name != RESUMO_PATH.name
    ]

    if not arquivos_para_processar:
        print(f"Nenhum dataset válido encontrado para processar.")
        return

    for caminho in arquivos_para_processar:
        try:
            rodar_um_arquivo(caminho)
        except Exception as e:
            erros.append((caminho, str(e)))
            print(f"  ERRO em {caminho}: {e}")

    print(f"\nConsolidado atualizado em: {RESUMO_PATH}")
    if erros:
        print(f"\n{len(erros)} arquivo(s) não processado(s):")
        for caminho, erro in erros:
            print(f"  - {caminho}: {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()
