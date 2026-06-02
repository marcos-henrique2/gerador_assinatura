@echo off
title Gerador de Assinaturas - Grupo Navesa
color 0A

echo.
echo  ================================================
echo    GRUPO NAVESA - Gerador de Assinaturas v2.0
echo  ================================================
echo.

cd /d "%~dp0"

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo  [OK] Ambiente virtual ativado.
) else (
    echo  [AVISO] Ambiente virtual nao encontrado. Usando Python global...
)

REM --- Verifica se o .env existe ---
if not exist .env (
    echo.
    echo  [ERRO] Arquivo .env nao encontrado.
    echo  Rode primeiro:  configurar_admin.bat
    echo.
    pause
    exit /b 1
)

REM --- Verifica se o waitress esta instalado ---
python -c "import waitress" 2>nul
if errorlevel 1 (
    echo.
    echo  [ERRO] O servidor 'waitress' nao esta instalado.
    echo  Rode:  pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo  Iniciando servidor em: http://localhost:5000
echo  Painel admin em:       http://localhost:5000/admin
echo  Para acessar de outro PC na rede, use o IP desta maquina.
echo.
echo  Pressione CTRL+C para encerrar.
echo  ------------------------------------------------
echo.

waitress-serve --listen=0.0.0.0:5000 app:app

pause
