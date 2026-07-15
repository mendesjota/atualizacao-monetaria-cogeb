# Manual de uso (equipe COGEB)

## Dois fluxos de trabalho

| Fluxo | Quando usar | Comando |
|-------|-------------|---------|
| **Padrão** | Valor mensal fixo conhecido | `python src/main.py` |
| **Completo** | Buscar SEGURIDADE SOCIAL real do SIGRH | `python src/main.py --completo entrada.csv saida.xlsx` |

---

## Fluxo padrão — valor fixo

Você preenche uma planilha com os beneficiários e os períodos; a ferramenta
consulta a série mensal do **IPCA-E** (site do SINDEC/TCDF) e devolve um Excel
com os valores corrigidos.

### Passo a passo

1. **Preencha a planilha de entrada**
   Abra `dados/entrada/beneficiarios.csv` (ou copie o modelo
   `dados/entrada/_modelo_entrada.csv`) e preencha uma linha por
   beneficiário/faixa:

   | Coluna | O que colocar | Exemplo |
   |--------|----------------|---------|
   | `nome` | Nome | LEVI BATISTA DA SILVA |
   | `matricula` | Matrícula | 00812188 |
   | `orgao` | Órgão | 652 |
   | `valor_mensal` | Valor mensal da parcela | 915,38 |
   | `competencia_inicial` | Mês/ano da 1ª parcela | 02/2025 ou fev/25 |
   | `competencia_final` | Mês/ano da última parcela | 06/2025 ou jun/25 |
   | `data_alvo` | Data de atualização (dd/mm/aaaa) | 02/02/2026 |
   | `observacao` | Livre (opcional) | devolucao seguridade |

   > **Datas**: aceita `MM/AAAA`, `DD/MM/AAAA`, `AAAA-MM` ou mês abreviado em
   > português (ex: `ago/23`, `set/25`, `jan/24`).

2. **Rode**
   ```powershell
   python src/main.py
   ```
   Ou:
   ```powershell
   python src/main.py dados/entrada/meus_dados.csv saida.xlsx
   ```

3. **Pegue o resultado**
   O arquivo sai em `dados/saida/resultado.xlsx`, formato COGEB.

---

## Fluxo completo — SEGURIDADE SOCIAL do SIGRH

Baixa automaticamente a Ficha Financeira de cada beneficiário do SIGRH, extrai
os valores reais de SEGURIDADE SOCIAL (código 40920), aplica o teto de
contribuição de cada ano, corrige com IPCA-E e gera o Excel final.

### Pré-requisitos

1. Playwright com Firefox instalado (uma vez):
   ```powershell
   .venv\Scripts\python -m playwright install firefox
   ```

2. Credenciais SIGRH no arquivo `.env` (raiz do projeto):
   ```env
   matricula_sigrh=2874946
   senha_sigrh=070790
   ```
   Ou digitar quando o programa pedir.

### Como rodar

**Duplo-clique** em `Pipeline completo.bat` — ele usa `dados/entrada/beneficiarios.csv`.

Ou pelo terminal:
```powershell
python src/main.py --completo dados/entrada/_modelo_entrada.csv
```
> O nome do arquivo de saída já sai com a data atual (ex: `resultado_2026_07_15.xlsx`).

Se a ficha já foi baixada antes (pular o SIGRH):
```powershell
python src/main.py --completo --xls fichas/ficha.xls dados/entrada/_modelo_entrada.csv
```

### Exemplo de entrada

```
nome;matricula;orgao;valor_mensal;competencia_inicial;competencia_final;data_alvo
OLGA ANDRADE ABRAHAO;17151538;990;0;ago/23;set/25;06/01/2026
```

> `valor_mensal=0` porque o valor real virá da ficha do SIGRH.

### O que o pipeline faz

```
CSV de entrada
  ↓
Extrator.py → baixa Ficha Financeira (.xls) do SIGRH
  ↓
Analisador.py → extrai 40920 SEGURIDADE SOCIAL mês a mês + 13º salário
                → aplica teto anual (cap)
  ↓
sindec_api.py → corrige cada parcela com IPCA-E composto
  ↓
io_planilha.py → gera Excel no formato COGEB
```

### Validação

O pipeline foi validado com a empregada **OLGA ANDRADE ABRAHAO**:

|        | Modelo de saída | Pipeline | Diferença |
|--------|----------------|----------|-----------|
| Total  | R$ 53.173,00   | R$ 53.173,00 | R$ 0,00 |

---

## Perguntas frequentes

- **Preciso saber programar?** Não. Só preencher a planilha e rodar o comando.
- **O índice usado é IPCA-E?** Sim.
- **Os números batem com o site?** Sim — validado (R$ 0,00 de diferença).
- **Deu erro "planilha não encontrada".** Confira se o arquivo de entrada existe.
- **Deu erro de conexão.** Cheque a internet.
- **Precisa de internet?** Sim — IPCA-E baixado do TCDF a cada execução.
- **SIGRH não acessível?** Use `--xls` com uma ficha já baixada.

## Instalação em outra máquina (uma vez)

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m playwright install firefox
```

Depois é só usar `python src/main.py`.
