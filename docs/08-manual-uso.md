# Manual de uso — Atualização Monetária COGEB

Este manual explica **cada passo** para usar a ferramenta, sem precisar saber
programação.

---

## Índice

1. [Antes de começar](#1-antes-de-começar)
2. [Preparar a planilha de entrada](#2-preparar-a-planilha-de-entrada)
3. [Rodar o programa](#3-rodar-o-programa)
4. [Entender a saída (Excel)](#4-entender-a-saída-excel)
5. [Primeira instalação numa máquina nova](#5-primeira-instalação-numa-máquina-nova)
6. [Problemas e soluções](#6-problemas-e-soluções)

---

## 1. Antes de começar

### O que você precisa

- Um computador com Windows
- Internet (o programa busca dados do SIGRH e do TCDF)
- Sua matrícula e senha do **SIGRH** (sistema de RH do governo)

### A estrutura de pastas

```
atualizacao-monetaria-cogeb/
├─ dados/
│  ├─ entrada/           ← VOCÊ COLA O ARQUIVO AQUI
│  └─ saida/             ← O RESULTADO SAI AQUI
├─ Pipeline completo.bat ← CLIQUE AQUI PARA RODAR
├─ src/                  ← programas (não mexa)
└─ docs/                 ← manuais (você está aqui)
```

---

## 2. Preparar a planilha de entrada

### 2.1 Onde fica o arquivo

O arquivo se chama `beneficiarios.csv` e fica dentro da pasta `dados/entrada/`.

> **Primeira vez?** Copie o arquivo modelo `dados/entrada/_modelo_entrada.csv`
> e renomeie para `beneficiarios.csv`.

### 2.2 Como preencher

Abra o arquivo no Excel. Cada linha é um beneficiário. As colunas são:

| Coluna | O que escrever | Exemplo |
|--------|---------------|---------|
| `nome` | Nome completo | ANTONIO GOMES DA SILVA |
| `matricula` | Número de matrícula | 16502711 |
| `orgao` | Código do órgão | 990 |
| `valor_mensal` | **0** (o valor real virá do SIGRH) | 0 |
| `competencia_inicial` | Mês/ano do **primeiro** mês | 01/2024 |
| `competencia_final` | Mês/ano do **último** mês | 12/2024 |
| `data_alvo` | Data de referência do cálculo | 30/06/2026 |

> **Datas:** você pode escrever de vários jeitos:
> - `01/2024` = janeiro de 2024
> - `15/01/2024` = 15 de janeiro de 2024
> - `2024-01` = janeiro de 2024
> - `jan/24` = janeiro de 2024 (mês abreviado em português)

### 2.3 Regras importantes

- **Separador é ponto e vírgula `;`** — o Excel do Brasil já usa isso.
- **valor_mensal = 0** significa "buscar o valor real da ficha do SIGRH".
  Se você já sabe o valor, pode colocar o número (ex: `1500,00`).
- Salve o arquivo como **CSV UTF-8** (no Excel: "Salvar como" → "CSV UTF-8").
- Para colocar vários períodos da mesma pessoa, repita a linha com valores
  diferentes:

```
ANTONIO GOMES DA SILVA;16502711;990;0;01/2024;06/2024;30/06/2026
ANTONIO GOMES DA SILVA;16502711;990;0;07/2024;12/2024;30/06/2026
```

### 2.4 Exemplo completo

```
nome;matricula;orgao;valor_mensal;competencia_inicial;competencia_final;data_alvo
OLGA ANDRADE ABRAHAO;17151538;990;0;08/2023;09/2025;06/01/2026
ANTONIO GOMES DA SILVA;16502711;990;0;05/2023;04/2025;06/01/2026
DIMAS GARCIA DE OLIVEIRA;0093383X;990;0;01/2023;01/2026;06/01/2026
```

---

## 3. Rodar o programa

### 3.1 Jeito mais fácil (duplo-clique)

1. Dê **dois cliques** no arquivo **`Pipeline completo.bat`**
2. Uma janela preta (terminal) vai abrir
3. O programa vai:
   - Pedir sua senha do SIGRH (se não estiver no `.env`)
   - Baixar a ficha financeira de cada pessoa
   - Extrair os valores de SEGURIDADE SOCIAL
   - Corrigir tudo com IPCA-E
   - Gerar o Excel
4. Quando terminar, aparece: `✔ Concluído.`
5. O resultado está em `dados/saida/resultado_AAAA_MM_DD.xlsx`

> ⏳ Pode levar alguns minutos, especialmente se tiver muitos beneficiários.
> O navegador Firefox vai abrir e fechar sozinho — é normal.

### 3.2 Se aparecer pedindo senha

Se você não criou o arquivo `.env`, o programa vai perguntar:

```
=== Credenciais SIGRH ===
Matrícula de Login: (digite sua matrícula)
Senha de Login: (digite sua senha — não aparece na tela)
```

### 3.3 Se a ficha já foi baixada antes

Se o SIGRH estiver fora do ar, mas você tem a ficha salva:

```
Pipeline completo.bat --xls "caminho/da/ficha.xls"
```

---

## 4. Entender a saída (Excel)

O arquivo gerado tem a seguinte estrutura para cada beneficiário:

```
NOME: MARIA DA SILVA - MATRÍCULA 123456         ÓRGÃO: 990

Data do Valor Original | Valor Original | Descrição         | (...) | Valor Corrigido
01/2023                | R$ 1.500,00    | DEVOLUÇÃO DA ...  |       | R$ 1.723,45
02/2023                | R$ 1.500,00    | DEVOLUÇÃO DA ...  |       | R$ 1.719,23
...
12/2023                | R$ 1.500,00    | DEVOLUÇÃO 13º SAL |       | R$ 1.690,12
----------------------------------------------------------------------------
Total                                             | R$ 21.345,67

RUBRICA                    | VALOR
30920 - SEGURIDADE SOCIAL  | R$ 19.543,22
30923 - SEG. SOC. - 13º   | R$ 1.802,45
20827 - ATUAL. MONETÁRIA. | R$ 1.234,56
```

**O que significa cada coisa:**
- **Valor Original**: o valor que estava na ficha do SIGRH (já com o teto aplicado)
- **Valor Corrigido**: o valor após aplicar a correção da inflação (IPCA-E)
- **Atualização Monetária**: a diferença (correção) — é o quanto o valor "aumentou"
- **30920**: soma de todos os valores mensais de seguridade social
- **30923**: soma do 13º salário
- **20827**: soma de toda a correção (atualização monetária)

---

## 5. Primeira instalação numa máquina nova

Só precisa fazer isso **uma vez** em cada computador.

### Passo 1 — Instalar o Python

1. Acesse https://www.python.org/downloads/
2. Baixe a versão 3.12 ou superior
3. Execute o instalador
4. **IMPORTANTE:** marque a opção **"Add Python to PATH"** (no final da tela)
5. Clique em "Install Now"

### Passo 2 — Abrir o PowerShell

- Tecla `Windows + X` → "Windows PowerShell"
- Ou: Windows → digitar "PowerShell" → abrir

### Passo 3 — Preparar o programa

No PowerShell, digite cada linha e aperte Enter:

```powershell
cd C:\caminho\ate\a\pasta\do\projeto
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m playwright install firefox
```

### Passo 4 — Colocar a senha permanentemente

Crie um arquivo chamado `.env` (sem nome, só a extensão) na pasta raiz com:

```
matricula_sigrh=SUA_MATRICULA_AQUI
senha_sigrh=SUA_SENHA_AQUI
```

### Pronto! Agora é só usar o `Pipeline completo.bat`.

> **Dica:** Se preferir não salvar a senha, pode digitar toda vez que rodar.

---

## 6. Problemas e soluções

### "O arquivo beneficiarios.csv não foi encontrado"

Verifique se:
- O arquivo existe em `dados/entrada/beneficiarios.csv`
- O nome está escrito igual (maiúsculas/minúsculas não importam)

### "Falha na conexão com o SINDEC"

- Verifique se a internet está funcionando
- O site do TCDF pode estar fora do ar temporariamente
- Tente rodar de novo mais tarde

### "O SIGRH não abriu / deu erro"

O programa **tenta automaticamente 3 vezes** com 15 segundos de intervalo.
Então é normal ver uma mensagem de falha seguida de nova tentativa.

Se mesmo assim falhar:
- Confira se sua matrícula e senha estão corretas
- O SIGRH pode estar lento ou em manutenção
- Se tiver pressa, baixe a ficha manualmente e use `--xls`

### "Apareceu um erro em inglês no terminal"

Não se assuste. Procure a palavra **"Erro"** ou **"Error"** na mensagem.
As soluções mais comuns:

| Mensagem | Provável causa | Solução |
|----------|---------------|---------|
| `FileNotFoundError` | Arquivo não encontrado | Confira o caminho do CSV |
| `ConnectionError` | Sem internet | Verifique a rede |
| `TimeoutError` | Site demorou a responder | Tente de novo mais tarde |
| `pip` não encontrado | Python não instalado direito | Reinstale o Python com "Add to PATH" |

### "O Excel gerou valores todos 0,00"

- Verifique se `valor_mensal` está com `0` e se a ficha do SIGRH foi baixada
- Veja se apareceu "Falha no Extrator" na tela — se sim, o SIGRH pode estar fora

### "Quanto tempo leva?"

- Para 1 beneficiário: ~1-2 minutos
- Para 4 beneficiários: ~5-10 minutos
- Quanto mais meses na ficha, mais demora (cada mês é uma linha no Excel)
- O programa baixa uma ficha por vez (respeita o site do governo)
- Se uma tentativa falhar, o programa espera 15s e tenta de novo (no máximo 3 vezes)

---

## Ainda com dúvida?

Chame alguém da equipe técnica da COGEB. A documentação para desenvolvedores
está nos outros arquivos da pasta `docs/`.
