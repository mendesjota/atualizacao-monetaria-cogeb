# Comandos do terminal — modos de executar

Todas as formas de rodar o programa, explicando cada parte.

---

## Índice

1. [Antes de rodar qualquer comando](#1-antes-de-rodar-qualquer-comando)
2. [Pipeline completo (SIGRH + SEGURIDADE + correção)](#2-pipeline-completo)
3. [Somente correção (SEM SIGRH)](#3-somente-correção-sem-sigrh)
4. [Apenas validar API](#4-apenas-validar-api)
5. [Baixar ficha manualmente (Extrator)](#5-baixar-ficha-manualmente-extrator)
6. [Extrair SEGURIDADE de uma ficha (Analisador)](#6-extrair-seguridade-de-uma-ficha-analisador)
7. [Rodar os testes](#7-rodar-os-testes)
8. [Bat files (duplo-clique)](#8-bat-files-duplo-clique)

---

## 1. Antes de rodar qualquer comando

### Abrir o terminal na pasta certa

No VS Code: **Terminal → New Terminal** (ou `Ctrl + '`).

No Explorador de Arquivos: clique na barra de endereço, digite `powershell`, Enter.

### Ativar o ambiente virtual

Sempre usar `.venv\Scripts\python` em vez de `python` puro:

```powershell
.venv\Scripts\python src/main.py --validar
```

> Se der `python não encontrado`, você pulou a instalação. Veja `docs/09-clonar-github.md`.

---

## 2. Pipeline completo

### Comando principal

```powershell
.venv\Scripts\python src/main.py --completo dados/entrada/beneficiarios.csv dados/saida/resultado.xlsx
```

| Parte | O que significa |
|-------|----------------|
| `.venv\Scripts\python` | Usa o Python do ambiente virtual (com as bibliotecas instaladas) |
| `src/main.py` | Arquivo principal do programa |
| `--completo` | Ativa o pipeline completo: baixar ficha → extrair SEGURIDADE → corrigir → Excel |
| `dados/entrada/beneficiarios.csv` | **Caminho da planilha de entrada** (relativo à raiz do projeto) |
| `dados/saida/resultado.xlsx` | **Caminho onde o Excel de saída será salvo** (relativo à raiz) |

### Por que o caminho tem que ser `dados/entrada/beneficiarios.csv`?

O programa lê o arquivo a partir da **pasta raiz do projeto**. O caminho relativo funciona porque você está executando o PowerShell **dentro da pasta do projeto**.

- Se o arquivo estiver em outro lugar, você precisa passar o caminho completo:
  ```powershell
  .venv\Scripts\python src/main.py --completo C:\Users\Maria\Desktop\entrada.csv saida.xlsx
  ```

- Se você omitir o caminho de saída, o programa usa o nome padrão:
  ```powershell
  .venv\Scripts\python src/main.py --completo dados/entrada/beneficiarios.csv
  # Saída: dados/saida/resultado_2026_07_20.xlsx (com a data de hoje)
  ```

- Se você omitir os dois, ele usa os valores padrão:
  ```powershell
  .venv\Scripts\python src/main.py --completo
  # Entrada: dados/entrada/beneficiarios.csv
  # Saída:   dados/saida/resultado_2026_07_20.xlsx
  ```

### Com --xls (pular download do SIGRH)

Se a ficha já foi baixada antes (ou você baixou manualmente):

```powershell
.venv\Scripts\python src/main.py --completo --xls "fichas financeiras/FICHA-FIN-123456.xls" dados/entrada/beneficiarios.csv dados/saida/resultado.xlsx
```

| Parte | O que significa |
|-------|----------------|
| `--xls "caminho/da/ficha.xls"` | Usa uma ficha já existente em vez de baixar do SIGRH |

> O `--xls` vai antes do caminho de entrada e saída.

---

## 3. Somente correção (SEM SIGRH)

Usa quando você já tem os valores manuais (preenche `valor_mensal` no CSV).

```powershell
.venv\Scripts\python src/main.py
```

Lê `dados/entrada/beneficiarios.csv` e grava `dados/saida/resultado_AAAA_MM_DD.xlsx`.

```powershell
.venv\Scripts\python src/main.py dados/entrada/entrada.csv dados/saida/saida.xlsx
```

Com caminhos explícitos — útil quando o arquivo não é o `beneficiarios.csv` padrão.

```powershell
.venv\Scripts\python src/main.py dados/entrada/entrada.csv
```

Omite a saída — usa o nome padrão com a data.

---

## 4. Apenas validar API

Testa se a API do SINDEC (IPCA-E) está respondendo. Não gera Excel.

```powershell
.venv\Scripts\python src/main.py --validar
```

Saída esperada:

```
→ Verificando conexão com a API do SINDEC (IPCA-E)...
  Série IPCA-E carregada: 414 meses (01/1992 a 06/2026)
```

Use isso para diagnosticar problemas de internet ou se o site do TCDF está fora do ar.

---

## 5. Baixar ficha manualmente (Extrator)

Baixa a Ficha Financeira do SIGRH **sem fazer correção**.

```powershell
.venv\Scripts\python src/Extrator.py
```

O programa pergunta **interativamente**:

| Pergunta | O que digitar |
|----------|---------------|
| Matrícula de Login | Sua matrícula do SIGRH |
| Senha de Login | Sua senha do SIGRH |
| Matrícula do Empregado | Matrícula do beneficiário |
| Código da Empresa | 990, 992, 037, 556 ou 652 |
| Competência Inicial | Ano inicial (ex: 2023) |
| Competência Final | Ano final (ex: 2026) |

O arquivo baixado vai para a pasta `fichas financeiras/`.

> Útil quando você quer baixar **uma ficha específica** sem rodar o pipeline inteiro, ou quando o SIGRH está lento e você quer tentar de novo depois.

---

## 6. Extrair SEGURIDADE de uma ficha (Analisador)

Extrai os valores de SEGURIDADE SOCIAL de uma ficha já baixada.

```powershell
.venv\Scripts\python src/Analisador.py "fichas financeiras/FICHA-FIN-123456.xls" 08/2023 09/2025
```

| Argumento | Exemplo |
|-----------|---------|
| Caminho do .xls | `fichas financeiras/FICHA-FIN-123456.xls` |
| Data início | `08/2023` (agosto de 2023) |
| Data fim | `09/2025` (setembro de 2025) |

Ou extraindo o período direto do CSV de entrada:

```powershell
.venv\Scripts\python src/Analisador.py "fichas financeiras/FICHA-FIN-123456.xls" --csv dados/entrada/beneficiarios.csv
```

A saída aparece no terminal como CSV:

```
competencia;valor_seg_social;teto_ano;valor_final
2023-08;3495.00;1733.65;1733.65
2023-09;3357.36;1733.65;1733.65
```

---

## 7. Rodar os testes

```powershell
.venv\Scripts\python -m pytest testes\ -v
```

Saída esperada:

```
testes\test_unit.py ............                        [100%]
19 passed in 0.32s
```

Os testes são **unitários** (sem internet, sem API). Servem para verificar se as regras de cálculo (datas, correção IPCA-E, parsing) continuam funcionando depois de alterações.

---

## 8. Bat files (duplo-clique)

Para quem **não quer digitar comandos** no terminal.

| Arquivo | O que faz |
|---------|-----------|
| `Pipeline completo.bat` | Pipeline completo: baixa SIGRH → extrai → corrige → Excel |
| `Atualizar valores.bat` | Só corrige (SEM SIGRH). Útil quando você já tem os valores manuais |

Basta dar dois cliques no arquivo. Uma janela preta abre, o programa roda, e no final mostra onde está o Excel.

### Diferença entre os dois

| Situação | Qual usar |
|----------|-----------|
| `valor_mensal = 0` no CSV (buscar do SIGRH) | `Pipeline completo.bat` |
| `valor_mensal = 1500,00` (valor fixo) | Qualquer um dos dois |
| SIGRH fora do ar, mas tenho a ficha | `Pipeline completo.bat --xls "ficha.xls"` |

---

## Resumo rápido

| O que você quer | Comando |
|-----------------|---------|
| Pipeline completo (SIGRH → Excel) | `.venv\Scripts\python src/main.py --completo dados/entrada/beneficiarios.csv` |
| Pipeline com ficha já baixada | `.venv\Scripts\python src/main.py --completo --xls "ficha.xls" dados/entrada/beneficiarios.csv` |
| Só corrigir (sem SIGRH) | `.venv\Scripts\python src/main.py` |
| Só testar API | `.venv\Scripts\python src/main.py --validar` |
| Baixar ficha manualmente | `.venv\Scripts\python src/Extrator.py` |
| Extrair SEGURIDADE de uma ficha | `.venv\Scripts\python src/Analisador.py "ficha.xls" 08/2023 09/2025` |
| Rodar testes | `.venv\Scripts\python -m pytest testes\ -v` |
| Sem digitar nada (iniciante) | Dar duplo-clique em `Pipeline completo.bat` |
