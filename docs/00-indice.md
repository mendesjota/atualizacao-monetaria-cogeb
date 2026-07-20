# Índice da documentação

Abaixo todos os documentos da pasta `docs/`, organizados por tipo de leitor.

---

## Para usuários finais (não precisa saber programação)

| # | Documento | O que contém |
|---|-----------|-------------|
| 1 | [`08-manual-uso.md`](08-manual-uso.md) | Manual completo: como preparar o CSV, rodar o programa (duplo-clique), entender o Excel de saída. |
| 2 | [`09-clonar-github.md`](09-clonar-github.md) | Passo a passo para baixar o programa do GitHub, instalar Python e configurar tudo pela primeira vez. |
| 3 | [`10-sincronizar-vscode.md`](10-sincronizar-vscode.md) | Como atualizar o código local para ficar igual ao GitHub (VS Code + git pull). |
| 4 | [`06-modelo-entrada.md`](06-modelo-entrada.md) | Explica como preencher a planilha CSV: colunas, formatos de data, exemplos. |
| 5 | [`11-comandos-terminal.md`](11-comandos-terminal.md) | Todas as formas de executar o programa pelo terminal (PowerShell), com cada argumento explicado. |
| 6 | [`04-glossario.md`](04-glossario.md) | Significado dos termos técnicos (IPCA-E, teto, SEGURIDADE SOCIAL, etc.) em linguagem simples. |

> **Por onde começar:** Se é a primeira vez, leia `09-clonar-github.md` (instalação), depois `08-manual-uso.md` (uso diário).

---

## Para desenvolvedores / manutenção

| # | Documento | O que contém |
|---|-----------|-------------|
| 7 | [`01-plano.md`](01-plano.md) | Plano do projeto em 5 fases. Mostra o que foi feito e as decisões de cada etapa. |
| 8 | [`05-decisoes.md`](05-decisoes.md) | Registro de decisões técnicas (ADRs): por que escolhemos IPCA-E, por que mudamos de INPC, etc. |
| 9 | [`07-api-tcdf.md`](07-api-tcdf.md) | Contrato da API do SINDEC (TCDF): endpoints, payloads, respostas. |
| 10 | [`analise-seguridade.md`](analise-seguridade.md) | Como o Analisador.py extrai SEGURIDADE SOCIAL do .xls do SIGRH: estrutura do arquivo, tetos, uso programático. |
| 11 | [`02-investigacao-tcdf.md`](02-investigacao-tcdf.md) | Registro da investigação inicial da calculadora do TCDF: como descobrimos a API e a fórmula de correção. |
| 12 | [`03-captura-network.md`](archive/03-captura-network.md) | **(Histórico)** Guia de como capturar a aba Network do navegador — usado na Fase 1, mantido como referência. |

> **Por onde começar:** Leia `01-plano.md` para o panorama geral, depois `05-decisoes.md` para entender as escolhas técnicas.

---

## Resumo: qual arquivo ler em cada situação

| Situação | Documento |
|----------|-----------|
| "Nunca usei isso, quero rodar" | [`08-manual-uso.md`](08-manual-uso.md) |
| "Meu computador não tem Python" | [`09-clonar-github.md`](09-clonar-github.md) |
| "Esqueci como preenche o CSV" | [`06-modelo-entrada.md`](06-modelo-entrada.md) |
| "O que significa tal termo?" | [`04-glossario.md`](04-glossario.md) |
| "Quais comandos existem?" | [`11-comandos-terminal.md`](11-comandos-terminal.md) |
| "Meu código está desatualizado" | [`10-sincronizar-vscode.md`](10-sincronizar-vscode.md) |
| "Como a extração funciona por dentro?" | [`analise-seguridade.md`](analise-seguridade.md) |
| "Por que o programa faz assim?" | [`05-decisoes.md`](05-decisoes.md) |
