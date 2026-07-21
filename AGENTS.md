# AGENTS.md — Atualização Monetária COGEB

## Stack & setup

- Python 3.12+, plain `requirements.txt` (no pyproject.toml)
- Virtual env: `.venv\Scripts\python.exe`
- Setup: `.venv\Scripts\pip install -r requirements.txt`
- **Playwright**: needs `python -m playwright install firefox` after pip (browsers not in pip)
- Dependencies: `requests`, `openpyxl`, `playwright`

## How to run

- `python src\main.py` — default input `dados/entrada/beneficiarios.csv` → output `dados/saida/resultado_YYYY_MM_DD.xlsx`
- `python src\main.py --validar` — only test API connectivity
- `python src\main.py <input.csv> <output.xlsx>` — explicit paths
- `Atualizar valores.bat` — double-click launcher for end users (uses SAIDA_PADRAO)
- `Pipeline completo.bat` — double-click launcher for --completo pipeline
- `python src\Extrator.py` — interactive CLI (prompts for credentials)
- `python src\main.py --completo <input.csv> <output.xlsx>` — pipeline completo SIGRH + SEGURIDADE + correção
- `python src\main.py --completo --xls <ficha.xls> <input.csv> <output.xlsx>` — pipeline com ficha já baixada

## Tests

- `python -m pytest testes\ -v` — 36 unit tests, no network, no integration

## Validação contra gabarito ODS

Pipeline de validação (`--completo` vs ODS oficial TCDF):

1. `src/extrator_ods_gabarito.py` — lê ODS oficial, extrai 507 beneficiários (~10.886 parcelas) de 13 abas mensais (JAN_-_2026 a DEZ_-_2026). Gera `dados/entrada/beneficiarios_gabarito.csv` e `dados/validacao/referencia_ods.json`.
2. `src/comparar_resultados.py` — compara XLSX gerado vs referência ODS, tolerância R$ 0,02.
3. Rodar: `python src/main.py --completo dados/entrada/beneficiarios_validacao.csv dados/saida/resultado_validacao.xlsx`

**Status**: 4 beneficiários validados com **52/52 parcelas OK, 0 divergências**. Comparador usa lista por competência (suporta regular + 13º no mesmo mês).

## Architecture

```
src/main.py                  → entry point (validation + orchestration)
src/sindec_api.py            → HTTP client for SINDEC API (context manager, cache, browser UA)
src/calculo.py               → business logic (Beneficiario → parcelas → IPCA-E composition)
src/io_planilha.py           → CSV/XLSX read, Excel write with COGEB formatting
src/Extrator.py              → Playwright automation: SIGRH ficha financeira download (.xls)
src/Analisador.py            → Extrai valores 40920 SEGURIDADE SOCIAL do .xls + aplica teto
src/comparar_resultados.py   → Compara XLSX gerado vs referência ODS
src/extrator_ods_gabarito.py → Extrai beneficiários do ODS gabarito oficial
```

## Critical domain facts

- **Index = IPCA-E** (`GET /api/ipcae`), not INPC (`POST /api/calcular`). See ADR-008 in `docs/05-decisoes.md`.
- Correction formula: `fator = Π(1 + taxa_mês/100) - 1` from competence (exclusive) to target-date (inclusive).
- 13º salary (40923): emitido **sempre em dezembro** (competência 12), independentemente do mês de pagamento no SIGRH. Só emitido para anos em que dezembro está dentro do período de análise. Valor capado no TETO, sem rateio. 40923 encontrado mesmo se estiver em mês anterior ao início do período (busca no primeiro ano).
- API: requires browser `User-Agent` header, 0.2s pause between calls, no auth.
- IPCA-E series fetched once per run (cached in `SindecClient._cache_ipcae`).
- Console: `sys.stdout` / `sys.stderr` reconfigured to UTF-8 (Windows cp1252 fix in `main.py`).
- **Diferenca (50920)**: extraído como tipo `diferenca`, renderizado com descrição `DIFERENÇA DE SEGURIDADE SOCIAL`. Ordenação: regular → diferenca → decimo_terceiro, cronológico.
- **Excel rubricas**: 30920 usa `SUMIFS` com `"<>*13º SAL*"` (regular + diferença), 30923 usa `SUMIFS` com `"*13º SAL*"` (apenas 13º). Ambos condicionais pela coluna C (descrição).

## Input format

CSV with `;` separator, UTF-8 with BOM (Brazilian Excel default).
Columns: `nome;matricula;orgao;valor_mensal;competencia_inicial;competencia_final;data_alvo;observacao`.

Date formats: `MM/AAAA`, `DD/MM/AAAA`, `AAAA-MM`, or PT-BR abbreviated (`ago/23`, `set/25`).

## Validation rule

Always cross-check against `dados/validacao/` before concluding. Reference: Levi Batista (R$ 7.561,93 → R$ 7.731,98, difference R$ 0.00). For --completo, reference: JOAO RESENDE FILHO (mat 835498, orgão 652) — valores 2023 R$ 386~423 → corrigido R$ 18.769,81 (38 parcelas).

## Phase rule

`docs/01-plano.md` has 5 phases. All concluídas. Current: Fase 5 done.

## Pipeline completo

```
python src/main.py --completo <entrada.csv> <saida.xlsx>
python src/main.py --completo --xls <ficha.xls> <entrada.csv> <saida.xlsx>
```

### CSV input format (--completo)

`;` separator, UTF-8 with BOM.
Columns: `nome;matricula;orgao;valor_mensal;competencia_inicial;competencia_final;data_alvo`

Date formats: `MM/AAAA`, `DD/MM/AAAA`, `AAAA-MM`, or PT-BR abbreviated (`ago/23`, `set/25`).
`valor_mensal` can be `0` (value comes from Analisador).

### .env credentials

```env
matricula_sigrh=SUA_MATRICULA_AQUI
senha_sigrh=SUA_SENHA_AQUI
```

### Analisador.py (SEGURIDADE SOCIAL extraction)

- **Filtro por matrícula**: `parse_xls()` extrai a matrícula de cada seção da ficha HTML (.xls) e filtra apenas as tabelas do vínculo correspondente ao beneficiário. Isso evita pegar valores de outro vínculo da mesma pessoa que apareça primeiro no arquivo.
- Caps at TETO per year
- Extracts 40920 (regular) + 40923 (13th salary) + 50920 (diferença)
- 13º salário (40923): emitido com competência 12 (dezembro), independentemente do mês de pagamento no SIGRH. Só emitido se dezembro estiver dentro do período. Valor = min(raw, TETO), sem rateio. 40923 encontrado no primeiro ano mesmo se mês for anterior ao início.
- Output: list of dicts with competencia, valor_seg_social, teto_ano, valor_final

## PII

`dados/entrada/*.csv`, `dados/saida/*`, `dados/validacao/*` gitignored. Never commit real beneficiary names.

## No CI/CD, no ruff, no mypy, no typechecker

## Extrator.py (SIGRH automation)

File: `src/Extrator.py` — Playwright script for SIGRH ficha financeira download in **Excel** (HTML table .xls, abre no Excel).
`run(matr_login, senha, matr_empregado, comp_ini, comp_fim, codigo_empresa="990", pasta_destino="fichas financeiras/", headless=True)`
Empresas: 990, 992, 037, 556, 652 (vem da planilha de entrada).
Uses `playwright` + `python -m playwright install firefox`. Headless=False by default.
**Mecanismo**: clique no botão EXCEL → popup → SignalR SSE → `#fimdoprocesso` (state=visible) → `context.expect_event("download")` → salva o .xls. Fallback automático para PDF via `#btnPDF` se EXCEL falhar.
