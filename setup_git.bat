@echo off
cd /d "%~dp0"
echo ===== Verificando Git =====
git --version
if errorlevel 1 (
    echo.
    echo GIT NAO ENCONTRADO. Instale o Git antes de continuar: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo.
echo ===== Configurando identidade (somente neste repositorio) =====
git config user.name "Davi Kilmer"
git config user.email "davikilmer13@gmail.com"
echo.
echo ===== Inicializando repositorio =====
if exist ".git" (
    echo Repositorio ja inicializado.
) else (
    git init
)
echo.
echo ===== Configurando branch principal =====
git branch -M main
echo.
echo ===== Adicionando arquivos =====
git add .
echo.
echo ===== Criando commit =====
git commit -m "Initial commit: PRA Divider plugin"
echo.
echo ===== Configurando remoto do GitHub =====
git remote remove origin >nul 2>&1
git remote add origin https://github.com/kilmer365/PRADivider.git
echo.
echo ===== Enviando para o GitHub (push) =====
git push -u origin main
echo.
echo ===== Status final =====
git status
echo.
echo ===== CONCLUIDO =====
pause
