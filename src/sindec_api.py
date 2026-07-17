"""
Cliente da API do SINDEC (TCDF).

Endpoints:
    POST /api/calcular  —  correção INPC anual (não usado no cálculo atual)
    GET  /api/ipcae     —  série mensal do IPCA-E (usado para correção por parcela)

Requer User-Agent de navegador (sem ele o servidor deixa a requisição pendurada).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import date

import requests

BASE_URL = "https://api-sindec.tc.df.gov.br/api"

# Cabeçalhos que imitam o navegador — necessários para o WAF liberar o POST.
_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://sindec.tc.df.gov.br",
    "Referer": "https://sindec.tc.df.gov.br/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


class SindecError(RuntimeError):
    """Erro ao falar com a API do SINDEC."""


@dataclass
class ResultadoCalculo:
    """Resultado de uma correção monetária de um único valor."""

    valor_original: float
    valor_corrigido: float
    correcao_monetaria: float
    fator: float
    indice: str
    data_valor_original: str  # dd/mm/yyyy (como o site devolve)
    data_atualizacao: str     # dd/mm/yyyy
    bruto: dict               # resposta completa da API, para auditoria


class SindecClient:
    """
    Cliente HTTP para o SINDEC.

    Uso:
        with SindecClient() as api:
            r = api.calcular(1500.0, date(2024, 1, 1), date(2025, 7, 1))
            print(r.valor_corrigido)  # 1572.60
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        pausa_entre_chamadas: float = 0.20,
        tentativas: int = 3,
        cache_por_ano: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.pausa = pausa_entre_chamadas  # respeita o servidor público
        self.tentativas = tentativas
        self.cache_por_ano = cache_por_ano
        self._sessao = requests.Session()
        self._sessao.headers.update(_HEADERS)
        self._cache: dict[tuple, ResultadoCalculo] = {}
        self._cache_ipcae: dict[tuple[int, int], float] | None = None
        self.chamadas_api = 0     # nº de chamadas efetivas ao servidor
        self.acertos_cache = 0    # nº de reaproveitamentos do cache

    # -- context manager -------------------------------------------------
    def __enter__(self) -> "SindecClient":
        return self

    def __exit__(self, *exc) -> None:
        self._sessao.close()

    # -- API pública -----------------------------------------------------
    def calcular(
        self,
        valor: float,
        data_valor_original: date,
        data_atualizacao: date,
        descricao: str = "",
    ) -> ResultadoCalculo:
        """
        Corrige um valor da sua data de origem até a data-alvo (INPC, sem juros).

        Levanta SindecError se a API recusar ou não responder.
        """
        if data_atualizacao < data_valor_original:
            raise SindecError(
                f"data_atualizacao ({data_atualizacao}) é anterior à "
                f"data_valor_original ({data_valor_original})."
            )

        valor = round(float(valor), 2)
        # Chave de cache: pelo ANO da origem (correção anual — ver docs/07) ou
        # pela data exata, conforme cache_por_ano.
        origem_chave = (
            data_valor_original.year
            if self.cache_por_ano
            else data_valor_original.isoformat()
        )
        chave = (valor, origem_chave, data_atualizacao.isoformat())
        if chave in self._cache:
            self.acertos_cache += 1
            base = self._cache[chave]
            # devolve uma cópia com a competência real desta parcela
            return ResultadoCalculo(
                valor_original=valor,
                valor_corrigido=base.valor_corrigido,
                correcao_monetaria=base.correcao_monetaria,
                fator=base.fator,
                indice=base.indice,
                data_valor_original=data_valor_original.strftime("%d/%m/%Y"),
                data_atualizacao=base.data_atualizacao,
                bruto=base.bruto,
            )

        payload = {
            "descricao": descricao or "atualizacao-monetaria-cogeb",
            "dataValorOriginal": data_valor_original.isoformat(),
            "valorOriginal": valor,
            "dataAtualizacao": data_atualizacao.isoformat(),
        }

        dados = self._post("/calcular", payload)
        self.chamadas_api += 1
        resultado = self._parse_resultado(valor, dados)
        self._cache[chave] = resultado
        return resultado

    # -- internos --------------------------------------------------------
    def _post(self, caminho: str, payload: dict) -> dict:
        url = f"{self.base_url}{caminho}"
        ultimo_erro: Exception | None = None

        for tentativa in range(1, self.tentativas + 1):
            try:
                resp = self._sessao.post(url, json=payload, timeout=self.timeout)
            except requests.RequestException as exc:  # rede/timeout
                ultimo_erro = exc
                time.sleep(self.pausa * tentativa)
                continue

            if resp.status_code == 200:
                if self.pausa:
                    time.sleep(self.pausa)
                try:
                    corpo = resp.json()
                except ValueError as exc:
                    raise SindecError("Resposta 200 não era JSON válido.") from exc
                if not corpo.get("sucesso"):
                    raise SindecError(f"API retornou sucesso=false: {corpo}")
                return corpo["resultado"]

            # 422 = validação; não adianta repetir com o mesmo payload
            if resp.status_code == 422:
                raise SindecError(
                    f"Validação falhou (422). Payload={payload}. "
                    f"Resposta={resp.text[:500]}"
                )

            ultimo_erro = SindecError(
                f"HTTP {resp.status_code} em {url}: {resp.text[:300]}"
            )
            time.sleep(self.pausa * tentativa)

        raise SindecError(
            f"Falha ao chamar {url} após {self.tentativas} tentativas: {ultimo_erro}"
        )

    def obter_taxas_mensais_ipcae(self) -> dict[tuple[int, int], float]:
        """
        Retorna {(ano, mes): taxa_decimal} com as taxas mensais do IPCA-E.

        Chamada única ao GET /api/ipcae; o resultado é cacheado na instância.
        Cada taxa é a variação percentual do mês (ex.: 1.23% → 0.0123).
        """
        if self._cache_ipcae is not None:
            return self._cache_ipcae

        url = f"{self.base_url}/ipcae"
        resp = self._sessao.get(url, timeout=self.timeout)
        if resp.status_code != 200:
            raise SindecError(
                f"GET /ipcae retornou HTTP {resp.status_code}: {resp.text[:300]}"
            )
        corpo = resp.json()
        raw = json.loads(corpo.get("historicoIPCAE", "[]"))

        taxas: dict[tuple[int, int], float] = {}
        for rec in raw:
            # formato: "01/01/1992" ou similar
            partes = rec["dataFormatada"].split("/")
            if len(partes) == 3:
                mes, ano = int(partes[1]), int(partes[2])
                taxas[(ano, mes)] = round(rec["valor"] / 100, 8)

        self._cache_ipcae = taxas
        return taxas

    def obter_taxas_anuais(
        self,
        anos: set[int],
        valor_base: float = 1000.0,
    ) -> dict[int, float]:
        """
        Retorna {ano: taxa_decimal} para cada ano em *anos*, consultando a API.
        A taxa é a variação INPC de jan/ano a jan/(ano+1).
        Anos sem dado disponível (futuros) retornam taxa 0.
        Resultados em cache (não repete chamadas para o mesmo ano).
        """
        taxas: dict[int, float] = {}
        for ano in sorted(anos):
            try:
                r = self.calcular(
                    valor=valor_base,
                    data_valor_original=date(ano, 1, 1),
                    data_atualizacao=date(ano + 1, 1, 1),
                    descricao=f"taxa INPC {ano}",
                )
                taxas[ano] = round(r.correcao_monetaria / valor_base, 8)
            except (SindecError, RuntimeError):
                taxas[ano] = 0.0
        return taxas

    @staticmethod
    def _parse_resultado(valor_enviado: float, resultado: dict) -> ResultadoCalculo:
        memoria = resultado.get("memoriaCalculo") or [{}]
        indice = memoria[0].get("indice", "?")
        # A API devolve strings formatadas ("R$ 1.572,60"); pegamos o número
        # da memória de cálculo quando disponível (mais preciso).
        valores = memoria[0].get("valores", {})
        valor_corrigido = valores.get("valorAtualizado")
        correcao = valores.get("correcaoMonetaria")
        if valor_corrigido is None:
            valor_corrigido = _moeda_para_float(resultado.get("valorCorrigido", "0"))
        if correcao is None:
            correcao = _moeda_para_float(resultado.get("correcaoMonetaria", "0"))

        correcao_float = round(float(correcao), 2)
        fator_calc = round(correcao_float / valor_enviado, 6) if valor_enviado > 0 else 0.0
        return ResultadoCalculo(
            valor_original=valor_enviado,
            valor_corrigido=round(float(valor_corrigido), 2),
            correcao_monetaria=correcao_float,
            fator=fator_calc,
            indice=indice,
            data_valor_original=resultado.get("dataValorOriginal", ""),
            data_atualizacao=resultado.get("dataAtualizacao", ""),
            bruto=resultado,
        )


def _moeda_para_float(texto: str) -> float:
    """Converte 'R$ 1.572,60' -> 1572.60."""
    limpo = (
        str(texto)
        .replace("R$", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )
    return float(limpo or 0)
