# AGENTS.md — Atualização Monetária COGEB

## Stack & setup

- Python 3.12+, plain `requirements.txt` (no pyproject.toml)
- Virtual env: `.venv\Scripts\python.exe`
- Setup: `.venv\Scripts\pip install -r requirements.txt`
- **Playwright**: needs `python -m playwright install firefox` after pip (browsers not in pip)
- Dependencies: `requests`, `openpyxl`, `playwright`

## How to run

- `python src\main.py` — default input `dados/entrada/beneficiarios.csv` → output `dados/saida/resultado.xlsx`
- `python src\main.py --validar` — only test API connectivity
- `python src\main.py <input.csv> <output.xlsx>` — explicit paths
- `Atualizar valores.bat` — double-click launcher for end users
- `python src\Extrator.py` — interactive CLI (prompts for credentials)
- `python src\main.py --completo <input.csv> <output.xlsx>` — pipeline completo SIGRH + SEGURIDADE + correção
- `python src\main.py --completo --xls <ficha.xls> <input.csv> <output.xlsx>` — pipeline com ficha já baixada

## Tests

- `python -m pytest testes\ -v` — 19 unit tests, no network, no integration

## Architecture

```
src/main.py          → entry point (validation + orchestration)
src/sindec_api.py    → HTTP client for SINDEC API (context manager, cache, browser UA)
src/calculo.py       → business logic (Beneficiario → parcelas → IPCA-E composition)
src/io_planilha.py   → CSV/XLSX read, Excel write with COGEB formatting
src/Extrator.py      → Playwright automation: SIGRH ficha financeira download (.xls)
src/Analisador.py    → Extrai valores 40920 SEGURIDADE SOCIAL do .xls + aplica teto
```

## Critical domain facts

- **Index = IPCA-E** (`GET /api/ipcae`), not INPC (`POST /api/calcular`). See ADR-008 in `docs/05-decisoes.md`.
- Correction formula: `fator = Π(1 + taxa_mês/100) - 1` from competence (exclusive) to target-date (inclusive).
- 13º salary auto-generated per year (1 per year with parcels, interleaved after Dec).
- API: requires browser `User-Agent` header, 0.2s pause between calls, no auth.
- IPCA-E series fetched once per run (cached in `SindecClient._cache_ipcae`).
- Console: `sys.stdout` / `sys.stderr` reconfigured to UTF-8 (Windows cp1252 fix in `main.py`).

## Input format

CSV with `;` separator, UTF-8 with BOM (Brazilian Excel default).
Columns: `nome;matricula;orgao;valor_mensal;competencia_inicial;competencia_final;data_alvo;observacao`.

Date formats: `MM/AAAA`, `DD/MM/AAAA`, `AAAA-MM`, or PT-BR abbreviated (`ago/23`, `set/25`).

## Validation rule

Always cross-check against `dados/validacao/` before concluding. Reference: Levi Batista (R$ 7.561,93 → R$ 7.731,98, difference R$ 0.00).

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
matricula_sigrh=2874946
senha_sigrh=070790
```

### Analisador.py (SEGURIDADE SOCIAL extraction)

- Uses **last** occurrence per year (second vínculo, higher values)
- Caps at TETO per year
- Extracts 40920 (regular) + 40923 (13th salary)
- Output: list of dicts with competencia, valor_seg_social, teto_ano, valor_final

## PII

`dados/entrada/*.csv`, `dados/saida/*`, `dados/validacao/*` gitignored. Never commit real beneficiary names.

## No CI/CD, no ruff, no mypy, no typechecker

## Extrator.py (SIGRH automation)

File: `src/Extrator.py` — Playwright script for SIGRH ficha financeira download in **Excel** (HTML table .xls, abre no Excel).
`run(matr_login, senha, matr_empregado, comp_ini, comp_fim, codigo_empresa="990", pasta_destino="fichas financeiras/", headless=False)`
Empresas: 990, 992, 037, 556, 652 (vem da planilha de entrada).
Uses `playwright` + `python -m playwright install firefox`. Headless=False by default.
**Mecanismo**: clique no botão EXCEL → popup → SignalR SSE → `#fimdoprocesso` (state=visible) → `context.expect_event("download")` → salva o .xls. Fallback automático para PDF via `#btnPDF` se EXCEL falhar.
