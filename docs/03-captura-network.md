# Como capturar a requisição da calculadora (aba Network)

Objetivo: descobrir se a calculadora do TCDF usa uma **API** e, se sim,
capturar exatamente o que ela envia e recebe. Isso decide a Fase 2.

> Faça 1 cálculo simples e conhecido, para servir também de **gabarito de
> validação**. Sugestão: R$ 1.500,00, de **jan/2024** até **jul/2024**.

---

## Passo a passo (Google Chrome ou Edge)

1. Abra a calculadora:
   <https://www2.tc.df.gov.br/sindec-sistema-de-indices-e-indicadores-economicos-e-de-atualizacao-de-valores/>
2. Pressione **F12** para abrir as Ferramentas do Desenvolvedor.
3. Clique na aba **Network** (Rede).
4. Marque a caixa **Preserve log** (Preservar log).
5. No filtro, clique em **Fetch/XHR** (mostra só chamadas de dados).
6. Clique no botão de **limpar** (🚫) para zerar a lista.
7. Agora **faça o cálculo no site**: preencha valor, data inicial, data final,
   índice e clique em calcular.
8. Vão aparecer linhas novas na aba Network. Clique na que parecer o cálculo
   (geralmente a que aparece logo após clicar em "calcular").

## O que copiar e colar de volta aqui

Para a requisição selecionada, na sub-aba **Headers**:

- [ ] **Request URL** (a URL completa)
- [ ] **Request Method** (GET ou POST)
- [ ] **Status Code**

Na sub-aba **Payload** (ou **Request** / "Form Data" / "Query String Parameters"):

- [ ] Todos os **parâmetros enviados** e seus valores
      (ex.: `valor=1500`, `dataInicial=01/2024`, `indice=IPCA-E`...)

Na sub-aba **Response** (Resposta):

- [ ] O **corpo da resposta** (se for JSON, copie tudo; se for HTML grande,
      copie o trecho que contém o valor calculado)

Na sub-aba **Headers → Request Headers**, verifique se há:

- [ ] `Cookie`, `X-CSRF-Token`, `Authorization` ou similar
      (indica que precisa de sessão/token — importante para automatizar)

### Atalho útil

Botão direito na requisição → **Copy** → **Copy as cURL (bash)**.
Cole aqui o resultado inteiro. O cURL contém URL, método, headers e payload
de uma vez só — é a forma mais completa.

> ⚠️ Antes de colar um cURL em local público, remova cookies/tokens pessoais.
> Como aqui é uso interno e o site é público, normalmente não há dado sensível,
> mas confira.

---

## Se NÃO aparecer nenhuma requisição ao calcular

Significa que o cálculo é feito **no próprio navegador (JavaScript)**, sem
chamar o servidor. Nesse caso:

1. Na aba **Sources** (Fontes), procure arquivos `.js` da página.
2. Ou copie o texto da página com a tabela de índices, se estiver visível.
3. Me avise — mudamos a estratégia para **replicar a fórmula (abordagem B)** e
   vou precisar da **tabela de índices** que o site usa.

---

## Onde salvar

Cole os achados em [02-investigacao-tcdf.md](02-investigacao-tcdf.md) seção 4,
ou simplesmente cole no chat que eu organizo.
