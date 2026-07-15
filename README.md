# Atualização Monetária COGEB

Automação do processo de trazer valores a **valor presente** (atualização
monetária) que hoje a equipe da COGEB faz manualmente na calculadora do
**TCDF (SINDEC)**:
<https://www2.tc.df.gov.br/sindec-sistema-de-indices-e-indicadores-economicos-e-de-atualizacao-de-valores/>

---

## O problema

O processo manual é lento e repetitivo:

1. Para cada beneficiário, digitar o valor **mês a mês** no sistema e aplicar
   a correção mensal (ex.: João recebe R$ 1.500 de janeiro a julho → 7
   lançamentos manuais).
2. Exportar o Excel gerado pelo site.
3. Copiar manualmente as informações do Excel para o modelo/template do projeto.

Para uma folha com dezenas de beneficiários e vários meses, isso consome horas.

## O objetivo

Reduzir esse fluxo a: **preencher uma planilha de entrada → rodar → receber a
saída pronta no formato do nosso modelo.**

---

## Status atual do projeto

> **Pipeline completo operacional** — baixa ficha do SIGRH → extrai SEGURIDADE SOCIAL → corrige com IPCA-E → gera Excel COGEB.

Ver o roadmap completo em [docs/01-plano.md](docs/01-plano.md).

| Fase | Descrição | Status |
|------|-----------|--------|
| 1 | Investigação (como a calculadora funciona por baixo) | ✅ Concluída |
| 2 | Automação do cálculo | ✅ Concluída |
| 3 | Saída no formato COGEB | ✅ Concluída |
| 4 | Interface simples para a equipe | ✅ Concluída |
| 5 | Pipeline SIGRH → SEGURIDADE → Correção → Excel | ✅ Concluída |

## Como usar (rápido)

### Fluxo padrão (valor fixo mensal)

1. Preencha `dados/entrada/beneficiarios.csv`.
2. Duplo-clique em **`Atualizar valores.bat`**.
3. Resultado em `dados/saida/resultado.xlsx`.

### Fluxo completo (com SEGURIDADE SOCIAL do SIGRH)

**Duplo-clique** em `Pipeline completo.bat` — ele lê `dados/entrada/beneficiarios.csv`
e gera o Excel em `dados/saida/`.

Ou pelo terminal:

```powershell
python src/main.py --completo dados/entrada/beneficiarios.csv
```

> Credenciais SIGRH lidas do `.env` (matricula_sigrh, senha_sigrh) ou digitadas.

Se a ficha já foi baixada:

```powershell
python src/main.py --completo --xls ficha.xls dados/entrada/beneficiarios.csv
```

Manual completo: [docs/08-manual-uso.md](docs/08-manual-uso.md).

## Como navegar nesta documentação

- **[docs/01-plano.md](docs/01-plano.md)** — plano completo em fases (o "norte" do projeto).
- **[docs/02-investigacao-tcdf.md](docs/02-investigacao-tcdf.md)** — o que sabemos/precisamos descobrir sobre a calculadora do TCDF. **Comece por aqui na Fase 1.**
- **[docs/03-captura-network.md](docs/03-captura-network.md)** — passo a passo para capturar a requisição da API no navegador (o que colar de volta aqui).
- **[docs/04-glossario.md](docs/04-glossario.md)** — termos (atualização monetária, índice, pro-rata, etc.).
- **[docs/05-decisoes.md](docs/05-decisoes.md)** — registro de decisões técnicas (ADR simplificado).
- **[docs/06-modelo-entrada.md](docs/06-modelo-entrada.md)** — formato da planilha de entrada.
- **[docs/07-api-tcdf.md](docs/07-api-tcdf.md)** — contrato da API do SINDEC (endpoints, payloads, gabarito).
- **[docs/08-manual-uso.md](docs/08-manual-uso.md)** — manual da equipe (como rodar).

## Estrutura de pastas

```
atualizacao-monetaria-cogeb/
├─ README.md               <- você está aqui
├─ Atualizar valores.bat   <- duplo-clique para rodar (equipe)
├─ requirements.txt        <- dependências Python
├─ docs/                   <- documentação de suporte
├─ src/                    <- código
│  ├─ sindec_api.py        <- cliente da API do TCDF (+ cache)
│  ├─ calculo.py           <- regras (parcelas mensais, agregação)
│  ├─ io_planilha.py       <- ler CSV/XLSX, gravar Excel de saída
│  ├─ main.py              <- ponto de entrada / validação
│  ├─ Extrator.py          <- automação SIGRH (Playwright)
│  ├─ Analisador.py        <- extrai SEGURIDADE SOCIAL do .xls do SIGRH
├─ fichas financeiras/     <- downloads do Extrator.py (gitignored)
├─ dados/
│  ├─ entrada/             <- planilha que a equipe preenche
│  ├─ saida/               <- resultado gerado (resultado.xlsx)
│  └─ validacao/           <- gabarito + tabela de índices
└─ testes/                 <- testes automatizados (pytest)
```

## Ambiente

- Windows + PowerShell
- (A definir na Fase 2) Python 3.x — ver [docs/01-plano.md](docs/01-plano.md).

## Uso legítimo

Ferramenta de uso institucional interno da COGEB. As requisições ao site do
TCDF devem ser feitas em volume razoável, sem sobrecarregar o serviço público.
