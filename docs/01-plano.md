# Plano do projeto — em fases

Este é o documento "norte". Cada fase só avança após aprovação.

---

## Fase 1 — Investigação ✅ CONCLUÍDA

**Meta:** entender como a calculadora do TCDF calcula, por baixo dos panos.

- [x] API REST pública identificada: `https://api-sindec.tc.df.gov.br/api`
- [x] Dois endpoints relevantes:
  - `POST /api/calcular` — **INPC anual** (mesmo fator para todo mês de um ano)
  - `GET /api/ipcae` — **IPCA-E mensal** (série com variação % de cada mês)
- [x] A tabela detalhada de parcelas do site usa **IPCA-E mensal composto**
- [x] Decisão documentada em [05-decisoes.md](05-decisoes.md) (ADR-008)

---

## Fase 2 — Automação do cálculo ✅ CONCLUÍDA (revisada)

**Meta:** eliminar a digitação mês a mês.

- [x] Implementar cálculo com **IPCA-E mensal composto**:
  - `GET /api/ipcae` → série mensal cacheada
  - `fator = Π(1 + taxa_mês/100) - 1` da competência até a data-alvo
- [x] Validado contra 8 parcelas reais do Levi Batista (R$ 7.561,93 → R$ 7.731,98) — **diferença R$ 0,00**
- [x] Tratar "valor recorrente por período" (gera N parcelas e soma)
- [x] Testes unitários (19) em `testes/`.
- [x] Cache: série IPCA-E é baixada uma única vez por execução

---

## Fase 3 — Saída no formato COGEB ✅ CONCLUÍDA

**Meta:** entregar já no formato do modelo do projeto, não no formato bruto do site.

- [x] Formato COGEB: blocos por beneficiário (NOME/MATRÍCULA/ÓRGÃO → tabela → Total → RUBRICA), tudo em aba "Relatório".
- [x] Formatação: cabeçalho azul marinho com texto branco, zebra nas linhas de dados, bordas finas, linha Total com borda dupla.
- [x] Espaçamento de 3 linhas entre blocos.
- [x] Coluna H (espaçador) e coluna "Data do Requerimento" na RUBRICA.

---

## Fase 4 — Interface simples de uso ✅ CONCLUÍDA

**Meta:** a equipe usa sem depender de ninguém técnico.

- [x] Forma de uso: planilha de entrada + linha de comando.
- [x] Manual da equipe em [08-manual-uso.md](08-manual-uso.md).

---

## Fase 5 — Pipeline SIGRH → SEGURIDADE → Correção ✅ CONCLUÍDA

**Meta:** integrar download da ficha financeira (Extrator), extração de
SEGURIDADE SOCIAL (Analisador), correção IPCA-E e saída Excel em um único
comando.

- [x] `Analisador.py` — extrai 40920 SEGURIDADE SOCIAL + 40923 (13º) do .xls do SIGRH
- [x] Aplica teto máximo de contribuição por ano (cap)
- [x] Usa **última ocorrência** de cada código por ano (segundo vínculo)
- [x] `parse_competencia` aceita mês abreviado PT-BR (`ago/23`, `set/25`)
- [x] `processar_beneficiario_com_analise()` em `calculo.py` — cria parcelas com valores reais
- [x] `main.py --completo` — pipeline completo em um comando
- [x] `main.py --xls` — pula download, usa ficha já baixada
- [x] Lê credenciais SIGRH do `.env` (matricula_sigrh, senha_sigrh)
- [x] Validado contra OLGA ANDRADE ABRAHAO — **R$ 0,00 de diferença** (R$ 53.173,00)
- [x] 13º salário extraído do código 40923 e corrigido separadamente
- [x] Testes unitários (19) continuam passando

---

## Requisitos e restrições (valem para todas as fases)

- Ambiente: **Windows, PowerShell**.
- **Validar SEMPRE** os resultados contra cálculos reais do site antes de considerar pronto (risco de divergência de arredondamento/pro-rata).
- Uso **legítimo e institucional** (COGEB); respeitar o site (sem volume abusivo).
- Priorizar solução que a **equipe consiga operar sozinha**.
