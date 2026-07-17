# Contexto para o Claude Code

Leia isto antes de trabalhar neste projeto.

## O que é

Automação da atualização monetária (valor presente) que a equipe da **COGEB**
faz na calculadora do **TCDF/SINDEC**. Objetivo: eliminar a digitação mês a mês.

Fonte oficial:
<https://www2.tc.df.gov.br/sindec-sistema-de-indices-e-indicadores-economicos-e-de-atualizacao-de-valores/>

## Onde está o plano

- Plano em fases: [docs/01-plano.md](docs/01-plano.md)
- Estado atual: **Fase 1 concluída → Fase 2**. Abordagem decidida: **A** —
  chamar `POST https://api-sindec.tc.df.gov.br/api/calcular` (índice **INPC**,
  sem juros). Contrato da API em [docs/07-api-tcdf.md](docs/07-api-tcdf.md).
- Recorrência: 1 parcela/mês, corrigida da competência até a data-alvo, somando.

## Regras de ouro

1. **Validar sempre** contra cálculos reais do site (`dados/validacao/`) antes
   de dar algo como pronto. Atualização monetária tem risco de divergência de
   arredondamento e pro-rata.
2. **Não avançar de fase sem aprovação** do usuário.
3. Ambiente **Windows + PowerShell**. Dados reais têm nomes de pessoas — não
   commitar (ver `.gitignore`).
4. Respeitar o site do TCDF: sem volume abusivo de requisições.

## Pendências do usuário

- Enviar exemplo do **modelo final** (Fase 3).
- Enviar **cálculos reais** do site para gabarito (Fase 1/2).
- Confirmar **índice oficial** e se há juros.
- Fazer a **captura da aba Network** — ver [docs/03-captura-network.md](docs/03-captura-network.md).
