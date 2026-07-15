"""
Testes unitários (sem rede) das regras de datas e parsing.
Rode com:  python -m pytest testes/ -v
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from calculo import _corrigir_parcela, meses_entre, parse_competencia
from io_planilha import _valor_para_float
from sindec_api import _moeda_para_float


def test_parse_competencia_barra():
    assert parse_competencia("01/2024") == date(2024, 1, 1)
    assert parse_competencia("12/2023") == date(2023, 12, 1)


def test_parse_competencia_iso():
    assert parse_competencia("2024-07") == date(2024, 7, 1)


def test_meses_entre_intervalo():
    meses = meses_entre(date(2024, 1, 1), date(2024, 7, 1))
    assert len(meses) == 7
    assert meses[0] == date(2024, 1, 1)
    assert meses[-1] == date(2024, 7, 1)


def test_meses_entre_atravessa_ano():
    meses = meses_entre(date(2023, 11, 1), date(2024, 2, 1))
    assert meses == [
        date(2023, 11, 1), date(2023, 12, 1),
        date(2024, 1, 1), date(2024, 2, 1),
    ]


def test_meses_entre_mesmo_mes():
    assert meses_entre(date(2024, 3, 1), date(2024, 3, 1)) == [date(2024, 3, 1)]


def test_meses_entre_invertido_erro():
    with pytest.raises(ValueError):
        meses_entre(date(2024, 7, 1), date(2024, 1, 1))


@pytest.mark.parametrize("texto,esperado", [
    ("1500.00", 1500.0),
    ("1500,00", 1500.0),
    ("1.500,00", 1500.0),
    ("R$ 3.200,50", 3200.50),
    (1500, 1500.0),
])
def test_valor_para_float(texto, esperado):
    assert _valor_para_float(texto) == esperado


@pytest.mark.parametrize("texto,esperado", [
    ("R$ 1.572,60", 1572.60),
    ("R$ 0,00", 0.0),
    ("R$ 12.345,67", 12345.67),
])
def test_moeda_para_float(texto, esperado):
    assert _moeda_para_float(texto) == esperado


# --- IPCA-E corrections ---

def test_corrigir_parcela_mesmo_mes():
    """Sem correção quando competência = data_alvo."""
    tx = {(2025, 2): 0.0123, (2025, 3): 0.0064}
    corr, v_corr, fator = _corrigir_parcela(
        1000.0, date(2025, 3, 1), date(2025, 3, 1), tx,
    )
    assert corr == 0.0
    assert v_corr == 1000.0
    assert fator == 0.0


def test_corrigir_parcela_um_mes():
    """Correção de um mês usa a taxa do mês de origem."""
    tx = {(2025, 1): 0.0011, (2025, 2): 0.0123}
    corr, v_corr, fator = _corrigir_parcela(
        1000.0, date(2025, 2, 1), date(2025, 3, 1), tx,
    )
    assert corr == 12.30
    assert v_corr == 1012.30
    assert fator == 0.0123


def test_corrigir_parcela_composto():
    """Compõe taxas mês a mês: fator = (1+t1)*(1+t2) - 1."""
    tx = {(2025, 1): 0.01, (2025, 2): 0.02}
    corr, v_corr, fator = _corrigir_parcela(
        1000.0, date(2025, 1, 1), date(2025, 3, 1), tx,
    )
    f_expected = round(1.01 * 1.02 - 1, 6)
    assert fator == f_expected
    assert v_corr == round(1000.0 * (1 + f_expected), 2)


def test_corrigir_parcela_atravessa_ano():
    """Compõe taxas de anos diferentes."""
    tx = {(2024, 11): 0.005, (2024, 12): 0.004, (2025, 1): 0.0011}
    corr, v_corr, fator = _corrigir_parcela(
        1000.0, date(2024, 11, 1), date(2025, 2, 1), tx,
    )
    f_expected = round(1.005 * 1.004 * 1.0011 - 1, 6)
    assert fator == f_expected
    assert v_corr == round(1000.0 * (1 + f_expected), 2)


def test_corrigir_parcela_mes_futuro_sem_taxa():
    """Mês sem taxa disponível é tratado como 0."""
    tx = {(2025, 1): 0.01}
    corr, v_corr, fator = _corrigir_parcela(
        1000.0, date(2025, 1, 1), date(2025, 4, 1), tx,
    )
    # jan=1%, fev/mar=0 (não estão em tx)
    assert fator == 0.01
    assert v_corr == 1010.00
