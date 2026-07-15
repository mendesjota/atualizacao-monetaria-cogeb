# Modelo de entrada

Arquivo de exemplo: [`dados/entrada/_modelo_entrada.csv`](../dados/entrada/_modelo_entrada.csv)
(separador `;`, padrão brasileiro do Excel).

## Colunas

| Coluna | Significado | Exemplo |
|--------|-------------|---------|
| `nome` | Nome do beneficiário | LEVI BATISTA DA SILVA |
| `matricula` | Matrícula do beneficiário | 00812188 |
| `orgao` | Órgão | 652 |
| `valor_mensal` | Valor de cada parcela (R$) | 915.38 |
| `competencia_inicial` | Mês/ano da primeira parcela | 02/2025 |
| `competencia_final` | Mês/ano da última parcela | 09/2025 |
| `data_alvo` | Data para a qual trazer o valor (dd/mm/aa ou mm/aaaa) | 02/02/2026 |
| `observacao` | Livre (opcional) | devolucao seguridade |

## Regras de interpretação

- **Parcela recorrente:** se `competencia_inicial` ≠ `competencia_final`, o
  sistema gera uma parcela `valor_mensal` para **cada mês** do intervalo
  (inclusive as pontas) e corrige cada uma até `data_alvo`.
  - Ex.: 02/2025 a 06/2025 = 5 parcelas de R$ 915,38.
- **Parcela única:** se as duas competências forem iguais, é 1 parcela só.
- **Valores diferentes no mesmo beneficiário:** crie uma linha para cada
  valor/faixa (ex.: Levi tem 2 linhas: Fev-Jun/2025 a R$ 915,38 e Jul-Set/2025
  a R$ 995,01).
- O **total corrigido** do beneficiário é a soma de todas as parcelas de todas
  as suas linhas.

## Índice

**IPCA-E** (série mensal). A ferramenta baixa automaticamente do site do TCDF
via `GET /api/ipcae`. Não há coluna de índice na planilha.
