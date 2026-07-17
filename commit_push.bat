@echo off
cd /d "%~dp0"
echo ===== Removendo zip do controle de versao =====
git rm --cached PRADivider.zip
echo.
echo ===== Adicionando alteracoes =====
git add -A
echo.
echo ===== Commit =====
git commit -m "Stop tracking release zip package"
echo.
echo ===== Enviando para o GitHub =====
git push
echo.
echo ===== CONCLUIDO =====
pause
