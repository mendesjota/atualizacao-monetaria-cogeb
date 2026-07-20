# Como usar o programa — guia completo para o terminal

Este guia ensina **tudo** que você pode fazer com o programa, do início ao fim.
Cada passo é explicado como se fosse a primeira vez que você abre um terminal.

> Se você NUNCA usou terminal antes, comece pela **[seção 1](#1-o-que-é-esse-tal-de-terminal)**.
> Se já sabe o básico, pule para a **[seção 4](#4-os-comandos-que-existem)**.

---

## Índice

1. [O que é esse tal de "terminal"?](#1-o-que-é-esse-tal-de-terminal)
2. [Como abrir o terminal na pasta certa](#2-como-abrir-o-terminal-na-pasta-certa)
3. [Regra de ouro: sempre usar .venv](#3-regra-de-ouro-sempre-usar-venv)
4. [Os comandos que existem](#4-os-comandos-que-existem)
   - [Cenário A — Pipeline completo (recomendado)](#cenário-a--pipeline-completo-recomendado)
   - [Cenário B — Só corrigir (sem SIGRH)](#cenário-b--só-corrigir-sem-sigrh)
   - [Cenário C — Só testar se a API está no ar](#cenário-c--só-testar-se-a-api-está-no-ar)
   - [Cenário D — Baixar ficha manualmente (Extrator)](#cenário-d--baixar-ficha-manualmente-extrator)
   - [Cenário E — Extrair SEGURIDADE de uma ficha existente](#cenário-e--extrair-seguridade-de-uma-ficha-existente)
   - [Cenário F — Rodar os testes](#cenário-f--rodar-os-testes)
5. [Os bat files (duplo-clique — sem digitar nada)](#5-os-bat-files-duplo-clique--sem-digitar-nada)
6. [Tabela resumo — o que digitar em cada situação](#6-tabela-resumo--o-que-digitar-em-cada-situação)

---

## 1. O que é esse tal de "terminal"?

O terminal (ou "PowerShell") é uma janela onde você **digita comandos** em vez de
clicar em ícones. O programa que você vai usar **só funciona digitando comandos**.

### Como é a tela do terminal

```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\MeuNome>
```

O `PS C:\Users\MeuNome>` é o "prompt" — significa que o terminal está esperando
você digitar alguma coisa.

> ⚠️ **Importante:** o terminal **não funciona com mouse** para a maioria das
> coisas. Você vai digitar os comandos e apertar **Enter** para executar.

---

## 2. Como abrir o terminal na pasta certa

O terminal **precisa estar aberto na pasta do projeto** para o programa funcionar.

### Jeito 1 — Pelo VS Code (mais fácil)

**Passo 1:** Abra o VS Code.

**Passo 2:** Clique em **File** (Arquivo) → **Open Folder...** (Abrir Pasta).

**Passo 3:** Escolha a pasta `atualizacao-monetaria-cogeb` e clique em
"Selecionar Pasta".

**Passo 4:** Agora clique em **Terminal** (no menu de cima) → **New Terminal**.

> **Atalho:** dá para fazer a mesma coisa apertando **Ctrl + '** (a tecla
> do acento agudo, do lado do Enter).

**Passo 5:** Uma janela vai aparecer na parte de baixo do VS Code.
É o terminal. Você vai ver algo como:

```
PS C:\Users\MeuNome\Desktop\Python\Projetos\atualizacao-monetaria-cogeb>
```

**Pronto.** O terminal já está na pasta certa.

### Jeito 2 — Pelo Explorador de Arquivos

**Passo 1:** Abra a pasta `atualizacao-monetaria-cogeb` no Explorador de
Arquivos (aquela janela que mostra as pastas do computador).

**Passo 2:** Clique na **barra de endereço** (mostra o caminho, tipo
`C:\Users\...\atualizacao-monetaria-cogeb`).

**Passo 3:** Apague o caminho e digite:

```
powershell
```

**Passo 4:** Aperte **Enter**.

**Passo 5:** Uma janela azul do PowerShell vai abrir. Pronto.

---

## 3. Regra de ouro: sempre usar .venv

### O que é .venv?

O `.venv` é uma pasta que foi criada dentro do projeto quando você instalou
o programa. Ela contém uma cópia do Python com as bibliotecas já instaladas.

**Sempre** que você for rodar o programa, você precisa usar o Python que
está DENTRO dessa pasta. Se você usar o Python "normal" do computador,
o programa não vai achar as bibliotecas e vai dar erro.

### Como saber se está no lugar certo

Antes de digitar qualquer comando, confira se o terminal mostra o caminho
da pasta do projeto. Exemplo de como DEVE aparecer:

```
PS C:\Users\MeuNome\Desktop\Python\Projetos\atualizacao-monetaria-cogeb>
```

Se mostrar outra coisa (tipo `PS C:\Users\MeuNome>`), você não está na pasta
certa. Volte para a [seção 2](#2-como-abrir-o-terminal-na-pasta-certa).

### Os comandos SEMPRE começam com `.venv\Scripts\python`

Veja a diferença:

| ❌ Errado | ✅ Certo |
|-----------|----------|
| `python src/main.py` | `.venv\Scripts\python src/main.py` |
| `python --versao` | `.venv\Scripts\python --versao` |

> **O que muda?** O `.venv\Scripts\python` diz "use o Python que está dentro
> da pasta .venv". Sem isso, o Windows usa o Python genérico do computador,
> que não tem as bibliotecas do projeto.

Pronto. Agora vamos aos comandos.

---

## 4. Os comandos que existem

### Cenário A — Pipeline completo (recomendado)

**Quando usar:** você quer fazer TUDO de uma vez:
1. Baixar a ficha financeira do SIGRH
2. Extrair os valores de SEGURIDADE SOCIAL
3. Corrigir com IPCA-E
4. Gerar o Excel

#### O comando

Digite **exatamente** isso no terminal:

```
.venv\Scripts\python src/main.py --completo dados/entrada/beneficiarios.csv
```

Aperte **Enter**.

#### Explicação de cada pedaço do comando

| Pedaço | O que significa |
|--------|----------------|
| `.venv\Scripts\python` | "Use o Python que está na pasta .venv" — é o nosso Python com as bibliotecas |
| `src/main.py` | "Execute o arquivo main.py que está dentro da pasta src" — é o programa principal |
| `--completo` | "Faça o pipeline completo" — baixar ficha, extrair, corrigir, gerar Excel |
| `dados/entrada/beneficiarios.csv` | "Leia a planilha que está em dados/entrada/beneficiarios.csv" — sua lista de pessoas |

#### O que vai aparecer na tela enquanto roda

```
→ Verificando conexão com a API do SINDEC (IPCA-E)...
  Série IPCA-E carregada: 414 meses (01/1992 a 06/2026)
→ Lendo entrada: dados\entrada\beneficiarios.csv
  3 beneficiário(s).

[1/3] MARIA DA SILVA — matrícula 123456
  Baixando ficha financeira (2023-2025)...
  ... (pode demorar alguns minutos)
  Ficha salva: fichas financeiras\FICHA-FIN-123456-990-2023-2025-xxxx.xls
  Analisando SEGURIDADE SOCIAL (01/2023 a 12/2025)...
  36 parcelas extraídas.
  Corrigindo com IPCA-E...

[2/3] JOAO DE SOUZA — matrícula 789012
  ...

✔ Concluído. 3 beneficiário(s), 120 parcela(s), total corrigido R$ 53.173,00
✔ Saída: dados\saida\resultado_2026_07_20.xlsx
```

> ⏳ **Quanto tempo leva?** Cerca de 1-2 minutos por pessoa. O navegador
> Firefox abre e fecha sozinho — é normal, é o programa baixando a ficha.

#### E se eu quiser que o Excel tenha um nome diferente?

Acrescente o nome do arquivo no final:

```
.venv\Scripts\python src/main.py --completo dados/entrada/beneficiarios.csv dados/saida/meu_resultado.xlsx
```

Agora o Excel vai se chamar `meu_resultado.xlsx` em vez do nome automático.

#### E se a ficha do SIGRH já foi baixada antes?

Use o `--xls` para pular o download (não precisa baixar de novo):

```
.venv\Scripts\python src/main.py --completo --xls "fichas financeiras/FICHA-FIN-123456.xls" dados/entrada/beneficiarios.csv dados/saida/resultado.xlsx
```

| Pedaço extra | O que significa |
|--------------|----------------|
| `--xls "fichas financeiras/FICHA-FIN-123456.xls"` | "Use esta ficha que já foi baixada, não baixe de novo" |

> ⚠️ O `--xls` fica **antes** do caminho de entrada e saída.

#### E se o CSV não estiver na pasta padrão?

Você pode passar o caminho completo de qualquer arquivo no computador:

```
.venv\Scripts\python src/main.py --completo C:\Users\MeuNome\Desktop\minha_planilha.csv C:\Users\MeuNome\Desktop\resultado.xlsx
```

#### O que pode dar errado (e o que fazer)

| Mensagem de erro | O que significa | O que fazer |
|------------------|----------------|-------------|
| `✖ Entrada não encontrada` | O arquivo CSV não existe no caminho que você passou | Confira se o arquivo existe. Veja se escreveu o caminho certo |
| `✖ Abortando: API indisponível` | O site do TCDF está fora do ar ou sem internet | Verifique a internet. Tente de novo mais tarde |
| `[SIGRH ERRO] ...` | O SIGRH falhou ao baixar a ficha | O programa tenta 3 vezes. Se falhar todas, o SIGRH pode estar lento |
| `... não encontrado ...` | Algum arquivo não foi achado | Verifique se o nome está escrito certo (maiúsculas/minúsculas) |

---

### Cenário B — Só corrigir (SEM SIGRH)

**Quando usar:** você já tem os valores (não precisa baixar ficha do SIGRH).
Você preencheu a coluna `valor_mensal` no CSV com os números.

#### O comando mais simples

```
.venv\Scripts\python src/main.py
```

**O que faz:** Lê `dados/entrada/beneficiarios.csv`, corrige tudo com IPCA-E
e gera o Excel em `dados/saida/resultado_AAAA_MM_DD.xlsx`.

#### Com caminhos diferentes

Se o CSV estiver em outro lugar (não no `beneficiarios.csv` padrão):

```
.venv\Scripts\python src/main.py dados/entrada/minha_planilha.csv
```

Se quiser controlar também onde o Excel vai ser salvo:

```
.venv\Scripts\python src/main.py dados/entrada/minha_planilha.csv dados/saida/meu_excel.xlsx
```

---

### Cenário C — Só testar se a API está no ar

**Quando usar:** você quer saber se o site do TCDF está funcionando antes
de começar o trabalho.

#### O comando

```
.venv\Scripts\python src/main.py --validar
```

#### O que aparece na tela

```
→ Verificando conexão com a API do SINDEC (IPCA-E)...
  Série IPCA-E carregada: 414 meses (01/1992 a 06/2026)
```

**Isso significa que está tudo OK.** O programa conseguiu falar com o site.

Se aparecer:

```
→ Verificando conexão com a API do SINDEC (IPCA-E)...
  ✖ Falha ao carregar IPCA-E: ...
```

**Significa que algo deu errado.** Pode ser:
- Sua internet está fora
- O site do TCDF está fora do ar (tente de novo mais tarde)
- O firewall do seu trabalho está bloqueando

---

### Cenário D — Baixar ficha manualmente (Extrator)

**Quando usar:** você quer baixar a ficha de UMA pessoa específica sem
rodar o pipeline inteiro. Pode ser útil para testar ou para ter a ficha
salva no computador.

#### O comando

```
.venv\Scripts\python src/Extrator.py
```

#### O que vai acontecer

O programa vai fazer perguntas **uma de cada vez**. Você digita a resposta
e aperta Enter:

```
=== Ficha Financeira SIGRH ===

Matrícula de Login: 123456
Senha de Login: ********** (não aparece enquanto digita)
Matrícula do Empregado: 17151538
Código da Empresa (990/992/037/556/652) [990]: 990
Competência Inicial (ex: 2023): 2023
Competência Final (ex: 2026): 2025
```

Depois da última pergunta, o programa:
1. Abre o navegador Firefox
2. Faz login no SIGRH
3. Pesquisa a matrícula
4. Baixa o arquivo
5. Fecha o navegador

**Onde o arquivo vai parar:** Na pasta `fichas financeiras/`.

**Exemplo de nome do arquivo:**
```
fichas financeiras/FICHA-FIN-17151538-990-2023-2025-123456789.xls
```

#### O que a senha não aparece na tela?

É normal. É um recurso de segurança — a senha fica oculta enquanto você digita.

#### Se aparecer erro

```
[SIGRH ERRO] ...
```

Pode ser:
- Matrícula/senha errados
- SIGRH fora do ar
- Internet lenta

O programa tenta novamente até 3 vezes.

---

### Cenário E — Extrair SEGURIDADE de uma ficha existente

**Quando usar:** você já tem a ficha baixada (`.xls`) e quer ver os valores
de SEGURIDADE SOCIAL que ela contém. O programa mostra na tela uma tabela
com mês, valor original, teto do ano e valor final.

#### O comando

```
.venv\Scripts\python src/Analisador.py "fichas financeiras/FICHA-FIN-123456.xls" 08/2023 09/2025
```

#### Explicação

| Parte do comando | Exemplo | O que significa |
|------------------|---------|----------------|
| `src/Analisador.py` | — | Programa que extrai SEGURIDADE SOCIAL |
| Caminho do .xls | `"fichas financeiras/FICHA-FIN-123456.xls"` | Qual arquivo ler |
| Data início | `08/2023` | A partir de agosto de 2023 |
| Data fim | `09/2025` | Até setembro de 2025 |

> As aspas `" "` em volta do caminho são necessárias porque o nome da pasta
> tem espaço (`fichas financeiras`).

#### O que aparece na tela

```
competencia;valor_seg_social;teto_ano;valor_final
2023-08;3495.00;1733.65;1733.65
2023-09;3357.36;1733.65;1733.65
...
```

Cada linha é um mês. O `valor_final` é o valor já com o teto aplicado.

#### Usando o CSV para pegar as datas automaticamente

Se você já tem o CSV de entrada, pode usar `--csv` em vez de digitar as
datas manualmente:

```
.venv\Scripts\python src/Analisador.py "fichas financeiras/FICHA-FIN-123456.xls" --csv dados/entrada/beneficiarios.csv
```

#### Formatos de data aceitos

| Formato | Exemplo | Significa |
|---------|---------|-----------|
| `MM/AAAA` | `08/2023` | Agosto de 2023 |
| `MM-AAAA` | `08-2023` | Agosto de 2023 (com traço) |
| Mês abreviado PT-BR | `ago/23` | Agosto de 2023 |

---

### Cenário F — Rodar os testes

**Quando usar:** alguém mexeu no código e você quer saber se as contas
continuam certas.

#### O comando

```
.venv\Scripts\python -m pytest testes\ -v
```

#### O que aparece na tela

```
testes\test_unit.py ............                        [100%]
19 passed in 0.32s
```

**19 passed** = os 19 testes passaram. Tudo certo.

Se aparecer **failed** no lugar de **passed**, algo está errado com o
código — avise o programador.

---

## 5. Os bat files (duplo-clique — sem digitar nada)

Se você **não quer digitar comandos**, é só dar dois cliques em um arquivo.

### Onde estão

Na pasta raiz do projeto:

```
atualizacao-monetaria-cogeb/
├── Pipeline completo.bat   ← CLIQUE AQUI para fazer TUDO
├── Atualizar valores.bat   ← CLIQUE AQUI para só corrigir (sem SIGRH)
```

### O que cada um faz

| Arquivo | O que faz |
|---------|-----------|
| `Pipeline completo.bat` | Baixa ficha do SIGRH → extrai SEGURIDADE → corrige → Excel |
| `Atualizar valores.bat` | Só corrige (SEM SIGRH). Precisa do valor preenchido no CSV |

### Como usar

1. Dê **dois cliques** no arquivo.
2. Uma janela preta (terminal) vai abrir sozinha.
3. O programa começa a rodar automaticamente.
4. No final, aparece uma mensagem dizendo onde está o Excel.
5. Pressione qualquer tecla para fechar a janela.

### Qual escolher

| Situação | Qual bat usar |
|----------|---------------|
| `valor_mensal = 0` no CSV (buscar do SIGRH) | `Pipeline completo.bat` |
| `valor_mensal = 1500,00` (valor fixo, não precisa do SIGRH) | Qualquer um |
| SIGRH fora do ar, mas tenho a ficha salva | `Pipeline completo.bat --xls "ficha.xls"` |

> ⚠️ **Importante:** o `Pipeline completo.bat` depende do arquivo
> `.env` com sua matrícula e senha do SIGRH. Se não criou o `.env`,
> o programa vai pedir a senha na tela.

---

## 6. Tabela resumo — o que digitar em cada situação

| Sua situação | O que digitar no terminal (ou clicar) |
|--------------|---------------------------------------|
| **Quero fazer TUDO** (SIGRH + correção + Excel) | `.venv\Scripts\python src/main.py --completo dados/entrada/beneficiarios.csv` |
| **Já tenho a ficha baixada** (pular SIGRH) | `.venv\Scripts\python src/main.py --completo --xls "ficha.xls" dados/entrada/beneficiarios.csv` |
| **Quero só corrigir** (valor fixo no CSV) | `.venv\Scripts\python src/main.py` |
| **Só testar se a API funciona** | `.venv\Scripts\python src/main.py --validar` |
| **Baixar uma ficha avulsa** | `.venv\Scripts\python src/Extrator.py` |
| **Ver os valores de uma ficha** | `.venv\Scripts\python src/Analisador.py "ficha.xls" 08/2023 09/2025` |
| **Testar se o código está certo** | `.venv\Scripts\python -m pytest testes\ -v` |
| **Não quero digitar nada** | Duplo-clique em `Pipeline completo.bat` |

---

> **Dúvidas?** Converse com o José ou com a equipe técnica.
