# Registro de decisões (ADR simplificado)

Cada decisão importante fica registrada aqui, com data e motivo. Serve para
lembrar "por que fizemos assim" no futuro.

Formato: **Data — Decisão — Motivo — Status**

---

## ADR-001 — Estrutura inicial do projeto e documentação

- **Data:** 2026-07-02
- **Decisão:** Criar o projeto em fases (investigar → automatizar → formatar →
  interface), com documentação de suporte antes de escrever qualquer código.
- **Motivo:** O ponto de maior incerteza é *como* a calculadora do TCDF calcula.
  Codar antes de saber isso levaria a retrabalho.
- **Status:** ✅ Aceito.

---

## ADR-002 — Abordagem de cálculo (API vs. planilha local)

- **Data:** 2026-07-02 (investigação concluída; escolha final aguarda 1 confirmação)
- **Achado:** Existe **API REST pública** do SINDEC:
  `https://api-sindec.tc.df.gov.br/api`, sem token. Contrato completo em
  [07-api-tcdf.md](07-api-tcdf.md). Testada e funcionando (gabarito real obtido).
- **Opções agora concretas:**
  - **A)** `POST /calcular` → devolve o valor corrigido pronto. Usa **INPC**.
    Bate 100% com o site, é rápido (~0,15s) e simples.
  - **B)** `GET /ipcae` → baixa a série IPCA-E e replicamos o fator localmente
    (offline). Necessário se o cálculo tiver que ser em IPCA-E.
- **DECISÃO:** **Abordagem A** — usar `POST /calcular`. Confirmado pela COGEB
  em 2026-07-02: o valor que copiam hoje é R$ 1.572,60 (INPC), idêntico ao da
  API. É a opção mais simples e que bate 100% com o site.
- **Status:** ⬆️ **Substituído pelo ADR-008** (cálculo atual usa IPCA-E, não INPC).

---

## ADR-003 — Linguagem/stack

- **Data:** 2026-07-02
- **Decisão:** **Python 3.12** + `requests` (HTTP) + `openpyxl` (Excel).
  Dispensamos pandas para manter leve. Testes com `pytest`.
- **Motivo:** Ecossistema forte para Excel e HTTP; leve; roda bem no Windows.
- **Status:** ✅ Aceito.

---

## ADR-004 — Parâmetros do cálculo (confirmados pela COGEB)

- **Data:** 2026-07-02
- **Decisão (revisada em ADR-005):**
  - Índice oficial: ~~IPCA-E~~ → **INPC** (ver ADR-005; era imprecisão).
  - **Sem juros de mora** — apenas correção monetária pura (mantido).
  - Entrada de dados via **planilha Excel/CSV** (a equipe preenche, o script consome).
- **Motivo:** Confirmado pelo usuário.
- **Status:** ✅ Aceito (sem juros mantido; índice posteriormente substituído pelo ADR-008).

---

## ADR-005 — Índice real do processo: INPC (RESOLVIDO)

- **Data:** 2026-07-02
- **Contexto:** COGEB disse usar IPCA-E, mas o `POST /calcular` aplica **INPC**.
- **Decisão:** ✅ O processo usa **INPC** (o calculador oficial). Confirmado: o
  valor conferido no site (R$ 1.572,60) é o do INPC. "IPCA-E" foi imprecisão de
  nomenclatura. A tabela IPCA-E (`GET /ipcae`) fica guardada como referência,
  mas não é usada no cálculo.
- **Status:** ⬆️ **Substituído pelo ADR-008** (cálculo atual usa IPCA-E mensal).

---

## ADR-006 — Regra de recorrência mensal

- **Data:** 2026-07-02 (revisado 2026-07-06)
- **Decisão:** Para valor recorrente (ex.: R$ 1.500/mês de jan a jul), gerar
  **uma parcela por mês**, corrigir cada uma da sua competência até a data-alvo
  e **somar** os valores corrigidos.
- **Revisão (2026-07-06):** A API retorna o **mesmo valor** para todo mês de
  um mesmo ano (correção anual do INPC). Para obter fatores que **variam por
  competência** (como no modelo da COGEB), o código agora:
  1. Extrai as **taxas anuais** do INPC via API (1 chamada por ano)
  2. Aplica **pro-rata mensal**: cada parcela recebe a fração proporcional
     da taxa anual (ex.: jan/24 → 12/12 da taxa 2024, jul/24 → 6/12)
  3. Calcula `fator = correção / valor_original` por parcela
- **Cache:** apenas as taxas anuais são cacheadas (chave = ano).
- **Motivo:** Reproduz a variação mensal observada no modelo de saída da COGEB.
- **Status:** ⬆️ **Substituído pelo ADR-008** (IPCA-E mensal composto).

---

## ADR-007 — Pro-rata mensal (substitui cache por ano)

- **Data:** 2026-07-06
- **Achado:** O `POST /calcular` retorna o mesmo valor para todo mês de um
  mesmo ano (correção anual do INPC). A COGEB precisa de fatores que variem
  por competência mensal.
- **Decisão:** Deixamos de chamar a API por parcela. Em vez disso:
  1. Extraímos as **taxas anuais** via `SindecClient.obter_taxas_anuais()`
     (1 chamada por ano, ex.: `API(R$ 1000, 01/01/2024, 01/01/2025)`)
  2. A correção de cada parcela é calculada **localmente** com pro-rata
     mensal das taxas anuais
  3. Anos sem dado disponível (futuros) recebem taxa 0
- **Cache:** as taxas anuais são cacheadas normalmente pelo `SindecClient`
- **Motivo:** Gera fatores que variam por competência, como esperado pela COGEB.
- **Status:** ⬆️ **Substituído pelo ADR-008** (IPCA-E mensal composto).

---

## ADR-008 — IPCA-E mensal substitui INPC anual + pro-rata

- **Data:** 2026-07-06
- **Achado:** O endpoint `POST /api/calcular` retorna correção **INPC anual** (mesmo fator para todo mês do ano). A calculadora do site TCDF, porém, mostra fatores **diferentes por mês** na tabela detalhada de parcelas. Investigação revelou que os fatores do site (ex.: Fev/2025→Fev/2026 = 0,045044) **batem exatamente** com a composição mensal do **IPCA-E** — e não com pro-rata do INPC anual (que daria ~0,0383 para o mesmo período).
- **Validação:** Testado com 8 parcelas reais do beneficiário **Levi Batista da Silva** (matrícula 00812188, órgão 652): R$ 7.561,93 → R$ 7.731,98. IPCA-E composto mês a mês reproduz **todos** os fatores e valores com diferença R$ 0,00.
- **Decisão:** Substituir o cálculo por pro-rata de taxas INPC anuais pelo **IPCA-E mensal composto**:
  1. Buscar a série IPCA-E uma única vez via `GET /api/ipcae` (cacheada na instância)
  2. Para cada parcela, compor as taxas mensais da competência (exclusive) até a data-alvo (inclusive): `fator = Π(1 + taxa_mês/100) - 1`
  3. O campo `indice` muda de `"INPC"` para `"IPCA-E"`
  4. O método `SindecClient.obter_taxas_mensais_ipcae()` substitui `SindecClient.obter_taxas_anuais()`
- **Motivo:** Única forma de reproduzir exatamente os fatores do site do TCDF.
- **Impacto:** O gabarito anterior (R$ 1.500, Jan/2024→Jul/2025 = R$ 1.572,60) era INPC e **não** se aplica mais. A validação em `main.py` agora apenas verifica se a série IPCA-E está disponível.
- **Status:** ✅ Aceito (decisão vigente — cálculo com IPCA-E mensal).

---

## Resumo da linha do tempo

```
ADR-001 (02/jul) → Estrutura do projeto em fases
ADR-002 (02/jul) → Escolha do POST /calcular (INPC)  ⬆️ substituído
ADR-003 (02/jul) → Stack: Python + requests + openpyxl
ADR-004 (02/jul) → Parâmetros: sem juros, entrada CSV
ADR-005 (02/jul) → Confirmação: índice INPC  ⬆️ substituído
ADR-006 (02/jul) → Regra de recorrência mensal  ⬆️ substituído
ADR-007 (06/jul) → Pro-rata mensal das taxas INPC  ⬆️ substituído
ADR-008 (06/jul) → ✅ **IPCA-E mensal composto** (decisão vigente)
```
