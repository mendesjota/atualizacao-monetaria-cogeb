# Planilha de entrada (o que você preenche)

Você vai preencher um arquivo `.csv` (abre no Excel) com os dados dos
beneficiários. O programa lê esse arquivo e faz todo o resto.

---

## Onde fica

`dados/entrada/beneficiarios.csv`

> Se o arquivo não existir, copie `dados/entrada/_modelo_entrada.csv` e
> renomeie para `beneficiarios.csv`.

---

## Como preencher

Cada linha = um beneficiário. As colunas são separadas por `;` (ponto e vírgula).

| Coluna | O que escrever | Exemplo |
|--------|---------------|---------|
| `nome` | Nome completo em maiúsculas | LEVI BATISTA DA SILVA |
| `matricula` | Número da matrícula no SIGRH | 00812188 |
| `orgao` | Código do órgão (3 dígitos) | 652 |
| `valor_mensal` | Valor da parcela **ou 0** | 0 |
| `competencia_inicial` | Mês/ano da **primeira** parcela | 02/2025 |
| `competencia_final` | Mês/ano da **última** parcela | 09/2025 |
| `data_alvo` | Data para onde corrigir | 02/02/2026 |

### valor_mensal = 0

Quando o valor é `0`, o programa busca o valor real da **Ficha Financeira do
SIGRH** (código 40920 - SEGURIDADE SOCIAL). Use `0` sempre que quiser o valor
exato do sistema.

Se você já sabe o valor fixo, pode colocar o número (ex: `1500,00`) — nesse
caso o programa vai usar esse valor para todos os meses do período.

### Datas — formatos aceitos

| Formato | Exemplo | O que significa |
|---------|---------|----------------|
| `MM/AAAA` | `01/2024` | Janeiro de 2024 |
| `DD/MM/AAAA` | `15/01/2024` | 15 de janeiro de 2024 |
| `AAAA-MM` | `2024-01` | Janeiro de 2024 |
| Mês abreviado PT-BR | `jan/24` | Janeiro de 2024 |

Abreviaturas: jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez

---

## Exemplos

### Um beneficiário, período único

```
nome;matricula;orgao;valor_mensal;competencia_inicial;competencia_final;data_alvo
LEVI BATISTA DA SILVA;00812188;652;0;02/2025;09/2025;02/02/2026
```

### Vários beneficiários

```
nome;matricula;orgao;valor_mensal;competencia_inicial;competencia_final;data_alvo
OLGA ANDRADE ABRAHAO;17151538;990;0;08/2023;09/2025;06/01/2026
ANTONIO GOMES DA SILVA;16502711;990;0;05/2023;04/2025;06/01/2026
DIMAS GARCIA DE OLIVEIRA;0093383X;990;0;01/2023;01/2026;06/01/2026
```

### Mesma pessoa com períodos diferentes

```
ANTONIO GOMES DA SILVA;16502711;990;0;01/2024;06/2024;30/06/2026
ANTONIO GOMES DA SILVA;16502711;990;0;07/2024;12/2024;30/06/2026
```

### Valor fixo (sem buscar do SIGRH)

```
MARIA JOSE;123456;990;1500,00;01/2025;06/2025;30/06/2026
```

---

## ⚠️ Regras importantes

- **Salve como CSV UTF-8** — no Excel: "Arquivo" → "Salvar como" → "CSV UTF-8"
- **Separador `;`** — padrão do Excel brasileiro
- **Não pule linhas** — se uma linha estiver vazia, o programa para de ler
- **Não mude os nomes das colunas** — o programa procura por eles
