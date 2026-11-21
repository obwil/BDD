@echo off
title Serveur BDD - ne pas fermer pendant l'utilisation
call "%~dp0_python.bat" || exit /b 1
cd /d "%~dp0"
if not exist "activites.db" (
    echo ERREUR : activites.db introuvable dans %CD%
    pause
    exit /b 1
)
echo Verification des dependances...
"%PYTHON%" -m pip install -r requirements.txt --quiet
echo.
echo Application disponible sur http://localhost:8000
echo Fermez cette fenetre pour arreter l'application.
echo.
"%PYTHON%" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
