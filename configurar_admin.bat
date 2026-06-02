@echo off
setlocal enabledelayedexpansion
title Configuracao do Painel Admin - Grupo Navesa
color 0B

echo.
echo  ================================================
echo    CONFIGURACAO DO PAINEL ADMIN - Grupo Navesa
echo  ================================================
echo.

cd /d "%~dp0"

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo  [ERRO] Ambiente virtual nao encontrado.
    echo  Crie com:  python -m venv venv
    echo  Depois:    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo  Vamos definir a senha de acesso ao painel administrativo.
echo  (a senha NAO sera exibida na tela enquanto voce digita)
echo.

REM --- Le a senha sem exibir na tela usando PowerShell ---
for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "$s=Read-Host 'Digite a senha do admin' -AsSecureString; $b=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s); [Runtime.InteropServices.Marshal]::PtrToStringAuto($b)"`) do set "ADMIN_SENHA=%%P"

if "!ADMIN_SENHA!"=="" (
    echo.
    echo  [ERRO] Senha vazia. Operacao cancelada.
    echo.
    pause
    exit /b 1
)

echo.
echo  Gerando chaves de seguranca...

REM --- Gera SECRET_KEY e HASH via Python/werkzeug e escreve o .env ---
python -c "import os; from werkzeug.security import generate_password_hash; senha=os.environ['ADMIN_SENHA']; sk=os.urandom(32).hex(); h=generate_password_hash(senha); open('.env','w',encoding='utf-8').write('SECRET_KEY='+sk+chr(10)+'ADMIN_PASSWORD_HASH='+h+chr(10)+'FLASK_DEBUG=0'+chr(10)); print('   [OK] Arquivo .env criado/atualizado com sucesso.')"

if errorlevel 1 (
    echo.
    echo  [ERRO] Falha ao gerar o .env. Verifique se as dependencias
    echo         estao instaladas:  pip install -r requirements.txt
    echo.
    set "ADMIN_SENHA="
    pause
    exit /b 1
)

REM --- Limpa a senha da memoria do script ---
set "ADMIN_SENHA="

echo.
echo  ================================================
echo    PRONTO! Senha do painel configurada.
echo    Acesse o painel em:  http://localhost:5000/admin
echo  ================================================
echo.
pause
