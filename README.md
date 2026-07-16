# Atualização Monetária COGEB

Ferramenta que **corrige valores com IPCA-E** (inflação) e gera uma planilha Excel
no formato que a COGEB precisa.

---

## ⚡ Como usar (rápido)

### 1. Preencha a planilha de entrada

Abra `dados/entrada/beneficiarios.csv` no Excel e preencha:

| nome | matricula | orgao | valor_mensal | competencia_inicial | competencia_final | data_alvo |
|------|-----------|-------|-------------|-------------------|-----------------|-----------|
| MARIA DA SILVA | 123456 | 990 | 0 | 01/2024 | 12/2024 | 30/06/2026 |

> Colunas com `;` (ponto e vírgula) separando. `valor_mensal=0` quando o
> valor real vem da ficha do SIGRH.

### 2. Dê dois cliques

Duplo-clique em **`Pipeline completo.bat`** e aguarde.

### 3. Pegue o resultado

O arquivo `resultado_AAAA_MM_DD.xlsx` aparece na pasta `dados/saida/`.

---

## 📖 O que a ferramenta faz automaticamente

```
Você preenche o CSV → o programa:
  1. Entra no SIGRH e baixa a Ficha Financeira de cada pessoa
  2. Extrai os valores de SEGURIDADE SOCIAL mês a mês
  3. Aplica o teto máximo de cada ano
  4. Corrige cada parcela com IPCA-E (inflação)
  5. Gera o Excel pronto, no formato que a COGEB usa
```

---

## 🔧 Instalação (faz uma vez só)

Só precisa fazer isso na primeira vez que for usar:

### 1. Instalar Python

1. Baixe o Python 3.12 ou superior em https://www.python.org/downloads/
2. Na instalação, **marque "Add Python to PATH"**
3. Abra o PowerShell (tecla Windows + X → "Windows PowerShell")
4. Digite: `python --version` — deve aparecer "Python 3.12..."

### 2. Preparar o programa

```powershell
cd C:\caminho\ate\a\pasta\atualizacao-monetaria-cogeb
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m playwright install firefox
```

### 3. Colocar a senha do SIGRH

Crie um arquivo `.env` na pasta raiz com:

```
matricula_sigrh=SUA_MATRICULA_AQUI
senha_sigrh=SUA_SENHA_AQUI
```

---

## ❓ Problemas comuns

| Problema | O que fazer |
|----------|-------------|
| "Arquivo não encontrado" | Verifique se o CSV existe em `dados/entrada/` |
| "Falha de conexão" | Confira se a internet está funcionando |
| SIGRH não abre ou timeout | O programa tenta **3 vezes automaticamente** com 15s de intervalo. Se persistir, o SIGRH pode estar fora do ar |
| Saiu tudo 0,00 | O `valor_mensal` está 0 mas a ficha não foi baixada (veja a mensagem de erro no terminal) |
| "pip não é reconhecido" | Reinstale o Python marcando "Add Python to PATH" |
| Demora muito | Normal para fichas com muitos meses (ex: 4 beneficiários leva ~10 minutos) |

---

> **Primeira vez baixando do GitHub?** Veja o guia `docs/09-clonar-github.md`
> — explica como baixar, instalar e rodar tudo passo a passo.
>
> **Precisa de ajuda técnica?** A documentação completa está na pasta `docs/`.
