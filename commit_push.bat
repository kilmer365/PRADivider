@echo off
cd /d "%~dp0"
echo ===== Adicionando alteracoes =====
git add -A
echo.
echo ===== Commit =====
git commit -m "Add English description to metadata.txt for QGIS repo requirements"
echo.
echo ===== Enviando para o GitHub =====
git push
echo.
echo ===== CONCLUIDO =====
pause
