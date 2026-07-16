#!/usr/bin/env python3
"""
write_to_sheets.py — Sobe o resumo_geral_testes.csv pra uma planilha do Google Sheets.

Isso é opcional (o script principal já gera o CSV pronto pra importar manualmente).
Só roda se você tiver uma credencial de conta de serviço do Google.

Como configurar (uma vez só):
1. Crie um projeto no Google Cloud Console e ative a Google Sheets API e a Google Drive API.
2. Crie uma conta de serviço, gere uma chave em JSON e salve como `credenciais_google.json`
   nessa pasta (esse arquivo NÃO deve ir pro Git — já está no .gitignore).
3. Crie uma planilha vazia no Sheets, compartilhe com o e-mail da conta de serviço
   (está dentro do JSON, campo "client_email") como Editor.
4. Copie o ID da planilha (a parte da URL entre /d/ e /edit) e passe como argumento.

Uso:
    pip install gspread google-auth
    python write_to_sheets.py <ID_DA_PLANILHA>
"""

import sys
from pathlib import Path

import pandas as pd

RESUMO_PATH = Path("resumo_geral_testes.csv")
CREDENCIAIS_PATH = Path("credenciais_google.json")


def main():
    if len(sys.argv) != 2:
        print("Uso: python write_to_sheets.py <ID_DA_PLANILHA>")
        sys.exit(1)

    if not RESUMO_PATH.exists():
        print(f"Não achei {RESUMO_PATH}. Rode o analyze_test.py primeiro.")
        sys.exit(1)

    if not CREDENCIAIS_PATH.exists():
        print(
            f"Não achei {CREDENCIAIS_PATH}. Veja as instruções no topo deste "
            f"arquivo pra gerar a credencial de conta de serviço do Google."
        )
        sys.exit(1)

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("Instale as dependências primeiro: pip install gspread google-auth")
        sys.exit(1)

    planilha_id = sys.argv[1]

    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credenciais = Credentials.from_service_account_file(CREDENCIAIS_PATH, scopes=escopos)
    cliente = gspread.authorize(credenciais)

    planilha = cliente.open_by_key(planilha_id).sheet1
    df = pd.read_csv(RESUMO_PATH)

    planilha.clear()
    planilha.update([df.columns.values.tolist()] + df.values.tolist())

    print(f"Planilha atualizada com {len(df)} teste(s).")
    print(f"https://docs.google.com/spreadsheets/d/{planilha_id}/edit")


if __name__ == "__main__":
    main()
