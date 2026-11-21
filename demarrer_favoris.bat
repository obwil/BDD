@echo off
call "%~dp0_python.bat" || exit /b 1
cd /d "%~dp0"

if not exist "activites.db" (
    echo ERREUR : activites.db introuvable.
    pause
    exit /b 1
)

:: Installer les dependances si besoin
"%PYTHON%" -m pip install fastapi "uvicorn[standard]" --quiet

:: Attendre que le serveur soit pret puis ouvrir l'interface
start "" cmd /c "timeout /t 3 /nobreak >nul && start "" "http://localhost:8000/static/favoris.html""

:: Lancer le serveur
"%PYTHON%" -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
