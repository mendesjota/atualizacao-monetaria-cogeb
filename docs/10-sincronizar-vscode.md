# Como sincronizar seu código com o GitHub (VS Code)

Este guia ensina a **atualizar** seu código local para ficar igual ao
que está no `main` do GitHub. Siga os passos abaixo.

---

## Índice

1. [Abrir o projeto no VS Code](#1-abrir-o-projeto-no-vs-code)
2. [Abrir o terminal](#2-abrir-o-terminal)
3. [Baixar as atualizações do GitHub](#3-baixar-as-atualizações-do-github)
4. [Verificar se deu certo](#4-verificar-se-deu-certo)
5. [Se aparecer "merge conflict" (conflito)](#5-se-aparecer-merge-conflict-conflito)
6. [Dicas](#6-dicas)

---

## 1. Abrir o projeto no VS Code

1. Abra o VS Code
2. Clique em **File** (Arquivo) → **Open Folder...** (Abrir Pasta)
3. Selecione a pasta do projeto (`atualizacao-monetaria-cogeb`)
4. A pasta vai aparecer na barra lateral esquerda

---

## 2. Abrir o terminal

1. Clique em **Terminal** (no menu superior) → **New Terminal**
2. Ou use o atalho: **Ctrl + '** (crase)
3. Uma janela vai abrir na parte de baixo do VS Code — é o terminal

---

## 3. Baixar as atualizações do GitHub

No terminal, digite um comando de cada vez, apertando **Enter** ao final de cada um:

```bash
git checkout main
```

> Muda para o branch `main` (a versão oficial).

```bash
git pull
```

> Baixa as alterações mais recentes do GitHub para o seu computador.

Se aparecer uma tela perguntando sobre mensagem de commit, apenas:
- Aperte **Esc**
- Digite `:q` e Enter (para sair)

Pronto. Seu código local agora está idêntico ao do GitHub.

---

## 4. Verificar se deu certo

No terminal, digite:

```bash
git status
```

Deve aparecer:

```
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

Isso significa que seu código está igual ao do GitHub.

---

## 5. Se aparecer "merge conflict" (conflito)

Isso acontece se você editou um arquivo **sem** puxar as atualizações primeiro.

### Resolvendo:

1. No terminal, digite:
   ```bash
   git stash
   ```
   Isso guarda suas alterações temporariamente.

2. Depois:
   ```bash
   git pull
   ```

3. Para recuperar suas alterações guardadas:
   ```bash
   git stash pop
   ```

Se ainda assim aparecer conflito, avise quem está cuidando do repositório
(provavelmente José) — ele resolve rapidamente.

---

## 6. Dicas

| Situação | Comando |
|----------|---------|
| Atualizar com o GitHub | `git checkout main` + `git pull` |
| Ver o status atual | `git status` |
| Ver o histórico | `git log --oneline -5` |
| Voltar atrás de uma alteração | Avise o responsável |

### Resumo — o que fazer toda vez antes de começar a trabalhar

1. Abrir o VS Code
2. **Terminal → New Terminal**
3. Digitar:
   ```bash
   git checkout main
   git pull
   ```
4. Pronto — seu código está atualizado.

---

> **Dúvidas?** Pergunte para o José.
