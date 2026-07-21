@echo off
REM ============================================================
REM  Pipeline Completo - COGEB  (ESTE E O ARQUIVO DO DIA A DIA)
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
  echo [ERRO] Ambiente Python ^(.venv^) nao encontrado.
  echo Rode uma vez, nesta pasta:
  echo    python -m venv .venv
  echo    .venv\Scripts\python -m pip install -r requirements.txt
  echo    .venv\Scripts\python -m playwright install firefox
  pause
  exit /b 1
)

REM O SIGRH e acessado por um Firefox controlado pelo Playwright. Sem esse
REM navegador instalado o download da ficha falha em TODOS os beneficiarios,
REM e o programa segue direto para o calculo - parecendo que "pulou o SIGRH".
"%PY%" -c "from playwright.sync_api import sync_playwright" >nul 2>&1
if errorlevel 1 goto :faltapw
"%PY%" -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); p.firefox.launch(headless=True).close(); p.stop()" >nul 2>&1
if errorlevel 1 goto :faltapw
goto :entrada

:faltapw
echo [ERRO] O navegador Firefox do Playwright nao esta instalado.
echo Sem ele o programa NAO consegue baixar as fichas do SIGRH.
echo.
echo Rode uma vez, nesta pasta:
echo    .venv\Scripts\python -m pip install -r requirements.txt
echo    .venv\Scripts\python -m playwright install firefox
echo.
pause
exit /b 1

:entrada
if "%~1"=="" (
  if exist "dados\entrada\beneficiarios.csv" (
    set "ENTRADA=dados\entrada\beneficiarios.csv"
  ) else (
    set "ENTRADA=dados\entrada\_modelo_entrada.csv"
  )
) else (
  set "ENTRADA=%~1"
)

echo.
echo === Pipeline Completo COGEB (COM SIGRH) ===
echo.
echo Entrada: %ENTRADA%
echo.

REM Sem %%* no fim: arrastar um CSV repetia o caminho como 2o argumento,
REM que o main.py interpreta como arquivo de SAIDA - sobrescrevendo o CSV.
"%PY%" "src\main.py" --completo "%ENTRADA%"

echo.
if errorlevel 1 (
  echo [!] Terminou com erro. Verifique as mensagens acima.
) else (
  echo [OK] Arquivo gerado em dados\saida\
)
echo.
pause
