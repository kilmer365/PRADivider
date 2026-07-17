@echo off
cd /d "%~dp0"
echo ===== Adicionando alteracoes =====
git add -A
echo.
echo ===== Commit =====
git commit -m "Bump version to 1.0.1"
echo.
echo ===== Enviando para o GitHub =====
git push
echo.
echo ===== CONCLUIDO =====
pause
