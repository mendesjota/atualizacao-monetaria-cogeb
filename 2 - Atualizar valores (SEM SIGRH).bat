@echo off
REM ============================================================
REM  Atualizacao Monetaria - COGEB / SINDEC-TCDF
REM  MODO SIMPLES: so corrige com IPCA-E os valores JA
REM  preenchidos na coluna valor_mensal do CSV.
REM  NAO entra no SIGRH e NAO baixa ficha financeira.
REM  Para baixar as fichas use "1 - Pipeline completo (COM SIGRH).bat"
REM ============================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo [ERRO] Ambiente Python ^(.venv^) nao encontrado.
  echo Rode uma vez, nesta pasta:
  echo    python -m venv .venv
  echo    .venv\Scripts\python -m pip install -r requirements.txt
  pause
  exit /b 1
)

echo.
echo ============================================================
echo  ATENCAO - MODO SIMPLES (SEM SIGRH)
echo ------------------------------------------------------------
echo  Este arquivo NAO baixa as fichas financeiras do SIGRH.
echo  Ele so corrige com IPCA-E o que ja estiver preenchido na
echo  coluna valor_mensal do CSV. Se essa coluna estiver 0, o
echo  resultado vai sair 0,00.
echo.
echo  Quer baixar as fichas do SIGRH?
echo  Feche esta janela e abra:
echo     1 - Pipeline completo (COM SIGRH).bat
echo ============================================================
echo.
choice /c SN /n /m "Continuar no modo simples? (S = sim / N = nao): "
if errorlevel 2 (
  echo Cancelado.
  echo.
  pause
  exit /b 0
)

echo.
echo === Atualizacao Monetaria COGEB (modo simples) ===
echo.
"%PY%" "src\main.py" %*

echo.
if errorlevel 1 (
  echo [!] Terminou com erro. Verifique as mensagens acima.
) else (
  echo [OK] Confira o resultado em: dados\saida\
)
echo.
pause
