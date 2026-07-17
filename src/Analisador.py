"""
Analisa a Ficha Financeira Individual (.xls do SIGRH) extraindo os valores
mensais de SEGURIDADE SOCIAL (código 40920) e 13º salário (40923)
para o período de análise, aplicando o teto (teto máximo de contribuição)
de cada ano.

Uso:
    python src/Analisador.py <caminho.xls> <data_inicio> <data_fim>
    python src/Analisador.py <caminho.xls> --csv <caminho_csv>

    data_inicio/data_fim: MM/YYYY ou MM-YYYY

Saída (stdout): CSV com colunas:
    competencia;valor_seg_social;teto_ano;valor_final
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

TETO: Dict[int, float] = {
    2020: 671.09,
    2021: 1487.39,
    2022: 1638.48,
    2023: 1733.65,
    2024: 1791.18,
    2025: 1872.37,
    2026: 1940.58,
}

CODIGOS = {
    "regular": (r"40920\s+SEGURIDADE SOCIAL", 1),
    "decimo": (r"40923\s+SEGURIDADE\.SOC\.GRAT\.NATALICIA", 2),
    "diferenca": (r"50920\s+DIF\.\s*SEGURIDADE SOCIAL", 3),
}


def _limpar_valor(texto: str) -> float:
    texto = texto.strip().replace("R$", "").replace(" ", "")
    if not texto or texto in ("-", ""):
        return 0.0
    negativo = texto.startswith("-")
    if negativo:
        texto = texto[1:]
    texto = texto.replace(".", "").replace(",", ".")
    valor = float(texto)
    return -valor if negativo else valor


def _extrair_valores(linha_tr: str) -> Optional[Tuple[str, List[float]]]:
    for tipo, (pattern, prioridade) in CODIGOS.items():
        if re.search(pattern, linha_tr):
            tds = re.findall(r"<td[^>]*>(.*?)</td>", linha_tr, re.DOTALL)
            if len(tds) < 13:
                return None
            valores = [_limpar_valor(tds[i]) for i in range(1, 13)]
            return tipo, valores
    return None


def parse_xls(caminho: str | Path) -> Dict[int, Dict[str, List[float]]]:
    """
    Lê o .xls (HTML) e retorna dict {ano: {"regular": [12 vals], "decimo": [12 vals]}}
    usando a ÚLTIMA ocorrência de cada código por ano (segundo vínculo prevalece).
    """
    caminho = Path(caminho)
    raw = caminho.read_bytes().decode("latin-1")

    tabelas = re.findall(r"<table[^>]*>(.*?)</table>", raw, re.DOTALL)

    anos: Dict[int, Dict[str, List[float]]] = {}
    ano_atual: Optional[int] = None

    for tbl in tabelas:
        txt_header = re.sub(r"<[^>]+>", " ", tbl)
        txt_header = re.sub(r"\s+", " ", txt_header).strip()

        m_ano = re.search(r"COMPET\w*NCIA\s*-\s*(\d{4})", txt_header, re.IGNORECASE)
        if m_ano:
            ano_atual = int(m_ano.group(1))
            continue

        if ano_atual is not None:
            if ano_atual not in anos:
                anos[ano_atual] = {}

            linhas = re.findall(r"<tr>(.*?)</tr>", tbl, re.DOTALL)
            for linha in linhas:
                extraido = _extrair_valores(linha)
                if extraido:
                    tipo, valores = extraido
<<<<<<< HEAD
                    # Sempre sobrescreve — última ocorrência vence
                    anos[ano_atual][tipo] = valores
=======
                    # Mantém a primeira ocorrência (primeiro vínculo)
                    if tipo not in anos[ano_atual]:
                        anos[ano_atual][tipo] = valores
>>>>>>> 262d0dbe654a79100d25d7d64f103e3a794e272d
            ano_atual = None

    return anos


def aplicar_teto(valores_por_ano: Dict[int, Dict[str, List[float]]]) -> Dict[int, Dict[str, List[float]]]:
    resultado: Dict[int, Dict[str, List[float]]] = {}
    for ano, dados in valores_por_ano.items():
        resultado[ano] = {}
        teto = TETO.get(ano)
        for tipo, vals in dados.items():
            if teto is None:
                resultado[ano][tipo] = vals[:]
            else:
                resultado[ano][tipo] = [min(v, teto) for v in vals]
    return resultado


def _emitir_entrada(
    competencia: str,
    valor_original: float,
    valor_final: float,
    teto: float,
    origem: str = "40920",
) -> Dict:
    return {
        "competencia": competencia,
        "valor_seg_social": valor_original,
        "teto_ano": teto,
        "valor_final": valor_final,
        "origem": origem,
    }


def gerar_matriz_mensal(
    valores_por_ano: Dict[int, Dict[str, List[float]]],
    data_inicio: str,
    data_fim: str,
) -> List[Dict]:
    """
    Gera a matriz de saída para cada mês + 13º salário + diferenças 50920.
    """
    def _parse_data(d: str) -> Tuple[int, int]:
        d = d.replace("-", "/")
        partes = d.split("/")
        return int(partes[1]), int(partes[0])

    ano_ini, mes_ini = _parse_data(data_inicio)
    ano_fim, mes_fim = _parse_data(data_fim)

    cappados = aplicar_teto(valores_por_ano)

    resultado: List[Dict] = []
    ano = ano_ini
    mes = mes_ini
    while (ano < ano_fim) or (ano == ano_fim and mes <= mes_fim):
        competencia = f"{ano:04d}-{mes:02d}"
        dados_ano = valores_por_ano.get(ano, {})
        teto = TETO.get(ano, 0.0)
        vals_reg = dados_ano.get("regular", [])
        vals_dif = dados_ano.get("diferenca", [])
        vals_dec = dados_ano.get("decimo", [])

        # Entrada regular 40920
        valor_original = 0.0
        valor_final = 0.0
        if vals_reg and mes <= len(vals_reg):
            valor_original = vals_reg[mes - 1]
            valor_final = cappados[ano]["regular"][mes - 1]

        resultado.append(
            _emitir_entrada(competencia, valor_original, valor_final, teto, "40920")
        )

        # Entrada extra 50920 (diferença) se houver valor
        if vals_dif and mes <= len(vals_dif) and vals_dif[mes - 1] != 0:
            dif_original = vals_dif[mes - 1]
            dif_final = min(dif_original, teto) if teto else dif_original
            resultado.append(
                _emitir_entrada(competencia, dif_original, dif_final, teto, "50920")
            )

        mes += 1
        if mes > 12:
            # Incluir 13º salário do ano que terminou
            if vals_dec:
                dec_val = sum(vals_dec)
                dec_final = dec_val
                if teto:
                    dec_final = min(dec_val, teto)
                resultado.append({
                    "competencia": f"{ano:04d}-13",
                    "valor_seg_social": dec_val,
                    "teto_ano": teto,
                    "valor_final": dec_final,
                    "origem": "40923",
                })
            mes = 1
            ano += 1

    return resultado


def _extrair_periodo_csv(caminho_csv: str | Path) -> Tuple[str, str]:
    caminho_csv = Path(caminho_csv)
    with open(caminho_csv, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            ci = row.get("competencia_inicial", "").strip()
            cf = row.get("competencia_final", "").strip()
            if ci and cf:
                return ci, cf
    raise ValueError("CSV vazio ou sem colunas competencia_inicial/competencia_final")


def analisar(
    caminho_xls: str | Path,
    data_inicio: str,
    data_fim: str,
) -> List[Dict]:
    valores_por_ano = parse_xls(caminho_xls)
    return gerar_matriz_mensal(valores_por_ano, data_inicio, data_fim)


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    xls_path = sys.argv[1]

    if "--csv" in sys.argv:
        idx = sys.argv.index("--csv")
        csv_path = sys.argv[idx + 1]
        data_inicio, data_fim = _extrair_periodo_csv(csv_path)
    elif len(sys.argv) >= 4:
        data_inicio = sys.argv[2]
        data_fim = sys.argv[3]
    else:
        print("Forneça <data_inicio> <data_fim> ou use --csv <caminho>", file=sys.stderr)
        sys.exit(1)

    resultado = analisar(xls_path, data_inicio, data_fim)

    writer = csv.writer(sys.stdout)
    writer.writerow(["competencia", "valor_seg_social", "teto_ano", "valor_final"])
    for row in resultado:
        writer.writerow([
            row["competencia"],
            f"{row['valor_seg_social']:.2f}",
            f"{row['teto_ano']:.2f}",
            f"{row['valor_final']:.2f}",
        ])


if __name__ == "__main__":
    main()
