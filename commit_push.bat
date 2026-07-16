@echo off
cd /d "%~dp0"
echo ===== Adicionando alteracoes =====
git add -A
echo.
echo ===== Commit =====
git commit -m "Fix bug, consolidate main class, update metadata links, clean up helper scripts"
echo.
echo ===== Enviando para o GitHub =====
git push
echo.
echo ===== Status final =====
git status
echo.
echo ===== CONCLUIDO =====
pause
