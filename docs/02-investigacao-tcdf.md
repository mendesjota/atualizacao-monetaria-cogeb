# Investigação — calculadora do TCDF (SINDEC)

Site: <https://www2.tc.df.gov.br/sindec-sistema-de-indices-e-indicadores-economicos-e-de-atualizacao-de-valores/>

---

## 1. O que é o SINDEC

Sistema de Índices e Indicadores Econômicos e de Atualização de Valores do
Tribunal de Contas do Distrito Federal. Permite atualizar (corrigir) um valor
de uma data para outra usando índices econômicos oficiais.

## 2. Perguntas que a Fase 1 precisa responder

| # | Pergunta | Resposta |
|---|----------|----------|
| 1 | O cálculo acontece no navegador (JS) ou no servidor (requisição)? | **Servidor** — API REST pública |
| 2 | Se no servidor: qual a URL do endpoint? | `https://api-sindec.tc.df.gov.br/api` |
| 3 | Método HTTP (GET/POST)? | POST para calcular, GET para séries históricas |
| 4 | Quais parâmetros são enviados? | `dataValorOriginal`, `valorOriginal`, `dataAtualizacao`, `descricao` (POST); nenhum (GET) |
| 5 | Formato da resposta (JSON, HTML, XML)? | **JSON** |
| 6 | Precisa de token/cookie/CSRF/sessão? | **Não** — API pública sem autenticação. Requer User-Agent de navegador (WAF) |
| 7 | Quais índices o site oferece? Qual a COGEB usa? | `POST /api/calcular` usa **INPC** (anual). `GET /api/ipcae` retorna **IPCA-E** (mensal). A **tabela detalhada de parcelas do site usa IPCA-E** (confirmado: Levi Batista, 8 parcelas, diferença R$ 0,00) |
| 8 | Existe endpoint só para baixar a **tabela de índices**? | Sim: `GET /api/ipcae` (IPCA-E mensal), `GET /api/itcdf` (INPC anual) |
| 9 | Como o site trata **pro-rata** (fração de mês)? | IPCA-E é composto mês a mês (sem pro-rata die — cada mês é um bloco fechado) |
| 10 | Há aplicação de **juros** além da correção? | **Não** — só correção monetária pura |

## 3. Fórmula de correção (confirmada)

```
fator = Π (1 + taxa_ipcae_mês / 100) - 1
       mês ∈ (competência, data_alvo]

valor_corrigido = valor_original × (1 + fator)
```

Para o caso "recorrente" (ex.: R$ 1.500/mês de jan a jul), cada parcela é
corrigida da sua própria competência até a data-alvo e depois somadas:

```
total = Σ ( parcela_mês_i × fator_i )
```

## 4. Endpoints descobertos

| Endpoint | Uso |
|----------|-----|
| `POST /api/calcular` | Correção INPC **anual** (não usado atualmente) |
| `GET /api/ipcae` | **IPCA-E mensal** — usado para correção por parcela |
| `GET /api/itcdf` | INPC anual (índice acumulado, não mensal) |
| `POST /api/calculo` | Salvar/recuperar cálculo (não usado) |

Detalhes completos em [07-api-tcdf.md](07-api-tcdf.md).

## 5. Validação com dados reais

**Levi Batista da Silva** (matrícula 00812188, órgão 652):
- 8 parcelas de Fev a Set/2025
- Data-alvo: 01/02/2026
- Valores: 5 × R$ 915,38 + 3 × R$ 995,01
- Total original: R$ 7.561,93
- **Total corrigido (IPCA-E): R$ 7.731,98** — bate exatamente com o site

## 6. Conclusão

- Abordagem adotada: **IPCA-E mensal composto** via `GET /api/ipcae`
- Registrado em [05-decisoes.md](05-decisoes.md) (ADR-008)
