@echo off
title Servidor - Gerador de Assinaturas Navesa
color 0A

echo ===================================================
echo Iniciando o Gerador de Assinaturas da Navesa...
echo ===================================================
echo.

:: 1. Entra na pasta atual onde o script .bat esta salvo
cd /d "%~dp0"

:: 2. Ativa o ambiente virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Ambiente virtual ativado.
) else (
    echo [AVISO] Ambiente virtual 'venv' nao encontrado!
    echo Tentando rodar com o Python global...
)

echo.
echo O sistema esta rodando. Para desligar, feche esta janela.
echo ---------------------------------------------------

:: 3. Roda o aplicativo Flask
python app.py

:: 4. Se o sistema der algum erro e parar, o 'pause' impede a tela de fechar
pause