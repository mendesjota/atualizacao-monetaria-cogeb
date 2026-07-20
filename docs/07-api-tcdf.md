# Contrato da API do SINDEC (descoberto na Fase 1)

> Resultado da investigação de 2026-07-02. A calculadora é uma SPA Vue.js
> (`https://sindec.tc.df.gov.br/`) que conversa com uma **API REST pública**.

**⚠️ Atenção (ADR-008):** O `POST /api/calcular` usa **INPC anual** (mesmo
fator para todo mês de um ano). A tabela detalhada de parcelas do site usa
**IPCA-E mensal**. O código atual (Fase 3) usa `GET /api/ipcae` (IPCA-E
mensal) — veja seção 2 abaixo. O `POST /api/calcular` ficou como referência.

## Base URL

```
https://api-sindec.tc.df.gov.br/api
```

- **Sem autenticação** (sem token/login) nos endpoints testados.
- Stack do servidor: PHP/Symfony + FOSRestBundle.
- Requer `User-Agent` de navegador — sem ele, o POST fica pendurado (WAF).
  Com `User-Agent: Mozilla/5.0 ...` responde normalmente (~0,15s).

---

## Endpoints relevantes

### 1. `POST /calcular` — atualização de valor (usa INPC)

Calcula a correção monetária de **um** valor, da data de origem até a data-alvo.

**Payload (JSON):**
```json
{
  "descricao": "texto livre",
  "dataValorOriginal": "2024-01-01",   // ISO YYYY-MM-DD (obrigatório)
  "valorOriginal": 1500,                // número
  "dataAtualizacao": "2025-07-01",      // ISO YYYY-MM-DD (obrigatório)
  "dataJuros": "2024-06-01"             // opcional
}
```

> ⚠️ **Datas em ISO `YYYY-MM-DD`.** Se enviar `dd/mm/yyyy` a API responde 422
> "This value is not a valid date".

**Resposta (200):**
```json
{
  "sucesso": true,
  "resultado": {
    "correcaoMonetaria": "R$ 72,60",
    "multa": "R$ 0,00",
    "jurosPre2020": "R$ 0,00",
    "jurosPos2020": "R$ 0,00",
    "valorCorrigido": "R$ 1.572,60",
    "dataValorOriginal": "01/01/2024",
    "valorOriginal": "R$ 1.500,00",
    "dataAtualizacao": "01/07/2025",
    "memoriaCalculo": [
      { "texto": "Correção Monetária", "indice": "INPC",
        "valores": { "valorAntes": 1500, "valorDepois": 1572.5999999873932,
                     "correcaoMonetaria": 72.59999998739318,
                     "valorAtualizado": 1572.5999999873932 } }
    ]
  }
}
```

> 🔴 **ATENÇÃO — índice INPC:** este endpoint aplica **INPC** (conforme
> LC 435/2001), não IPCA-E. Ver questão em aberto abaixo.

#### Comportamento CONFIRMADO: correção é ANUAL (não mês a mês)

Testes na Fase 1 (valor R$ 1.500, alvo fixo 01/07/2025):

| Data de origem | Valor corrigido |
|----------------|-----------------|
| 01/01/2024 | R$ 1.572,60 |
| 01/04/2024 | R$ 1.572,60 |
| 01/07/2024 | R$ 1.572,60 |
| 01/11/2024 | R$ 1.572,60 |
| 01/12/2024 | R$ 1.572,60 |
| 01/01/2023 | R$ 1.633,15 |
| 01/01/2025 | R$ 1.500,00 (sem correção) |

**Conclusão:** para um mesmo alvo, o valor corrigido depende apenas do **ano**
da data de origem — todos os meses de um mesmo ano dão o mesmo resultado. É a
variação **anual** do INPC (LC 435/2001).

**⚠️ Histórico (Fase 2):** tentamos usar este endpoint para extrair taxas anuais
e aplicar pro-rata mensal, mas os fatores não batiam com o site (ex.: Fev/2025→
Fev/2026: pro-rata INPC dava ~0,0383, site mostra 0,045044). **Solução (ADR-008):**
substituímos pelo IPCA-E mensal composto via `GET /api/ipcae` — ver seção 2.

Outros endpoints de cálculo (mesmo padrão de payload):
- `POST /calcularEncargosMoratorios`
- `POST /calcular3013`

### 2. `GET /ipcae` — série histórica do IPCA-E (**endpoint principal do cálculo**)

Retorna a tabela mensal do IPCA-E (variação % de cada mês). É o endpoint
**usado atualmente** pelo código: a correção de cada parcela é feita compondo
as taxas mensais da competência até a data-alvo.

**Resposta:** `{ "historicoIPCAE": "<string JSON>" }` — ao dar parse:
```json
[ { "dataFormatada": "01/01/1992", "valor": 25.6 },
  { "dataFormatada": "01/06/2026", "valor": 0.41 } ]   // 414 registros
```
`valor` = variação percentual do mês. Fator do período =
Π (1 + valor_mês/100). Ex.: 8 parcelas do Levi Batista (Fev–Set/2025 →
Fev/2026) batem exatamente com o site (R$ 7.731,98 total).

A série é cacheada na instância do `SindecClient` (uma única chamada HTTP).

Endpoints-irmãos (mesmo formato, outros índices):
`GET /itcdf` (INPC — **anual**, não mensal), `GET /selic`, `GET /tr`,
`GET /metaSelic`, `GET /moeda?data=`.

### 3. `POST /calculo` e `GET /calculo/{hash}` — salvar/recuperar

`POST /calculo` persiste um conjunto de cálculos e devolve um `hash`
compartilhável; `GET /calculo/{hash}` recupera; `GET /calculo/{hash}/recalcular?dataAtualizacao=`
reatualiza. Úteis se quisermos gerar link/registro no site, mas **não são
necessários** para obter o valor corrigido.

---

## Gabarito de validação (real, do servidor)

| Campo | Valor |
|-------|-------|
| Valor original | R$ 1.500,00 |
| Data valor original | 01/01/2024 |
| Data atualização | 01/07/2025 |
| Índice | INPC |
| Correção monetária | **R$ 72,60** |
| **Valor corrigido** | **R$ 1.572,60** |

---

## INPC vs IPCA-E — ESCLARECIDO (revisado 2026-07-06)

O site do TCDF tem **dois modos de cálculo**:

1. **Calculadora de valor único** (`POST /api/calcular`) → usa **INPC anual**.
   Ex.: R$ 1.500 de Jan/2024 a Jul/2025 = R$ 1.572,60 (confirmado pela COGEB).
2. **Tabela detalhada de parcelas** (mesmo site, visualização expandida) →
   usa **IPCA-E mensal**. Ex.: Levi Batista, Fev/2025→Fev/2026 fator 0,045044
   = composto IPCA-E, não INPC.

**Decisão (ADR-008):** o código atual usa IPCA-E mensal (`GET /api/ipcae`),
porque é o único que reproduz exatamente os fatores que variam por competência
na saída COGEB. O `POST /api/calcular` (INPC) ficou como referência histórica.
