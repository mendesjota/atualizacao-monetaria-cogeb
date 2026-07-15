"""
Ponto de entrada da automação de atualização monetária (COGEB / SINDEC-TCDF).

Fluxo padrão:
   1. Valida a conexão com a API (busca série IPCA-E).
   2. Lê a planilha de entrada (.csv).
   3. Corrige cada parcela com IPCA-E composto mês a mês.
   4. Grava o Excel de saída (formato COGEB).

Fluxo completo (--completo):
   1. Baixa Ficha Financeira de cada beneficiário via SIGRH (Extrator).
   2. Extrai SEGURIDADE SOCIAL mês a mês (Analisador).
   3. Corrige com IPCA-E.
   4. Grava o Excel de saída.

Uso:
    python src/main.py                          # entrada/saída padrão
    python src/main.py <entrada> <saida>        # caminhos explícitos
    python src/main.py --validar                # só testa a conexão com a API
    python src/main.py --completo <entrada.csv> <saida.xlsx>   # pipeline completo
"""
from __future__ import annotations

import os
import sys
from datetime import date as _date
from getpass import getpass
from pathlib import Path

# Console do Windows costuma ser cp1252; força UTF-8 para os símbolos (→, ✔, R$).
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from calculo import processar_beneficiario_com_analise, processar_todos
from io_planilha import escrever_saida, ler_entrada
from sindec_api import SindecClient, SindecError

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA_PADRAO = RAIZ / "dados" / "entrada" / "beneficiarios.csv"
_HOJE = _date.today().strftime("%Y_%m_%d")
SAIDA_PADRAO = RAIZ / "dados" / "saida" / f"resultado_{_HOJE}.xlsx"


def validar_api(client: SindecClient) -> bool:
    """Confere se a série IPCA-E está disponível."""
    print("→ Verificando conexão com a API do SINDEC (IPCA-E)...")
    try:
        taxas = client.obter_taxas_mensais_ipcae()
        qtd = len(taxas)
        meses = sorted(taxas.keys())
        print(f"  Série IPCA-E carregada: {qtd} meses "
              f"({meses[0][0]}/{meses[0][1]:02d} a {meses[-1][0]}/{meses[-1][1]:02d})")
        return True
    except (SindecError, RuntimeError, ValueError) as exc:
        print(f"  ✖ Falha ao carregar IPCA-E: {exc}")
        return False


def _progresso(i: int, total: int, ben) -> None:
    print(f"  [{i}/{total}] {ben.nome} "
          f"({ben.competencia_inicial:%m/%Y}–{ben.competencia_final:%m/%Y})")


def _obter_credenciais_sigrh():
    """Retorna (login, senha) de .env, env vars ou prompt."""
    # Tentar ler .env
    env_file = RAIZ / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k == "matricula_sigrh":
                os.environ.setdefault("SIGRH_LOGIN", v)
            elif k == "senha_sigrh":
                os.environ.setdefault("SIGRH_SENHA", v)

    login = os.environ.get("SIGRH_LOGIN")
    senha = os.environ.get("SIGRH_SENHA")
    if login and senha:
        return login, senha
    print("\n=== Credenciais SIGRH ===")
    if not login:
        login = input("Matrícula de Login: ").strip()
    if not senha:
        senha = getpass("Senha de Login: ").strip()
    return login, senha


def main_completo(entrada: Path, saida: Path, xls_path: Path = None) -> int:
    from Analisador import analisar
    from Extrator import run as extrator_run

    if not entrada.exists():
        print(f"✖ Entrada não encontrada: {entrada}")
        return 2

    login, senha = (None, None) if xls_path else _obter_credenciais_sigrh()

    with SindecClient() as client:
        if not validar_api(client):
            print("✖ Abortando: API indisponível.")
            return 1

        print(f"→ Lendo entrada: {entrada}")
        beneficiarios = ler_entrada(entrada)
        print(f"  {len(beneficiarios)} beneficiário(s).")

        resumos = []
        for i, ben in enumerate(beneficiarios, start=1):
            print(f"\n[{i}/{len(beneficiarios)}] {ben.nome} — matrícula {ben.matricula}")

            # Formatar competência para o Analisador
            data_ini = f"{ben.competencia_inicial.month:02d}/{ben.competencia_inicial.year}"
            data_fim = f"{ben.competencia_final.month:02d}/{ben.competencia_final.year}"

            # 1. Baixar ou usar ficha existente
            if xls_path:
                ficha_path = xls_path
                print(f"  Usando ficha existente: {ficha_path}")
            else:
                ano_ini = str(ben.competencia_inicial.year)
                ano_fim = str(ben.competencia_final.year)
                print(f"  Baixando ficha financeira ({ano_ini}-{ano_fim})...")
                ficha_path, erro = extrator_run(
                    matricula_login=login,
                    senha_login=senha,
                    matricula_empregado=ben.matricula,
                    competencia_inicial=ano_ini,
                    competencia_final=ano_fim,
                    codigo_empresa=ben.orgao,
                    pasta_destino=RAIZ / "fichas financeiras",
                    headless=False,
                )
                if erro or not ficha_path:
                    print(f"  ✖ Falha no Extrator: {erro}")
                    continue
                print(f"  Ficha salva: {ficha_path}")

            # 2. Extrair SEGURIDADE SOCIAL
            print(f"  Analisando SEGURIDADE SOCIAL ({data_ini} a {data_fim})...")
            analise = analisar(ficha_path, data_ini, data_fim)
            print(f"  {len(analise)} parcelas extraídas.")

            # 3. Corrigir com IPCA-E
            print(f"  Corrigindo com IPCA-E...")
            resumo = processar_beneficiario_com_analise(ben, analise, client)
            resumos.append(resumo)

    if not resumos:
        print("✖ Nenhum beneficiário processado com sucesso.")
        return 1

    caminho = escrever_saida(resumos, saida)
    total_parcelas = sum(r.qtd_parcelas for r in resumos)
    total_geral = sum(r.total_corrigido for r in resumos)
    print(f"\n✔ Concluído. {len(resumos)} beneficiário(s), "
          f"{total_parcelas} parcela(s), "
          f"total corrigido R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print(f"✔ Saída: {caminho}")
    return 0


def main(argv: list[str]) -> int:
    if "--validar" in argv:
        with SindecClient() as client:
            return 0 if validar_api(client) else 1

    if "--completo" in argv:
        args = [a for a in argv if a != "--completo"]
        xls_path = None
        if "--xls" in args:
            idx = args.index("--xls")
            xls_path = Path(args[idx + 1])
            args = args[:idx] + args[idx + 2:]
        entrada = Path(args[0]) if args else ENTRADA_PADRAO
        saida = Path(args[1]) if len(args) >= 2 else SAIDA_PADRAO
        return main_completo(entrada, saida, xls_path=xls_path)

    entrada = Path(argv[0]) if len(argv) >= 1 else ENTRADA_PADRAO
    saida = Path(argv[1]) if len(argv) >= 2 else SAIDA_PADRAO

    if not entrada.exists():
        print(f"✖ Planilha de entrada não encontrada: {entrada}")
        print(f"  Crie o arquivo (modelo: dados/entrada/_modelo_entrada.csv).")
        return 2

    try:
        with SindecClient() as client:
            if not validar_api(client):
                print("✖ Abortando: a validação da API falhou.")
                return 1

            print(f"→ Lendo entrada: {entrada}")
            beneficiarios = ler_entrada(entrada)
            print(f"  {len(beneficiarios)} beneficiário(s) encontrado(s).")

            print("→ Calculando correção com IPCA-E mensal...")
            resumos = processar_todos(beneficiarios, client, progresso=_progresso)

            caminho = escrever_saida(resumos, saida)
    except (SindecError, ValueError, FileNotFoundError) as exc:
        print(f"✖ Erro: {exc}")
        return 1

    total_parcelas = sum(r.qtd_parcelas for r in resumos)
    print(f"  {total_parcelas} parcela(s) corrigidas.")

    total_geral = sum(r.total_corrigido for r in resumos)
    print(f"✔ Concluído. {len(resumos)} beneficiário(s), "
          f"total corrigido R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print(f"✔ Saída gravada em: {caminho}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
