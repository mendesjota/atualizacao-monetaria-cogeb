# Como baixar este programa do GitHub

Este guia ensina **passo a passo** como pegar o programa que está no GitHub
e colocar ele funcionando no seu computador. Qualquer pessoa consegue seguir.

---

## Índice

1. [O que é GitHub?](#1-o-que-é-github)
2. [Baixar o programa (2 jeitos)](#2-baixar-o-programa-2-jeitos)
3. [Instalar o Python](#3-instalar-o-python)
4. [Preparar o programa](#4-preparar-o-programa)
5. [Configurar a senha do SIGRH](#5-configurar-a-senha-do-sigrh)
6. [Rodar o programa](#6-rodar-o-programa)
7. [Problemas comuns](#7-problemas-comuns)

---

## 1. O que é GitHub?

O GitHub é um site que guarda programas. O nosso programa está lá.
Você vai **baixar uma cópia** para o seu computador.

O endereço do repositório (local do programa) é algo como:
```
https://github.com/anomalyco/atualizacao-monetaria-cogeb
```

> Substitua pelo endereço certo que a equipe técnica passar para você.

---

## 2. Baixar o programa (2 jeitos)

### Jeito 1 — Baixar o ZIP (mais fácil)

1. Abra o navegador (Chrome, Edge, Firefox)
2. Acesse o link do repositório no GitHub
3. Clique no botão verde **"Code"**
4. Clique em **"Download ZIP"**
5. O navegador vai baixar um arquivo `.zip`
6. Vá até a pasta de Downloads
7. **Clique com o botão direito** no arquivo ZIP → "Extrair tudo"
8. Escolha uma pasta para extrair (ex: `C:\Users\SeuNome\Desktop\`)
9. Pronto — a pasta extraída é o programa

### Jeito 2 — Clonar com Git (se tiver o Git instalado)

1. Abra o PowerShell (tecla Windows + X → Windows PowerShell)
2. Digite (substitua o endereço pelo certo):

```powershell
cd C:\Users\SeuNome\Desktop
git clone https://github.com/anomalyco/atualizacao-monetaria-cogeb.git
```

3. Pronto — a pasta `atualizacao-monetaria-cogeb` apareceu na sua Área de Trabalho

### O que tem dentro da pasta

```
atualizacao-monetaria-cogeb/
├── dados/
│   ├── entrada/          ← você coloca o CSV aqui
│   └── saida/            ← o resultado aparece aqui
├── src/                  ← programas (não mexa)
├── docs/                 ← manuais
├── Pipeline completo.bat ← clique aqui para rodar
├── requirements.txt      ← lista de peças necessárias
└── .env                  ← sua senha do SIGRH (você vai criar)
```

---

## 3. Instalar o Python

O Python é um programa que faz o nosso programa funcionar.
Se você já tiver instalado, pule esta etapa.

### Passo a passo

1. Acesse https://www.python.org/downloads/
2. Clique no botão amarelo **"Download Python 3.12"**
3. Execute o arquivo baixado
4. **IMPORTANTE:** Na primeira tela, marque a opção:
   **"Add Python to PATH"** (lá embaixo)
5. Clique em **"Install Now"**
6. Aguarde a instalação terminar
7. Feche a janela

### Testar se deu certo

1. Tecla Windows → digite `PowerShell` → abra
2. Digite: `python --version`
3. Deve aparecer algo como: `Python 3.12.x`

---

## 4. Preparar o programa

Agora você vai instalar as "peças" que o programa precisa.

### Abrir o PowerShell na pasta certa

1. Vá até a pasta do programa (a que você extraiu do ZIP)
2. Clique na **barra de endereço** do Windows Explorer (mostra o caminho)
3. Digite `powershell` e aperte Enter
4. Uma janela azul do PowerShell vai abrir **dentro da pasta certa**

### Digitar os comandos

Digite cada comando e aperte Enter. Aguarde cada um terminar:

```powershell
python -m venv .venv
```

> Cria um ambiente virtual (uma "caixa" isolada para o programa).
> Aguarde aparecer o cursor piscando de novo.

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
```

> Instala as peças necessárias. Pode demorar alguns segundos.

```powershell
.venv\Scripts\python -m playwright install firefox
```

> Instala o navegador Firefox que o programa usa.
> Aguarde baixar e instalar (pode demorar 1-2 minutos).

### Pronto! O programa está preparado.

---

## 5. Configurar a senha do SIGRH

O programa precisa da sua matrícula e senha do SIGRH para baixar
as fichas financeiras.

### Criar o arquivo .env

1. Na pasta do programa, **clique com o botão direito** em um espaço vazio
2. Novo → Arquivo de Texto
3. Nomeie como: `.env` (sem nome, só a extensão)
4. Se o Windows reclamar, nomeie como `_env.txt` e depois renomeie para `.env`
5. Abra o arquivo no Bloco de Notas (clique com o direito → Abrir com)
6. Escreva exatamente (substituindo pelos seus dados):

```
matricula_sigrh=SUA_MATRICULA
senha_sigrh=SUA_SENHA
```

> Exemplo real:
> ```
> matricula_sigrh=123456
> senha_sigrh=minhaSenha123
> ```

7. Salve (Ctrl + S) e feche

### Opção sem criar o .env

Se você não quiser salvar a senha, o programa vai pedir
toda vez que você rodar (a senha não aparece na tela enquanto digita).

---

## 6. Rodar o programa

1. Dê **dois cliques** no arquivo **`Pipeline completo.bat`**
2. Uma janela preta (terminal) vai abrir
3. O programa vai:
   - Verificar a conexão com o site do IPCA-E
   - Pedir sua senha (se não tiver criado o `.env`)
   - Baixar as fichas do SIGRH para cada pessoa
   - Extrair os valores de SEGURIDADE SOCIAL
   - Corrigir tudo com IPCA-E
   - Gerar o Excel
4. Quando terminar, aparece: **`✔ Concluído.`**
5. O resultado está em `dados/saida/resultado_AAAA_MM_DD.xlsx`

### ⏳ Quanto tempo leva?

- 1 pessoa: ~1-2 minutos
- 4 pessoas: ~5-10 minutos
- Quanto mais meses, mais demora

---

## 7. Problemas comuns

### "python não é reconhecido"

O Python não foi instalado ou não marcou "Add to PATH".
Solução: Reinstale o Python e **marque "Add Python to PATH"**.

### "pip não encontrado"

Mesmo problema acima. Reinstale o Python.

### "O PowerShell acusou erro mas não entendi"

Tire uma **foto da tela** e mande para a equipe técnica.
Ela consegue entender o que aconteceu.

### "Deu timeout / SIGRH não respondeu"

O programa tenta **3 vezes automaticamente** com 15s de intervalo.
Se mesmo assim falhar:
- O SIGRH pode estar fora do ar
- Sua internet pode estar lenta
- Tente de novo mais tarde

### "O Excel só tem R$ 0,00"

Alguma etapa falhou. Verifique se apareceu "ERRO" na tela.
Se o SIGRH falhou, tente rodar de novo.

### "GitHub pediu usuário e senha"

Se você escolheu "Clonar com Git" e não tem conta no GitHub:
- Prefira o **Jeito 1 (Download ZIP)** que é mais fácil
- Ou crie uma conta gratuita em github.com

---

## Resumo dos passos

| Passo | O que fazer |
|-------|-------------|
| 1 | Baixar o ZIP do GitHub e extrair |
| 2 | Instalar Python (marcar "Add to PATH") |
| 3 | Abrir PowerShell na pasta e digitar os 3 comandos |
| 4 | Criar o arquivo `.env` com matrícula e senha |
| 5 | Dar duplo-clique em `Pipeline completo.bat` |

> **Ainda com dúvida?** Peça ajuda para a equipe técnica da COGEB.
> Mande uma foto da tela que eles ajudam.
