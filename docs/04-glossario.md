# Glossário

Termos usados no projeto, em linguagem simples.

- **Atualização monetária (correção monetária):** trazer um valor do passado
  para uma data de referência, corrigindo a perda do poder de compra pela
  inflação. Não é juro — é só "recompor" o valor.

- **Valor presente:** o quanto um valor do passado "vale" hoje (ou na data-alvo),
  já corrigido.

- **Índice econômico:** número que mede a variação de preços ao longo do tempo.
  Exemplos: IPCA, IPCA-E, INPC, IGP-M. Cada mês tem um valor de índice.

- **Fator de correção:** razão entre o índice da data final e o da data inicial.
  `fator = índice_final / índice_inicial`. Multiplica o valor original.

- **Competência:** o mês/ano a que um valor se refere (ex.: salário de jan/2024
  tem competência 01/2024).

- **Pro-rata die:** cálculo proporcional aos dias, quando o período não fecha
  um mês cheio. Fonte comum de pequenas divergências entre cálculos.

- **Juros de mora:** acréscimo por atraso, aplicado (quando cabível) **sobre** o
  valor já corrigido. Correção ≠ juros; podem ou não incidir juntos.

- **SINDEC:** Sistema de Índices e Indicadores Econômicos e de Atualização de
  Valores, do TCDF. A calculadora que este projeto automatiza.

- **TCDF:** Tribunal de Contas do Distrito Federal.

- **COGEB:** área/equipe que executa o processo (usuária desta ferramenta).

- **API / endpoint:** endereço no servidor que recebe dados e devolve um
  resultado. Se a calculadora tiver um, dá para "conversar" com ela por
  programa em vez de digitar na tela.

- **Payload:** os dados enviados numa requisição (ex.: valor, datas, índice).

- **Gabarito de validação:** um cálculo feito manualmente no site, guardado para
  conferir se a automação chega no mesmo número.
