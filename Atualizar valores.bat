@echo off
REM ============================================================
REM  Atualizacao Monetaria - COGEB / SINDEC-TCDF
REM  Duplo-clique para rodar. Le a planilha de entrada e gera
REM  o Excel de saida com os valores corrigidos.
REM ============================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo [ERRO] Ambiente Python (.venv) nao encontrado.
  echo Rode uma vez:  python -m venv .venv  ^&^&  .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

echo.
echo === Atualizacao Monetaria COGEB ===
echo.
"%PY%" "src\main.py" %*

echo.
if errorlevel 1 (
  echo [!] Terminou com erro. Verifique as mensagens acima.
) else (
  echo [OK] Confira o resultado em: dados\saida\resultado.xlsx
)
echo.
pause
