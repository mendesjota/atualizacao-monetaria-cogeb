"""
Regras de negócio: transforma a planilha de entrada em parcelas mensais,
corrige cada parcela com IPCA-E composto mês a mês e agrega os totais.

Índice: IPCA-E (série mensal obtida via GET /api/ipcae do SINDEC).
Cada parcela é corrigida da sua competência até a data-alvo compondo
as taxas mensais: fator = Π(1 + taxa_mês/100) - 1.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from itertools import groupby
from typing import Literal

from sindec_api import SindecClient


@dataclass
class Beneficiario:
    """Uma linha da planilha de entrada."""

    nome: str
    matricula: str
    orgao: str
    valor_mensal: float
    competencia_inicial: date
    competencia_final: date
    data_alvo: date
    observacao: str = ""


@dataclass
class ParcelaCalculada:
    """Uma parcela mensal já corrigida."""

    nome: str
    competencia: date
    valor_original: float
    valor_corrigido: float
    correcao: float
    fator: float
    indice: str
    tipo: Literal["regular", "decimo_terceiro", "diferenca"] = "regular"


@dataclass
class ResumoBeneficiario:
    """Total consolidado de um beneficiário."""

    nome: str
    matricula: str
    orgao: str
    qtd_parcelas: int
    total_original: float
    total_corrigido: float
    total_correcao: float
    data_alvo: date
    observacao: str = ""
    parcelas: list[ParcelaCalculada] = field(default_factory=list)


# --------------------------------------------------------------------------
# Datas / competências
# --------------------------------------------------------------------------
_MESES_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}


def parse_competencia(texto: str) -> date:
    """
    Converte string de data para date.

    Aceita formatos:
      - 'MM/AAAA'      -> date(AAAA, MM, 1)
      - 'DD/MM/AAAA'   -> date(AAAA, MM, DD)
      - 'AAAA-MM'      -> date(AAAA, MM, 1)
      - 'ago/23'       -> date(2023, 8, 1)   (mês abreviado PT-BR + 2 dígitos ano)
    """
    t = str(texto).strip()

    # Formato PT-BR abreviado: 'ago/23'
    m_pt = re.match(r"^([a-z]{3})/(\d{2})$", t, re.IGNORECASE)
    if m_pt:
        mes_num = _MESES_PT.get(m_pt.group(1).lower())
        if mes_num is None:
            raise ValueError(f"Mês inválido: {m_pt.group(1)}")
        ano = int(m_pt.group(2)) + 2000
        return date(ano, mes_num, 1)

    if "-" in t and "/" not in t:  # formato ISO parcial AAAA-MM
        ano, mes = t.split("-")[:2]
        return date(int(ano), int(mes), 1)

    partes = t.split("/")
    if len(partes) == 3:  # DD/MM/AAAA
        dia, mes, ano = int(partes[0]), int(partes[1]), int(partes[2])
        return date(ano, mes, dia)
    # MM/AAAA
    mes, ano = int(partes[0]), int(partes[1])
    return date(ano, mes, 1)


def meses_entre(inicio: date, fim: date) -> list[date]:
    """Lista o 1º dia de cada mês de `inicio` até `fim`, inclusive."""
    if fim < inicio:
        raise ValueError(
            f"competência final ({fim}) é anterior à inicial ({inicio})."
        )
    meses: list[date] = []
    ano, mes = inicio.year, inicio.month
    while (ano, mes) <= (fim.year, fim.month):
        meses.append(date(ano, mes, 1))
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
    return meses


# --------------------------------------------------------------------------
# Correção com IPCA-E mensal
# --------------------------------------------------------------------------
def _corrigir_parcela(
    valor: float,
    competencia: date,
    data_alvo: date,
    taxas_mensais: dict[tuple[int, int], float],
) -> tuple[float, float, float]:
    """
    Corrige uma parcela com IPCA-E mensal composto.

    O fator é o produto de (1 + taxa_mês) para cada mês entre a competência
    (exclusive) e a data-alvo (inclusive).

    Retorna (correcao, valor_corrigido, fator).
    """
    fator = 1.0
    ano, mes = competencia.year, competencia.month
    while (ano, mes) < (data_alvo.year, data_alvo.month):
        taxa = taxas_mensais.get((ano, mes), 0.0)
        fator *= 1.0 + taxa
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1

    fator -= 1.0
    correcao = round(valor * fator, 2)
    valor_corrigido = round(valor + correcao, 2)
    fator_arred = round(fator, 6)
    return correcao, valor_corrigido, fator_arred


# --------------------------------------------------------------------------
# 13º salário
# --------------------------------------------------------------------------
def gerar_parcelas_13(
    parcelas_regulares: list[ParcelaCalculada],
    data_alvo: date,
    taxas_mensais: dict[tuple[int, int], float],
) -> list[ParcelaCalculada]:
    """
    Gera uma parcela de 13º salário por ano,
    com valor igual ao mensal e competência em dezembro.
    """
    if not parcelas_regulares:
        return []

    por_ano: dict[int, list[ParcelaCalculada]] = defaultdict(list)
    for p in parcelas_regulares:
        por_ano[p.competencia.year].append(p)

    decimos: list[ParcelaCalculada] = []
    for ano in sorted(por_ano):
        ref = por_ano[ano][0]
        valor_13 = ref.valor_original
        comp_13 = date(ano, 12, 1)
        correcao, valor_corrigido, fator = _corrigir_parcela(
            valor_13, comp_13, data_alvo, taxas_mensais,
        )
        decimos.append(ParcelaCalculada(
            nome=ref.nome,
            competencia=comp_13,
            valor_original=valor_13,
            valor_corrigido=valor_corrigido,
            correcao=correcao,
            fator=fator,
            indice="IPCA-E",
            tipo="decimo_terceiro",
        ))

    return decimos


def _ordenar_ods(parcelas: list[ParcelaCalculada]) -> list[ParcelaCalculada]:
<<<<<<< HEAD
    """Ordena: mensais por (ano, mês), 13º após dezembro de cada ano."""
=======
    """Ordena: mensais (regular + diferenca) cronológico, 13º no final."""
>>>>>>> 262d0dbe654a79100d25d7d64f103e3a794e272d
    mensais = sorted(
        [p for p in parcelas if p.tipo != "decimo_terceiro"],
        key=lambda p: (p.competencia.year, p.competencia.month),
    )
    dec = sorted(
        [p for p in parcelas if p.tipo == "decimo_terceiro"],
<<<<<<< HEAD
        key=lambda p: (p.competencia.year, 13),
    )
    result: list[ParcelaCalculada] = []
    for ano, grupo in groupby(mensais, key=lambda p: p.competencia.year):
        result.extend(grupo)
        for d in dec:
            if d.competencia.year == ano:
                result.append(d)
    for d in dec:
        if d not in result:
            result.append(d)
    return result
=======
        key=lambda p: (p.competencia.year, p.competencia.month),
    )
    return mensais + dec
>>>>>>> 262d0dbe654a79100d25d7d64f103e3a794e272d


# --------------------------------------------------------------------------
# Orquestração
# --------------------------------------------------------------------------
def processar_beneficiario(
    ben: Beneficiario,
    client: SindecClient,
) -> ResumoBeneficiario:
    """Expande as parcelas mensais, corrige cada uma e gera 13º."""
    competencias = meses_entre(ben.competencia_inicial, ben.competencia_final)
    taxas = client.obter_taxas_mensais_ipcae()

    parcelas_reg: list[ParcelaCalculada] = []
    for comp in competencias:
        correcao, valor_corrigido, fator = _corrigir_parcela(
            ben.valor_mensal, comp, ben.data_alvo, taxas,
        )
        parcelas_reg.append(
            ParcelaCalculada(
                nome=ben.nome,
                competencia=comp,
                valor_original=ben.valor_mensal,
                valor_corrigido=valor_corrigido,
                correcao=correcao,
                fator=fator,
                indice="IPCA-E",
                tipo="regular",
            )
        )

    parcelas_13 = gerar_parcelas_13(parcelas_reg, ben.data_alvo, taxas)
    parcelas = _ordenar_ods(parcelas_reg + parcelas_13)

    total_orig = round(sum(p.valor_original for p in parcelas), 2)
    total_corr = round(sum(p.valor_corrigido for p in parcelas), 2)
    return ResumoBeneficiario(
        nome=ben.nome,
        matricula=ben.matricula,
        orgao=ben.orgao,
        qtd_parcelas=len(parcelas),
        total_original=total_orig,
        total_corrigido=total_corr,
        total_correcao=round(total_corr - total_orig, 2),
        data_alvo=ben.data_alvo,
        observacao=ben.observacao,
        parcelas=parcelas,
    )


def processar_beneficiario_com_analise(
    ben: Beneficiario,
    analise: list[dict],
    client: SindecClient,
) -> ResumoBeneficiario:
    """
    Cria parcelas a partir da análise de SEGURIDADE SOCIAL (Analisador.py).
    Cada item de `analise` tem competencia, valor_seg_social, teto_ano, valor_final.
    O valor_final já está com teto aplicado; é usado como valor_original da parcela.
    """
    taxas = client.obter_taxas_mensais_ipcae()

    parcelas: list[ParcelaCalculada] = []
    for row in analise:
        comp_str: str = row["competencia"]  # "2023-08" ou "2023-13"
        valor_final: float = row["valor_final"]
        origem: str = row.get("origem", "40920")

        if comp_str.endswith("-13"):
            ano = int(comp_str[:4])
            comp = date(ano, 12, 1)
            tipo: Literal["regular", "decimo_terceiro", "diferenca"] = "decimo_terceiro"
        elif origem == "50920":
            ano_s, mes_s = comp_str.split("-")
            comp = date(int(ano_s), int(mes_s), 1)
            tipo = "diferenca"
        else:
            ano_s, mes_s = comp_str.split("-")
            comp = date(int(ano_s), int(mes_s), 1)
            tipo = "regular"

        correcao, valor_corrigido, fator = _corrigir_parcela(
            valor_final, comp, ben.data_alvo, taxas,
        )

        parcelas.append(ParcelaCalculada(
            nome=ben.nome,
            competencia=comp,
            valor_original=valor_final,
            valor_corrigido=valor_corrigido,
            correcao=correcao,
            fator=fator,
            indice="IPCA-E",
            tipo=tipo,
        ))

    parcelas = _ordenar_ods(parcelas)

    total_orig = round(sum(p.valor_original for p in parcelas), 2)
    total_corr = round(sum(p.valor_corrigido for p in parcelas), 2)
    return ResumoBeneficiario(
        nome=ben.nome,
        matricula=ben.matricula,
        orgao=ben.orgao,
        qtd_parcelas=len(parcelas),
        total_original=total_orig,
        total_corrigido=total_corr,
        total_correcao=round(total_corr - total_orig, 2),
        data_alvo=ben.data_alvo,
        observacao=ben.observacao,
        parcelas=parcelas,
    )


def processar_todos(
    beneficiarios: list[Beneficiario],
    client: SindecClient,
    progresso=None,
) -> list[ResumoBeneficiario]:
    """
    Processa a lista inteira. `progresso` (opcional) é chamado como
    progresso(indice, total, beneficiario) para feedback na tela.
    """
    resumos: list[ResumoBeneficiario] = []
    total = len(beneficiarios)
    for i, ben in enumerate(beneficiarios, start=1):
        if progresso:
            progresso(i, total, ben)
        resumos.append(processar_beneficiario(ben, client))
    return resumos
