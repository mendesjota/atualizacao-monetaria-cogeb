# Análise de Seguridade Social — 40920

## Objetivo

Extrair os valores mensais de **SEGURIDADE SOCIAL** (código 40920) da Ficha
Financeira Individual baixada pelo SIGRH, aplicar o teto máximo de contribuição
de cada ano, e gerar uma matriz mês a mês para alimentar a API de correção
monetária.

## Estrutura da Ficha (.xls)

O arquivo .xls gerado pelo SIGRH é na verdade um HTML table com extensão .xls.
Cada ano do período é composto por **3 tabelas consecutivas**:

| Tabela | Conteúdo | Exemplo |
|--------|----------|---------|
| Header | Cabeçalho com identificação do ano | `COMPETÊNCIA - 2023` |
| Data | Linhas com rubricas mensais (14 colunas) | `40920 SEGURIDADE SOCIAL` |
| Footer | Rodapé (emitido em...) | — |

Cada rubrica na tabela Data possui **14 células `<td>`**:

```
td[0]  = código + descrição (ex: "40920 SEGURIDADE SOCIAL")
td[1]  = Janeiro
td[2]  = Fevereiro
...
td[12] = Dezembro
td[13] = Total anual (soma dos 12 meses)
```

Alguns empregados possuem **múltiplos vínculos** no mesmo período, resultando em
duas ocorrências de 40920 por ano. O `Analisador.py` usa **a primeira ocorrência**
de cada ano (primeiro vínculo).

## Teto máximo (teto de contribuição)

Os valores de SEGURIDADE SOCIAL são limitados ao teto anual do respectivo ano:

| Ano | Teto (R\$) |
|-----|-----------|
| 2020 | 671,09 |
| 2021 | 1.487,39 |
| 2022 | 1.638,48 |
| 2023 | 1.733,65 |
| 2024 | 1.791,18 |
| 2025 | 1.872,37 |
| 2026 | 1.940,58 |

Regra: `valor_final = min(valor_40920, teto_ano)`

## Uso

### Linha de comando

```powershell
.venv\Scripts\python src/Analisador.py <caminho.xls> <data_inicio> <data_fim>
.venv\Scripts\python src/Analisador.py <caminho.xls> --csv dados/entrada/beneficiarios.csv
```

Datas no formato `MM/AAAA`, `MM-AAAA`, `ago/23` (mês abreviado PT-BR + 2 dígitos ano).

### Exemplo

```powershell
.venv\Scripts\python src/Analisador.py "fichas financeiras/FICHA-FIN-05320908-990-2023-2025-xxxx.xls" 08/2023 09/2025
```

Saída (CSV):

```csv
competencia,valor_seg_social,teto_ano,valor_final
2023-08,3495.00,1733.65,1733.65
2023-09,3357.36,1733.65,1733.65
...
```

### Programática

```python
from src.Analisador import analisar

resultado = analisar("caminho.xls", "08/2023", "09/2025")
for row in resultado:
    print(row["competencia"], row["valor_final"])
```

## Integração com Extrator.py

Para usar o pipeline completo (baixar → extrair → corrigir → Excel), execute:

```powershell
.venv\Scripts\python src/main.py --completo dados/entrada/beneficiarios.csv saida.xlsx
```

Ou com uma ficha já baixada:

```powershell
.venv\Scripts\python src/main.py --completo --xls ficha.xls dados/entrada/beneficiarios.csv saida.xlsx
```

## Validação

Para a empregada **OLGA ANDRADE ABRAHAO** (17151538), o pipeline completo
produz os seguintes valores mensais (já com teto aplicado):

| Período      | Valor original (cap) | Valor corrigido |
|-------------|---------------------|-----------------|
| ago/2023    | R$ 1.733,65         | R$ 1.925,25     |
| set/2023    | R$ 1.733,65         | R$ 1.919,87     |
| ...         | ...                 | ...             |
| 13º 2023    | R$ 1.350,02         | R$ 1.481,81     |
| 13º 2024    | R$ 1.791,18         | R$ 1.876,54     |

Total: **R$ 53.173,00**.
