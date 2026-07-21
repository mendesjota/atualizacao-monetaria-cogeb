"""
Validação completa do pipeline --completo contra gabarito ODS.
Processa em lotes com checkpoint para retomada.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from io_planilha import ler_entrada, escrever_saida
from sindec_api import SindecClient
from Analisador import analisar
from main import (
    validar_api,
    _obter_credenciais_sigrh,
    _baixar_ficha,
    processar_beneficiario_com_analise,
)
from calculo import ResumoBeneficiario

CHECKPOINT_FILE = RAIZ / "dados" / "validacao" / "checkpoint_validacao.json"
LOTE_SIZE = 25


def _carregar_checkpoint() -> list[dict]:
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def _salvar_checkpoint(dados: list[dict]) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CHECKPOINT_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    tmp.replace(CHECKPOINT_FILE)


def _resumo_para_dict(r: ResumoBeneficiario) -> dict:
    return {
        "nome": r.nome,
        "matricula": r.matricula,
        "orgao": r.orgao,
        "qtd_parcelas": r.qtd_parcelas,
        "total_corrigido": r.total_corrigido,
    }


def main():
    entrada = RAIZ / "dados" / "entrada" / "beneficiarios_gabarito.csv"
    saida = RAIZ / "dados" / "saida" / "resultado_validacao.xlsx"

    if not entrada.exists():
        print(f"✖ Entrada não encontrada: {entrada}")
        return 1

    login, senha = _obter_credenciais_sigrh()

    with SindecClient() as client:
        if not validar_api(client):
            print("✖ API indisponível.")
            return 1

        print(f"→ Lendo entrada: {entrada}")
        beneficiarios = ler_entrada(entrada)
        print(f"  {len(beneficiarios)} beneficiário(s).")

        checkpoint = _carregar_checkpoint()
        processados_ids = {r["matricula"] + "|" + str(r["orgao"]) for r in checkpoint}
        resumos_dicts = list(checkpoint)

        pendentes = [
            b for b in beneficiarios
            if b.matricula + "|" + str(b.orgao) not in processados_ids
        ]

        if checkpoint:
            print(f"  Checkpoint encontrado: {len(checkpoint)} já processados.")
            print(f"  Restam: {len(pendentes)}")

        if not pendentes:
            print("✔ Todos já processados. Gerando saída final...")
        else:
            inicio = time.time()
            for i, ben in enumerate(pendentes, start=1):
                seq = len(processados_ids) + i
                total = len(beneficiarios)
                decorrido = time.time() - inicio
                ritmo = decorrido / i if i > 0 else 0
                restante = ritmo * (len(pendentes) - i)
                print(
                    f"\n[{seq}/{total}] {ben.nome} — mat {ben.matricula} "
                    f"(~{restante/60:.0f}min restantes)"
                )

                data_ini = f"{ben.competencia_inicial.month:02d}/{ben.competencia_inicial.year}"
                data_fim = f"{ben.competencia_final.month:02d}/{ben.competencia_final.year}"

                ficha_path, erro = _baixar_ficha(
                    login, senha, ben, RAIZ / "fichas financeiras"
                )
                if erro or not ficha_path:
                    print(f"  ✖ Falha no Extrator: {erro}")
                    continue

                print(f"  Analisando ({data_ini} a {data_fim})...")
                try:
                    analise = analisar(ficha_path, data_ini, data_fim, ben.matricula)
                except Exception as e:
                    print(f"  ✖ Erro no Analisador: {e}")
                    continue
                print(f"  {len(analise)} parcelas.")

                print(f"  Corrigindo com IPCA-E...")
                try:
                    resumo = processar_beneficiario_com_analise(ben, analise, client)
                except Exception as e:
                    print(f"  ✖ Erro na correção: {e}")
                    continue

                resumos_dicts.append(_resumo_para_dict(resumo))

                if i % LOTE_SIZE == 0:
                    _salvar_checkpoint(resumos_dicts)
                    print(f"  ✔ Checkpoint salvo ({len(resumos_dicts)} processados)")

            _salvar_checkpoint(resumos_dicts)
            print(f"\n✔ Processados: {len(resumos_dicts)} beneficiários.")

        # Gerar saída final
        from calculo import ResumoBeneficiario

        resumos = []
        for r in resumos_dicts:
            resumos.append(
                ResumoBeneficiario(
                    nome=r["nome"],
                    matricula=r["matricula"],
                    orgao=r["orgao"],
                    qtd_parcelas=r["qtd_parcelas"],
                    total_corrigido=r["total_corrigido"],
                )
            )

        caminho = escrever_saida(resumos, saida)
        total_parcelas = sum(r.qtd_parcelas for r in resumos)
        total_geral = sum(r.total_corrigido for r in resumos)
        print(
            f"\n✔ Finalizado. {len(resumos)} beneficiário(s), "
            f"{total_parcelas} parcela(s), "
            f"total corrigido R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        print(f"✔ Saída: {caminho}")

        # Comparar
        from comparar_resultados import comparar

        sys.argv = ["comparar_resultados.py", str(caminho)]
        comparar()

    return 0


if __name__ == "__main__":
    sys.exit(main())
