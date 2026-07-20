# Glossário — termos usados no projeto

Em linguagem simples, para quem não é da área de economia ou TI.

---

### Atualização monetária (correção monetária)

Aplicar a inflação em um valor do passado para saber quanto ele "vale" hoje.
Não é juro — é só para não perder o poder de compra.

> Exemplo: R$ 1.000,00 de janeiro viram R$ 1.072,60 em julho por causa da
> inflação do período.

### Índice econômico

Número que mede quanto os preços subiram num período. Exemplos:
- **IPCA-E**: índice oficial usado neste projeto (mede inflação mês a mês)
- **INPC**: outro índice, parecido, mas anual
- **IGP-M**: índice usado em contratos de aluguel

### Fator de correção

O "multiplicador" que transforma o valor antigo no valor corrigido.
Exemplo: fator 0,0726 = 7,26% de correção.

### Competência

O mês e ano a que um valor se refere. Exemplo: "salário de janeiro/2024"
tem competência `01/2024`.

### Data-alvo (data de atualização)

A data para a qual você está trazendo os valores. Geralmente é a data do
cálculo ou a data em que o processo foi aberto.

### Teto (cap)

Valor máximo permitido por mês. A SEGURIDADE SOCIAL tem um teto que muda
todo ano. Se o valor ultrapassar o teto, o programa usa o teto.

### SINDEC / TCDF

**SINDEC** = Sistema do Tribunal de Contas do DF que calcula correção
monetária. A ferramenta consulta automática esse sistema pela internet.

### SIGRH

Sistema de RH do Governo do Distrito Federal. É de lá que a ferramenta
baixa a Ficha Financeira de cada empregado.

### Ficha Financeira

Documento do SIGRH que mostra todos os valores recebidos por um empregado
mês a mês (salário, seguridade social, 13º etc.).

### SEGURIDADE SOCIAL (código 40920)

Um tipo de valor que aparece na Ficha Financeira. É a contribuição do
empregado para a seguridade social (previdência). O código 40920 é como
o SIGRH identifica essa rubrica.

### 13º salário (código 40923)

A parcela do 13º salário que também aparece na Ficha Financeira, com
código próprio (40923). Pode ser paga em um mês específico (ex.: novembro)
ou dividida em dois meses.

### Diferença de SEGURIDADE SOCIAL (código 50920)

Valor complementar de SEGURIDADE SOCIAL que aparece na Ficha Financeira
em meses específicos. É extraído separadamente e entra no cálculo como
uma parcela extra no mês em que foi paga.

### Pipeline completo (`--completo`)

Modo de execução que faz **tudo de uma vez**: baixa a ficha do SIGRH,
extrai os valores de SEGURIDADE SOCIAL, corrige com IPCA-E e gera o
Excel. Ativado com a flag `--completo` no terminal.

### Ambiente virtual (`.venv`)

Pasta criada pelo Python que contém uma cópia isolada do Python com
as bibliotecas do projeto. Todos os comandos devem usar
`.venv\Scripts\python` em vez de `python` puro.

### CSV

Tipo de arquivo que o Excel consegue ler e salvar. As colunas são
separadas por `;` (ponto e vírgula). É o formato da planilha de entrada.

### Pipeline

O "caminho" que os dados percorrem: baixar ficha → extrair valores →
corrigir → gerar Excel. O `--completo` faz o pipeline inteiro de uma vez.
