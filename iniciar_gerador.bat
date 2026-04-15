@echo off
title Gerador de Assinaturas — Grupo Navesa
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

echo.
echo  Iniciando servidor em: http://localhost:5000
echo  Para acessar de outro PC na rede, use o IP desta maquina.
echo.
echo  Pressione CTRL+C para encerrar.
echo  ------------------------------------------------
echo.

python app.py

pause
