@echo off
REM ============================================================
REM  Pipeline Completo - COGEB
REM  Baixa fichas do SIGRH, extrai SEGURIDADE SOCIAL,
REM  corrige com IPCA-E e gera o Excel de saida.
REM
REM  Uso: duplo-clique (le dados/entrada/beneficiarios.csv)
REM       ou arraste um CSV sobre este arquivo.
REM ============================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo [ERRO] Ambiente Python (.venp) nao encontrado.
  echo Rode uma vez:  python -m venv .venv  ^&^&  .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

if "%~1"=="" (
  set "ENTRADA=dados\entrada\beneficiarios.csv"
) else (
  set "ENTRADA=%~1"
)

echo.
echo === Pipeline Completo COGEB ===
echo.
echo Entrada: %ENTRADA%
echo.

"%PY%" "src\main.py" --completo "%ENTRADA%"

echo.
if errorlevel 1 (
  echo [!] Terminou com erro. Verifique as mensagens acima.
) else (
  echo [OK] Arquivo gerado em dados\saida\
)
echo.
pause
