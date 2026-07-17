@echo off
cd /d "%~dp0"
echo ===== Adicionando alteracoes =====
git add -A
echo.
echo ===== Commit =====
git commit -m "Fix Bandit B110: avoid bare except-pass in UTM CRS check"
echo.
echo ===== Enviando para o GitHub =====
git push
echo.
echo ===== CONCLUIDO =====
pause
