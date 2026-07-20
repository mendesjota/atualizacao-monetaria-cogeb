"""
Testes de extração: compara valores da ficha financeira (simulada) com os
valores de saída do Analisador (que viram "Valor Original" na planilha final).

Rode com:  python -m pytest testes/test_analisador.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from Analisador import TETO, aplicar_teto, gerar_matriz_mensal


def _dict_por_ano(
    regular: list[float] | None = None,
    decimo: list[float] | None = None,
    diferenca: list[float] | None = None,
    ano: int = 2024,
) -> dict:
    """Monta {ano: {tipo: [12 vals]}} com zeros nos tipos não informados."""
    dados = {}
    if regular is not None:
        dados["regular"] = regular
    if decimo is not None:
        dados["decimo"] = decimo
    if diferenca is not None:
        dados["diferenca"] = diferenca
    return {ano: dados}


# ---------------------------------------------------------------------------
# aplicar_teto
# ---------------------------------------------------------------------------

def test_aplicar_teto_abaixo():
    """Valor abaixo do teto permanece igual."""
    entrada = {2024: {"regular": [1500.0] * 12}}
    saida = aplicar_teto(entrada)
    assert saida[2024]["regular"][0] == 1500.0


def test_aplicar_teto_acima():
    """Valor acima do teto é limitado."""
    entrada = {2024: {"regular": [5000.0] * 12}}
    saida = aplicar_teto(entrada)
    assert saida[2024]["regular"][0] == TETO[2024]


def test_aplicar_teto_ano_sem_teto():
    """Ano sem teto definido não sofre corte."""
    entrada = {2030: {"regular": [5000.0] * 12}}
    saida = aplicar_teto(entrada)
    assert saida[2030]["regular"][0] == 5000.0


# ---------------------------------------------------------------------------
# gerar_matriz_mensal — valores da ficha → valor_final
# ---------------------------------------------------------------------------

def test_regular_mantem_valores():
    """40920 mensais viram valor_final sem alteração (abaixo do teto)."""
    reg = [1500.0 + i * 10 for i in range(12)]  # 1500, 1510, ..., 1610
    entrada = _dict_por_ano(regular=reg)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")
    assert len(resultado) == 12
    for i, row in enumerate(resultado):
        assert row["competencia"] == f"2024-{i+1:02d}"
        assert row["valor_final"] == reg[i]
        assert row["origem"] == "40920"


def test_regular_com_teto():
    """40920 acima do teto é capado no valor_final."""
    reg = [5000.0] * 12
    entrada = _dict_por_ano(regular=reg)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")
    for row in resultado:
        assert row["valor_final"] == TETO[2024]


def test_decimo_unico_mes():
    """40923 em novembro gera entrada de 13º em novembro, não em dezembro."""
    reg = [1500.0] * 12
    dec = [0.0] * 12
    dec[10] = 1747.69  # novembro
    entrada = _dict_por_ano(regular=reg, decimo=dec)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")

    # 12 regulares + 1 decimo
    assert len(resultado) == 13

    dec_entries = [r for r in resultado if r["origem"] == "40923"]
    assert len(dec_entries) == 1
    assert dec_entries[0]["competencia"] == "2024-11"
    assert dec_entries[0]["valor_final"] == 1747.69


def test_decimo_dividido_dois_meses():
    """40923 dividido em março e novembro gera 2 entradas de 13º."""
    reg = [1500.0] * 12
    dec = [0.0] * 12
    dec[2] = 800.00   # março
    dec[10] = 947.69  # novembro
    entrada = _dict_por_ano(regular=reg, decimo=dec)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")

    dec_entries = [r for r in resultado if r["origem"] == "40923"]
    assert len(dec_entries) == 2
    assert dec_entries[0]["competencia"] == "2024-03"
    assert dec_entries[0]["valor_final"] == 800.00
    assert dec_entries[1]["competencia"] == "2024-11"
    assert dec_entries[1]["valor_final"] == 947.69


def test_decimo_valor_zero_ignorado():
    """40923 com todos os meses zerados não gera entrada de 13º."""
    reg = [1500.0] * 12
    dec = [0.0] * 12
    entrada = _dict_por_ano(regular=reg, decimo=dec)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")

    dec_entries = [r for r in resultado if r["origem"] == "40923"]
    assert len(dec_entries) == 0
    assert len(resultado) == 12


def test_decimo_sem_lista_ignorado():
    """Ano sem chave 'decimo' não gera entrada de 13º."""
    reg = [1500.0] * 12
    entrada = {2024: {"regular": reg}}  # sem decimo
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")

    dec_entries = [r for r in resultado if r["origem"] == "40923"]
    assert len(dec_entries) == 0
    assert len(resultado) == 12


def test_decimo_com_teto():
    """40923 acima do teto é limitado no valor_final."""
    reg = [1500.0] * 12
    dec = [0.0] * 12
    dec[10] = 5000.0  # acima do teto 2024 (1791.18)
    entrada = _dict_por_ano(regular=reg, decimo=dec)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")

    dec_entries = [r for r in resultado if r["origem"] == "40923"]
    assert len(dec_entries) == 1
    assert dec_entries[0]["valor_final"] == TETO[2024]


def test_diferenca_gerada():
    """50920 com valor não-zero gera entrada separada."""
    reg = [1500.0] * 12
    dif = [0.0] * 12
    dif[5] = 500.00  # junho
    entrada = _dict_por_ano(regular=reg, diferenca=dif)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")

    dif_entries = [r for r in resultado if r["origem"] == "50920"]
    assert len(dif_entries) == 1
    assert dif_entries[0]["competencia"] == "2024-06"
    assert dif_entries[0]["valor_final"] == 500.00


def test_diferenca_valor_zero_ignorado():
    """50920 zerado não gera entrada."""
    reg = [1500.0] * 12
    dif = [0.0] * 12
    entrada = _dict_por_ano(regular=reg, diferenca=dif)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")

    dif_entries = [r for r in resultado if r["origem"] == "50920"]
    assert len(dif_entries) == 0


def test_combinado_tres_tipos():
    """40920 + 40923 + 50920 no mesmo mês geram 3 entradas."""
    reg = [1500.0] * 12
    dec = [0.0] * 12
    dec[9] = 1747.69  # outubro
    dif = [0.0] * 12
    dif[9] = 300.00   # outubro
    entrada = _dict_por_ano(regular=reg, decimo=dec, diferenca=dif)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")

    # outubro deve ter: regular + 13º + diferença
    out_entries = [r for r in resultado if r["competencia"] == "2024-10"]
    assert len(out_entries) == 3
    origens = {r["origem"] for r in out_entries}
    assert origens == {"40920", "40923", "50920"}

    assert len(resultado) == 14  # 12 reg + 1 dec + 1 dif


def test_periodo_parcial_primeiros_meses():
    """Período menor que 12 meses só retorna os meses solicitados."""
    reg = [1500.0] * 12
    entrada = _dict_por_ano(regular=reg)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "03/2024")
    assert len(resultado) == 3
    assert resultado[0]["competencia"] == "2024-01"
    assert resultado[1]["competencia"] == "2024-02"
    assert resultado[2]["competencia"] == "2024-03"


def test_periodo_parcial_meio_ano():
    """Período no meio do ano (jun a set) retorna só esses meses."""
    reg = [1500.0] * 12
    entrada = _dict_por_ano(regular=reg)
    resultado = gerar_matriz_mensal(entrada, "06/2024", "09/2024")
    assert len(resultado) == 4
    assert resultado[0]["competencia"] == "2024-06"
    assert resultado[-1]["competencia"] == "2024-09"


def test_multianual_com_decimos():
    """13º em anos diferentes, cada um no mês correto de cada ano."""
    reg_2023 = [1500.0] * 12
    dec_2023 = [0.0] * 12
    dec_2023[11] = 1733.65  # dezembro 2023

    reg_2024 = [1600.0] * 12
    dec_2024 = [0.0] * 12
    dec_2024[10] = 1747.69  # novembro 2024

    entrada = {
        2023: {"regular": reg_2023, "decimo": dec_2023},
        2024: {"regular": reg_2024, "decimo": dec_2024},
    }
    resultado = gerar_matriz_mensal(entrada, "01/2023", "12/2024")

    # 12 + 12 reg + 1 dec 2023 + 1 dec 2024 = 26
    assert len(resultado) == 26

    dec_entries = [r for r in resultado if r["origem"] == "40923"]
    assert len(dec_entries) == 2
    assert dec_entries[0]["competencia"] == "2023-12"
    assert dec_entries[0]["valor_final"] == 1733.65
    assert dec_entries[1]["competencia"] == "2024-11"
    assert dec_entries[1]["valor_final"] == 1747.69


def test_cenario_livia():
    """
    Caso real: Lívia — 40923 apenas em novembro/2024.
    Deve gerar entrada 13º em 2024-11, não em 2024-12.
    """
    reg = [1747.69] * 12
    dec = [0.0] * 12
    dec[10] = 1747.69  # novembro
    entrada = _dict_por_ano(regular=reg, decimo=dec)
    resultado = gerar_matriz_mensal(entrada, "01/2024", "12/2024")

    dec_entries = [r for r in resultado if r["origem"] == "40923"]
    assert len(dec_entries) == 1
    assert dec_entries[0]["competencia"] == "2024-11"
    assert dec_entries[0]["valor_final"] == 1747.69

    # Garante que NÃO tem entrada 13º em dezembro
    dec_dez = [r for r in dec_entries if r["competencia"] == "2024-12"]
    assert len(dec_dez) == 0
